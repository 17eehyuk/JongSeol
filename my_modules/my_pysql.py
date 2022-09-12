from unittest import result
import pymysql
import time, datetime
import json


# UPDATE recipes SET rate = rate + 1 WHERE url='{url}';

def cnn():
    mydb = pymysql.connect(
    user='tmp',
    database='jongseol',
    passwd='1234',
    host='127.0.0.1',       #Local
    # host='3.39.94.57',      #AWS
    charset='utf8'
    )
    return mydb

#로그인
def login(id, pw):
    mydb = cnn()
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    command = f'''
    SELECT id, pw FROM users WHERE id = '{id}' AND pw = md5('{pw}') AND state='0';
    '''
    sql_cursor.execute(command)
    result = sql_cursor.fetchone()
    mydb.commit()
    sql_cursor.close()
    mydb.close()
    if result == None:
        return '''로그인에 실패했습니다.'''
    else:
        return result        # 데이터가 있으며 {'userid': 'A', 'userpw': '1234'}, 없으면 None 이 return됨
#회원가입
def register(id, pw, sex, yb):

    if not((sex=='M')or(sex=='F')):
        return 'manipulated'
    try:
        yb = int(yb)
        adult_year = datetime.datetime.now().year -18
        if not((yb>=1900) and (yb<=adult_year)):
            return 'manipulated'
    except:
        return 'manipulated'


    if (id=='admin') or (id=='dbadmin') or not(str(id).isalnum()):      # not(str(id).isalnum()): 특수문자방지
        return '''사용불가능한 id 입니다.'''
    mydb = cnn()
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
    mydb.close()
    return result



#회원탈퇴
def drop_user(id):
    mydb = cnn()
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    command = f'''
    UPDATE users SET state='1' WHERE id = '{id}';
    '''
    sql_cursor.execute(command)
    mydb.commit()
    sql_cursor.close()
    mydb.close()
    return f'''사용자 {id} 탈퇴 성공'''



#개인정보확인
def my_profile(id):
    mydb = cnn()
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    command = f'''
        SELECT sex, yb FROM users WHERE id='{id}';
    '''
    sql_cursor.execute(command)
    result = sql_cursor.fetchone()
    mydb.commit()
    sql_cursor.close()
    mydb.close()
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
    mydb = cnn()
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    if pw == '':        
        #비밀번호 변경X
        command = f'''
        UPDATE users SET sex='{sex}', yb='{yb}' WHERE id = '{id}';
        '''
        sql_cursor.execute(command)
        mydb.commit()
        sql_cursor.close()
        mydb.close()
        return print('업데이트성공')
    else:
        #비밀번호 까지 변경
        command = f'''
            UPDATE users SET sex='{sex}', yb='{yb}', pw=md5('{pw}') WHERE id = '{id}';
        '''
        sql_cursor.execute(command)
        mydb.commit()
        sql_cursor.close()
        mydb.close()
        return print('업데이트성공')


#레시피명 중복인지 확인 (return 값이 None이면 중복 없음, 아닌경우 중복존재)
def dup_check(id, recipe_name):
    mydb = cnn()
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    command = f'''
    SELECT * FROM recipes WHERE id= '{id}' AND recipe_name='{recipe_name}';
    '''
    sql_cursor.execute(command)
    result = sql_cursor.fetchone()
    mydb.commit()
    sql_cursor.close()
    mydb.close()
    return result


#새로운 레시피 생성
def new_recipe(id, dic):
    tmp_dict = dict(dic)                     # {'recipe_name': '아메리카노', 'drink0': '물', 'drink0_amount': '600', 'drink1': '에스프레소', 'drink1_amount': '100'}
    print(tmp_dict)


    # 레시피명과 0번은 공백이 될 수 가 없음, 오류역시 말도안됨
    try:
        if ((tmp_dict['recipe_name']=='') or (tmp_dict['drink0'] == '') or (tmp_dict['drink0_amount'] == '')):
            return 'manipulated'
    except:
        return 'manipulated'

    
    dic_len = int((len(tmp_dict) - 1)/2)     # -1: recipe_name

    if (dic_len<1) or (dic_len>8):       # 행이 하나도 없다는 의미, 행을 많이 추가한 경우
        return 'manipulated'
   

    # 새 레시피이기 때문에 무조건 id==author
    keys ='url, id , author, recipe_name, comments, '
    values = f''' replace(unix_timestamp(now(6)), '.','0'), '{id}', '{id}', '{tmp_dict['recipe_name']}', '{{}}', '''

    total_amout = 0

    for i in range(dic_len):
        drink = 'drink' + str(i)                # drink0
        drink_amount = drink + '_amount'        # drink0_amount

        keys = keys + drink + ', ' + drink_amount + ', '

        try:
            amount = int(tmp_dict[drink_amount])
            if not((amount > 0) and (amount <= 600)):
                return 'manipulated'

            total_amout = total_amout + amount
            
            if total_amout>700:
                return 'manipulated'

        except:
            # int()가 안된다는 의미 따라서 무조건 조작
            return 'manipulated'       
        values = values + f''' '{tmp_dict[drink]}', '{tmp_dict[drink_amount]}', '''


    keys = keys[:-2]
    values = values[:-2]
    mydb = cnn()
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    command = f'''
    INSERT INTO recipes ({keys}) values  ({values});
    '''
    print(command)

    sql_cursor.execute(command)
    mydb.commit()
    sql_cursor.close()
    mydb.close()

    return '레시피 추가 성공'

#레시피 목록출력
def my_recipes(id):
    mydb = cnn()
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    command = f'''
    SELECT url, time, author, recipe_name FROM recipes WHERE id='{id}';
    '''
    sql_cursor.execute(command)
    recipes =  sql_cursor.fetchall()
    mydb.commit()
    sql_cursor.close()
    mydb.close()
    return recipes


#레시피보기
def show_detail_recipe(id, url):
    mydb = cnn()
    # {'id': 'A', 'author': 'A', 'recipe_name': '물', 'drink0': '물', 'drink0_amount': '200'}
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    command = f'''
    SELECT * FROM recipes WHERE id= '{id}' AND url='{url}';
    '''
    sql_cursor.execute(command)
    result_dict = dict(sql_cursor.fetchone())
    mydb.commit()
    sql_cursor.close()
    mydb.close()
    return result_dict

#레시피삭제
def delete_recipe(id, recipe_name):
    mydb = cnn()
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    command = f'''
    DELETE FROM recipes WHERE id= '{id}' AND recipe_name='{recipe_name}';
    '''
    sql_cursor.execute(command)
    mydb.commit()
    sql_cursor.close()
    mydb.close()
    return '삭제완료'


def update_recipe(cmd, url):
    mydb = cnn()
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    command = f'''
    UPDATE recipes SET share_time='{now}', {cmd} WHERE url='{url}';
    '''
    sql_cursor.execute(command)
    mydb.commit()
    sql_cursor.close()
    mydb.close()
    return '수정완료'
    #update recipes set drink0_amount=150, drink1_amount=150 WHERE id='A' AND recipe_name='아메리카노';


def show_recipe_url(url):
    mydb = cnn()
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    command = f'''
    SELECT * FROM recipes WHERE url = '{url}'
    '''
    sql_cursor.execute(command)
    mydb.commit()
    result_dict = sql_cursor.fetchone()
    # 없는경우 None
    if result_dict != None:
        result_dict = dict(result_dict)
    sql_cursor.close()
    mydb.close()
    return result_dict



# {'url': '165313508204980', 'share': '0', 'time': datetime.datetime(2022, 5, 21, 21, 11, 22), 'share_time': datetime.datetime(2022, 5, 21, 21, 11, 22), 'title': '', 'id': 'a', 'author': 'a',
# 'recipe_name': 'gd', 'drink0': '노', 'drink0_amount': '600', 'drink1': None, 'drink1_amount': None, 'drink2': None, 'drink2_amount': None, 'drink3': None, 'drink3_amount': None, 'content': '', 'comments': '{}'}


def sharing(url, title, content):
    mydb = cnn()
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cmd = f'''
    share='1', share_time='{now}', title='{title}', content='{content}'
    '''
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    command = f'''
    UPDATE recipes SET {cmd} WHERE url= '{url}';
    '''
    sql_cursor.execute(command)
    mydb.commit()
    sql_cursor.close()
    mydb.close()
    return '공유완료'

def show_sharings(page_count, recipe_name=''):
    mydb = cnn()
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    if recipe_name=='':
        command = f'''
        SELECT * FROM recipes WHERE share='1' ORDER BY share_time DESC LIMIT {5*(page_count-1)}, 5;
        '''
    else:
        command = f'''
        SELECT * FROM recipes WHERE share='1' AND recipe_name = '{recipe_name}' ORDER BY share_time DESC LIMIT {5*(page_count-1)}, 5;
        '''
    sql_cursor.execute(command)
    mydb.commit()
    recipes = sql_cursor.fetchall()   # 없는경우는 tuple임    # 있는경우는 list임
    sql_cursor.close()
    mydb.close()
    if recipes == ():
        recipes = 'empty'
    return recipes


def sharing_recipe_row_count(recipe_name=''):
    mydb = cnn()
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    if recipe_name=='':
        command = f'''
        SELECT COUNT(*) FROM recipes WHERE share = '1';
        '''
    else:
        command = f'''
        SELECT COUNT(*) FROM recipes WHERE share = '1' AND recipe_name = '{recipe_name}';
        '''
    sql_cursor.execute(command)
    mydb.commit()
    count = sql_cursor.fetchone()   # 없는경우는 tuple임    # 있는경우는 list임
    sql_cursor.close()
    mydb.close()
    return count['COUNT(*)']


def sharing_hide(url):
    mydb = cnn()
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    command = f'''
    UPDATE recipes SET share='0' WHERE url= '{url}';
    '''
    sql_cursor.execute(command)
    mydb.commit()
    sql_cursor.close()
    mydb.close()
    return '비공개완료'

def sharing_search_by_ingredient(ingredient):
    # 수정해야됨 #
    mydb = cnn()
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    command = f'''
    (SELECT * FROM recipes WHERE drink0 LIKE '{ingredient}')
    UNION
    (SELECT * FROM recipes WHERE drink1 LIKE '{ingredient}')
    UNION
    (SELECT * FROM recipes WHERE drink2 LIKE '{ingredient}')
    UNION
    (SELECT * FROM recipes WHERE drink3 LIKE '{ingredient}');
    '''
    sql_cursor.execute(command)
    mydb.commit()
    recipes = sql_cursor.fetchall()   # 없는경우는 tuple임    # 있는경우는 list임
    sql_cursor.close()
    mydb.close()
    if recipes == ():
        recipes = 'empty'
    return recipes

    
def sharing_search_by_recipe_name(recipe_name):
    mydb = cnn()
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    command = f'''
    SELECT * FROM recipes WHERE share = '1' AND recipe_name = '{recipe_name}'
    '''
    sql_cursor.execute(command)
    mydb.commit()
    recipes = sql_cursor.fetchall()   # 없는경우는 tuple임    # 있는경우는 list임
    sql_cursor.close()
    mydb.close()
    if recipes == ():
        recipes = 'empty'
    return recipes



############## 관리자 ################


#모든유저출력
def all_users():
    mydb = cnn()
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    command = f'''
    SELECT id FROM users;
    '''
    sql_cursor.execute(command)
    tables =  sql_cursor.fetchall()
    mydb.commit()
    sql_cursor.close()
    mydb.close()
    users = []
    for table in tables:
        users.append(table['id'])
    return users

#PW초기화(1234로 초기화시킴)    #admin만 가능
def pw_clear(id):
    mydb = cnn()
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    #비밀번호 까지 변경
    command = f'''
        UPDATE users SET pw=md5('1234') WHERE id = '{id}';
    '''
    sql_cursor.execute(command)
    mydb.commit()
    sql_cursor.close()
    mydb.close()
    return f'''사용자 {id} 비밀번호 초기화 성공(1234)'''


# 계정복구
def recovery(id):
    mydb = cnn()
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    command = f'''
    UPDATE users SET state='0' WHERE id = '{id}';
    '''
    sql_cursor.execute(command)
    mydb.commit()
    sql_cursor.close()
    mydb.close()
    return f'''사용자 {id} 복구성공'''


# json -> dict
def fetch_comments(url):
    # 댓글
    mydb = cnn()
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    sql_cmd = f'''
    SELECT comments FROM recipes WHERE url='{url}';
    '''
    sql_cursor.execute(sql_cmd)
    try:
        comments = sql_cursor.fetchone()['comments']
        comments = json.loads(comments)
    except:
        comments = {}
    sql_cursor.close()
    mydb.close()
    return comments

# a=fetch_comments('16532049760734386')
# print(a)
# print(type(a))



def new_comments(req_dict : dict, url):
    # 새댓글
    comment_id = str(time.time()).replace('.','0')
    nowDatetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    old_comments = fetch_comments(url)

    req_dict['time'] = nowDatetime
    # json은 따옴표 금지
    req_dict['content'] = req_dict['content'].strip('"')
    req_dict['content'] = req_dict['content'].strip("'")
    req_dict['content'] = req_dict['content'].strip('\\')

    new_comment = {comment_id : req_dict}

    # 합치기
    comments = dict(old_comments, **new_comment)
    comments = json.dumps(comments, ensure_ascii=False)  # dict -> json 변환

    # SQL
    mydb = cnn()
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    sql_cmd = f'''
    UPDATE recipes SET comments = '{comments}' WHERE url='{url}';
    '''
    sql_cursor.execute(sql_cmd)
    mydb.commit()
    sql_cursor.close()
    mydb.close()
    return '추가완료'

def delete_comment(url, comment_id):
    comments = fetch_comments(url)
    for key in comments.keys():
        if key == comment_id:
            del comments[comment_id]
            comments = json.dumps(comments, ensure_ascii=False)  # dict -> json 변환
            mydb = cnn()
            sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
            sql_cmd = f'''
            UPDATE recipes SET comments = '{comments}' WHERE url='{url}';
            '''
            sql_cursor.execute(sql_cmd)
            mydb.commit()
            sql_cursor.close()
            mydb.close()
            return '삭제성공'


def show_columns(table_name):
    mydb = cnn()
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    sql_cmd = f'''
    SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}';
    '''
    sql_cursor.execute(sql_cmd)
    mydb.commit()
    column_names = sql_cursor.fetchall()
    sql_cursor.close()
    mydb.close()
    column_names_list = []
    for column_name in column_names:
        column_names_list.append(column_name['COLUMN_NAME'])
    return column_names_list



def recipe_count(id):
    mydb = cnn()
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    sql_cmd = f'''
    SELECT recipe_name FROM recipes WHERE id='{id}';
    '''
    sql_cursor.execute(sql_cmd)
    mydb.commit()
    recipe_names = sql_cursor.fetchall()
    sql_cursor.close()
    mydb.close()
    return len(recipe_names)   




def sharing_copy(id, url):
    # 복사하는 함수
    if recipe_count(id)<8:
        # 가져올: copy_url, share, id,       author, recipe_name, drink0, drink0_amount
        # 매칭될: url,       2,    내아이디, author, recipe_name,  drink0, drink0_amount
        mydb = cnn()
        sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
        sql_cmd = f'''
        INSERT INTO recipes (url, copy_url, share, id, author, recipe_name, drink0, drink0_amount, drink1, drink1_amount)
        SELECT replace(unix_timestamp(now(6)), '.','0'), url, '2', '{id}', author, recipe_name, drink0, drink0_amount, drink1, drink1_amount FROM recipes WHERE url='{url}';
        '''
        sql_cursor.execute(sql_cmd)
        mydb.commit()
        sql_cursor.close()
        mydb.close()
        return '복사완료'
    else:
        return '레시피 8개 초과' 


# 복사 1번만 가능하게 하는 함수
def copy_check(id, url):
    mydb = cnn()
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    sql_cmd = f'''
    SELECT * FROM recipes WHERE id='{id}' AND copy_url = '{url}';
    '''
    sql_cursor.execute(sql_cmd)
    mydb.commit()
    result = sql_cursor.fetchone()
    sql_cursor.close()
    mydb.close()
    # 결과가 없으면 copy 가능 있으면 copy 불가
    if result == None:
        return 'available'
    else:
        return 'unavailable'

# def fetch_copied(url):
#     mydb = cnn()
#     sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
#     sql_cmd = f'''
#     SELECT url, author, recipe_name, drink0, drink0_amount, drink1, drink1_amount FROM recipes WHERE url='{url}';
#     '''
#     sql_cursor.execute(sql_cmd)
#     mydb.commit()
#     copied = sql_cursor.fetchone()
#     sql_cursor.close()
#     mydb.close()
#     return copied

# # INSERT INTO recipes (url, id , author, recipe_name, comments, drink0, drink0_amount) values  ( replace(unix_timestamp(now(6)), '.','0'), 'a', 'a', '물', '{}',  '물', '600');
    
# def sharing_copy(id, url):
#     copied_data = fetch_copied(url)
#     mydb = cnn()
#     sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
#     sql_cmd = f'''
#     INSERT INTO recipes (copy_url, share, id, author, recipe_name, drink0, drink0_amount, drink1, drink1_amount)
#     VALUES ('{copied_data['url']}', '2', '{id}', '{copied_data['author']}', '{copied_data['recipe_name']}',
#     '{copied_data['drink0']}', '{copied_data['drink0_amount']}',
#     '{copied_data['drink1']}', '{copied_data['drink1_amount']}');
#     '''
#     print(sql_cmd)
#     sql_cursor.execute(sql_cmd)
#     mydb.commit()
#     sql_cursor.close()
#     mydb.close()
#     return '복사완료'


# sharing_copy('gd', '16532303070759508')


# print(show_columns('recipes'))
# print(show_recipe_url('16532164050765863'))


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

