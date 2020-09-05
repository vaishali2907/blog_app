# import sqlite3
import mysql.connector
from mysql.connector import errorcode
import click
from flask import current_app, g
from flask.cli import with_appcontext
from . import schema


def get_db():
    if 'db' not in g:
        # g.db = sqlite3.connect(current_app.config['DATABASE'], detect_types=sqlite3.PARSE_DECLTYPES)
        # g.db.row_factory = sqlite3.Row
        try:
            g.db = mysql.connector.connect(**current_app.config['DATABASE'])
        except mysql.connector.Error as err:
            print(err)
    return g.db


def close_db(self):
    db = g.pop('db', None)
    if db is not None:
        db.close()


@click.command('init-db')
@with_appcontext
def init_db_command():
    get_db()
    click.echo('Initialized the database...')
    use_database()


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def create_database(cursor):
    try:
        cursor.execute("CREATE DATABASE {}".format(schema.DATABASE))
    except mysql.connector.Error as err:
        print("Failed creating Database {} because of {}".format(schema.DATABASE, err))
        exit(1)


def use_database():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("USE {}".format(schema.DATABASE))
        print("Database {} changed successfully!!!".format(schema.DATABASE))
        create_table(cursor)
    except mysql.connector.Error as err:
        print("Database {} doesn't exits!!!".format(schema.DATABASE))
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_database(cursor)
            print("Database {} successfully created!!!".format(schema.DATABASE))
            db.database = schema.DATABASE
            cursor.execute("USE {}".format(schema.DATABASE))
            print("Database {} changed successfully!!!".format(schema.DATABASE))
            create_table(cursor)
        else:
            print(err)
            exit(1)


def create_table(cursor):
    try:
        for table in schema.TABLES:
            print("Creating table {}: ".format(table), end='')
            create_statement = schema.TABLES[table]
            cursor.execute(create_statement)
            print("Table successfully created!!!")
    # except Exception as err:
    #     print(err)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("Table {} already exits!!!")
        else:
            print(err)
    else:
        print("OK!!")
