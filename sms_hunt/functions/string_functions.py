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
    return content


def add_country_code(number, code):
    if number[0] == '0':
        return code + number[1:]
    else:
        return code + number


def strip_number_str(number, code):
    number = number.replace(' ', '')
    # +44777xxxxxxx cases
    if number[0] == '+':
        return number[1:]
    # 0044777xxxxxxx cases
    if number[:2] == '00':
        return number[2:]
    # 0777xxxxxxx cases
    if number[0] == '0':
        return add_country_code(number, code)
    # 777xxxxxxx cases
    if number[0] == '7':  # valid for UK numbers, fix for international numbers
        return add_country_code(number, code)
    return number


def validate_number(number, code='44'):
    if type(number) == int:
        number = str(number)
    return strip_number_str(number, code)
