#!/usr/bin/python3

import os
import sqlite3
import traceback

from flask import Flask, g, redirect, render_template, request, url_for

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


def do_query(cursor, query, *params):
    cursor.execute(query, params)
    return [tuple(r) for r in cursor.fetchall()]


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


@app.route('/')
@login_required
def front():
    return render_template(
        'front.html'
    )


@app.route('/persona/<name>', methods=['GET'])
@login_required
def persona(name):
    c = get_db().cursor()
    awards = do_query(c, 'SELECT p2.name, award_types.name, awards.date FROM personae AS p1 JOIN personae AS p2 ON p1.person_id = p2.person_id JOIN awards ON p2.id = awards.persona_id JOIN award_types ON awards.type_id = award_types.id WHERE p1.name = ? ORDER BY awards.date', name)

    return render_template(
        'persona.html',
        name=name,
        awards=awards
    )


@app.route('/person/<surname>/<prename>', methods=['GET'])
@login_required
def person(surname, prename):
    c = get_db().cursor()
    awards = do_query(c, 'SELECT personae.name, award_types.name, awards.date FROM people JOIN personae ON people.id = personae.person_id JOIN awards ON personae.id = awards.persona_id JOIN award_types ON awards.type_id = award_types.id WHERE people.surname = ? AND people.prename = ? ORDER BY awards.date', surname, prename)

    return render_template(
        'person.html',
        surname=surname,
        prename=prename,
        awards=awards
    )


# TODO: add checkbox for name when given vs name last used?

@app.route('/award', methods=['GET', 'POST'])
@login_required
def award():
    results = None

    c = get_db().cursor()
    awards_sca = do_query(c, 'SELECT award_types.id, award_types.name FROM award_types WHERE award_types.group_id = 1 ORDER BY award_types.name')
    awards_dw = do_query(c, 'SELECT award_types.id, award_types.name FROM award_types WHERE award_types.group_id = 2 ORDER BY award_types.name')
    awards_id = do_query(c, 'SELECT award_types.id, award_types.name FROM award_types WHERE award_types.group_id = 27 ORDER BY award_types.name')
    awards_nm = do_query(c, 'SELECT award_types.id, award_types.name FROM award_types WHERE award_types.group_id = 3 ORDER BY award_types.name')
    awards_aa = do_query(c, 'SELECT award_types.id, award_types.name FROM award_types WHERE award_types.group_id = 4 ORDER BY award_types.name')
    awards_kc = do_query(c, 'SELECT award_types.id, award_types.name FROM award_types WHERE award_types.group_id = 5 ORDER BY award_types.name')
    awards_st = do_query(c, 'SELECT award_types.id, award_types.name FROM award_types WHERE award_types.group_id = 25 ORDER BY award_types.name')
    awards_gv = do_query(c, 'SELECT award_types.id, award_types.name FROM award_types WHERE award_types.group_id = 30 ORDER BY award_types.name')

    if request.method == 'POST':
        a_ids = [int(v) for v in request.form if v.isdigit()]
        results = do_query(c, 'SELECT personae.name, award_types.name, awards.date FROM awards JOIN personae ON awards.persona_id = personae.id JOIN award_types ON awards.type_id = award_types.id WHERE award_types.id IN ({}) ORDER BY awards.date, personae.name'.format(','.join(['?'] * len(a_ids))), *a_ids)

    return render_template(
        'award.html',
        awards_sca=awards_sca,
        awards_dw=awards_dw,
        awards_id=awards_id,
        awards_nm=awards_nm,
        awards_aa=awards_aa,
        awards_kc=awards_kc,
        awards_st=awards_st,
        awards_gv=awards_gv,
        results=results
    )


@app.route('/modern', methods=['GET', 'POST'])
@login_required
def modern_search():
    matches = []

    if request.method == 'POST':
        prename = request.form['prename'].strip()
        surname = request.form['surname'].strip()

        if prename or surname:
            c = get_db().cursor()

            qhead = 'SELECT id, surname, prename FROM people WHERE '

            if surname:
                if prename:
                    matches = do_query(c, qhead + 'surname LIKE ? AND prename LIKE ?', '%{}%'.format(surname), '%{}%'.format(prename))
                else:
                    matches = do_query(c, qhead + 'surname LIKE ?', '%{}%'.format(surname))
            elif prename:
                matches = do_query(c, qhead + 'prename LIKE ?', '%{}%'.format(prename))

            if len(matches) == 1:
                return redirect(url_for('person', surname=matches[0][1], prename=matches[0][2]))

    return render_template(
        'modern.html',
        matches=matches
    )


@app.route('/sca', methods=['GET', 'POST'])
@login_required
def sca_search():
    matches = []

    if request.method == 'POST':
        persona = request.form['persona'].strip()
        if persona:
            c = get_db().cursor()
            matches = do_query(c, 'SELECT id, name FROM personae WHERE name LIKE ?', '%{}%'.format(persona))

            if len(matches) == 1:
                return redirect(url_for('persona', name=matches[0][1]))

    return render_template(
        'sca.html',
        matches=matches
    )


@app.route('/date', methods=['GET', 'POST'])
@login_required
def date():
    results = None

    if request.method == 'POST':
        begin = request.form['begin'].strip()
        end = request.form['end'].strip()
        c = get_db().cursor()
        results = do_query(c, 'SELECT personae.name, award_types.name, awards.date FROM personae JOIN awards ON personae.id = awards.persona_id JOIN award_types ON awards.type_id = award_types.id WHERE datetime(?) <= datetime(awards.date) AND datetime(awards.date) <= datetime(?) ORDER BY awards.date', begin, end)

    return render_template(
        'date.html',
        results=results
    )




@app.route('/reign', methods=['GET', 'POST'])
@login_required
def reign():
    return render_template(
        'front.html'
    )


@app.route('/op', methods=['GET', 'POST'])
@login_required
def op():
    results = None

    if request.method == 'POST':
        min_precedence = request.form['precedence']
        c = get_db().cursor()
        results = do_query(c, 'SELECT mrp.name, award_types.name, awards.date, MAX(award_types.precedence) FROM awards JOIN personae ON awards.persona_id = personae.id JOIN award_types ON awards.type_id = award_types.id JOIN (SELECT personae.person_id, personae.name, MAX(awards.date) FROM personae JOIN awards ON personae.id = awards.persona_id GROUP BY personae.person_id ORDER BY personae.name) AS mrp ON mrp.person_id = personae.person_id WHERE award_types.precedence >= ? GROUP BY mrp.person_id ORDER BY award_types.precedence DESC, awards.date, mrp.name', min_precedence)

    return render_template(
        'op.html',
        results=results
    )


if __name__ == '__main__':
    app.run()
