from datetime import datetime

from backend.db_functions import insert_array_to_table, get_table_columns
from functions.db_functions import (get_tour_from_active_table, get_maximum_stage_number,
                                    get_tour_column, get_all_stages)


class Tour:
    def __init__(self, tour_id, current_stage=None):
        self.tour_id = tour_id
        self.tour_name = None

        self.total_stages = None
        self.current_stage = current_stage
        self.all_stages = None

    def set_stage(self, number):
        self.current_stage = number

    def get_all_stages(self):
        df = get_all_stages(self.tour_id)
        self.all_stages = df

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

        # Add message to table
        insert_array_to_table(table_name, db,
                              get_table_columns('tables/' + table_name + '_table.json'),
                              text_row)

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
