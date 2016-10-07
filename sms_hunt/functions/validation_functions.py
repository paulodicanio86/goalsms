import string

from string_functions import validate_number, convert_special_characters, is_integer_string, matches_reg_ex
from sms_hunt.views import teams


def convert_white_space_in_link(input_string):
    input_string = string.replace(input_string, ' ', '%20')
    return input_string


def valid_name(name):
    """
    Checks if email is valid and a string.
    """
    reg_ex = '[-0-9a-zA-Z.+_]+'
    if (isinstance(name, basestring)
        and len(name) == 0):
        return False
    else:
        return matches_reg_ex(name, reg_ex)


def valid_phone_number(number):
    """
    Checks if account_number is valid and a string.
    Valid: 12345678
    """
    return is_integer_string(number)


def valid_team(team):
    if team in teams:
        return True
    else:
        return False


#######################################
# combining the above functions in two
#######################################
def convert_entries(entry, value, country_code):
    if entry == 'phone_number':
        return validate_number(value, code=country_code)
    if entry == 'name':
        return convert_special_characters(value)
    else:
        return value


def validate_entries(entry, value):
    if entry == 'phone_number':
        return valid_phone_number(value)
    elif entry == 'name':
        return valid_name(value)
    elif entry == 'team':
        return valid_team(value)
    else:
        return False
