def add_brackets(string):
    return '(' + string + ')'


def convert_values_to_string(array_values):
    string = ''
    for element in array_values:
        if type(element) == str:
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
    if len(columns) == len(types):
        print('equal length')
    for i, element in enumerate(columns):
        string += element + ' ' + types[i] + ", "

    return add_brackets(string[:-2])


def join_rows(array_rows):
    return ','.join(array_rows)
