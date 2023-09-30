# Set up your local environment (this assumes a mac terminal environment)

## Set up database

Create a sqlite file named op.sqlite with the contents of the op.sqlite.sql file, then spool that data over to MySQL. Our application's history began with sqlite, and is now using MySQL.

```shell
sqlite3 op.sqlite < op.sqlite.sql
mysql -uroot 'CREATE DATABASE drachdb;'
mysql -uroot "GRANT ALL PRIVILEGES ON drachdb.* TO 'op'@'localhost' IDENTIFIED BY 'op';"
```

So, now you have an empty local MySQL database, primed to transfer the sqlite data into.

With a virtualenv running:

```shell
python transferdb.py
```

## Start the Flask app

```shell
pip install virtualenv

virtualenv venv

source ./venv/bin/activate

pip install -r requirements.txt

flask --app viewer run
```

### Alternative for `flask --app viewer run`:

```shell
export FLASK_APP=viewer.py
export FLASK_DEBUG=true

flask run
```


# Local docker

```
docker-compose up
```

The website can be found at 127.0.0.1:5000.


### updating your website
askja:dw_op hennar$ ls
__pycache__		editor.py		requirements.txt	templates
auth.py			editor.wsgi		shield.svg		transferdb.py
combo.wsgi		get_armorial.py		sql-init		viewer.py
config.py		op.sqlite.sql		start_op_ovh.sh		viewer.wsgi
docker-compose.yml	readme.md		static
askja:dw_op hennar$ cd sql-init/
askja:sql-init hennar$ ls
dev-db.sql	dev-db2.sql
askja:sql-init hennar$ bbedit dev-db.sql 
askja:sql-init hennar$ vim dev-db.sql 
askja:sql-init hennar$ ls
dev-db.sql	dev-db2.sql
askja:sql-init hennar$ docker ps
CONTAINER ID   IMAGE        COMMAND                  CREATED          STATUS          PORTS                      NAMES
7a063fbb8acf   mariadb      "docker-entrypoint.s…"   27 minutes ago   Up 27 minutes   0.0.0.0:3306->3306/tcp     dw_op_db_1
a5afb60bc967   python:3.5   "bash -c 'cd /build …"   27 minutes ago   Up 27 minutes   127.0.0.1:5000->5000/tcp   dw_op_python_1
askja:sql-init hennar$ docker exec -it dw_op_db_1 bash
root@7a063fbb8acf:/# exit
exit
askja:sql-init hennar$ ls
dev-db.sql	dev-db2.sql
askja:sql-init hennar$ cd..
-bash: cd..: command not found
askja:sql-init hennar$ cd ..
askja:dw_op hennar$ ls
__pycache__		config.py		editor.wsgi		readme.md		sql-init		templates		viewer.wsgi
auth.py			docker-compose.yml	get_armorial.py		requirements.txt	start_op_ovh.sh		transferdb.py
combo.wsgi		editor.py		op.sqlite.sql		shield.svg		static			viewer.py
askja:dw_op hennar$ docker volume ls
DRIVER    VOLUME NAME
local     dw_op2_data
local     dw_op_data
askja:dw_op hennar$ docker volume ls
DRIVER    VOLUME NAME
local     dw_op2_data
local     dw_op_data
askja:dw_op hennar$ docker volume rm dw_op_data
Error response from daemon: remove dw_op_data: volume is in use - [7a063fbb8acf3f036dbd7cfcc6b1eebb7253bfe29ec600f5b62c6d646651d46b]
askja:dw_op hennar$ docker volume rm dw_op_data
dw_op_data
askja:dw_op hennar$ 

