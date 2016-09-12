from backend.db_functions import insert_array_to_table, get_table_columns


class Match:
    def __init__(self, localteam_name, visitorteam_name, time_str, date_str, status,
                 localteam_score='', visitorteam_score=''):
        self.localteam_name = localteam_name
        self.visitorteam_name = visitorteam_name

        self.localteam_score_str = localteam_score  # "0"
        self.localteam_score = int(self.localteam_score_str)

        self.visitorteam_score_str = visitorteam_score  # "1"
        self.visitorteam_score = int(self.visitorteam_score_str)

        self.time_str = time_str  # "13:30"
        self.date_str = date_str  # "03.01.2016"

        self.status = status  # "FT"

    def save_to_db(self, db, table_name='matches'):
        text_row = [self.date_str, self.localteam_name, self.visitorteam_name,
                    self.localteam_score, self.visitorteam_score, self.time_str,
                    self.status]
        # Add message to table
        insert_array_to_table(table_name, db, get_table_columns('tables/' + table_name + '_table.json'), text_row)

    def update_score_db(self, db, localteam_score, visitorteam_score):
        self.localteam_score_str = localteam_score  # "0"
        self.localteam_score = int(self.localteam_score_str)

        self.visitorteam_score_str = visitorteam_score  # "1"
        self.visitorteam_score = int(self.visitorteam_score_str)

        self.save_to_db(db)

    def get_score_message_text(self):
        minute = '49'
        message = 'new score: {localteam_name} {localteam_score_str} - {visitorteam_score_str} {visitorteam_name}'
        message = message.format(localteam_name=self.localteam_name, localteam_score_str=self.localteam_score_str,
                                 visitorteam_name=self.visitorteam_name,
                                 visitorteam_score_str=self.visitorteam_score_str)
        message = minute + '. minute, ' + message
        return message
