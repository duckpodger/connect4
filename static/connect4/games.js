var webSocketBridge = new channels.WebSocketBridge();
webSocketBridge.connect('/connect4/games');

var joiningGame = false

$(document).ready(function(){
    $('#newGame').on('submit', function(event){
        event.preventDefault();
        create_game();
    });
    $('.joinGame').on('submit', function(event){
        event.preventDefault();
        join_game(this);
    });

    webSocketBridge.listen(function(action, stream) { });

    webSocketBridge.demultiplex('games', function(action, stream) {
        // total cop-out
        // what i'd like to do is to recieve json, render a client side template and insert/update the tables.
        // if i had used mustache instead of django templates i could have reused templates from the server side
        if (!joiningGame){
            window.location.reload()
        }
    });
})

// todo could replace these with websocket send
function create_game() {
    $.ajax({
        url : ".", // the endpoint
        type : "POST", // http method
        data: $("#newGame").serialize(), // data sent with the post request

        // handle a successful response
        success : function(json) {},

        // handle a non-successful response
        error : function(xhr,errmsg,err) {}
    });
};

function join_game(form) {
    $.ajax({
        url : form.action, // the endpoint
        type : "PUT", // http method
        data: $(form).serialize(), // data sent with the post request

        // handle a successful response
        success : function (json){
              //var gameUrl = $(form).find('.game').attr('value')+"/"
              window.location.assign(form.action)
              joiningGame = true
        },

        // handle a non-successful response
        error : function(xhr,errmsg,err) {}
    });
};