from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import models
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.db.models import Q


def signup(request):
    if request.method =='POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('games')
    elif request.method != 'GET':
        return HttpResponse(status = 405)
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def games(request):
    if request.method =='POST':
        game = models.Game(player1 = request.user, status = "advertising")
        game.save()
        response = HttpResponse(status=201)
        response['Location'] = "games/%s" % game.id
        return response
    if request.method != 'GET':
        return HttpResponse(status = 405)
    waiting = models.Game.objects\
        .filter(player2 = None)\
        .order_by('created_date')
    playing = models.Game.objects\
        .filter(Q(player1 = request.user) | Q(player2 = request.user))\
        .exclude(player2 = None)\
        .order_by('created_date')
    return render(request, 'games.html', {'waiting': waiting, 'playing': playing})

@login_required
def game(request, game):
    game = models.Game.objects.get(id = game)
    if request.method =='PUT':
        if (game.player1 == request.user) | (game.player2 != None):
            return HttpResponse(status = 403)
        else:
            game.player2 = request.user
            game.status = "Started"
            game.save()
            response = HttpResponse(status=201)
            response['Location'] = "games/%s" % game.id
            return response
    elif request.method != 'GET':
        return HttpResponse(status = 405)
    coins = models.Coin.objects.filter(game = game)
    coinJson = str([{'player': str(coin.player.username), 'column': coin.column, 'row': coin.row} for coin in coins])
    return render(request, "game_board.html", {'game':game, 'coins':coinJson})

@login_required
def coins(request, game):
    game = models.Game.objects.get(id = game)
    if request.method =='POST':
        column = int(request.POST.get('column'))
        row = int(request.POST.get('row'))
        playerId = request.POST.get('player')
        player = User.objects.get(username = playerId)
        coin = models.Coin(game = game, player = player, column = column, row = row)
        coin.save()
        return HttpResponse(201)
    else:
        return HttpResponse(status = 405)
