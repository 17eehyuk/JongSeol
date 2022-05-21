import pymysql
import time, datetime

# # AWS
# mydb = pymysql.connect(
#     user='tmp',
#     database='jongseol',
#     passwd='1234',
#     host='3.39.94.57',
#     charset='utf8'
# )
# Local
mydb = pymysql.connect(
    user='tmp',
    database='jongseol',
    passwd='1234',
    host='localhost',
    charset='utf8'
)




#로그인
def login(id, pw):
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    command = f'''
    SELECT id, pw FROM users WHERE id = '{id}' AND pw = md5('{pw}') AND state='0';
    '''
    sql_cursor.execute(command)
    result = sql_cursor.fetchone()
    sql_cursor.close()
    if result == None:
        return '''로그인에 실패했습니다.'''
    else:
        return result        # 데이터가 있으며 {'userid': 'A', 'userpw': '1234'}, 없으면 None 이 return됨
#회원가입
def register(id, pw, sex, yb):

    if not((sex=='M')or(sex=='F')):
        return '조작감지' #'manipulated'

    try:
        yb = int(yb)
        adult_year = datetime.datetime.now().year -18
        if not((yb>=1900) and (yb<=adult_year)):
            return '조작감지' #'manipulated'
    except:
        return '조작감지' #'manipulated'


    if (id=='admin') or (id=='dbadmin') or not(str(id).isalnum()):      # not(str(id).isalnum()): 특수문자방지
        return '''사용불가능한 id 입니다.'''
    
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    command = f'''
    INSERT INTO users VALUES ('{id}', md5('{pw}'), '{sex}', '{yb}', '0');
    '''
    try:
        sql_cursor.execute(command)         # 중복인 경우 에러 발생하므로 try/except 사용
        mydb.commit()
        result = f'''{id}님 회원가입을 축하드립니다.'''
    except:
        result = f'''아이디 : {id} 중복입니다. 다른 아이디를 사용해 주세요'''
    
    sql_cursor.close()
    return result



#회원탈퇴
def drop_user(id):
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    command = f'''
    UPDATE users SET state='1' WHERE id = '{id}';
    '''
    sql_cursor.execute(command)
    mydb.commit()
    sql_cursor.close()
    return f'''사용자 {id} 탈퇴 성공'''



#개인정보확인
def my_profile(id):
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    command = f'''
        SELECT sex, yb FROM users WHERE id='{id}';
    '''
    sql_cursor.execute(command)
    result = sql_cursor.fetchone()
    sql_cursor.close()
    return result

#개인정보 수정
def update_profile(sex, yb, pw, id):

    if not((sex=='M')or(sex=='F')):
        return 'manipulated'

    try:
        yb = int(yb)
        adult_year = datetime.datetime.now().year -18
        if not((yb>=1900) and (yb<=adult_year)):
            return 'manipulated'
    except:
        return 'manipulated'
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    if pw == '':        
        #비밀번호 변경X
        command = f'''
        UPDATE users SET sex='{sex}', yb='{yb}' WHERE id = '{id}';
        '''
        sql_cursor.execute(command)
        mydb.commit()
        sql_cursor.close()
        return print('업데이트성공')
    else:
        #비밀번호 까지 변경
        command = f'''
            UPDATE users SET sex='{sex}', yb='{yb}', pw=md5('{pw}') WHERE id = '{id}';
        '''
        sql_cursor.execute(command)
        mydb.commit()
        sql_cursor.close()
        return print('업데이트성공')


#레시피명 중복인지 확인 (return 값이 None이면 중복 없음, 아닌경우 중복존재)
def dup_check(id, recipe_name):
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    command = f'''
    SELECT * FROM recipes WHERE id= '{id}' AND recipe_name='{recipe_name}';
    '''
    sql_cursor.execute(command)
    result = sql_cursor.fetchone()
    sql_cursor.close()
    return result


#새로운 레시피 생성
def new_recipe(id, dic):
    tmp_dict = dict(dic)                     # {'id': 'a', 'author': 'a', 'recipe_name': '물', 'drink0': '물', 'drink0_amount': '200'}
    dic_len = int((len(tmp_dict) - 3)/2)     # id, author, recipe_name

    if (dic_len<1) or (dic_len>8):       # 행이 하나도 없다는 의미, 행을 많이 추가한 경우
        return 'manipulated'
    try:
        if (id != tmp_dict['id'] or id != tmp_dict['author']):        # 새 레시피이기 때문에 반드시 id와 author가 같아야됨
            return 'manipulated'
    except:
        return 'manipulated'                                          # 오류가 날 수가 없는데 오류가 난 경우이므로 무조건 조작

    if dup_check(id, tmp_dict['recipe_name']) != None:               # 유효성검사를 한다면 무조건 None이어야되는데 아닌경우이므로 조작한것
        return 'manipulated'


    url = str(time.time()).replace('.','0')[:15]

    keys ='url, id , author, recipe_name, '
    values = f''' '{url}', '{tmp_dict['id']}', '{tmp_dict['author']}', '{tmp_dict['recipe_name']}', '''


    for i in range(dic_len):
        drink = 'drink' + str(i)                # drink0
        drink_amount = drink + '_amount'        # drink0_amount

        keys = keys + drink + ', ' + drink_amount + ', '

        try:
            amount = int(tmp_dict[drink_amount])
            if not((amount >= 0) and (amount <= 600)):
                return 'manipulated'
        except:
            return 'manipulated'       # 숫자로 안바뀐다는 의미 따라서 조작


        values = values + f''' '{tmp_dict[drink]}', '{tmp_dict[drink_amount]}', '''
    keys = keys[:-2]
    values = values[:-2]

    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    command = f'''
    INSERT INTO recipes ({keys}) values  ({values});
    '''
    print(command)

    sql_cursor.execute(command)
    mydb.commit()
    sql_cursor.close()

    return print('레시피 추가 성공')

#레시피 목록출력
def my_recipes(id):
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    command = f'''
    SELECT recipe_name FROM recipes WHERE id='{id}';
    '''
    sql_cursor.execute(command)
    recipes =  sql_cursor.fetchall()
    sql_cursor.close()
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
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    command = f'''
    SELECT * FROM recipes WHERE id= '{id}' AND recipe_name='{recipe_name}';
    '''
    sql_cursor.execute(command)
    result_dict = dict(sql_cursor.fetchone())
    sql_cursor.close()
    return result_dict

#레시피삭제
def delete_recipe(id, recipe_name):
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    command = f'''
    DELETE FROM recipes WHERE id= '{id}' AND recipe_name='{recipe_name}';
    '''
    sql_cursor.execute(command)
    mydb.commit()
    sql_cursor.close()
    return print('삭제완료')


def update_recipe(id, cmd, recipe_name):
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    command = f'''
    UPDATE recipes SET {cmd} WHERE id= '{id}' AND recipe_name='{recipe_name}';
    '''
    sql_cursor.execute(command)
    mydb.commit()
    sql_cursor.close()
    return print('수정완료')
    #update recipes set drink0_amount=150, drink1_amount=150 WHERE id='A' AND recipe_name='아메리카노';


def show_recipe_url(url):
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    command = f'''
    SELECT * FROM recipes WHERE url = '{url}'
    '''
    sql_cursor.execute(command)
    result_dict = dict(sql_cursor.fetchone())
    sql_cursor.close()
    return result_dict


############## 관리자 ################


#모든유저출력
def all_users():
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    command = f'''
    SELECT id FROM users;
    '''
    sql_cursor.execute(command)
    tables =  sql_cursor.fetchall()
    sql_cursor.close()
    users = []
    for table in tables:
        users.append(table['id'])
    return users

#PW초기화(1234로 초기화시킴)    #admin만 가능
def pw_clear(id):
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    #비밀번호 까지 변경
    command = f'''
        UPDATE users SET pw=md5('1234') WHERE id = '{id}';
    '''
    sql_cursor.execute(command)
    mydb.commit()
    sql_cursor.close()
    return f'''사용자 {id} 비밀번호 초기화 성공(1234)'''


# 계정복구
def recovery(id):
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    command = f'''
    UPDATE users SET state='0' WHERE id = '{id}';
    '''
    sql_cursor.execute(command)
    mydb.commit()
    sql_cursor.close()
    return f'''사용자 {id} 복구성공'''








############## 더미코드 ################

# #노즐출력
# def nozzles(id):
#     command = f'''
#     SELECT * FROM nozzles WHERE id='{id}';
#     '''
#     sql_cursor.execute(command)
#     return list(dict(sql_cursor.fetchone()).values())[1:]       # [None, None, None, None, None, None, None, None]

# def nozzle_update(new_datas, id):
#     command = f'''
#     UPDATE nozzles SET {new_datas} WHERE id = '{id}';
#     '''
#     sql_cursor.execute(command)
#     mydb.commit()
#     return print('업데이트성공')


# #회원탈퇴
# def drop_user(id):
#     command = f'''
#         SHOW TABLES
#         '''
#     sql_cursor.execute(command)
#     tables =  sql_cursor.fetchall()
#     for table in tables:
#         current_table = list(dict(table).values())[0]        # 현재 테이블명
#         command = f'''
#         DELETE FROM {current_table} WHERE id='{id}';
#         '''
#         sql_cursor.execute(command)
#         mydb.commit()
#     return f'''사용자 '{id}' 탈퇴 성공'''

