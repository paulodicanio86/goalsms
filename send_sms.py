
import urllib      # URL functions
import urllib2     # URL functions
import json
from pprint import pprint

with open('sms_config.json') as data_file:
    data_config = json.load(data_file)
pprint(data_config)

encoding = 'utf-8'


# Define your message
message = 'hey test 1234!'

# Set your username and sender name.
# Sender name must alphanumeric and
# between 3 and 11 characters in length.
username = data_config['uname']
sender = data_config['sender']

# Your unique hash is available from the docs page
# https://control.txtlocal.co.uk/docs/
hash = data_config['hash']

# Set the phone number you wish to send
# message to.
# The first 2 digits are the country code.
# 44 is the country code for the UK
# Multiple numbers can be specified if required
# e.g. numbers = ('447xxx123456','447xxx654321')
numbers = ('447776031697')

# Set flag to 1 to simulate sending
# This saves your credits while you are
# testing your code.
# To send real message set this flag to 0
test_flag = data_config['test_flag']

#-----------------------------------
# No need to edit anything below this line
#-----------------------------------

values = {'test'    : test_flag,
          'uname'   : username,
          'hash'    : hash,
          'message' : message,
          'from'    : sender,
          'selectednums' : numbers }

url = data_config['url_send']

postdata = urllib.urlencode(values)
req = urllib2.Request(url, postdata)

print 'Attempt to send SMS ...'

try:
  response = urllib2.urlopen(req)
  response_url = response.geturl()
  if response_url==url:
    print 'SMS sent!'
except urllib2.URLError, e:
  print 'Send failed!'
  print e.reason