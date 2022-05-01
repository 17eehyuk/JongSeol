nozzles = [{'nozzle_id': 0, 'drink_name': '물'}, {'nozzle_id': 1, 'drink_name': '우유'}, {'nozzle_id': 2, 'drink_name': '커피'}, {'nozzle_id': 3, 'drink_name': ''}, {'nozzle_id': 4, 'drink_name': ''}, {'nozzle_id': 5, 'drink_name': ''}, {'nozzle_id': 6, 'drink_name': ''}, {'nozzle_id': 7, 'drink_name': ''}]

noz_str = ''

for nozzle in nozzles:
    
    noz_str = noz_str + f'''
    <tr>
        <td>{nozzle['nozzle_id']}</td>
        <td>{nozzle['drink_name']}</td>
    </tr>
    '''

print(noz_str)
