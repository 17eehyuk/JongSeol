import json
path = "./tmp.json"
with open(path, 'r', encoding='utf-8') as json_file:
    json_data = json.load(json_file)
print(json_data)


rated_users = json_data['rated_users']


for user in rated_users:
    print(user)
