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
        df = get_maximum_stage_number(db, self.tour_id)
        self.total_stages = int(df['total'].values[0] + 1)

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

    def save_to_db(self, db, sender, started_str, duration, score, table_name='finished_tours'):
        text_row = [sender, self.tour_id, started_str, duration, score]
        print(text_row)
        # Add message to table
        insert_array_to_table(table_name, db, get_table_columns('tables/' + table_name + '_table.json'), text_row)

    def get_question(self, db):
        df = get_question(db, self.tour_id, self.current_stage)
        question_str = str(df['question'].values[0])
        return question_str

    def get_answer(self, db):
        df = get_answer(db, self.tour_id, self.current_stage)
        question_str = str(df['answer'].values[0])
        return question_str

    def get_all_stages(self):
        df = get_all_stages(self.tour_id)
        self.all_stages = df


def follow_tour(db, sms):
    # Check if sms is active and not a keyword
    # If not then add to active table and send 1st message
    if not sms.is_in_active_table(db):

        # Is the sms triggering a start of a tour?
        if sms.is_start_sms:
            # Initiate tour, get stages and make active
            tour = Tour(sms.tour_id, 0)
            tour.get_total_stages(db)
            tour.add_tour_to_active_table(db, sms.sender, sms.tour_id)

            # Make a welcome sms and send
            welcome_sms = Sms(content=welcome_text,
                              receiver=sms.sender)
            welcome_sms.send()
            # Make a reply sms with the question and send
            reply_sms = Sms(content=tour.get_question(db),
                            receiver=sms.sender)
            reply_sms.send()

            print('-------> start message has been received')
            return None
        else:
            # Do nothing in this case.
            # Maybe reply a message to ask if he wanted to start the tour?
            print('-------> A random message has been received')
            return None

    # Does the sms contain and trigger a keyword?
    if sms.is_keyword:
        # it is a keyword! let us investigate which one and take the right action
        # ...
        print('-------> we received a keyword message!')
        return None

    # The tour is active, the sms is not a keyword, hence it must be an answer.
    # Make a tour object based on this sms
    tour = Tour(sms.tour_id)
    # Get the total stages of the tour
    tour.get_total_stages(db)
    # Get the current stage of the tour from the active table
    tour.get_stage_from_active_table(db, sms.sender)

    # Let us check whether the answer is right
    question = tour.get_question(db)
    right_answer = tour.get_answer(db)
    answer = sms.content
    print('stage: ', tour.current_stage, tour.is_final_stage())
    print(question, right_answer, answer)

    if right_answer.lower() == answer.lower():
        # A right answer has been received
        print('correct answer')

        # Reset the attempts counter
        update_active_table(db, 'attempts', 0, sms.sender, tour.tour_id)

        # If the tour is not at the end of the tour
        if not tour.is_final_stage():
            # Update tour stage and active table
            new_stage = tour.current_stage + 1
            tour.set_stage(new_stage)
            update_active_table(db, 'stage_number', new_stage, sms.sender, tour.tour_id)

            # Send the next question
            reply_sms = Sms(content=tour.get_question(db),
                            receiver=sms.sender)
            reply_sms.send()
            print('-------> a right answer has been received. new stage reached')

        else:
            # Calculate the duration of the game
            df = get_tour_from_active_table(db, sms.sender, tour.tour_id)

            dt_start = pd.Timestamp(df['date_started'].values[0]).to_datetime()
            dt_start_str = '{:%Y-%m-%d %H:%M:%S}'.format(dt_start)
            duration_int = int((datetime.now() - dt_start).total_seconds())

            # Calculate the final score and save to database
            score_int = int(df['score'].values[0])
            tour.save_to_db(db, sms.sender, dt_start_str, duration_int, score_int)

            # send message that it is over now.

            # Delete tour from active table
            delete_from_active_table(db, sms.sender, tour.tour_id)

            print('-------> game successfully finished')

    else:
        # A wrong answer has been received
        # Increase the number of attempts and score
        df = get_tour_from_active_table(db, sms.sender, tour.tour_id)
        attempt = int(df['attempts'].values[0]) + 1
        update_active_table(db, 'attempts', attempt, sms.sender, tour.tour_id)

        score = int(df['score'].values[0]) + 1
        update_active_table(db, 'score', score, sms.sender, tour.tour_id)

        # if attempts score < 3 send a message that the answer is wrong
        # if attempts score = 3 and hints exists, send a hint
        # if attempts score = 3 and no hint exists, send message you failed.
        #     then increase stage number in active table and send new question
        # if attempts score > 3 send message you failed.
        #     then increase stage number in active table and send new question
        print('-------> a wrong answer has been received')

    return None
