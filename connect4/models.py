from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from channels.binding.websockets import WebsocketBinding
import datetime

# Create your models here.

@python_2_unicode_compatible
class Game(models.Model):
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player_1')
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player_2', blank=True, null=True)
    status = models.CharField(max_length=10)
    winner = models.CharField(max_length=10)
    created_date = models.DateTimeField(default=timezone.now)


    def __str__(self):
        if self.player2:
            return ' vs '.join([self.player1.username, self.player2.username])

        else:
            return 'Join now to play %s'%self.player1.username

    @property
    def start_date(self):
        return self.coin_set.order_by('created_date')[0].created_date

    @property
    def last_move(self):
        return self.coin_set.order_by('-created_date')[0]

    @property
    def last_action_date(self):
        return self.last_move.created_date

    def join_up(self, player_2):
        if self.player2 is None:
            self.player2 = player_2
            self.save()
            return True
        else:
            return False

    def make_move(self, player, row, column):
        try:
             self.coin_set.create(game=self, player=player, row=row, column=column)
        except:
             return False

        return True

# binding for updates in a single game
class GameBinding(WebsocketBinding):
    model = Game
    stream = "game"
    fields = ["game", "winner", "status"]

    @classmethod
    def group_names(cls, instance):
        return ["game-"+str(instance.id)]

    def has_permission(self, user, action, pk):
        gameObj = Game.objects.get(id = self.kwargs['game'])
        return (gameObj.player1.pk == user.pk) or (gameObj.player2.pk == user.pk)

# binding for all games
class GamesBinding(WebsocketBinding):
    model = Game
    stream = "games"
    fields = ["game", "player1", "player2", "winner", "status", "created_date"]

    @classmethod
    def group_names(cls, instance):
        return ["games"]

    def has_permission(self, user, action, pk):
        return False

@python_2_unicode_compatible
class Coin(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    column = models.IntegerField()
    row = models.IntegerField()
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return ' '.join([
            self.player, 'to', self.row, self.column
        ])

class CoinBinding(WebsocketBinding):
    model = Coin
    stream = "coins"
    fields = ["game", "player", "column", "row"]

    @classmethod
    def group_names(cls, instance):
        return ["game-"+str(instance.game.id)]

    def has_permission(self, user, action, pk):
        gameObj = Game.objects.get(id = self.kwargs['game'])
        return (gameObj.player1.pk == user.pk) or (gameObj.player2.pk == user.pk)

    # override to update the game state
    @classmethod
    def game_updating_consumer(cls, message, **kwargs):
        game = Game.objects.get(id = kwargs['game'])
        # ignore coins if game already won
        if game.winner == None or len(game.winner) == 0:
            CoinBinding.consumer(message, **kwargs)
            player = message.user
            game.status = "Last move by %s at %s" % (player.username, datetime.datetime.now())
            coins = Coin.objects.filter(game = game, player = player).order_by('-created_date')
            winner = CoinBinding.is_winner(coins)
            if (winner):
                game.winner = player.username
                game.status = "Won by %s" % player.username
            game.save()

    @classmethod
    def is_winner(cls, coins):
        newCoin = coins[0]
        antiClkDiag = [None for _ in range(0,7)]
        clkDiag = [None for _ in range(0,7)]
        horizontal = [None for _ in range(0,7)]
        vertical = [None for _ in range(0,4)]
        for direction in [antiClkDiag, clkDiag, horizontal]:
            direction[3] = newCoin
        vertical[0] = newCoin
        for coin in coins[1:]:
            colDiff = (coin.column - newCoin.column)
            rowDiff = (coin.row - newCoin.row)
            if colDiff == 0 and rowDiff in range(1,4):
                vertical[rowDiff] = coin
            elif rowDiff == 0 and colDiff in range(-3, 4):
                horizontal[colDiff + 3] = coin
            elif rowDiff == colDiff and colDiff in range(-3, 4):
                clkDiag[colDiff + 3] = coin
            elif rowDiff == -colDiff and colDiff in range(-3, 4):
                antiClkDiag[colDiff + 3] = coin

        return CoinBinding.connected_four(vertical) |\
               CoinBinding.connected_four(horizontal) | \
               CoinBinding.connected_four(antiClkDiag) | \
               CoinBinding.connected_four(clkDiag)


    @classmethod
    def connected_four(cls, direction):
        consecutive = 0
        for coin in direction:
            if coin != None:
                consecutive += 1
            else:
                consecutive = 0
            if consecutive >= 4:
                return True
        return False