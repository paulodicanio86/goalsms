import urllib
import urllib2
from datetime import datetime

from goalsms import sms_config

from functions.string_functions import validate_content, convert_number
from backend.db_functions import insert_array_to_table, get_table_columns


def send_sms_txtlocal(number, content, config):
    encoding = 'utf-8'
    username = config['username']
    sender = config['sender']
    hash_code = config['hash']
    test_flag = config['test_flag']  # real messages have test_flag = 0
    url = config['url_send']

    values = {'test': test_flag,
              'username': username,
              'hash': hash_code,
              'message': content,
              'from': sender,
              'numbers': number}

    post_data = urllib.urlencode(values)
    post_data = post_data.encode(encoding)
    request = urllib2.Request(url)

    # print 'Attempt to send SMS ...'
    try:
        f = urllib2.urlopen(request, post_data)
        fr = f.read()
        # print 'SMS sent!'

    except urllib2.URLError, error:
        # print 'Send failed!'
        print error.reason


def send_sms_messagebird(number, content, config):
    encoding = 'auto'
    sender = config['sender']
    test_flag = config['test_flag']  # real messages have test_flag = 0
    key = ''

    if test_flag == 0:
        key = config['live_key']
    elif test_flag == 1:
        key = config['test_key']

    url = config['url_send']

    values = {
        'access_key': key,
        'originator': sender,
        'body': content,
        'recipients': number,
        'datacoding': encoding
    }

    post_data = urllib.urlencode(values)
    request = urllib2.Request(url)

    # print 'Attempt to send SMS ...'
    try:
        f = urllib2.urlopen(request, post_data)
        fr = f.read()
        # print 'SMS sent!'

    except urllib2.URLError, error:
        # print 'Send failed!'
        print error.reason


def send_sms(number, content, config, service=None):
    if not service:
        service = config['service']

    if service == 'txtlocal':
        send_sms_txtlocal(number, content, config[service])
    elif service == 'messagebird':
        send_sms_messagebird(number, content, config[service])


class Sms:
    def __init__(self, content, sender=None, receiver=None):
        self.content = content  # not defined as str here because of unicode characters. Use encode function instead.
        self.sender = str(sender)

        self.multiple_receivers = False
        self.receiver = None
        self.set_receiver(receiver)

    def encode_content(self, encoding='utf-8'):
        self.content = self.content.encode(encoding)

    def set_receiver(self, receiver):
        # check if
        if receiver:
            if type(receiver) == list:
                if len(receiver) > 1:
                    self.multiple_receivers = True
                    self.receiver = receiver
                elif len(receiver) == 1:
                    self.receiver = str(receiver[0])
                else:
                    self.receiver = None
            else:
                self.receiver = receiver

    def validate_content(self):
        # This function should only be used if the content is for sure a string (not unicode encoded, as special
        # character are removed..!
        self.content = validate_content(self.content)

    def save_message_to_db(self, db, table_name='message'):
        # Get date and datetime
        dt = datetime.now()
        dt_str = '{:%Y-%m-%d %H:%M:%S}'.format(dt)
        d_str = '{:%Y-%m-%d}'.format(dt)

        text_row = [self.sender, self.content, d_str, dt_str]
        # Add message to table
        insert_array_to_table(table_name, db, get_table_columns('tables/' + table_name + '_table.json'), text_row)

    def send(self, service=None):
        # Function to send a sms

        # Check if one number or multiple, and turn multiple into tuple, then send
        if self.multiple_receivers:
            number = tuple(self.receiver)
        else:
            number = self.receiver

        send_sms(number, self.content, sms_config, service)
        print ('SMS SENT to ' + str(number) + ' and content: ' + self.content)
