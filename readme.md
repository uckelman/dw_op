# Set up your local environment (this assumes a mac terminal environment)

## Create a sqlite file named op.sqlite with the contents of the op.sqlite.sql file

```shell
sqlite3 op.sqlite < op.sqlite.sql
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

export FLASK_ENV=development

flask run
```

# Local docker

```
docker-compose up
```

The website can be found at 127.0.0.1:5000.
