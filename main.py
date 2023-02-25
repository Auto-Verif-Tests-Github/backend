import flask
import sqlite3
import csv


def get_hash_password(s):
    return hash(s)


def calc_request(s, args):
    params = []
    for key, val in args.items():
        if val != None:
            if isinstance(val, str):
                params.append(f'{key} = "{val}"')
            else:
                params.append(f'{key} = {val}')
    params = ' AND '.join(params)
    con = sqlite3.connect('syspro.db')
    cur = con.cursor()
    if params:
        cur.execute(f"SELECT * FROM {s} WHERE {params};")
    else:
        cur.execute(f"SELECT * FROM {s}")
    res = cur.fetchall()
    cur.close()
    con.close()
    return res


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
    con = sqlite3.connect(db)
    parser = Parser_csv()
    ar = parser.file_to_list_of_tuple(file)
    parser.download_list_to_table(con, 'people', ar)
    con.close()


def create_db(name):
    con = sqlite3.connect(name)
    dbcur = con.cursor()
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
            login TEXT,
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
            PRIMARY KEY (id),
            FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE,
            FOREIGN KEY (people_id) REFERENCES people (id) ON DELETE CASCADE
        )""")
    con.commit()
    dbcur.close()
    con.close()


app = flask.Flask(__name__)


@app.route("/api/courses/", methods=['get', 'create'], defaults={'id': None, 'stream_id': None, 'name': None, 'teacher_id': None})
def req_courses(id, stream_id, name, teacher_id):
    if flask.request.method == 'get':
        return calc_request('courses', flask.request.args.to_dict())
    elif flask.request.method == 'create':
        pass


@app.route("/api/streams/", methods=['get', 'create'], defaults={'id': None, 'name': None, 'classroom': None})
def req_streams(id, name, classroom_link):
    if flask.request.method == 'get':
        return calc_request('streams', flask.request.args.to_dict())
    elif flask.request.method == 'create':
        pass


@app.route("/api/people/", methods=['get', 'create'], defaults={'id': None, 'name': None, 'github_name': None, 'stream_id': None})
def req_people(id, name, github_name, stream_id):
    if flask.request.method == 'get':
        return calc_request('people', flask.request.args.to_dict())
    elif flask.request.method == 'create':
        pass


@app.route("/api/teachers/", methods=['get', 'create'], defaults={'id': None, 'login': None, 'password': None, 'name': None})
def req_teachers(id, login, password, name):
    if flask.request.method == 'get':
        return calc_request('teachers', flask.request.args.to_dict())
    elif flask.request.method == 'create':
        pass


@app.route("/api/tasks/", methods=['get', 'create'], defaults={'id': None, 'course_id': None, 'stream_id': None, 'start_date': None, 'deadline_date': None, 'name': None})
def req_tasks(id, course_id, stream_id, start_date, deadline_date, name):
    if flask.request.method == 'get':
        return calc_request('tasks', flask.request.args.to_dict())
    elif flask.request.method == 'create':
        pass


@app.route("/api/solutions/", methods=['get', 'create'], defaults={'id': None, 'task_id': None, 'people_id': None, 'status': None, 'github_link': None})
def req_solutions(id, task_id, people_id, status, github_link):
    if flask.request.method == 'get':
        return calc_request('solutions', flask.request.args.to_dict())
    elif flask.request.method == 'create':
        pass


if __name__ == '__main__':
    create_db("syspro.db")
    app.run()
