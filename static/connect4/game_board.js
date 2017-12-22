// Consider using d3 for the data binding of coins. I think that given the size of the d3 library, it is overkill right
// now

// todo, this should all be styling, should replace css with e.g. less so that I can do calculations in styling
// also should probably precompute these constants rather than calculate them client side
var rows = 6, columns = 7
var borderWidth = 5, gapToBoard = 100, discWidth = 80
var rowHeight = 100, columnWidth = 120
var colMargin = columnWidth - discWidth, rowMargin = rowHeight - discWidth
var initialX = borderWidth + colMargin + (discWidth / 2),  initialY = gapToBoard + borderWidth + rowMargin + (discWidth / 2)
var boardHeight = (2 * borderWidth) + (rows * rowHeight) + rowMargin
var boardWidth = (2 * borderWidth) + (columns * columnWidth) + colMargin
var textSize = 40

// since we alternate turns and player 1 always goes first
var nextPlayerIdx = (initialCoins.length + 1) % 2
var players = [player1, player2]
var nextEmpty = new Array(columns).fill(rows - 1)

var board = create_board()

var webSocketBridge = new channels.WebSocketBridge();
webSocketBridge.connect(wsUrl);

$(document).ready(function(){
    // set the next player
    set_next_player(nextPlayerIdx)

    // add the initially loaded coins
    for (let i = 0; i < initialCoins.length; i++) {
        var coin = initialCoins[i]
        var column = coin['column']
        add_coin(coin['row'], column , players.findIndex(function(player) { return player === coin['player']}))
    }

    if (winner) {
        playerWon(winner)
    }

    webSocketBridge.listen(function(action, stream) { });

    webSocketBridge.demultiplex('coins', function(action, stream) {
      var coin = action.data
      add_coin(coin['row'], coin['column'] , playerId2Idx[coin['player']])
      toggle_next_player()
    });

    webSocketBridge.demultiplex('game', function(action, stream) {
      var game = action.data
      $('#status').text(game.status)
      if ('winner' in game && game.winner != "") {
            playerWon(game.winner)
      }
    });
})

function playerWon(player) {
    $('.overlay').removeClass('hidden')
    if (player === thisPlayer) {
        $('#winner').text('You win!')
    } else {
        $('#winner').text('You lose!')
    }
}

function create_board() {
  var board = SVG('board')//.size(boardWidth, boardHeight + gapToBoard)
  board.viewbox(0, 0, boardWidth, boardHeight + gapToBoard)
  board.attr({preserveAspectRatio:'xMidYMid meet'})
  var defs = board.defs()
  var holes = defs.group()
  var holeEdges = defs.group()
  var mask = defs.mask()
  mask.rect("100%","100%").fill("white")
  for (let r = 0; r < rows; r++) {
     for (let c = 0; c < columns; c++) {
        var x = initialX + (c * columnWidth), y = initialY + (r * rowHeight)
        // holes are part of group that will perform the mask operation on the main board
        holes.circle(80).attr({fill:"black", cx: x, cy: y})
        // edges will provide the borders
        holeEdges.circle(80).attr({cx:x, cy:y}).addClass('edges')
     }
  }
  mask.use(holes)
  board.rect(boardWidth - (2 * borderWidth), boardHeight - (2 * borderWidth))
      .attr({x: borderWidth, y: gapToBoard + borderWidth})
      .addClass('board').addClass('boardRect')
      .maskWith(mask)
  board.rect(boardWidth - (2 * borderWidth), boardHeight - (2 * borderWidth))
      .attr({x: borderWidth, y: gapToBoard + borderWidth})
      .addClass('edges').addClass('boardRect')
  board.use(holeEdges)

  setup_columns(board)

  return board
}

function setup_columns(board) {
    for (let col = 0; col < columns; col++){
        function handle_click(){
            var player = players[nextPlayerIdx]
            // disable clicks until we get a coin from our opponent
            board.select('.clickColumn').addClass('inActive')
            webSocketBridge
                .stream('coins')
                .send({action:'create', data:{game: gameId, row: nextEmpty[col], player: thisPlayerId, column: col}})
        }
        var placeX = initialX + (col * columnWidth)
        board.rect(columnWidth, boardHeight + gapToBoard)
            .addClass('clickColumn')
            .attr({x: placeX - (columnWidth / 2), y: 0})
            .click(function(){ if (!this.hasClass('inActive')) { handle_click() }})
            .mouseover(function(){if (!this.hasClass('inActive')) {this.addClass('highlighted')}})
            .mouseout(function(){this.removeClass('highlighted')})

        board.text(""+(col+1))
            .addClass('boardText')
            .attr({ x: placeX , y: textSize / 2})
        $(document).keypress(function(e) {
          // 48 is ascii for 0
          if(e.which == (48+col+1)) {
            handle_click()
          }
        })
    }
}

function set_next_player(next){
    // toggle highlighted next player
    $('#player'+(nextPlayerIdx+1)).addClass('nextPlayer')
    
    // disable column click if we are not the next player
    if (players[nextPlayerIdx] == thisPlayer) {
        board.select('.clickColumn').removeClass('inActive')
    } else {
        board.select('.clickColumn').addClass('inActive')
    }
}

function toggle_next_player() {
    $('.nextPlayer').removeClass('nextPlayer')
    set_next_player(nextPlayerIdx^=1)
}

function add_coin(r, c, playerIdx) {
    if (r >= 0 && r < rows && c >= 0 && c < columns) {
        nextEmpty[c]--
        var destX = initialX + (c * columnWidth), destY = initialY + (r * rowHeight)
        var player = 'player'+(playerIdx+1)
        var coin = board.circle(discWidth)
            .attr({cx: destX, cy: 0})
            .addClass(player)
            .back()
            .animate(1000,'<>',0)
            .dy(destY)
    }
}