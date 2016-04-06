import urllib  # URL functions
import urllib2  # URL functions
import os
import json

from string_functions import *
from db_functions import *
import pandas as pd

# Open sms config string file
sms_json_path = os.path.dirname(os.path.abspath(__file__))
sms_json_path = os.path.abspath(os.path.join(os.sep, sms_json_path, 'sms_config.json'))

keywords = ['start', 'help']
start_keyword = 'start'

with open(sms_json_path) as sms_config_file:
    sms_config = json.load(sms_config_file)


def send_sms(number, content, config):
    encoding = 'utf-8'
    username = config['uname']
    sender = config['sender']
    hash_code = config['hash']
    test_flag = config['test_flag']  # real messages have test_flag = 0
    url = config['url_send']

    values = {'test': test_flag,
              'uname': username,
              'hash': hash_code,
              'message': content,
              'from': sender,
              'selectednums': number}

    post_data = urllib.urlencode(values)
    request = urllib2.Request(url, post_data)

    # print 'Attempt to send SMS ...'
    try:
        response = urllib2.urlopen(request)
        response_url = response.geturl()
        if response_url == url:
            print 'SMS sent!'
    except urllib2.URLError, error:
        # print 'Send failed!'
        print error.reason


class Sms:
    def __init__(self, content, sender=None, receiver=None):
        self.content = str(content)
        self.sender = str(sender)

        self.multiple_receivers = False
        self.receiver = None
        self.set_receiver(receiver)
        self.tour_id = None
        self.is_valid = False
        self.is_start_sms = False
        self.is_keyword = False

    def set_receiver(self, receiver):
        # check if
        if receiver:
            self.receiver = receiver
            if type(receiver) == list:
                if len(receiver) > 1:
                    self.multiple_receivers = True
                elif len(receiver) == 1:
                    self.receiver = str(receiver[0])
                else:
                    self.receiver = None

    def validate_sender(self):
        self.sender = validate_number(self.sender)

    def validate_content(self):
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

    def send(self):
        # Function to send a sms
        print ('SMS SENT to ' + self.receiver + ' and content: ' + self.content)

        # check if one number or multiple, and turn multiple into tuple
        number = self.receiver
        if self.multiple_receivers:
            number = tuple(self.receiver)

        send_sms(number, self.content, sms_config)
