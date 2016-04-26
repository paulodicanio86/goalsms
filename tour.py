from datetime import datetime
import pandas as pd

from string_functions import *
from db_functions import *

from sms import *
from make_default_tables import get_table_columns

# Open sms content string file
content_json_path = os.path.dirname(os.path.abspath(__file__))
content_json_path = os.path.join(os.sep, content_json_path, 'content', 'sms_content.json')

with open(content_json_path) as sms_content_file:
    content = json.load(sms_content_file)

welcome_text = content['welcome_text']  # "Welcome to the tour: "
game_over_text = content['game_over_text']  # "Game is over"
final_help_text = content['final_help_text']  # "This seems too difficult, you will receive the next question."
help_1_int = content['help_1_int']  # 3
help_2_int = content['help_2_int']  # 5
next_stage_int = content['next_stage_int']  # 7


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

    def get_tour_column(self, db, column_name):
        df = get_tour_column(db, column_name, self.tour_id, self.current_stage)
        result_str = str(df[column_name].values[0])
        return result_str

    def get_question(self, db):
        return self.get_tour_column(db, 'question')

    def get_answer(self, db):
        return self.get_tour_column(db, 'answer')

    def get_help_1(self, db):
        return self.get_tour_column(db, 'help_1')

    def get_help_2(self, db):
        return self.get_tour_column(db, 'help_2')

    def get_all_stages(self):
        df = get_all_stages(self.tour_id)
        self.all_stages = df


def follow_tour(db, sms):
    # Check if sms is active. If not, start a tour
    if not sms.is_in_active_table(db):
        start_tour(db, sms)
        return None

    # Does the sms contain and trigger a keyword?
    if sms.is_keyword:
        # it is a keyword! let us investigate which one and take the right action
        # ...
        print('-------> we received a keyword message!')
        return None

    # The tour is active, the sms is not a keyword, hence it must be an answer.
    # Make a tour object based on this sms, get the total stages and current stage of the tour (from active table)
    tour = Tour(sms.tour_id)
    tour.get_total_stages(db)
    tour.get_stage_from_active_table(db, sms.sender)

    # Check whether the answer is right
    question = tour.get_question(db)
    right_answer = tour.get_answer(db)
    answer = sms.content
    print('stage: ', tour.current_stage, tour.is_final_stage())
    print(question, right_answer, answer)

    if right_answer.lower() == answer.lower():
        # A right answer has been received
        proceed_to_next_stage(db, tour, sms)

    else:
        # A wrong answer has been received
        process_wrong_answer(db, tour, sms)

    return None


def start_tour(db, sms):
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

    else:
        # Do nothing in this case.
        # Maybe reply a message to ask if he wanted to start the tour?
        print('-------> A random message has been received')
    return None


def proceed_to_next_stage(db, tour, sms):
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
        reply_sms = Sms(content=game_over_text,
                        receiver=sms.sender)
        reply_sms.send()

        # Delete tour from active table
        delete_from_active_table(db, sms.sender, tour.tour_id)

        print('-------> game successfully finished')

    return None


def process_wrong_answer(db, tour, sms):
    # Increase the number of attempts and score
    df = get_tour_from_active_table(db, sms.sender, tour.tour_id)
    attempt = int(df['attempts'].values[0]) + 1
    update_active_table(db, 'attempts', attempt, sms.sender, tour.tour_id)

    score = int(df['score'].values[0]) + 1
    update_active_table(db, 'score', score, sms.sender, tour.tour_id)

    print('-------> a wrong answer has been received')
    help_1 = tour.get_help_1(db)
    help_2 = tour.get_help_2(db)

    if attempt == help_1_int and help_1 != '':
        help_sms = Sms(content=help_1,
                       receiver=sms.sender)
        help_sms.send()
        print(help_1)

    if attempt == help_2_int and help_2 != '':
        help_sms = Sms(content=help_2,
                       receiver=sms.sender)
        help_sms.send()
        print(help_2)

    if (attempt >= next_stage_int) and (next_stage_int > 0):
        print('-------> new stage is moved onto automatically')
        # Send sms that the answer is wrong and the next stage will follow
        help_sms = Sms(content=final_help_text,
                       receiver=sms.sender)
        help_sms.send()

        proceed_to_next_stage(db, tour, sms)

    return None
