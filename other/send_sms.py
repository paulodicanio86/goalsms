import json
from sms_functions import *

with open('sms_config.json') as data_file:
    data_config = json.load(data_file)


# Set the phone number you wish to send
# message to.
# The first 2 digits are the country code.
# 44 is the country code for the UK
# Multiple numbers can be specified if required
# e.g. numbers = ('447xxx123456','447xxx654321')
number = ('447776031697')
content = 'hey test 1234 afasda!'

send_sms(number, content, data_config)
