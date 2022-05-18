import pymysql

#MySQL 접속
mydb = pymysql.connect(
    user='global',
    database='tmpdb',
    passwd='1234',
    host='localhost',
    charset='utf8'
)

#커서생성
sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)

#로그인
def login(id, pw):
    command = f'''
    SELECT id, pw FROM users WHERE id = '{id}' AND pw = password('{pw}');
    '''
    sql_cursor.execute(command)
    result = sql_cursor.fetchone()
    if result == None:
        return '''로그인에 실패했습니다.'''
    else:
        return result        # 데이터가 있으며 {'userid': 'A', 'userpw': '1234'}, 없으면 None 이 return됨
#회원가입
def register(id, pw, sex, yb):
    if id=='admin':
        return '''admin은 사용불가능 합니다.'''
    command = f'''
    INSERT INTO users VALUES ('{id}', password('{pw}'), '{sex}', '{yb}');
    '''
    try:
        sql_cursor.execute(command)         # 중복인 경우 에러 발생하므로 try/except 사용
        mydb.commit()
        return f'''{id}님 회원가입을 축하드립니다.'''
    except:
        return f'''아이디 : '{id}' 중복입니다. 다른 아이디를 사용해 주세요'''
    

#회원탈퇴
def drop_user(id):
    command = f'''
        SHOW TABLES
        '''
    sql_cursor.execute(command)
    tables =  sql_cursor.fetchall()
    for table in tables:
        current_table = list(dict(table).values())[0]        # 현재 테이블명
        command = f'''
        DELETE FROM {current_table} WHERE id='{id}';
        '''
        sql_cursor.execute(command)
        mydb.commit()
    return f'''사용자 '{id}' 탈퇴 성공'''

#개인정보확인
def my_profile(id):
    command = f'''
        SELECT sex, yb FROM users WHERE id='{id}';
    '''
    sql_cursor.execute(command)
    return sql_cursor.fetchone()

#개인정보 수정
def update_profile(sex, yb, pw, id):

    if pw == '':        
        #비밀번호 변경X
        command = f'''
        UPDATE users SET sex='{sex}', yb='{yb}' WHERE id = '{id}';
        '''
        sql_cursor.execute(command)
        mydb.commit()
        return print('업데이트성공')
    else:
        #비밀번호 까지 변경
        command = f'''
            UPDATE users SET sex='{sex}', yb='{yb}', pw=password('{pw}') WHERE id = '{id}';
        '''
        sql_cursor.execute(command)
        mydb.commit()
        return print('업데이트성공')

#모든유저출력
def all_users():
    command = f'''
    SELECT id FROM users;
    '''
    sql_cursor.execute(command)
    tables =  sql_cursor.fetchall()
    users = []
    for table in tables:
        users.append(table['id'])
    return users

#PW초기화(1234로 초기화시킴)    #admin만 가능
def pw_clear(id):
    #비밀번호 까지 변경
    command = f'''
        UPDATE users SET pw=password('1234') WHERE id = '{id}';
    '''
    sql_cursor.execute(command)
    mydb.commit()
    return print('비밀번호 초기화 성공(1234)')


#새로운 레시피 생성
def new_recipe(dic):
    tmp_dict = dict(dic)
    keys =''
    values = ''
    for key, value in tmp_dict.items():
        keys = keys + key + ','
        values = values + "'" + value + "'" + ","
    keys = keys[:-1]
    values = values[:-1] 

    command = f'''
    INSERT INTO recipes ({keys}) values  ({values});
    '''
    sql_cursor.execute(command)
    mydb.commit()
    return print('레시피 추가 성공')

#레시피 목록출력
def my_recipes(id):
    command = f'''
    SELECT recipe_name FROM recipes WHERE id='{id}';
    '''
    sql_cursor.execute(command)
    recipes =  sql_cursor.fetchall()
    result = []
    for recipe in recipes:
        tmp_dict = dict(recipe)     
        tmp_list = list(tmp_dict.values())      # ['아메리카노', 'A']
        recipe_name = tmp_list[0]
        result.append(recipe_name)
    return result


#레시피보기
def show_detail_recipe(id, recipe_name):
    # {'id': 'A', 'author': 'A', 'recipe_name': '물', 'drink0': '물', 'drink0_amount': '200'}
    command = f'''
    SELECT * FROM recipes WHERE id= '{id}' AND recipe_name='{recipe_name}';
    '''
    sql_cursor.execute(command)
    result = {}
    result_dict = dict(sql_cursor.fetchone())
    for key, value in result_dict.items():
        if value == None:
            continue
        else:
            result[key] = value
    return result

#레시피삭제
def delete_recipe(id, recipe_name):
    command = f'''
    DELETE FROM recipes WHERE id= '{id}' AND recipe_name='{recipe_name}';
    '''
    sql_cursor.execute(command)
    mydb.commit()
    return print('삭제완료')


def update_recipe(id, cmd, recipe_name):
    command = f'''
    UPDATE recipes SET {cmd} WHERE id= '{id}' AND recipe_name='{recipe_name}';
    '''
    sql_cursor.execute(command)
    mydb.commit()
    return print('수정완료')
    #update recipes set drink0_amount=150, drink1_amount=150 WHERE id='A' AND recipe_name='아메리카노';





############## 로컬 ################

# #노즐출력
# def nozzles(id):
#     command = f'''
#     SELECT * FROM nozzles WHERE id='{id}';
#     '''
#     sql_cursor.execute(command)
#     return list(dict(sql_cursor.fetchone()).values())[1:]       # [None, None, None, None, None, None, None, None]

def nozzle_update(new_datas, id):
    command = f'''
    UPDATE nozzles SET {new_datas} WHERE id = '{id}';
    '''
    sql_cursor.execute(command)
    mydb.commit()
    return print('업데이트성공')
