from flask import Flask, session, render_template
from flask import request, redirect
from db_connector import connect_to_database, execute_query
import sys

def qquery(query, data = None):
    db_connection = connect_to_database()
    if data == None:
        return execute_query(db_connection, query)
    else:
        return execute_query(db_connection, query, data)

def getPlayerList():
    db_connection = connect_to_database()
    query = "select ru.username, ru.id from registered_users ru inner join league l on ru.id = l.pid;"
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
        data = (int(player[1]), int(player[1]))
        result = execute_query(db_connection, query, data)
        result = list(result.fetchall())
        wins = []
        loses = []
        for r in result:
            if r[0] == player[1]:
                iswin = r[2] > r[3]
                opp = r[1]
            elif r[1] == player[1]:
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
        name = player[0]
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
            if players[x][1] == players[y][1]:
                res = "-"
            else:
                for z in db_results:
                    if z[0] == players[x][1] and z[1] == players[y][1]:
                        res = str(z[2]) + " " + str(z[3])
                    elif z[0] == players[y][1] and z[1] == players[x][1]:
                        res = str(z[3]) + " " + str(z[2])
            temp.append(res)
        results.append(temp)
    return results

def is_logged_in(session):
    if 'id' in session:
        if session['id'] == None:
            return False
        return True
    return False

app = Flask(__name__)
app.secret_key = "qpoerguinpqeirbunpwqrbiwergpvi4p50y93bn0456uy03569hj3v5690vhm38n"

legal_paths = ["/login", "/login_failed", '/register_account', '/heritage']
@app.before_request
def check():
    if request.path in legal_paths:
        return None
    if is_logged_in(session):
        return None
    return redirect("/login")
    

@app.route('/')
def hello_world():
    return redirect("/league")

'''
login and register pages, plus anything that doesn't require logging in.
'''

@app.route('/register_account', methods=["GET", "POST"])
def new_account():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        query = 'insert into registered_users (username, password) values (%s, %s)'
        data = (username, password)
        qquery(query, data)
        return redirect('/') 
    else:
        return render_template("register_account.html", post_addr='/register_account')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        query = 'select id from registered_users where username = %s and password = %s'
        data = (username, password)
        results = qquery(query, data)
        result = results.fetchone();
        if result == None:
            return redirect('/login_failed')
        session['id'] = result
        return redirect('/') 
    else:
        return render_template("register_account.html", post_addr='/login', login=True)

@app.route('/login_failed', methods=["GET"])
def login_failed():
        return render_template("register_account.html", post_addr='/login', login=True, error='Login Failed!')



@app.route('/heritage')
def heritage():
    return redirect("https://sites.google.com/site/magicbychirod/urf")

'''
league
'''

@app.route("/league")
def league():
    players = getPlayerList()
    results = getResultsArray(players)
    standings = createStandings(players)
    return render_template("league.html", players = players, results = results, standings = standings)

@app.route("/report/<int:opp>", methods=["GET","POST"])
def report(opp):
    if opp == session['id']:
        return redirect('/league')
    if request.method == "POST":
        wins = request.form['wins']
        loses = request.form['loses']
        db_connection = connect_to_database()
        query = "insert into results (p1, p2, p1_w, p2_w) values (%s, %s, %s, %s);"
        data = (session['id'], opp, wins, loses)
        execute_query(db_connection, query, data)
        return redirect('/league') 
    else:
        return render_template('report.html', id1=session['id'], id2=opp)

@app.route('/join', methods=["GET"])
def register():
    qquery("insert into league (id, pid) values (1, %s);", (session['id'],))
    return redirect("/league")
