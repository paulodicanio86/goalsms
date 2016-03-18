from datetime import datetime
import pandas as pd

from string_functions import *
from db_functions import *

from sms import *
from make_default_tables import get_table_columns

welcome_text = 'Welcome to the tour: '


class Tour:
    def __init__(self, tour_id, question):
        self.tour_id = tour_id
        self.tour_name = ''
        self.question = question

        df = get_total_number_of_questions(tour_id)
        self.total_questions = int(df['total'].values[0])

    def get_tour_name(self):  # Do we need this function?!
        self.tour_name = 'blabla'

    def add_tour_to_active_table(self, db, sms):
        dt = datetime.now()
        dt_str = '{:%Y-%m-%d %H:%M:%S}'.format(dt)

        values = [sms.sender, sms.tour_id, 0, self.total_questions, dt_str, 0, 0]
        insert_array_to_table('active', db, get_table_columns('tables/active_table.json'), values)

    def get_question(self, db):
        df = get_question(db, self.tour_id, self.question)
        question_str = str(df['question'].values[0])
        return question_str


def follow_tour(db, sms):
    # Check if sms is active and not a keyword
    # If not then add to active table and send 1st message

    if not sms.is_in_active_table(db):

        if start_keyword in sms.content:
            # Initiate tour
            tour = Tour(sms.tour_id, 0)
            # Make tour active
            tour.add_tour_to_active_table(db, sms)
            # Make a welcome sms and send
            welcome_sms = Sms(content=welcome_text + tour.tour_name,
                              receiver=sms.sender)
            welcome_sms.send()
            # Make a reply sms with the question and send
            reply_sms = Sms(content=tour.get_question(db),
                            receiver=sms.sender)
            reply_sms.send()

            print('scenario 1')
            return None
        else:
            # Do nothing in this case.
            # Maybe reply a message to ask if he wanted to start the tour?
            print('scenario 2')
            return None

    if sms.is_keyword:
        # it is a keyword! let us investigate which one and take the right action
        # ...
        print('scenario 3')
        return None

    # tour is active, it is not a keyword, it must be an answer.
    # Let us check whether the answer is right.
    # if not, send a hint. increas penalty score in active table
    # if yes, increase the question number in active table and send the next question.
    # ...
    print('scenario 4')
    return None
