import flask
import sqlite3
from csv import reader


class Parser_csv():
    def file_to_list_of_tuple(self, file):
        res = []
        with open(file, 'r', encoding='utf-8') as csvfile:
            rd = csv.reader(csvfile)
            for row in rd:
                res.append((row[0], row[1]))
        return res

    # arr содежит (ФИ, ник на гите)
    def download_list_to_table(self, table, cursor, arr):
        for i in range(1, len(arr)):
            cursor.execute(
                f'INSERT INTO {table} (name_surname,git_name) VALUES (?, ?)', arr[i])


if __name__ == '__main__':
    app.run()
