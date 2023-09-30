ln -sf combo.wsgi server.py
ln -sf /usr/share/ovh/app.py viewer2.py
#pip3 install --user virtualenv
#export PATH=$PATH:~/.local/bin
#virtualenv --version
virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt
