import flask
import sqlite3
import csv


def get_hash_password(s):
    return hash(s)


def calc_request(s, args*):


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
            id INTEGER AUTO_INCREMENT,
            name TEXT,
            github_name TEXT,
            stream_id INTEGER,
            PRIMARY KEY (id),
            FOREIGN KEY (stream_id) REFERENCES streams (id) ON DELETE CASCADE
        )""")
    dbcur.execute(f"""CREATE TABLE IF NOT EXISTS teachers(
            id INTEGER AUTO_INCREMENT,
            login TEXT,
            password TEXT,
            name TEXT,
            PRIMARY KEY (id)
        )""")
    dbcur.execute(f"""CREATE TABLE IF NOT EXISTS streams(
            id INTEGER AUTO_INCREMENT,
            name TEXT,
            classroom_link TEXT,
            PRIMARY KEY (id)
        )""")
    dbcur.execute(f"""CREATE TABLE IF NOT EXISTS courses(
            id INTEGER AUTO_INCREMENT,
            stream_id INTEGER,
            name TEXT,
            teacher_id INTEGER,
            PRIMARY KEY (id),
            FOREIGN KEY (stream_id) REFERENCES streams (id) ON DELETE CASCADE,
            FOREIGN KEY (teacher_id) REFERENCES teachers (id) ON DELETE CASCADE
        )""")
    dbcur.execute(f"""CREATE TABLE IF NOT EXISTS tasks(
            id INTEGER AUTO_INCREMENT,
            course_id INTEGER,
            stream_id INTEGER,
            start_date TEXT,
            deadline_date TEXT,
            name TEXT,
            PRIMARY KEY (id),
            FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE CASCADE,
            FOREIGN KEY (stream_id) REFERENCES streams (id) ON DELETE CASCADE
        )""")
    dbcur.execute(f"""CREATE TABLE IF NOT EXISTS solutions(
            id INTEGER AUTO_INCREMENT,
            task_id INTEGER,
            people_id INTEGER,
            status TEXT,
            github_link TEXT,
            task_id INTEGER,
            PRIMARY KEY (id),
            FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE,
            FOREIGN KEY (people_id) REFERENCES people (id) ON DELETE CASCADE
        )""")


app = flask.Flask(__name__)


@app.route("/api/courses/", methods=['get', 'create'], defaults={'id':})
def req_courses():
    query = flask.request.args.to_dict()
    id, stream_id, name, teacher_id = None, None, None, None
    if 'id' in query:
        id = query['id']
    if 'stream_id' in query:
        stream_id = query['stream_id']
    if 'name' in query:
        name = query['name']
    if 'teacher_id' in query:
        teacher_id = query['teacher_id']
    # json string
    return calc_request('courses', id, stream_id, name, teacher_id)


@app.route("/api/streams/", methods=['get', 'create'])
def req_streams():
    query = flask.request.args.to_dict()
    id, name, classroom_link = None, None, None
    if 'id' in query:
        id = query['id']
    if 'name' in query:
        name = query['name']
    if 'classroom_link' in query:
        classroom_link = query['classroom_link']
    # json string
    return calc_request('streams', id, name, classroom_link)


@app.route("/api/people/", methods=['get', 'create'])
def req_people():
    query = flask.request.args.to_dict()
    id, name, github_name, stream_id = None, None, None, None
    if 'id' in query:
        id = query['id']
    if 'name' in query:
        name = query['name']
    if 'github_name' in query:
        github_name = query['github_name']
    if 'stream_id' in query:
        stream_id = query['stream_id']
    # json string
    return calc_request('people', id, name, github_name, stream_id)


@app.route("/api/teachers/", methods=['get', 'create'])
def req_teachers():
    query = flask.request.args.to_dict()
    id, login, password, name = None, None, None, None
    if 'id' in query:
        id = query['id']
    if 'login' in query:
        login = query['login']
    if 'password' in query:
        password = query['password']
    if 'name' in query:
        name = query['name']
    # json string
    return calc_request('teachers', id, login, password, name)


@app.route("/api/tasks/", methods=['get', 'create'])
def req_tasks():
    query = flask.request.args.to_dict()
    id, course_id, stream_id, start_date, deadline_date, name = None, None, None, None, None, None
    if 'id' in query:
        id = query['id']
    if 'course_id' in query:
        course_id = query['course_id']
    if 'stream_id' in query:
        stream_id = query['stream_id']
    if 'start_date' in query:
        start_date = query['start_date']
    if 'deadline_date' in query:
        deadline_date = query['deadline_date']
    if 'name' in query:
        name = query['name']
    # json string
    return calc_request('tasks', id, course_id, stream_id, start_date, deadline_date)


@app.route("/api/solutions/", methods=['get', 'create'])
def req_solutions():
    query = flask.request.args.to_dict()
    id, task_id, people_id, status, github_link, task_id = None, None, None, None, None, None
    if 'id' in query:
        id = query['id']
    if 'task_id' in query:
        task_id = query['task_id']
    if 'people_id' in query:
        people_id = query['people_id']
    if 'status' in query:
        status = query['status']
    if 'github_link' in query:
        github_link = query['github_link']
    if 'task_id' in query:
        task_id = query['task_id']
    return calc_request('solutions', id, task_id, people_id, status, github_link, task_id)


if __name__ == '__main__':
    create_db("syspro")
    app.run()
