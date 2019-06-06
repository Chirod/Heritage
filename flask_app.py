
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template
from flask import request, redirect
from db_connector import connect_to_database, execute_query
import sys

def getPlayerList():
    db_connection = connect_to_database()
    query = "select first_name, last_name, id from players;"
    players = execute_query(db_connection, query)
    return list(players.fetchall()) 

def checkPlayerPin(player_id, pin):
    db_connection = connect_to_database()
    query = "select 1 from players where id = %s and pin = %s;"
    data = (player_id, pin)
    result = execute_query(db_connection, query, data)
    rl = list(result.fetchall())
    return len(rl)

def getResultsArray(players):
    db_connection = connect_to_database()
    query = "select p1, p2, p1_w, p2_w from results"
    db_results = execute_query(db_connection, query)
    num_players = len(players)
    results = []
    for x in range(len(players)):
        temp = []
        for y in range(len(players)):
            res = "Report" 
            if players[x][2] == players[y][2]:
                res = "-"
            else:
                for z in db_results:
                    if z[0] == players[x][2] and z[1] == players[y][2]:
                        res = str(z[2]) + " " + str(z[3])
                    elif z[0] == players[y][2] and z[1] == players[x][2]:
                        res = str(z[3]) + " " + str(z[2])
            temp.append(res)
        results.append(temp)
    return results

app = Flask(__name__)

@app.route('/')
def hello_world():
    return redirect("/league")

@app.route('/heritage')
def heritage():
    return redirect("https://sites.google.com/site/magicbychirod/urf")

@app.route("/league")
def league():
    players = getPlayerList()
    results = getResultsArray(players)
    return render_template("league.html", players = players, results = results)

@app.route("/league/<string:error>")
def league_error(error):
    players = getPlayerList()
    results = getResultsArray(players)
    return render_template("league.html", players = players, results = results, error = error)

@app.route("/report/<int:id1>/<int:id2>", methods=["GET","POST"])
def report(id1, id2):
    if id1 == id2:
        return redirect('/league')
    if request.method == "POST":
        wins = request.form['wins']
        pin = request.form['pin']
        loses = request.form['loses']
        if checkPlayerPin(id1, pin):
            return redirect('/report/' + str(id1) + '/' + str(id2) + '/' + pin + '/' + str(wins) + '/' + str(loses))
        elif checkPlayerPin(id2, pin):
            return redirect('/report/' + str(id2) + '/' + str(id1) + '/' + pin + '/' + str(wins) + '/' + str(loses))
        else:
            return redirect('/league/PIN_ID_FAILED!')
    else:
        return render_template("report.html", id1=id1, id2=id2)    

@app.route("/report/<int:player>/<int:opponent>/<string:pin>/<int:mine>/<int:theirs>")
def report_ex(player, opponent, pin, mine, theirs):
    if checkPlayerPin(player, pin):
        db_connection = connect_to_database()
        query = "insert into results (p1, p2, p1_w, p2_w) values (%s, %s, %s, %s);"
        data = (player, opponent, mine, theirs)
        execute_query(db_connection, query, data)
        return redirect('/league') 
    else:
        return "pin doesnt match"

@app.route('/register', methods=["POST","GET"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        return redirect("/register/" + request.form["first"] + '/' + request.form["last"] + '/' + request.form["pin"])

@app.route('/register/<string:first>/<string:second>/<string:third>')
def add_player(first, second, third):
    db_connection = connect_to_database()
    query = "insert into players (first_name, last_name, pin) values (%s, %s, %s);"
    data = (first, second, third)
    try:
        execute_query(db_connection, query, data)
    except:
        return redirect('/league/Failed to add you!')
    return redirect('/league') 


