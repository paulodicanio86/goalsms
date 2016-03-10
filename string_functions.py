def add_brackets(string):
    return '(' + string + ')'


def convert_values_to_string(array_values):
    string = ''
    for element in array_values:
        if type(element) == str: 
            # to clean the message we need to remove ' and "
            element = element.replace("'", "")
            element = element.replace('"', '')

            string += "'" + element + "', "
        else:
            string += str(element) + ", "

    return add_brackets(string[:-2])


def convert_columns_to_string(array_values):
    string = ''
    for element in array_values:
        string += element + ", "
    return add_brackets(string[:-2])


def convert_column_types_to_string(columns, types):
    string = ''
    for i, element in enumerate(columns):
        string += element + ' ' + types[i] + ", "

    return add_brackets(string[:-2])


def join_rows(array_rows):
    return ','.join(array_rows)


def add_country_code(number, code):
    if number[0] == '0':
        return code + number[1:]
    else:
        return code + number


def strip_number_str(number, code):
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
