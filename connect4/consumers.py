from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http

@channel_session_user_from_http
def connect_game(message, game):
    Group('game-' + game).add(message.reply_channel)
    message.reply_channel.send({'accept':True})

@channel_session_user
def game_disconnect(message, game):
    Group('game-' + game).discard(message.reply_channel)


@channel_session_user_from_http
def connect_games(message):
    Group('games').add(message.reply_channel)
    message.reply_channel.send({'accept':True})

@channel_session_user
def games_disconnect(message):
    Group('games').discard(message.reply_channel)