import urllib
import urllib2
from datetime import datetime

from sms_hunt import sms_config, sms_content

from functions.string_functions import validate_content, validate_number
from functions.db_functions import (get_tour_from_active_table,
                                    select_number_from_valid_table)
from backend.db_functions import insert_array_to_table, get_table_columns

keywords = sms_content['keywords']
start_keyword = sms_content['start_keyword']


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
        self.tour_id = None
        self.is_valid = False
        self.is_start_sms = False
        self.is_keyword = False

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

    def validate_sender(self):
        self.sender = validate_number(self.sender)

    def validate_content(self):
        # This function should only be used if the content is for sure a string (not unicode encoded, as special
        # character are removed..!
        self.content = validate_content(self.content)
        if start_keyword in self.content:
            self.is_start_sms = True
        if self.content in keywords:
            self.is_keyword = True

    def validate_sms_and_get_tour(self, db):
        df = select_number_from_valid_table(db, self.sender)
        if len(df) == 0:
            self.is_valid = False
        else:
            self.tour_id = df['tour_id'].values[0]
            self.is_valid = True

    def is_in_active_table(self, db):
        df = get_tour_from_active_table(db, self.sender, self.tour_id)
        if len(df) == 0:
            return False
        else:
            return True

    def get_message_array(self):
        return [self.sender, self.content, self.tour_id]

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
        if self.multiple_receivers:
            receiver = ','.join(self.receiver)
        else:
            receiver = self.receiver

        # Check if one number or multiple, and turn multiple into tuple, then send
        if self.multiple_receivers:
            number = tuple(self.receiver)
        else:
            number = self.receiver

        send_sms(number, self.content, sms_config, service)
        print ('SMS SENT to ' + str(number) + ' and content: ' + self.content)
