from flask import Flask, g, render_template, request, redirect
import sqlite3
app = Flask(__name__)

# Database File
DATABASE = 'app.db'

# First Run SQL queries
FIRST_RUN = 'first.sql'

# To get the Database Instance (create connections)
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db
    

# When Page is loaded, close the db connection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Basic Command to  get a table using select commands
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

# Basic Command to execute sql query
def execute_db(query):
    cur = get_db()
    cur.execute(query)
    cur.commit()
    cur.close()

# on first run make the required tables
@app.route('/init')
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource(FIRST_RUN, mode='r') as f:
            db.cursor().execute(f.read())
        db.commit()
    return 'DB Initialised'


# Home Page - Display all the meetings
@app.route('/')
def index():
    init_db()
    return render_template('view.html',data = query_db('select * from meeting'))

# to add new meeting entry - show form and
@app.route('/add', methods=['POST', 'GET'])
def add_meeting():
    if request.method == 'POST':
        # the user has submitted the form
        # add the form data to the database
        sql = 'insert into meeting(venue,ondate,objectives,outcomes) \
        values("'+ request.form['venue'] +'","'+ request.form['ondate'] +'" \
        ,"' + request.form['objectives'] + '","' + request.form['outcomes'] + '")'
        execute_db(sql)
        return redirect('/')
    else:
        # show the user the submit form
        return render_template('add.html')

@app.route('/remove/<id>')
def remove_meeting(id):
  sql = 'delete from meeting where id=' + id
  execute_db(sql)
  return redirect('/')

@app.route('/edit/<id>',methods=['POST','GET'])
def edit_meeting(id):
    if request.method == 'POST':
        # the user has submitted the form
        # add the form data to the database
        sql = 'update meeting set venue="'+ request.form['venue'] +'" \
        ,ondate="'+ request.form['ondate'] +'" \
        ,objectives="'+ request.form['objectives'] +'" \
        ,outcomes="'+ request.form['outcomes'] +'" where id=' + id
        execute_db(sql)
        return redirect('/')
    else:
        # show the user the submit form
        sql = 'select * from meeting where id=' + id
        return render_template('add.html',editlink='/edit/'+id, data = query_db(sql))

@app.route('/filter')
def filter():
  return redirect('/')

@app.route('/filter/venue')
def filter_venue_f():
  sql = 'select distinct(venue) from meeting'
  return render_template('filtervenue.html',venues = query_db(sql))

@app.route('/filter/venue/<venue>')
def filter_venue(venue):
  sql='select * from meeting where venue="'+ venue +'"'
  return render_template('view.html',data = query_db(sql))

@app.route('/filter/date/<ondate>')
def filter_date(ondate):
  sql='select * from meeting where ondate="'+ ondate +'"'
  return render_template('view.html',data = query_db(sql))

@app.route('/filter/date',methods=['POST','GET'])
def filter_date_b():
  if request.method=="POST":
    url = '/filter/date/' + request.form['from'] + '/to/' + request.form['to']
    return redirect(url)
  else:
    return render_template('filterdate.html')

@app.route('/filter/date/<startdate>/to/<enddate>')
def filter_date_between(startdate,enddate):
  sql='select * from meeting where ondate between "'+ startdate +'" and "'+ enddate +'" '
  return render_template('view.html',data = query_db(sql))

@app.route('/search', methods=['GET'])
def search_meeting():
  sql = 'select * from meeting'
  if 'q' in request.args:
    term = request.args["q"]
    sql = 'select * from meeting where objectives like ("%'+ term +'%") \
        or outcomes like ("%'+ term +'%")'
  return render_template('view.html',data = query_db(sql))

# For running the app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
