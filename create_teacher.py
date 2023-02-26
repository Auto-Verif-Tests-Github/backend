import hashlib


def get_hash_password(s):
    return hashlib.sha3_256(s.encode()).hexdigest()


if __name__ == '__main__':
    from sqlite3 import connect
    from pathlib import Path
    from sys import argv

    if len(argv) < 5:
        print('invalid params [PATH_DATABASE] [LOGIN] [PASSWORD] [TEACHER_FULLNAME]')
        exit(1)

    database = Path(argv[1])
    if database.exists() and database.is_file():
        db = connect(database)
        db.execute(f'INSERT INTO teachers (login, password, name) VALUES ("{argv[2]}", "{get_hash_password(argv[3])}", "{argv[4]}");')
        db.commit()
        db.close()
    else:
        print('database not found')
