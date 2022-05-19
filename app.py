from flask import Flask, render_template, request, redirect, session, url_for
from my_modules import my_pysql
import json
import serial

app = Flask(__name__)
app.secret_key = "ssijfo@#!@#123"       # session을 사용하기 위해서는 반드시 있어야함


def local():
    path = "./local.json"
    with open(path, 'r', encoding='utf-8') as json_file:
        return json.load(json_file)

def len3(string):
    if len(string) == 1:
        string = '00'+string
    elif len(string) == 2:
        string = '0'+string
    return string

def len32(string):
    return str(string) + ''.join(list('!' for i in range(32-len(string))))

def my_serial(cmd):
    py_serial = serial.Serial(
        port='COM4',    #본인에게 맞는 포트 설정해주기
        baudrate=9600,
    )
    serial_flag = 0
    rx_result = ''

    while True:
        if py_serial.readable():
            rx = py_serial.readline()[:-1].decode()
            print(rx)
            rx_result = rx_result + rx + '\n'

        # 명령어 전송
        if serial_flag==0 :
            tx = len32(cmd)
            py_serial.write(tx.encode())
            serial_flag = 1

        if rx[0:9] == 'Complete!':
            break
    return rx_result


@app.route('/', methods=['GET', 'POST'])
def index():
    # 더미코드
    try:
        request.form
    except:
        pass
    if 'session_id' in session:
        return render_template('index.html', login_state=True, user_id=session['session_id'])
    else:
        return render_template('index.html', login_state=False)

############################################################### main ###############################################################
@app.route('/managing/', methods=['GET', 'POST'])
def managing():
    if request.method == 'GET':
        if 'session_id' in session:
            my_profile = my_pysql.my_profile(session['session_id'])
            return render_template('./main/managing.html', login_state=True, user_id=session['session_id'], nozzles=local(), nozzle_update=0, my_profile=my_profile)
        else:
            return render_template('./login/login.html', login_state = False)
    elif request.method == 'POST':
       return render_template('./main/managing.html', login_state=True, user_id=session['session_id'], nozzles=local(), nozzle_update=1)

@app.route('/making/', methods=['GET', 'POST'])
def making():
    if request.method == 'GET':
        if 'session_id' in session:
            return render_template('./main/making.html', login_state=True, user_id=session['session_id'])
        else:
            return render_template('./login/login.html', login_state = False)
    elif request.method == 'POST':
       return render_template('./main/making.html', login_state=True, user_id=session['session_id'])



@app.route('/recipe/', methods=['GET', 'POST'])
def recipe():
    # 더미코드 form을 show_recipe와 같이 쓰기 때문에 없으면 오류가남
    try:
        request.form
    except:
        pass
    if 'session_id' in session:
            return render_template('./main/recipe.html', login_state=True, user_id=session['session_id'], recipes=my_pysql.my_recipes(session['session_id']), html_message=0)
    else:
        return render_template('./login/login.html', login_state = False)
        



@app.route('/new_recipe/', methods=['POST'])
def new_recipe():
    # 더미코드 form을 show_recipe와 같이 쓰기 때문에 없으면 오류가남
    try:
        request.form
    except:
        pass
    return render_template('./main/new_recipe.html', login_state=True, user_id=session['session_id'], recipes=my_pysql.my_recipes(session['session_id']))


@app.route('/show_recipe/', methods=['POST'])
def show_recipe():
    recipe_name = request.form['recipe_name']
    recipe_dict = my_pysql.show_detail_recipe(session['session_id'],recipe_name)
    return render_template('./main/show_recipe.html', login_state=True, user_id=session['session_id'] , recipe_dict = recipe_dict)

@app.route('/delete_recipe/', methods=['POST'])
def delete_recipe():
    # 더미코드 form을 show_recipe와 같이 쓰기 때문에 없으면 오류가남
    recipe_name = request.form['recipe_name']
    return render_template('./main/delete_recipe.html', login_state=True, user_id=session['session_id'] ,recipe_name=recipe_name)

@app.route('/update_recipe/', methods=['POST'])
def update_recipe():
    recipe_name = request.form['recipe_name']    
    recipe_dict = my_pysql.show_detail_recipe(session['session_id'],recipe_name)
    return render_template('./main/update_recipe.html', login_state=True, user_id=session['session_id'] , recipe_dict = recipe_dict, recipes=my_pysql.my_recipes(session['session_id']))

@app.route('/make_recipe/', methods=['POST'])
def make_recipe():
    recipe_dict = dict(request.form)                # {'recipe_name': '아메리카노', 'drink0': '물', 'drink0_amount': '200', 'drink1': '에스프레소', 'drink1_amount': '25'}
    recipe_name = recipe_dict['recipe_name']        # 아메리카노
    recipe_len = int((len(recipe_dict)-1)/2)        # 2 (레시피 길이 추출)
    nozzles=local()                                 # {'admin_id': 'admin', 'admin_pw': '1251', 'nozzle0': '', 'nozzle1': '', 'nozzle2': '', 'nozzle3': '우유', 'nozzle4': '', 'nozzle5': '', 'nozzle6': '물', 'nozzle7': '에스프레소'}
                             
    cmd = ''
    err = ''

    for i in range(recipe_len):
        no_nozzle = 1
        drink = recipe_dict['drink'+str(i)]
        for j in range(8):
            nozzle = nozzles['nozzle'+str(j)]
            if drink==nozzle:
                cmd = cmd + str(j) + len3(recipe_dict['drink'+str(i)+'_amount'])
                no_nozzle = 0
                break
        if no_nozzle == 1:
            err = err + f'''{drink} 노즐없음, '''
    
    alert = ''
    print(err[:-2])
    if err=='':     # 에러가 없는 경우
        alert = f'''{recipe_name} 제작완료'''
        serial_result = my_serial(cmd)      # 나중에 보고서 쓸때 주석해놓기
    else:
        alert = err[:-2]
        serial_result = ''
    return render_template('./main/recipe.html', login_state=True, user_id=session['session_id'], recipes=my_pysql.my_recipes(session['session_id']),html_message=1,recipe_name=recipe_name, html_alert=alert, serial_result=serial_result) 



############################################################### main_processes ###############################################################
@app.route('/managing_process/', methods=['POST'])
def managing_process():
    new_nozzles = dict(request.form)
    old_nozzles = local()
    for i in range(len(new_nozzles)):
        nozzle = 'nozzle'+str(i)
        old_nozzles[nozzle] = new_nozzles[nozzle]       # json 데이터 수정
    with open('./local.json', 'w', encoding='utf-8') as update:
        json.dump(old_nozzles, update)      # 수정된 데이터 저장하기
    return redirect('/managing/')

@app.route('/new_recipe_process/', methods=['POST'])
def new_recipe_process():
    my_pysql.new_recipe(request.form)
    return redirect('/recipe/')

@app.route('/delete_recipe_process/', methods=['POST'])
def delete_recipe_process():
    my_pysql.delete_recipe(session['session_id'], request.form['recipe_name'])
    return redirect('/recipe/')



@app.route('/update_recipe_process/', methods=['POST'])
def update_recipe_process():
    # {'recipe_name': '아메리카노', 'drink0': '물', 'drink0_amount': '200', 'drink1': '에스프레소', 'drink1_amount': '25'}
    req_dict= dict(request.form)
    recipe_name = req_dict['recipe_name']
    amounts = int((len(req_dict)-1)/2)
    new_recipe_name = req_dict['new_recipe_name']
    print(new_recipe_name)
    cmd = f'''recipe_name='{new_recipe_name}', '''
    for i in range(amounts):
        drink_amount = 'drink' + str(i) +'_amount'
        drink_amount_num = req_dict[drink_amount]
        cmd = cmd + f'''{drink_amount}='{drink_amount_num}', '''

    cmd = cmd[:-2]
    my_pysql.update_recipe(session['session_id'], cmd, recipe_name)

    return redirect('/recipe/')


############################################################### login ###############################################################  
@app.route('/login/')
def login():
    if 'session_id' in session:     # 이미 로그인한 상태
        return redirect('/')
    else:
        return render_template('./login/login.html', login_state = False)

@app.route('/register/')
def register():
    if 'session_id' in session:     # 이미 로그인한 상태
        return redirect('/')
    else:
        return render_template('./login/register.html', login_state = False)

@app.route('/logout/', methods=['post'])
def logout():
    session.pop('session_id')      # session에서 제거
    return redirect('/')

@app.route('/update_user/', methods=['post'])
def update_user():
    old_profile = dict(request.form)
    return render_template('./login/update_user.html', login_state=True, user_id=session['session_id'], my_profile=my_pysql.my_profile(session['session_id']), old_profile = old_profile)


@app.route('/drop_user/', methods=['post'])
def drop_user():
    #print(request.form)
    return render_template('./login/drop_user.html', login_state=True, user_id=session['session_id'])

@app.route('/admin/', methods=['POST'])
def admin():
    return render_template('./login/admin.html', login_state=True, user_id=session['session_id'], all_users=my_pysql.all_users())

############################################################### login_processes ###############################################################  
@app.route('/login_process/', methods=['POST'])
def login_process():
    user_id = request.form['user_id']
    user_pw = request.form['user_pw']
    if user_id != 'admin':
        sql_result = my_pysql.login(user_id, user_pw)
        # 로그인 실패 (실패시 '''로그인에 실패했습니다.''' 가 반환되므로 type('str') 이다.)
        if type(sql_result) == type('str'):
            return render_template('frame.html', message_state = True, frame_message = sql_result)
        # 로그인 성공
        else:
            session['session_id'] = user_id    # 세션에 현재 아이디 입력
            return redirect('/')
    elif user_id == 'admin':
        if user_pw == local()['admin_pw']:
            session['session_id'] = user_id    # 성공
            return redirect('/')
        else:
            return render_template('frame.html', message_state = True, frame_message = '로그인에 실패했습니다.')

    

@app.route('/register_process/', methods=['POST'])
def register_process():
    user_id = request.form['user_id']
    user_pw = request.form['user_pw']
    user_sex = request.form['user_sex']
    user_yb = request.form['user_yb']
    sql_message =my_pysql.register(user_id, user_pw, user_sex, user_yb)      # return값을 반환하기 때문('이미 존재하는 회원', '회원가입 완료')
    return render_template('frame.html', message_state = True, frame_message = sql_message)

@app.route('/drop_process/', methods=['post'])
def drop_process():
    if session['session_id'] == 'dbadmin':
        # 체크가 안돼있으면 에러 발생 따라서 try/except 이용
        try:
            if request.form['selcetd_user'] == '1':
                if request.form['user_id'] != 'dbadmin':
                    sql_message = my_pysql.drop_user(request.form['user_id'])
        except:
            pass
        return render_template('./login/admin.html', login_state=True, user_id=session['session_id'], all_users=my_pysql.all_users())  
    else:
        sql_message = my_pysql.drop_user(request.form['user_id'])
        if request.form['user_id'] != 'admin':
            session.pop('session_id')      # session에서 제거
        return render_template('frame.html', message_state = True, frame_message = sql_message)

@app.route('/pw_clear_process/', methods=['post'])
def pw_clear_process():
    # 체크가 안돼있으면 에러 발생 따라서 try/except 이용
    try:
        if request.form['selcetd_user'] == '1':
            my_pysql.pw_clear(request.form['user_id'])
    except:
        pass
    return render_template('./login/admin.html', login_state=True, user_id=session['session_id'], all_users=my_pysql.all_users())  


@app.route('/recovery_process/', methods=['post'])
def recovery_process():
    # 체크가 안돼있으면 에러 발생 따라서 try/except 이용
    try:
        if request.form['selcetd_user'] == '1':
            my_pysql.recovery(request.form['user_id'])
    except:
        pass
    return render_template('./login/admin.html', login_state=True, user_id=session['session_id'], all_users=my_pysql.all_users())  





@app.route('/update_process/', methods=['post'])      
def update_process():
    new_sex = request.form['user_sex']
    new_yb = request.form['user_yb']
    new_pw = request.form['user_pw']
    my_pysql.update_profile(new_sex, new_yb, new_pw, session['session_id'])
    return redirect('/managing/')

############################################################### errs ###############################################################
@app.errorhandler(404)
def page_not_found(error):
    if 'session_id' in session:
        return render_template('./errs/404.html', login_state=True, user_id=session['session_id'])
    else:
        return render_template('./errs/404.html', login_state=False)

@app.errorhandler(405)
def page_not_found(error):
    if 'session_id' in session:
        return render_template('./errs/405.html', login_state=True, user_id=session['session_id'])
    else:
        return render_template('./errs/405.html', login_state=False)
####################################################################################################################################
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)