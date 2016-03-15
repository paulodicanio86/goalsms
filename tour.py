from string_functions import *
from db_functions import *
import pandas as pd


class Tour:
    def __init__(self):
        self.tour_id = 1
        self.tour_name = ''
        self.current_question = 3
        self.total_questions = 6

    def get_tour_name(self):
        self.tour_name = 'blabla'
