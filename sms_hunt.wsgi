import os
import sys
import site

# virtual env
activate_this = '/var/www/sms_hunt/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

# Path of execution
sys.path.append('/var/www/sms_hunt')

# import my_flask_app as application
from app import app as application