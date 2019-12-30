#!/usr/bin/python3

import json
import os
import sqlite3
import traceback 

from flask import Flask, g, render_template, request, Response

from auth import User, handle_login, handle_logout, login_required


def default_config():
    return dict(
        SECRET_KEY=os.urandom(128),
        DEBUG=True
    )


app = Flask(__name__)
app.config.update(default_config())
app.config.from_pyfile('config.py')
app.config['USERS'] = { x[0]: User(*x) for x in app.config['USERS'] }


def connect_db():
    db = sqlite3.connect(app.config['DB_PATH'])
#    db = sqlite3.connect(
#        'file:/%s?mode=ro'.format(app.config['DB_PATH']), uri=True
#    )
    db.row_factory = sqlite3.Row
    db.cursor().execute('PRAGMA foreign_keys=ON')
    return db


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_db()
    return db


@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.errorhandler(Exception)
def handle_exception(ex):
  ex_text = traceback.format_exc()
  return render_template('exception.html', ex=ex_text), 500


@app.route('/login', methods=['GET', 'POST'])
def login():
  return handle_login(lambda x: None, 'front')


@app.route('/logout')
@login_required
def logout():
  return handle_logout(lambda x: None)


#
# JSON API
#

class SQLite3RowEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, sqlite3.Row):
            return dict(obj)
        return super().default(self, obj)


def api_read_table(c, table):
    query = 'SELECT * FROM {}'.format(table)
    c.execute(query)

    return json.dumps(
        {r['id']: r for r in c.fetchall()}, cls=SQLite3RowEncoder
    )


def api_create_row(c, table, data):
    if 'id' in data:
        raise ValueError

    query = 'INSERT INTO {} ({}) VALUES ({})'.format(
        table,
        ', '.join(data),
        ', '.join(':{}'.format(k) for k in data)
    )

    c.execute(query, data)
    return json.dumps({'id': c.lastrowid})


def api_read_row(c, table, id):
    query = 'SELECT * FROM {} WHERE id = ?'.format(table)
    c.execute(query, (id,))
    return json.dumps(c.fetchone(), cls=SQLite3RowEncoder)


def api_update_row(c, table, id, data):
    if 'id' in data:
        raise ValueError
    data['id'] = id

    query = 'UPDATE {} SET {} WHERE id = :id'.format(
        table,
        ', '.join('{} = :{}'.format(k, k) for k in data)
    )

    c.execute(query, data)


def api_delete_row(c, table, id):
    query = 'DELETE FROM {} WHERE id = ?'.format(table)
    c.execute(query, (id,))


def api_list_tables(c):
    query = 'SELECT name FROM sqlite_master WHERE type = "table"'
    c.execute(query)
    return json.dumps([t[0] for t in c.fetchall()])


@app.route('/api/tables', methods=['GET'])
@login_required
def api_tables():
    db = get_db()
    c = db.cursor()
    return Response(api_list_tables(c), mimetype='application/json')


@app.route('/api/<table>', methods=['GET', 'POST'])
@login_required
def api_table(table):
    db = get_db()
    c = db.cursor()

    if request.method == 'GET':
        # retrieve a table
        return Response(api_read_table(c, table), mimetype='application/json')
    elif request.method == 'POST':
        # create a row
        with db:
            return Response(
                api_create_row(c, table, request.get_json()),
                mimetype='application/json'
            )
    else:
        # should not happen
        raise ValueError


@app.route('/api/<table>/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
@login_required
def api_table_id(table, id):
    db = get_db()
    c = db.cursor()

    if request.method == 'GET':
        # retrieve a row
        return Response(api_read_row(c, table, id), mimetype='application/json')
    elif request.method == 'PATCH':
        # update a row
        with db:
            api_update_row(c, table, id, request.get_json())
            return Response(status=200)
    elif request.method == 'DELETE':
        # delete a row
        with db:
            api_delete_row(c, table, id)
            return Response(status=200)
    else:
        # should not happen
        raise ValueError


@app.route('/posthorn/editor')
@login_required
def show_posthorn_editor():
    tables = json.loads(api_list_tables(get_db().cursor()))

    return render_template(
        'editor.html',
        tables=tables,
        model_type='PosthornModel'
    )


@app.route('/signet/editor')
@login_required
def show_signet_editor():
#    tables = json.loads(api_list_tables(get_db().cursor()))
    tables = ['awards', 'scribes', 'scroll_status']

    return render_template(
        'editor.html',
        tables=tables,
        model_type='SignetModel'
    )


if __name__ == '__main__':
    app.run()
