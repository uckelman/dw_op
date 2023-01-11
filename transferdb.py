import sqlite3
from sqlite3 import Error
import mysql.connector


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def create_mysql_connector():
    cnx = mysql.connector.connect(user='oop', password='Oop_33!!', host='127.0.0.1', database='oop', autocommit=True)

    return cnx

def get_all_tables(conn, priority):
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    rows = cur.fetchall()

    for row in rows:
        print(row)


def get_table_data(conn, table):
    cur = conn.cursor()
    cur.execute('SELECT * FROM {}'.format(table))
    rows = cur.fetchall()

    return rows


def get_table_sql(conn, table):
    cur = conn.cursor()
    cur.execute("SELECT sql FROM sqlite_schema WHERE name = '{}'".format(table))
    rows = cur.fetchall()

    return rows


def cur_execute(cur, sql):
    if (sql.find('groups') != -1):
        cur.execute(sql.replace("groups", "`groups`"))
    else:
        cur.execute(sql.replace("'groups'", "`groups`"))
    

def create_table_mysql(conn, sql):
    cur = conn.cursor()
    
    cur_execute(cur, sql)

    return "Done"


def drop_table_mysql(conn, table):
    cur = conn.cursor()
    
    deleteSql = "DROP TABLE IF EXISTS {}".format(table)
    cur_execute(cur, deleteSql)
    
    
def get_sql_row(row):
    result = ""
    for value in row:
        if result != "":
            result = result + ', '
    
        if value is None:
            result = result + "NULL"
        else:
            result = result + "'{}'".format(str(value).replace("'", "''"))
        
    return result


def insert_data_mysql(conn, table, columns, rows, printinfo):
    i = 0
    cur = conn.cursor()

    for row in rows:
        fixedrow = get_sql_row(row)
            
        sql = "INSERT INTO {} {} VALUES ({})".format(table, columns, fixedrow)

        if (table == "award_types" and sql.find(", '')") != -1):
            sql = sql.replace(", '')", ", NULL)")

        if (printinfo):
            print(sql)
   
        cur_execute(cur, sql)
        
        i = i + 1

    return i


def move_tables_data(conn, cnx, table, columns, printinfo):
    rows = get_table_data(conn, table)
    
    result = insert_data_mysql(cnx, table, columns, rows, printinfo)

    return result


def main():
    database = r"op.sqlite"

    # create a sqlite database connection
    conn = create_connection(database)
    with conn:
        # create mysql database connection
        cnx = create_mysql_connector()
        
        with cnx:
            print("Dropping tables")
            drop_table_mysql(cnx, "awards")
            drop_table_mysql(cnx, "personae")
            drop_table_mysql(cnx, "people")
            drop_table_mysql(cnx, "crowns")
            drop_table_mysql(cnx, "reigns")
            drop_table_mysql(cnx, "scribes")
            drop_table_mysql(cnx, "events")
            drop_table_mysql(cnx, "scroll_status")
            drop_table_mysql(cnx, "award_types")
            drop_table_mysql(cnx, "groups")
            drop_table_mysql(cnx, "regions")
            
            sql = "CREATE TABLE regions (id INTEGER PRIMARY KEY, name TEXT)"
            create_table_mysql(cnx, sql)
            dataCount = move_tables_data(conn, cnx, "regions", "(id, name)", False)
            print("regions rows {}".format(dataCount,))

            sql = "CREATE TABLE groups (id INTEGER PRIMARY KEY, name TEXT NOT NULL)"
            create_table_mysql(cnx, sql)
            dataCount = move_tables_data(conn, cnx, "groups", "(id, name)", False)
            print("groups rows {}".format(dataCount,))
            
            sql = "CREATE TABLE award_types (id INTEGER PRIMARY KEY, name TEXT NOT NULL, precedence INTEGER NOT NULL, group_id INTEGER NOT NULL REFERENCES groups(id), open INTEGER CHECK(open IN (0, 1, NULL)))"
            create_table_mysql(cnx, sql)
            dataCount = move_tables_data(conn, cnx, "award_types", "(id, name, precedence, group_id, open)", False)
            print("award_types rows {}".format(dataCount,))

            sql = "CREATE TABLE crowns (id INTEGER PRIMARY KEY, name TEXT)"
            create_table_mysql(cnx, sql)
            dataCount = move_tables_data(conn, cnx, "crowns", "(id, name)", False)
            print("crowns rows {}".format(dataCount,))

            sql = "CREATE TABLE reigns (id INTEGER PRIMARY KEY, sov1 TEXT, sov2 TEXT, begin TEXT, end TEXT)"
            create_table_mysql(cnx, sql)
            dataCount = move_tables_data(conn, cnx, "reigns", "(id, sov1, sov2, begin, end)", False)
            print("reigns rows {}".format(dataCount,))

            sql = "CREATE TABLE scribes(id INTEGER PRIMARY KEY, name TEXT NOT NULL, description TEXT)"
            create_table_mysql(cnx, sql)
            dataCount = move_tables_data(conn, cnx, "scribes", "(id, name, description)", False)
            print("scribes rows {}".format(dataCount,))

            sql = "CREATE TABLE scroll_status (id INTEGER PRIMARY KEY, name TEXT NOT NULL)"
            create_table_mysql(cnx, sql)
            dataCount = move_tables_data(conn, cnx, "scroll_status", "(id, name)", False)
            print("scroll_status rows {}".format(dataCount,))            

            sql = "CREATE TABLE events (id INTEGER, name TEXT NOT NULL, slug TEXT, provenance TEXT, PRIMARY KEY(id))"
            create_table_mysql(cnx, sql)
            dataCount = move_tables_data(conn, cnx, "events", "(id, name, slug, provenance)", False)
            print("events rows {}".format(dataCount,))
            
            sql = "CREATE TABLE people (id INTEGER, surname TEXT, forename TEXT, region_id INTEGER NOT NULL, blazon TEXT, emblazon TEXT, notes TEXT, PRIMARY KEY(id), FOREIGN KEY(region_id) REFERENCES regions(id))"
            create_table_mysql(cnx, sql)
            dataCount = move_tables_data(conn, cnx, "people", "(id, surname, forename, region_id, blazon, emblazon, notes)", False)
            print("people rows {}".format(dataCount,))
            
            sql = "CREATE TABLE personae (id INTEGER PRIMARY KEY, name TEXT NOT NULL, person_id INTEGER NOT NULL REFERENCES people(id), official INTEGER NOT NULL CHECK(official IN (0, 1)), search_name TEXT)"
            create_table_mysql(cnx, sql)
            dataCount = move_tables_data(conn, cnx, "personae", "(id, name, person_id, official, search_name)", False)
            print("personae rows {}".format(dataCount,))

            sql = "CREATE TABLE awards (id INTEGER, type_id INTEGER NOT NULL, persona_id INTEGER NOT NULL, crown_id INTEGER, event_id INTEGER, date TEXT, scribe_id INTEGER, scroll_status_id INTEGER, scroll_updated TEXT, scroll_comment TEXT, provenance TEXT, PRIMARY KEY(id), FOREIGN KEY(type_id) REFERENCES award_types(id), FOREIGN KEY(event_id) REFERENCES events(id), FOREIGN KEY(scribe_id) REFERENCES scribes(id), FOREIGN KEY(crown_id) REFERENCES crowns(id), FOREIGN KEY(persona_id) REFERENCES personae(id), FOREIGN KEY(scroll_status_id) REFERENCES scroll_status(id))"
            create_table_mysql(cnx, sql)
            dataCount = move_tables_data(conn, cnx, "awards", "(id, type_id, persona_id, crown_id, event_id, date, scribe_id, scroll_status_id, scroll_updated, scroll_comment, provenance)", False)
            print("awards rows {}".format(dataCount,))

            
if __name__ == '__main__':
    main()
    
