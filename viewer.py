#!/usr/bin/python3

import itertools
import os
import sqlite3
import traceback

from flask import Flask, flash, g, redirect, render_template, request, url_for

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


@app.route('/privacy')
def privacy():
    return render_template(
        'privacy.html'
    )

# FIXME: always display with most recent name
# FIXME: clean up queries

@app.route('/persona/<name>', methods=['GET'])
def persona(name):
    c = get_db().cursor()

    person_id, has_modname, region, blazon, emblazon = do_query(c, 'SELECT people.id, people.surname IS NOT NULL OR people.forename IS NOT NULL, regions.name, people.blazon, people.emblazon FROM personae JOIN people ON personae.person_id = people.id JOIN regions ON people.region_id = regions.id WHERE personae.name = ?', name)[0]

    cur_id, curname, _ = do_query(c, 'SELECT personae.id, personae.name, MAX(awards.date) FROM awards JOIN personae ON awards.persona_id = personae.id JOIN people ON people.id = personae.person_id WHERE people.id = ?', person_id)[0];

    former = do_query(c, 'SELECT name FROM personae WHERE person_id = ? AND id != ? ORDER BY name', person_id, cur_id);
    if former:
        former = [f[0] for f in former]

    if emblazon:
        emblazon = '<img class="emblazon" src="{}"/>'.format(url_for('static', filename='images/arms/' + emblazon))
    else:
        emblazon = '<div class="emblazon noarms"><div>I have not given<br/>Post Horn my<br/> registered<br/> arms.</div></div>'

    awards = do_query(c, 'SELECT p2.name, award_types.name, awards.date, crowns.name, events.name FROM personae AS p1 JOIN personae AS p2 ON p1.person_id = p2.person_id JOIN awards ON p2.id = awards.persona_id JOIN award_types ON awards.type_id = award_types.id JOIN events ON awards.event_id = events.id LEFT OUTER JOIN crowns ON awards.crown_id = crowns.id WHERE p1.name = ? ORDER BY awards.date, award_types.name', name)

    return render_template(
        'persona.html',
        name=curname,
        former=former,
        region=region,
        has_modname=has_modname,
        blazon=blazon,
        emblazon=emblazon,
        awards=awards
    )


# FIXME: fails with just one name component

@app.route('/person/<surname>/<forename>', methods=['GET'])
def person(surname, forename):
    c = get_db().cursor()

    awards = do_query(c, 'SELECT award_types.name, awards.date, crowns.name, events.name FROM awards JOIN personae ON awards.persona_id = personae.id JOIN people ON personae.person_id = people.id JOIN award_types ON awards.type_id = award_types.id JOIN events ON awards.event_id = events.id LEFT OUTER JOIN crowns ON awards.crown_id = crowns.id WHERE people.surname = ? AND people.forename = ? ORDER BY awards.date, award_types.name', surname, forename)

    return render_template(
        'person.html',
        surname=surname,
        forename=forename,
        awards=awards
    )


# TODO: add checkbox for name when given vs name last used?

@app.route('/awards', methods=['GET', 'POST'])
def awards():
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
        results = do_query(c, 'SELECT personae.name, award_types.name, awards.date, crowns.name, events.name FROM awards JOIN personae ON awards.persona_id = personae.id JOIN award_types ON awards.type_id = award_types.id JOIN events ON awards.event_id = events.id LEFT OUTER JOIN crowns ON awards.crown_id = crowns.id WHERE award_types.id IN ({}) ORDER BY awards.date, personae.name, award_types.name'.format(','.join(['?'] * len(a_ids))), *a_ids)

    return render_template(
        'awards.html',
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


@app.route('/date', methods=['GET'])
def date():
    begin = request.args['begin'].strip()
    end = request.args['end'].strip()
    results = None

    c = get_db().cursor()
    results = do_query(c, 'SELECT personae.name, award_types.name, awards.date, crowns.name, events.name FROM personae JOIN awards ON personae.id = awards.persona_id JOIN award_types ON awards.type_id = award_types.id JOIN events ON awards.event_id = events.id LEFT OUTER JOIN crowns ON awards.crown_id = crowns.id WHERE date(?) <= date(awards.date) AND date(awards.date) <= date(?) ORDER BY awards.date, personae.name, award_types.name', begin, end)

    return render_template(
        'date.html',
        begin=begin,
        end=end,
        results=results
    )


@app.route('/award', methods=['GET'])
def award():
    award = request.args['award'].strip()
    results = None

    c = get_db().cursor()
    results = do_query(c, 'SELECT personae.name, award_types.name, awards.date, crowns.name, events.name FROM personae JOIN awards ON personae.id = awards.persona_id JOIN award_types ON awards.type_id = award_types.id JOIN events ON awards.event_id = events.id LEFT OUTER JOIN crowns ON awards.crown_id = crowns.id WHERE award_types.name LIKE ? ORDER BY awards.date, personae.name, award_types.name', '%{}%'.format(award))

    return render_template(
        'award.html',
        award=award,
        results=results
    )


@app.route('/crown', methods=['GET'])
def crown():
    crown_id = request.args['crown_id']
    results = None

    c = get_db().cursor()

    crown = do_query(c, 'SELECT name FROM crowns WHERE id = ?', crown_id)[0][0]

    results = do_query(c, 'SELECT personae.name, award_types.name, awards.date, crowns.name, events.name FROM personae JOIN awards ON personae.id = awards.persona_id JOIN award_types ON awards.type_id = award_types.id JOIN events ON awards.event_id = events.id JOIN crowns ON awards.crown_id = crowns.id WHERE crowns.id = ? ORDER BY awards.date, personae.name, award_types.name', crown_id)

    return render_template(
        'crown.html',
        crown=crown,
        results=results
    )


@app.route('/op', methods=['GET', 'POST'])
def op():
    headers = None
    results = None

    if request.method == 'POST':
        min_precedence = int(request.form['precedence'].strip())
        c = get_db().cursor()
        results = do_query(c, 'SELECT DISTINCT cur.name, awards.date, award_types.precedence FROM awards JOIN personae ON awards.persona_id = personae.id JOIN award_types ON awards.type_id = award_types.id LEFT JOIN (SELECT personae.person_id, awards.date, award_types.precedence FROM awards JOIN personae ON awards.persona_id = personae.id JOIN award_types ON awards.type_id = award_types.id) AS pjoin ON personae.person_id = pjoin.person_id AND award_types.precedence < pjoin.precedence LEFT JOIN (SELECT personae.person_id, awards.date, award_types.precedence FROM awards JOIN personae ON awards.persona_id = personae.id JOIN award_types ON awards.type_id = award_types.id) AS djoin ON personae.person_id = djoin.person_id AND award_types.precedence = djoin.precedence AND awards.date > djoin.date JOIN (SELECT DISTINCT personae.name, personae.person_id FROM awards JOIN personae ON awards.persona_id = personae.id LEFT JOIN (SELECT personae.person_id, awards.persona_id, awards.date FROM awards JOIN personae ON awards.persona_id = personae.id) AS sjoin ON personae.person_id = sjoin.person_id AND awards.date < sjoin.date WHERE sjoin.date IS NULL) AS cur ON cur.person_id = personae.person_id WHERE pjoin.precedence IS NULL AND djoin.date IS NULL AND award_types.precedence >= ? ORDER BY award_types.precedence DESC, awards.date, cur.name', min_precedence)

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

        results = itertools.groupby(results, key=lambda r: r[2])

    return render_template(
        'op.html',
        headers=headers,
        results=results
    )


@app.route('/reigns', methods=['GET'])
def reigns():
    c = get_db().cursor()
    principality = do_query(c, 'SELECT sov1 || " and " || sov2, begin, end FROM reigns WHERE date(begin) < date("1993-06-05") ORDER BY begin')
    kingdom = do_query(c, 'SELECT sov1 || " and " || sov2, begin, end FROM reigns WHERE date(begin) >= date("1993-06-05") ORDER BY begin')

    return render_template(
        'reigns.html',
        principality=principality,
        kingdom=kingdom
    )


# TODO: make an alphabetic index
# FIXME: returning field not in the GROUP BY?

@app.route('/armorial', methods=['GET'])
def armorial():
    c = get_db().cursor()
    results = do_query(c, 'SELECT p2.name, people.emblazon FROM people JOIN personae AS p1 ON p1.person_id = people.id JOIN personae AS p2 ON p1.person_id = p2.person_id JOIN awards ON p2.id = awards.persona_id WHERE people.emblazon IS NOT NULL GROUP BY p2.person_id HAVING awards.date = MAX(awards.date) ORDER BY p2.name')

    return render_template(
        'armorial.html',
        columns=6,
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


class FormError(Exception):
  def __init__(self, message):
    super(FormError, self).__init__()
    self.message = message


def search_modern(c, surname, forename):
    query = 'SELECT id, surname, forename FROM people WHERE '

    if surname:
        if forename:
            query += 'surname LIKE ? AND forename LIKE ?'
            params = ('%{}%'.format(surname), '%{}%'.format(forename))
        else:
            query += 'surname LIKE ?'
            params = ('%{}%'.format(surname),)
    else:
        query += 'forename LIKE ?'
        params = ('%{}%'.format(forename),)

    matches = do_query(c, query, *params)

    if len(matches) == 1:
        return redirect(url_for(
            'person',
            surname=matches[0][1],
            forename=matches[0][2]
        ))
    else:
        return render_template('choose_person.html', matches=matches)


def search_persona(c, persona):
    matches = do_query(c, 'SELECT id, name FROM personae WHERE name LIKE ?', '%{}%'.format(persona))

    if len(matches) == 1:
        return redirect(url_for('persona', name=matches[0][1]))
    else:
        return render_template('choose_persona.html', matches=matches)


def throw_if(*args):
    if any(args):
        raise FormError('Choose a single type of search.')


def get_crowns_list(c):
    return do_query(c, 'SELECT id, name FROM crowns ORDER BY name')


def stripped(d, k):
    return d.get(k, default='').strip() or None


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        persona = stripped(request.form, 'persona')
        forename = stripped(request.form, 'forename')
        surname = stripped(request.form, 'surname')
        begin = stripped(request.form, 'begin')
        end = stripped(request.form, 'end')
        crown = stripped(request.form, 'crown')
        award = stripped(request.form, 'award')

        try:
            if forename or surname:
                throw_if(persona, begin, end, crown, award)
                return search_modern(get_db().cursor(), surname, forename)
            elif persona:
                throw_if(forename, surname, begin, end, crown, award)
                return search_persona(get_db().cursor(), persona)
            elif begin or end:
                throw_if(forename, surname, persona, crown, award)
                return redirect(url_for('date', begin=begin, end=end))
            elif crown:
                throw_if(forename, surname, persona, begin, end, award)
                return redirect(url_for('crown', crown_id=crown))
            elif award:
                throw_if(prename, surname, persona, begin, end, crown)
                return redirect(url_for('award', award=award))
        except Exception as e:
            flash(e.message, 'error')

    crowns = get_crowns_list(get_db().cursor())
    return render_template(
        'search.html',
        crowns=crowns
    )


if __name__ == '__main__':
    app.run()
