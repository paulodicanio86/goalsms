import sys

# virtual env
activate_this = '/home/ec2-user/venv_sms_hunt/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

# Path of execution
sys.path.append('/var/www/sms_hunt')
sys.path.append('/home/ec2-user/venv_sms_hunt/local/lib64/python2.7/site-packages')

# import my_flask_app as application
# from app import app as application
from sms_hunt import app as application
