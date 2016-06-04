import string
from string_functions import validate_number, is_integer_string, matches_reg_ex


def convert_white_space_in_link(input_string):
    input_string = string.replace(input_string, ' ', '%20')
    return input_string


def valid_email(email):
    """
    Checks if email is valid and a string.
    """
    reg_ex = '[-0-9a-zA-Z.+_]+@[-0-9a-zA-Z.+_]+\.[a-zA-Z]{2,4}'
    if (isinstance(email, basestring)
        and len(email) == 0):
        return True
    else:
        return matches_reg_ex(email, reg_ex)


def valid_phone_number(account_number):
    """
    Checks if account_number is valid and a string.
    Valid: 12345678
    """
    return is_integer_string(account_number)


def valid_team(team):
    if team in ['England', 'Northern Ireland', 'Wales']:
        return True
    else:
        return False


#######################################
# combining the above functions in two
#######################################
def convert_entries(entry, value, country_code):
    if entry == 'phone_number':
        return validate_number(value, code=country_code)
    else:
        return value


def validate_entries(entry, value):
    if entry == 'phone_number':
        return valid_phone_number(value)
    elif entry == 'email':
        return valid_email(value)
    elif entry == 'team':
        return valid_team(value)
    else:
        return False
