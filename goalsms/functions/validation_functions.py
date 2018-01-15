import string

from string_functions import convert_number, convert_special_characters, is_integer_string, matches_reg_ex


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


def valid_phone_number(number, prefixes):
    """
    Checks if phone number is valid and a string.
    Valid: 12345678
    """
    return is_integer_string(number) and (len(number) > 4) and (number[:2] in prefixes)


#######################################
# combining the above functions in two
#######################################
def convert_entries(entry, value, prefix='44'):
    if entry == 'phone_number':
        return convert_number(value, prefix)
    if entry == 'name':
        return convert_special_characters(value)
    else:
        return value


def validate_entries(entry, value, prefixes):
    if entry == 'phone_number':
        return valid_phone_number(value, prefixes)
    elif entry == 'name':
        return valid_name(value)
    else:
        return False
