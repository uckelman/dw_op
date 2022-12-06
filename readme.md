# Set up your local environment (this assumes a mac terminal environment)

# Create a sqllite file named op.sqlite with the contents of the op.sqlite.sql file

pip install virtualenv

virtualenv venv

source ./venv/bin/activate

pip install -r requirements.txt

flask --app viewer run
