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

    person_id, has_modname, region, blazon, emblazon = do_query(c, 'SELECT people.id, people.surname IS NOT NULL OR people.prename IS NOT NULL, regions.name, people.blazon, people.emblazon FROM personae JOIN people ON personae.person_id = people.id JOIN regions ON people.region_id = regions.id WHERE personae.name = ?', name)[0]

    former = do_query(c, 'SELECT name FROM personae WHERE person_id = ? AND name != ? ORDER BY name', person_id, name);
    if former:
        former = [f[0] for f in former]

    if emblazon:
        emblazon = '<img class="emblazon" src="{}"/>'.format(url_for('static', filename='images/arms/' + emblazon))
    else:
        emblazon = '<div class="emblazon noarms"><div>I have not given<br/>Post Horn my<br/> arms. I am a<br/> bad person.</div></div>'

    awards = do_query(c, 'SELECT p2.name, award_types.name, awards.date, crowns.name, events.name FROM personae AS p1 JOIN personae AS p2 ON p1.person_id = p2.person_id JOIN awards ON p2.id = awards.persona_id JOIN award_types ON awards.type_id = award_types.id JOIN groups ON award_types.group_id = groups.id JOIN events ON awards.event_id = events.id LEFT OUTER JOIN crowns ON awards.crown_id = crowns.id WHERE p1.name = ? ORDER BY awards.date', name)

    return render_template(
        'persona.html',
        name=name,
        former=former,
        region=region,
        has_modname=has_modname,
        blazon=blazon,
        emblazon=emblazon,
        awards=awards
    )


@app.route('/person/<surname>/<prename>', methods=['GET'])
@login_required
def person(surname, prename):
    c = get_db().cursor()
    awards = do_query(c, 'SELECT personae.name, award_types.name, groups.name, awards.date FROM people JOIN personae ON people.id = personae.person_id JOIN awards ON personae.id = awards.persona_id JOIN award_types ON awards.type_id = award_types.id JOIN groups ON award_types.group_id = groups.id WHERE people.surname = ? AND people.prename = ? ORDER BY awards.date', surname, prename)

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
    begin = None
    end = None

    if request.method == 'POST':
        begin = request.form['begin'].strip()
        end = request.form['end'].strip()
        c = get_db().cursor()
        results = do_query(c, 'SELECT personae.name, award_types.name, awards.date, crowns.name, events.name FROM personae JOIN awards ON personae.id = awards.persona_id JOIN award_types ON awards.type_id = award_types.id JOIN events ON awards.event_id = events.id LEFT OUTER JOIN crowns ON awards.crown_id = crowns.id WHERE date(?) <= date(awards.date) AND date(awards.date) <= date(?) ORDER BY awards.date, personae.name, award_types.name', begin, end)

    return render_template(
        'date.html',
        begin=begin,
        end=end,
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
        results = do_query(c, 'SELECT mrp.name, awards.date, MAX(award_types.precedence) FROM awards JOIN personae ON awards.persona_id = personae.id JOIN award_types ON awards.type_id = award_types.id JOIN (SELECT personae.person_id, personae.name, MAX(awards.date) FROM personae JOIN awards ON personae.id = awards.persona_id GROUP BY personae.person_id ORDER BY personae.name) AS mrp ON mrp.person_id = personae.person_id WHERE award_types.precedence >= ? GROUP BY mrp.person_id ORDER BY award_types.precedence DESC, awards.date, mrp.name', min_precedence)

        headers = {
            1000: 'Duchy',
             900: 'County',
             800: 'Vicounty',
             700: 'Bestowed peerages',
             600: 'Court Barony',
             500: 'Grant of Arms awards',
             400: 'Grant of Arms',
             300: 'Award of Arms awards',
             200: 'Award of Arms'
        }

        x = collections.defaultdict(list)
        for r in results:
            x[headers[r[2]]].append((r[0], r[1]))
        results = x

    return render_template(
        'op.html',
        results=results
    )


@app.route('/reigns', methods=['GET'])
@login_required
def reigns():
    c = get_db().cursor()
    results = do_query(c, 'SELECT sov1 || " and " || sov2, begin, end FROM reigns ORDER BY begin')

    return render_template(
        'reigns.html',
        results=results
    )


@app.route('/backlog', methods=['GET', 'POST'])
@login_required
def backlog():
    c = get_db().cursor()
    results = do_query(c, 'SELECT personae.name, award_types.name, crowns.name, awards.date, events.name, scroll_status.name, scribes.name FROM awards JOIN personae ON awards.persona_id = personae.id JOIN award_types ON awards.type_id = award_types.id JOIN events ON awards.event_id = events.id LEFT OUTER JOIN crowns ON awards.crown_id = crowns.id JOIN scroll_status ON awards.scroll_status_id = scroll_status.id JOIN scribes ON awards.scribe_id = scribes.id WHERE awards.scroll_status_id != 4 ORDER BY awards.date, personae.name')

    return render_template(
        'backlog.html',
        results=results
    )


if __name__ == '__main__':
    app.run()
