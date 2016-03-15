from string_functions import *
from db_functions import *
import pandas as pd


class Sms:
    def __init__(self, content, sender='', receiver=''):
        self.content = str(content)
        self.sender = str(sender)
        self.receiver = str(receiver)
        self.tour_id = None
        self.is_valid = False

    def validate_sender(self):
        self.sender = validate_number(self.sender)

    def validate_content(self):
        self.content = validate_content(self.content)

    def validate_sms_and_get_tour(self, db):
        df = select_number_from_valid_table(db, self.sender)
        if len(df) == 0:
            self.is_valid = False
        else:
            self.tour_id = df['tour_id'].values[0]
            self.is_valid = True

    def get_message_array(self):
        return [self.sender, self.content, self.tour_id]

    def part_of_active_tour(self):
        # function to check if sms is part of active tour
        return False

    def send_sms(self):
        # Function to send a sms
        return None
