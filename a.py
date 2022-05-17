tmp_dict ={'recipe_name': '1', 'id': 'A', 'author': 'A', 'drink0': '1', 'drink0_amount': '1'}


def a():
    keys =''
    values = ''
    for key, value in tmp_dict.items():
        keys = keys + key + ','
        values = values + "'" + value + "'" + ","
    keys = keys[:-1]
    values = values[:-1] 

    return f'''
    INSERT INTO recipes ({keys}) values  ({values});
    '''


print(a())