import flask
import sqlite3
import csv



#chanfe lastcomm
def get_hash_password(s):
    return hash(s)
def check_hash(cur_hash):
    dbcon = sqlite3.connect('syspro.db')
    dbcur = dbcon.cursor()
    dbcur.execute(f"SELECT password FROM teachers")
    hashes = dbcur.fetchall()
    dbcur.close()
    dbcon.close()
    return cur_hash in hashes
def calc_request(s, args):
    params = []
    for key, val in args.items():
        if val is not None:
            if isinstance(val, str):
                params.append(f'{key} = "{val}"')
            else:
                params.append(f'{key} = {val}')
    params = ' AND '.join(params)
    dbcon = sqlite3.connect('syspro.db')
    dbcur = dbcon.cursor()
    if params:
        dbcur.execute(f"SELECT * FROM {s} WHERE {params};")
    else:
        dbcur.execute(f"SELECT * FROM {s}")
    columns = [col[0] for col in dbcur.description]
    rows = {'items': [dict(zip(columns, row)) for row in dbcur.fetchall()]}
    dbcur.close()
    dbcon.close()
    return rows
def delete_el(s, args):
    if not(args['hash']) or not(check_hash(args['hash'])):
        flask.abort(403)
    params = []
    for key, val in args.items():
        if val is not None:
            if isinstance(val, str):
                params.append(f'{key} = "{val}"')
            else:
                params.append(f'{key} = {val}')
    params = ' AND '.join(params)
    dbcon = sqlite3.connect('syspro.db')
    dbcur = dbcon.cursor()
    if params:
        dbcur.execute(f"DELETE FROM {s} WHERE {params}")
        dbcon.commit()
    else:
        dbcur.close()
        dbcon.close()
        return
    dbcur.close()
    dbcon.close()

def adding_el_to_table(s, args):
    if not(args['hash']) or not(check_hash(args['hash'])):
        flask.abort(403)
    dbcon = sqlite3.connect('syspro.db')
    dbcur = dbcon.cursor()
    template = '('
    args_template = '('
    for key, val in args.items():
        if val is not None and key!='id':
            template = template+key+', '
            if isinstance(val, str):
                args_template = args_template+f'"{val}", '
            else:
                args_template = args_template+f'{val}, '
    template = template+')'
    args_template = args_template+')'
    if template != '()':
        template = template[:-3]+')'
        args_template = args_template[:-3]+')'
        dbcur.execute(f"INSERT INTO {s} {template} VALUES {args_template}")
        dbcon.commit()
    dbcur.close()
    dbcon.close()

class Parser_csv():
    def file_to_list_of_tuple(self, file):
        res = []
        with open(file, 'r', encoding='utf-8') as csvfile:
            rd = csv.reader(csvfile)
            for row in rd:
                res.append((row[0], row[1]))
        return res

    # arr содежит (ФИ, ник на гите)
    def download_list_to_table(self, dbcon, table, arr):
        dbcur = dbcon.cursor()
        for i in range(1, len(arr)):
            dbcur.execute(
                f'INSERT INTO {table} (name,github_name) VALUES (?, ?)', arr[i])
            dbcon.commit()
        dbcur.close()


def download_csv_to_db(db, file):
    dbcon = sqlite3.connect(db)
    parser = Parser_csv()
    ar = parser.file_to_list_of_tuple(file)
    parser.download_list_to_table(dbcon, 'people', ar)
    dbcon.close()


def create_db(name):
    dbcon = sqlite3.connect(name)
    dbcur = dbcon.cursor()
    dbcur.execute(f"""CREATE TABLE IF NOT EXISTS people(
            id INTEGER ,
            name TEXT,
            github_name TEXT,
            stream_id INTEGER,
            PRIMARY KEY (id),
            FOREIGN KEY (stream_id) REFERENCES streams (id) ON DELETE CASCADE
        )""")
    dbcur.execute(f"""CREATE TABLE IF NOT EXISTS teachers(
            id INTEGER ,
            login TEXT UNIQUE,
            password TEXT,
            name TEXT,
            PRIMARY KEY (id)
        )""")
    dbcur.execute(f"""CREATE TABLE IF NOT EXISTS streams(
            id INTEGER ,
            name TEXT,
            classroom_link TEXT,
            PRIMARY KEY (id)
        )""")
    dbcur.execute(f"""CREATE TABLE IF NOT EXISTS courses(
            id INTEGER ,
            stream_id INTEGER,
            name TEXT,
            teacher_id INTEGER,
            PRIMARY KEY (id),
            FOREIGN KEY (stream_id) REFERENCES streams (id) ON DELETE CASCADE,
            FOREIGN KEY (teacher_id) REFERENCES teachers (id) ON DELETE CASCADE
        )""")
    dbcur.execute(f"""CREATE TABLE IF NOT EXISTS tasks(
            id INTEGER ,
            course_id INTEGER,
            stream_id INTEGER,
            start_date INTEGER,
            deadline_date INTEGER,
            name TEXT,
            PRIMARY KEY (id),
            FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE CASCADE,
            FOREIGN KEY (stream_id) REFERENCES streams (id) ON DELETE CASCADE
        )""")
    dbcur.execute(f"""CREATE TABLE IF NOT EXISTS solutions(
            id INTEGER ,
            task_id INTEGER,
            people_id INTEGER,
            status TEXT,
            github_link TEXT,
            last_update TEXT,
            PRIMARY KEY (id),
            FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE,
            FOREIGN KEY (people_id) REFERENCES people (id) ON DELETE CASCADE
        )""")
    dbcon.commit()
    dbcur.close()
    dbcon.close()


app = flask.Flask(__name__)


@app.route("/api/courses/",methods=['GET', 'POST'])
def req_courses():
    if flask.request.args['del'] and flask.request.method == 'POST':
        delete_el('courses',flask.request.args.to_dict())
    elif flask.request.method == 'GET':
        return calc_request('courses', flask.request.args.to_dict())
    elif flask.request.method == 'POST':
        adding_el_to_table('courses', flask.request.args.to_dict())
    return str({"response": 1})

@app.route("/api/streams/",methods=['GET', 'POST'])
def req_streams():
    if flask.request.args['del'] and flask.request.method == 'POST':
        delete_el('streams',flask.request.args.to_dict())
    elif flask.request.method == 'GET':
        return calc_request('streams', flask.request.args.to_dict())
    elif flask.request.method == 'POST':
        adding_el_to_table('streams', flask.request.args.to_dict())
    return str({"response": 1})
#@app.route("/api/streams/?del=1")
@app.route("/api/people/",methods=['GET', 'POST'])
def req_people():
    if flask.request.args['del'] and flask.request.method == 'POST':
        delete_el('people',flask.request.args.to_dict())
    elif flask.request.method == 'GET':
        return calc_request('people', flask.request.args.to_dict())
    elif flask.request.method == 'POST':
        adding_el_to_table('people', flask.request.args.to_dict())
    return str({"response": 1})

@app.route("/api/teachers/",methods=['GET', 'POST'])
def req_teachers():
    if flask.request.args['password']:
        flask.request.args['password']=get_hash_password(flask.request.args['password'])
    if flask.request.args['del'] and flask.request.method == 'POST':
        delete_el('teachers',flask.request.args.to_dict())
    elif flask.request.method == 'GET':
        return calc_request('teachers', flask.request.args.to_dict())
    elif flask.request.method == 'POST':
        adding_el_to_table('teachers', flask.request.args.to_dict())
    return str({"response": 1})
@app.route("/api/tasks/",methods=['GET', 'POST'])
def req_tasks():
    if flask.request.args['del'] and flask.request.method == 'POST':
        delete_el('tasks', flask.request.args.to_dict())
    elif flask.request.method == 'GET':
        return calc_request('tasks', flask.request.args.to_dict())
    elif flask.request.method == 'POST':
        adding_el_to_table('tasks', flask.request.args.to_dict())
    return str({"response": 1})


@app.route("/api/solutions/",methods=['GET', 'POST'])
def req_solutions():
    if flask.request.args['del'] and flask.request.method == 'POST':
        delete_el('solutions',flask.request.args.to_dict())
    elif flask.request.method == 'GET':
        return calc_request('solutions', flask.request.args.to_dict())
    elif flask.request.method == 'POST':
        adding_el_to_table('solutions', flask.request.args.to_dict())
    return str({"response": 1})


if __name__ == '__main__':
    create_db("syspro.db")
    app.run()
