from python_game.game import Game
from init import create_app
from flask import Flask, jsonify, request, render_template, abort, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import or_, and_, update, delete, insert
from database import db_session
from models import User, GameT, gameDetails, userStats, Tournament, Message
import os, ast, models, pdb, string, random
import auth, game_base, multiplayer, tournament

app = create_app()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route('/')
def home():
    button = "Login"
    url = "http://localhost:5000/login"
    if current_user.is_authenticated:
        button = "Logout"
        url = "http://localhost:5000/logout"
    return render_template('home.html', url = url, button = button)

@app.route('/play')
@login_required
def play():
    return render_template('play.html')

@app.route('/end_waiting', methods=['POST'])
@login_required
def end_waiting():
    current_user.is_waiting = False
    db_session.commit()
    return "OK"

@app.route('/profile')
@login_required                
def profile():
    stats_query = db_session.query(userStats).filter_by(user_id = current_user.id)
    stats = stats_query.first()
    
    if stats.played_games == "":
        return render_template('profile.html', username=current_user.username,
                                            game_count=0,
                                            win_rate=stats.win_rate)

    game_ids = ast.literal_eval(stats.played_games)
    game_count = len(game_ids)
    game_desc = []
    game_dates = []
    game_endings = []
    
    if game_count > 0:
        for id in game_ids:
            game = db_session.query(GameT).filter_by(id = id).first()

            opponent = None
            if current_user.id == game.w_player:
                opponent = db_session.query(User).filter_by(id = game.b_player).first()
            else:
                opponent = db_session.query(User).filter_by(id = game.w_player).first()
            
            opponent = opponent.username
            game_desc.append("Game with " + opponent)

            details = db_session.query(gameDetails).filter_by(game_id = id).first()
            game_dates.append(str(details.start_date))

            if details.winner == current_user.id:
                game_endings.append("win")
            elif details.winner < 1:
                if details.winner == -1 * current_user.id:
                    game_endings.append("draw-win")
                else:
                    game_endings.append("draw-loss")
            else:
                game_endings.append("loss")
    
    return render_template('profile.html', username=current_user.username,
                                            game_count=game_count,
                                            game_ids=game_ids,
                                            games=game_desc,
                                            game_dates=game_dates,
                                            game_endings=game_endings,
                                            win_rate=stats.win_rate)


@app.route('/replay/<string:game_id>', methods=['GET', 'POST'])
@login_required
def replay(game_id):
    if request.method == "GET":
        game = db_session.query(GameT).filter_by(id = game_id).first()
        if current_user.id == game.w_player:
            return render_template("whites_replay.html")
        else:
            return render_template("blacks_replay.html")
    else:
        game = db_session.query(GameT).filter_by(id = game_id).first()
        w_player = db_session.query(User).filter_by(id = game.w_player).first().username
        b_player = db_session.query(User).filter_by(id = game.b_player).first().username
        w_player = "Whites: " + w_player 
        b_player = "Blacks: " + b_player

        game_details = db_session.query(gameDetails).filter_by(game_id = game_id).first()
        moves = ast.literal_eval(game_details.moves)

        variable = request.get_json()
        if isinstance(variable, str) != True:
            return abort(404)
        
        move_counter = int(variable)

        py_game = Game([], [], None)

        neg = 0
        if move_counter < 0:
            move_counter *= -1
            neg = 1 

        if move_counter > len(moves):
            move_counter = len(moves)
        
        for i in range(move_counter):
            if moves[i] and len(moves[i]) == 1:
                if not neg:
                    move_counter = min(len(moves), move_counter + 1)
        
        if not neg:
            if move_counter < len(moves) and len(moves[move_counter]) == 1:
                move_counter = min(len(moves), move_counter + 1)
        else:
            if move_counter < len(moves) and len(moves[move_counter]) == 1:
                move_counter = min(len(moves), move_counter - 1)
    
        py_game.run(moves[:move_counter])

        w_won_figs = []
        b_won_figs = []

        name_board = [{}, {}, {}, {}, {}, {}, {}, {}]
        
        
        for fig in py_game.w_player.won_figures:
            w_won_figs.append(fig[0])

        for fig in py_game.b_player.won_figures:
            b_won_figs.append(fig[0])
        
        counter = 0
        for line in py_game.chess_board.board:
            for key in line:
                if line[key] == None:
                    name_board[counter][key] = "  "
                    continue
                name_board[counter][key] = line[key].name
            counter += 1

        taken_figures = py_game.w_player.won_figures + py_game.b_player.won_figures

        variables = dict(board = name_board,
                        alive_figures = py_game.alive_figures,
                        taken_figures = taken_figures,
                        move_counter = move_counter,
                        w_player = w_player,
                        b_player = b_player)

        return variables

if __name__=='__main__':
    app.run(debug=True)