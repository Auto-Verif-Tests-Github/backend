import flask
import sqlite3
import csv


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
            PRIMARY KEY (id)
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
            classroom_linx TEXT,
            PRIMARY KEY (id)
        )""")
    dbcur.execute(f"""CREATE TABLE IF NOT EXISTS courses(
            id INTEGER AUTO_INCREMENT,
            stream_id INTEGER,
            name TEXT,
            teacher_id INTEGER,
            PRIMARY KEY (id)
        )""")
    dbcur.execute(f"""CREATE TABLE IF NOT EXISTS tasks(
            id INTEGER AUTO_INCREMENT,
            course_id INTEGER,
            stream_id INTEGER,
            start_date TEXT,
            deadline_date TEXT,
            name TEXT,
            PRIMARY KEY (id)
        )""")
    dbcur.execute(f"""CREATE TABLE IF NOT EXISTS solution(
            id INTEGER AUTO_INCREMENT,
            task_id INTEGER,
            people_id INTEGER,
            status TEXT,
            github_link TEXT,
            PRIMARY KEY (id)
        )""")


app = flask.Flask(__name__)


@app.route("/api/courses/")
def f1():
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
    return calc_request(courses, id, stream_id, name, teacher_id)


if __name__ == '__main__':
    create_db("syspro")
    app.run()
