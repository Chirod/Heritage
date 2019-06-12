from flask import Flask, session, render_template
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

def createStandings(players):
    db_connection = connect_to_database()
    vals = []
    for player in players:
        query = "select p1, p2, p1_w, p2_w from results where p1 = %s or p2 = %s order by id desc"
        data = (int(player[2]), int(player[2]))
        result = execute_query(db_connection, query, data)
        result = list(result.fetchall())
        wins = []
        loses = []
        for r in result:
            if r[0] == player[2]:
                iswin = r[2] > r[3]
                opp = r[1]
            elif r[1] == player[2]:
                iswin = r[3] > r[2]
                opp = r[0]
            if opp in wins:
                if not iswin:
                    wins.remove(opp)
                    loses.append(opp)
            elif opp in loses:
                if iswin:
                    loses.remove(opp)
                    wins.append(opp)
            else:
                if iswin:
                    wins.append(opp)
                else:
                    loses.append(opp)
        score = len(wins) * 3
        possible = (len(players) - len(wins) - len(loses)) * 3 - 3 + score
        name = player[0] + " " + player[1]
        vals.append((name, score, possible))
    i = 1
    ret = []
    while len(vals) > 0:
        best = 0
        for x in range(len(vals)):
            if vals[x][1] > vals[best][1]:
                best = x
        temp = vals.pop(best)
        ret.append((i, temp[0], temp[1], temp[2]))
        i += 1
    return ret

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
app.secret_key = "qpoerguinpqeirbunpwqrbn"

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
    standings = createStandings(players)
    return render_template("league.html", players = players, results = results, standings = standings)

@app.route("/league/<string:error>")
def league_error(error):
    players = getPlayerList()
    results = getResultsArray(players)
    standings = createStandings(players)
    return render_template("league.html", players = players, results = results, standings = standings, error = error)

@app.route("/report/<int:id1>/<int:id2>", methods=["GET","POST"])
def report(id1, id2):
    if id1 == id2:
        return redirect('/league')
    if request.method == "POST":
        wins = request.form['wins']
        pin = request.form['pin']
        loses = request.form['loses']
        if checkPlayerPin(id1, pin):
            player = str(id1)
            opponent = str(id2)
        elif checkPlayerPin(id2, pin):
            player = str(id2)
            opponent = str(id1)
        else:
            return redirect('/league/PIN_ID_FAILED!')
        db_connection = connect_to_database()
        query = "insert into results (p1, p2, p1_w, p2_w) values (%s, %s, %s, %s);"
        data = (player, opponent, wins, loses)
        execute_query(db_connection, query, data)
        return redirect('/league') 
    else:
        return render_template('report.html', id1=id1, id2=id2)

@app.route('/register', methods=["POST","GET"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        db_connection = connect_to_database()
        query = "insert into players (first_name, last_name, pin) values (%s, %s, %s);"
        first = request.form['first']
        second = request.form['last']
        third = request.form['pin']
        data = (first, second, third)
        try:
            execute_query(db_connection, query, data)
        except:
            return redirect('/league/Failed to add you!')
        return redirect('/league') 
