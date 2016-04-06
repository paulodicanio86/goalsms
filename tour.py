from datetime import datetime
import pandas as pd

from string_functions import *
from db_functions import *

from sms import *
from make_default_tables import get_table_columns

welcome_text = 'Welcome to the tour: '


class Tour:
    def __init__(self, tour_id, current_stage=None):
        self.tour_id = tour_id
        self.tour_name = None

        self.total_stages = None
        self.current_stage = None
        self.set_stage(current_stage)
        self.all_stages = None

    def set_stage(self, number):
        self.current_stage = number

    def is_final_stage(self):
        if self.current_stage and self.total_stages and self.current_stage == self.total_stages - 1:
            return True
        else:
            return False

    def get_stage_from_active_table(self, db, phone_number):
        df = get_tour_from_active_table(db, phone_number, self.tour_id)
        self.set_stage(int(df['stage_number'].values[0]))

    def get_total_stages(self, db):
        df = get_total_number_of_stages(db, self.tour_id)
        self.total_stages = int(df['total'].values[0])

    def add_tour_to_active_table(self, db, sender, tour_id, dt=None):
        if not dt:
            dt = datetime.now()
        dt_str = '{:%Y-%m-%d %H:%M:%S}'.format(dt)

        values = [sender, tour_id,
                  self.current_stage, self.total_stages,
                  dt_str, 0, 0]
        insert_array_to_table('active', db,
                              get_table_columns('tables/active_table.json'),
                              values)

    def get_question(self, db):
        df = get_question(db, self.tour_id, self.current_stage)
        question_str = str(df['question'].values[0])
        return question_str

    def get_answer(self, db):
        df = get_question(db, self.tour_id, self.current_stage)
        question_str = str(df['answer'].values[0])
        return question_str

    def get_all_stages(self):
        df = get_all_stages(self.tour_id)
        self.all_stages = df


def follow_tour(db, sms):
    # Check if sms is active and not a keyword
    # If not then add to active table and send 1st message

    if not sms.is_in_active_table(db):

        if sms.is_start_sms:
            # Initiate tour
            tour = Tour(sms.tour_id, 0)
            # get total stages of tour
            tour.get_total_stages(db)
            # Make tour active
            tour.add_tour_to_active_table(db, sms.sender, sms.tour_id)
            # Make a welcome sms and send
            welcome_sms = Sms(content=welcome_text,
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

    # let us get the current stage of sms
    tour = Tour(sms.tour_id)
    # get total stages of tour
    tour.get_total_stages(db)
    # get current stage from active table
    tour.get_stage_from_active_table(db, sms.sender)

    current_stage = tour.current_stage
    is_final_stage = tour.is_final_stage()
    # print('stage: ', current_stage, is_final_stage)

    if sms.is_keyword:
        # it is a keyword! let us investigate which one and take the right action
        # ...
        print('scenario 3')
        return None

    # tour is active, it is not a keyword, it must be an answer.
    # Let us check whether the answer is right.
    # if not, send a hint. increase penalty score in active table
    # if yes, increase the question number in active table and send the next question.
    # ...
    print('scenario 4')
    return None
