# Set up your local environment (this assumes a mac terminal environment)

pip install virtualenv

virtualenv venv

source ./venv/bin/activate

pip install -r requirements.txt

flask --app viewer run
