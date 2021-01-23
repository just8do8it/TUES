var count = 0;
var sourceId = "";
var destinationId = "";
var prevColor = "";
var command = "";
var board = [];
var all_figures, w_won_figures, b_won_figures;

window.onbeforeunload = function () {
	quit_game();
	return "OK";
}

function quit_game(){
	$.ajax({
		url: '/quit_game',
		data: $('form').serialize(),
        type: 'POST',
		success: function(response){
			console.log(response);
		},
		error: function(error){
			console.log(error);
		}
	});
};

function clicked(clicked_id) {
	if (count == 0) {
		prevColor = document.getElementById(clicked_id).style.backgroundColor;
		sourceId = clicked_id;
		document.getElementById(clicked_id).style.backgroundColor = "#5c5c5c";
		count++;
	} else {
		destinationId = clicked_id;
		document.getElementById(sourceId).style.backgroundColor = prevColor;
		count = 0;
		command = sourceId + "-" + destinationId;
		sendCommand();
	}
}

function sendCommand() {
	var game = new String(window.location);
	game.slice(21);
	fetch(game, {
	    method: 'POST',
		body: JSON.stringify(command),
		headers: {
			'Content-Type': 'application/json'
		}
	}).then(function (response) {
		response.json().then(function(data) {
			console.log(data);
			board = data["board"];
			all_figures = data["all_figures"];
			w_won_figures = data["w_won_figures"];
			b_won_figures = data["b_won_figures"];

			changeHTML();
		});
	});
}

function changeHTML() {
	for (var i = 0; i < 8; i++) {
		var currLine = board[i];

		for (var key in currLine) {
			if (currLine[key] == "  ") {
				document.getElementById(key + String(i + 1)).innerHTML = "&nbsp;";
				continue;
			}

			var currFig;
			var black = 0;

			for (var j = 0; j < all_figures.length; ++j) {
				currFig = all_figures[j];

				if (String.fromCharCode(currFig[0]) == key && currFig[1] == (i + 1)) {
					if (currFig[2] == "black") {
						black = 1;
					}
				}
			}

			if (currLine[key] == "R1" || currLine[key] == "R2") {
				if (black)
					document.getElementById(key + String(i + 1)).innerHTML = "&#9820;";
				else
					document.getElementById(key + String(i + 1)).innerHTML = "&#9814;";
			} 

			else if (currLine[key] == "H1" || currLine[key] == "H2") {
				if (black)
					document.getElementById(key + String(i + 1)).innerHTML = "&#9822;";
				else
					document.getElementById(key + String(i + 1)).innerHTML = "&#9816;";
			} 

			else if (currLine[key] == "B1" || currLine[key] == "B2") {
				if (black)
					document.getElementById(key + String(i + 1)).innerHTML = "&#9821;";
				else
					document.getElementById(key + String(i + 1)).innerHTML = "&#9815;";
			} 

			else if (currLine[key] == "Q1") {
				if (black)
					document.getElementById(key + String(i + 1)).innerHTML = "&#9819;";
				else
					document.getElementById(key + String(i + 1)).innerHTML = "&#9813;";
			} 

			else if (currLine[key] == "K1") {
				if (black)
					document.getElementById(key + String(i + 1)).innerHTML = "&#9818;";
				else
					document.getElementById(key + String(i + 1)).innerHTML = "&#9812;";
			}

			else if (currLine[key][0] == "P") {
				if (black)
					document.getElementById(key + String(i + 1)).innerHTML = "&#9823;";
				else
					document.getElementById(key + String(i + 1)).innerHTML = "&#9817;";
			}
		}
	}
}