import csv
import datetime
import hashlib
import json
import sqlite3

import flask
from flask_cors import CORS


def get_hash_password(s):
    return hashlib.sha3_256(s.encode()).hexdigest()


def check_hash(cur_hash):
    if not cur_hash:
        return False
    dbcon = sqlite3.connect('syspro.db')
    dbcur = dbcon.cursor()
    hashes = dbcur.execute(f"SELECT password FROM teachers").fetchone()
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
    if not check_hash(args.get("hash")):
        flask.abort(403)
    params = []
    for key, val in args.items():
        if val is not None and key not in ['hash', 'del']:
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


def get_time():
    tm = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(hours=7)
    return int(tm.timestamp() * 1000)


def add_update_solution(args):
    dbcon = sqlite3.connect('syspro.db')
    dbcur = dbcon.cursor()
    num = len([v for k, v in args.items() if v is not None and k not in ['del', 'hash']])

    if num == 2 and 'id' in args and 'status' in args:
        el_time = get_time()
        el = {'date': el_time, 'status': args['status']}
        dbcur.execute(f'SELECT updates FROM solutions WHERE id={args["id"]}')
        updates = dbcur.fetchone()[0]
        js_obj = json.loads(updates)
        js_obj['updates'].append(el)
        dbcur.execute(
            f"UPDATE solutions SET updates = '{json.dumps(js_obj)}', status = '{args['status']}' WHERE id = {int(args['id'])}")
        dbcon.commit()
    else:
        adding_el_to_table('solutions', args)
    dbcur.close()
    dbcon.close()


def adding_el_to_table(s, args):
    if not check_hash(args.get("hash")):
        flask.abort(403)
    dbcon = sqlite3.connect('syspro.db')
    dbcur = dbcon.cursor()
    template = '('
    args_template = '('
    for key, val in args.items():
        if val is not None and key not in ['id', 'hash']:
            template = template + key + ', '
            if isinstance(val, str):
                args_template = args_template + f'"{val}", '
            else:
                args_template = args_template + f'{val}, '
    template = template + ')'
    args_template = args_template + ')'
    if template != '()':
        template = template[:-3] + ')'
        args_template = args_template[:-3] + ')'
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
    dbcur.execute("""CREATE TABLE IF NOT EXISTS people(
            id INTEGER ,
            name TEXT,
            github_name TEXT,
            stream_id INTEGER,
            PRIMARY KEY (id),
            FOREIGN KEY (stream_id) REFERENCES streams (id) ON DELETE CASCADE
        )""")
    dbcur.execute("""CREATE TABLE IF NOT EXISTS teachers(
            id INTEGER ,
            login TEXT UNIQUE,
            password TEXT,
            name TEXT,
            PRIMARY KEY (id)
        )""")
    dbcur.execute("""CREATE TABLE IF NOT EXISTS streams(
            id INTEGER ,
            name TEXT,
            classroom_link TEXT,
            PRIMARY KEY (id)
        )""")
    dbcur.execute("""CREATE TABLE IF NOT EXISTS courses(
            id INTEGER ,
            stream_id INTEGER,
            name TEXT,
            teacher_id INTEGER,
            PRIMARY KEY (id),
            FOREIGN KEY (stream_id) REFERENCES streams (id) ON DELETE CASCADE,
            FOREIGN KEY (teacher_id) REFERENCES teachers (id) ON DELETE CASCADE
        )""")
    dbcur.execute("""CREATE TABLE IF NOT EXISTS tasks(
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
    dbcur.execute("""CREATE TABLE IF NOT EXISTS solutions(
            id INTEGER ,
            task_id INTEGER,
            people_id INTEGER,
            status TEXT NOT NULL DEFAULT "N/A",
            github_link TEXT,
            updates TEXT NOT NULL DEFAULT '{"updates": []}',
            PRIMARY KEY (id),
            PRIMARY KEY (task_id, people_id)
            FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE,
            FOREIGN KEY (people_id) REFERENCES people (id) ON DELETE CASCADE
        )""")
    dbcon.commit()
    dbcur.close()
    dbcon.close()


app = flask.Flask(__name__)


@app.route("/api/courses/", methods=['GET', 'POST'])
def req_courses():
    if flask.request.form.get('del') and flask.request.method == 'POST':
        delete_el('courses', flask.request.form.to_dict())
    elif flask.request.method == 'GET':
        return calc_request('courses', flask.request.args.to_dict())
    elif flask.request.method == 'POST':
        adding_el_to_table('courses', flask.request.form.to_dict())
    return str({"response": 1})


@app.route("/api/streams/", methods=['GET', 'POST'])
def req_streams():
    if flask.request.form.get('del') and flask.request.method == 'POST':
        delete_el('streams', flask.request.form.to_dict())
    elif flask.request.method == 'GET':
        return calc_request('streams', flask.request.args.to_dict())
    elif flask.request.method == 'POST':
        adding_el_to_table('streams', flask.request.form.to_dict())
    return str({"response": 1})


@app.route("/api/people/", methods=['GET', 'POST'])
def req_people():
    if flask.request.form.get('del') and flask.request.method == 'POST':
        delete_el('people', flask.request.form.to_dict())
    elif flask.request.method == 'GET':
        return calc_request('people', flask.request.args.to_dict())
    elif flask.request.method == 'POST':
        adding_el_to_table('people', flask.request.form.to_dict())
    return str({"response": 1})


@app.route("/api/teachers/", methods=['GET', 'POST'])
def req_teachers():
    dic = flask.request.form.to_dict
    if flask.request.form.get('password'):
        dic['password'] = str(get_hash_password(flask.request.form.get('password')))
    if flask.request.form.get('del') and flask.request.method == 'POST':
        delete_el('teachers', dic)
    elif flask.request.method == 'GET':
        return calc_request('teachers', flask.request.args.to_dict())
    elif flask.request.method == 'POST':
        adding_el_to_table('teachers', dic)
    return str({"response": 1})


@app.route("/api/tasks/", methods=['GET', 'POST'])
def req_tasks():
    if flask.request.form.get('del') and flask.request.method == 'POST':
        delete_el('tasks', flask.request.form.to_dict())
    elif flask.request.method == 'GET':
        return calc_request('tasks', flask.request.args.to_dict())
    elif flask.request.method == 'POST':
        adding_el_to_table('tasks', flask.request.form.to_dict())
    return str({"response": 1})


@app.route("/api/solutions/", methods=['GET', 'POST'])
def req_solutions():
    if flask.request.form.get('del') and flask.request.method == 'POST':
        delete_el('solutions', flask.request.form.to_dict())
    elif flask.request.method == 'GET':
        return calc_request('solutions', flask.request.args.to_dict())
    elif flask.request.method == 'POST':
        add_update_solution(flask.request.form.to_dict())
    return str({"response": 1})


@app.route("/api/course/get.solutions/<int:course_id>")
def course_solutions(course_id):
    connection = sqlite3.connect('syspro.db')
    res = connection.execute(f'SELECT solutions.people_id, solutions.id, solutions.status, solutions.updates, tasks.id FROM solutions JOIN tasks ON solutions.task_id = tasks.id WHERE tasks.course_id = {course_id};').fetchall()
    items = dict()
    for el in res:
        people_id = el[0]
        solution_id = el[1]
        status = el[2]
        updates = el[3]
        task_id = el[4]

        if (item := items.get(str(people_id))) is not None:
            item.append(json.dumps({'solution_id': solution_id, 'status': status, 'updates': updates, 'task_id': task_id}))
        else:
            items[str(people_id)] = [json.dumps({'solution_id': solution_id, 'status': status, 'updates': updates, 'task_id': task_id})]
    return ''.join(['{', f'"items": [{json.dumps(items)}]', '}'])


if __name__ == '__main__':
    create_db("syspro.db")
    CORS(app)
    app.run()
