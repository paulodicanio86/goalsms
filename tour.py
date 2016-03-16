from string_functions import *
from db_functions import *
import pandas as pd
from sms import *


class Tour:
    def __init__(self):
        self.tour_id = -1
        self.tour_name = ''
        self.current_question = -1
        self.total_questions = -1

    def get_tour_name(self):  # Do we need this function?!
        self.tour_name = 'blabla'

    def add_tour_to_active_table(self, db, sms):
        return None

    def get_reply_sms(self, db, sms, question_number):
        return Sms(receiver=sms.sender)


def follow_tour(db, sms):
    # Check if sms is active and not a keyword
    # If not then add to active table and send 1st message

    if not sms.is_in_active_table(db):

        if start_keyword in sms.content:
            tour = Tour()
            tour.add_tour_to_active_table(db, sms)
            question_sms = tour.get_reply_sms(db, sms, 0)
            question_sms.send()
            return None
        else:
            return None

    if sms.is_keyword:
        # it is a keyword! let us investigate which one and take the right action
        # ...
        return None

    # tour is active, it is not a keyword, it must be an answer.
    # Let us check whether the answer is right.
    # if not, send a hint. increas penalty score in active table
    # if yes, increase the question number in active table and send the next question.
    # ...

    return None
