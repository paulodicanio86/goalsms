import re
import string


def absolute_price(price):
    """
    Input/Output are strings
    129.99 -> 12999
    """
    return str(int(float(price) * 100.0))


def relative_price(price):
    """
    Input/Output are strings
    123 -> 1.23
    """
    if is_integer_string(price):
        return two_digit_string(int(price) / 100.0)


def two_digit_string(value):
    if type(value) == str or type(value) == unicode:
        value = float(value)
    return '{0:.2f}'.format(value)


def is_integer_string(input_string):
    return (isinstance(input_string, basestring)
            and input_string.isdigit())


def matches_reg_ex(input_string, reg_ex):
    """
    Checks if input_string is string or unicode object
    and if it matches the regular expression.
    Empty strings return False.
    """
    return (isinstance(input_string, basestring)
            and re.match(reg_ex, input_string) != None)


def validate_content(content):
    # to clean the message we need to remove ' and "
    content = content.replace("'", "")
    content = content.replace('"', '')
    content = content.replace(';', '')
    content = content.replace('(', '')
    content = content.replace(')', '')
    # remove white space
    content = content.strip()
    # make lower case
    content = content.lower()
    content = convert_special_characters(content)
    return content


def convert_special_characters(input_string):
    input_string = string.replace(input_string, '"', '_')
    input_string = string.replace(input_string, "'", "_")
    input_string = string.replace(input_string, '#', '_')
    input_string = string.replace(input_string, '<', '_')
    input_string = string.replace(input_string, '>', '_')
    input_string = string.replace(input_string, '\t', '_')
    input_string = string.replace(input_string, '\n', '_')
    input_string = string.replace(input_string, '/', '_')
    input_string = string.replace(input_string, '\\', '_')
    return input_string


def add_country_code(number, prefix):
    if number[0] == '0':
        return prefix + number[1:]
    else:
        return prefix + number


def prefix_number_str(number, prefix='44'):
    number = number.replace(' ', '')

    # if number is not long enough then exit here.
    if len(number) < 4:
        return number

    # +yy777xxxxxxx cases DE, UK
    if number[0] == '+':
        return add_country_code(number[3:], prefix)
    # 00yy777xxxxxxx cases and 00yy172xxxxx cases DE, UK
    if number[:2] == '00':
        return add_country_code(number[4:], prefix)
    # prefix+yyyyyyyyyyy cases
    if number[:2] == prefix:
        return number

    # all other cases
    return add_country_code(number, prefix)


def convert_number(number, prefix):
    if type(number) == int:
        number = str(number)
    return prefix_number_str(number, prefix)
