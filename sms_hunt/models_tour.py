import os
import json
from datetime import datetime

import pandas as pd

from sms import Sms
from tour import Tour
from functions.db_functions import (get_tour_from_active_table, update_active_table, delete_from_active_table)

# Open sms content string file
content_json_path = os.path.dirname(os.path.abspath(__file__))
content_json_path = os.path.join(os.sep, content_json_path, 'content', 'sms_content.json')

with open(content_json_path) as sms_content_file:
    sms_content = json.load(sms_content_file)

welcome_text = sms_content['welcome_text']
game_over_text = sms_content['game_over_text']
final_help_text = sms_content['final_help_text']
help_1_int = sms_content['help_1_int']
help_2_int = sms_content['help_2_int']
next_stage_int = sms_content['next_stage_int']


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

        # Send message that it is over now.
        reply_sms = Sms(content=game_over_text,
                        receiver=sms.sender)
        reply_sms.send()

        # Delete tour from active table
        delete_from_active_table(db, sms.sender, tour.tour_id)

        print('-------> game successfully finished')

    return None


def process_wrong_answer(db, tour, sms):
    # Get the current tour
    df = get_tour_from_active_table(db, sms.sender, tour.tour_id)

    # Increase the number of attempts
    attempt = int(df['attempts'].values[0]) + 1
    update_active_table(db, 'attempts', attempt, sms.sender, tour.tour_id)
    # Increase the score
    score = int(df['score'].values[0]) + 1
    update_active_table(db, 'score', score, sms.sender, tour.tour_id)

    print('-------> a wrong answer has been received')
    help_1 = tour.get_help_1(db)
    help_2 = tour.get_help_2(db)

    if attempt == help_1_int and help_1 != '':
        # Send first help sms
        help_sms = Sms(content=help_1,
                       receiver=sms.sender)
        help_sms.send()

    if attempt == help_2_int and help_2 != '':
        # Send second help sms
        help_sms = Sms(content=help_2,
                       receiver=sms.sender)
        help_sms.send()

    if (attempt >= next_stage_int) and (next_stage_int > 0):
        print('-------> new stage is moved onto automatically')
        # Send sms that the answer is wrong and the next stage will follow
        help_sms = Sms(content=final_help_text,
                       receiver=sms.sender)
        help_sms.send()

        proceed_to_next_stage(db, tour, sms)

    return None
