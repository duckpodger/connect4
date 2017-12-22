from . import consumers
from channels.routing import route, route_class
from channels.generic.websockets import WebsocketDemultiplexer
from connect4.models import CoinBinding, GameBinding, GamesBinding

# handles the streams for a single game
class GameDemultiplexer(WebsocketDemultiplexer):
    channel_session_user = True
    http_session_user = True

    consumers = {
        "coins": CoinBinding.game_updating_consumer,
        "game": GameBinding.consumer,
    }

    def connection_groups(self, game):
        return ["game-" + game]

# handles the streams for all games
class GamesDemultiplexer(WebsocketDemultiplexer):
    channel_session_user = True
    http_session_user = True

    consumers = {
        "games": GamesBinding.consumer,
    }

    def connection_groups(self):
        return ["games"]

channel_routing = [
    route("websocket.connect", consumers.connect_game, path=r'^/connect4/games/(?P<game>\w+)$'),
    route("websocket.disconnect", consumers.game_disconnect, path=r'^/connect4/games/(?P<game>\w+)$'),
    route_class(GameDemultiplexer, path="/connect4/games/(?P<game>\w+)"),
    route("websocket.connect", consumers.connect_games, path=r'^/connect4/games$'),
    route("websocket.disconnect", consumers.games_disconnect, path=r'^/connect4/games$'),
    route_class(GamesDemultiplexer, path="/connect4/games"),
]