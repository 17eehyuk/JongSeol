from flask import Flask, render_template, request, redirect, session, flash
from my_modules import my_pysql
import json
import socket, time
import serial

app = Flask(__name__)
app.secret_key = "ssijfo@#!@#123"       # session을 사용하기 위해서는 반드시 있어야함
app.jinja_env.add_extension('jinja2.ext.loopcontrols')      # jinja에서 break 사용가능


# ip주소
get_ip_addr = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
get_ip_addr.connect(("8.8.8.8", 80))
ip_addr = get_ip_addr.getsockname()[0]






def esp32_tcp(cmd):
    print(cmd)
    # TCP접속
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip_addr, 9008)) # ip주소(ipconfig IPv4 주소), 포트번호 지정
    server_socket.listen(0)     # 클라이언트의 연결요청을 기다리는 상태    
    client_socket, addr = server_socket.accept() # 연결 요청을 수락함. 길이가 2인 튜플 데이터를 가져옴
    
    # 명령 보내기
    client_socket.send(cmd.encode())      # 클라이언트에게 메세지 전송


    # ESP32 메시지1 (확인용)
    rx_msg = client_socket.recv(100) # 클라이언트로 부터 데이터를 받음. 출력되는 버퍼 사이즈. (만약 2할 경우, 2개의 데이터만 전송됨)
    print(rx_msg.decode()) # 받은 데이터를 해석함.

    # ESP 메시지2 (아두이노 결과)
    rx_msg = client_socket.recv(100) # 클라이언트로 부터 데이터를 받음. 출력되는 버퍼 사이즈. (만약 2할 경우, 2개의 데이터만 전송됨)
    print(rx_msg.decode()) # 받은 데이터를 해석함.

    server_socket.close()   
    time.sleep(1)
    return rx_msg.decode()












############################################################### function ###############################################################
def local():
    path = "./local.json"
    with open(path, 'r', encoding='utf-8') as json_file:
        return json.load(json_file)

def len3(string):
    string =str(string)
    if len(string) == 1:
        string = '00'+string
    elif len(string) == 2:
        string = '0'+string
    return string

def len32(string):
    return str(string) + ''.join(list('!' for i in range(32-len(string))))

def len16(string):
    return str(string) + ''.join(list('!' for i in range(16-len(string))))


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

def manipulated():
    flash('조작감지')
    return render_template('index.html', login_state=True, user_id=session['session_id'])

############################################################### home ###############################################################
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

@app.route('/recipe/', methods=['GET', 'POST'])
def recipe():
    # 더미코드 form을 show_recipe와 같이 쓰기 때문에 없으면 오류가남
    try:
        request.form
    except:
        pass
    if 'session_id' in session:
            return render_template('./main/recipe.html', login_state=True, user_id=session['session_id'], recipes=my_pysql.my_recipes(session['session_id']))
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
    url = request.form['url']
    recipe_dict = my_pysql.show_detail_recipe(session['session_id'],url)
    return render_template('./main/show_recipe.html', login_state=True, user_id=session['session_id'] , recipe_dict = recipe_dict)





@app.route('/delete_recipe/', methods=['POST'])
def delete_recipe():
    recipe_dict = request.form
    return render_template('./main/delete_recipe.html', login_state=True, user_id=session['session_id'] ,recipe_dict=recipe_dict)

@app.route('/update_recipe/', methods=['POST'])
def update_recipe():
    url = request.form['url']    
    recipe_dict = my_pysql.show_detail_recipe(session['session_id'],url)
    return render_template('./main/update_recipe.html', login_state=True, user_id=session['session_id'] , recipe_dict = recipe_dict, recipes=my_pysql.my_recipes(session['session_id']))




@app.route('/make_recipe/', methods=['POST'])
def make_recipe():
    recipe_dict = dict(request.form)                # {'recipe_name': '아메리카노', 'drink0': '물', 'drink0_amount': '200', 'drink1': '에스프레소', 'drink1_amount': '25'}
    print(recipe_dict)
    recipe_name = recipe_dict['recipe_name']        # 아메리카노
    nozzles=local()                                 # {'admin_id': 'admin', 'admin_pw': '1251', 'nozzle0': '', 'nozzle1': '', 'nozzle2': '', 'nozzle3': '우유', 'nozzle4': '', 'nozzle5': '', 'nozzle6': '물', 'nozzle7': '에스프레소'}
                             
    cmd = ''
    err = ''

    for i in range(8):
        no_nozzle = 1
        try:
            drink = recipe_dict['drink'+str(i)]         # 받은값
        except:
            continue
        
        for j in range(8):
            nozzle = nozzles['nozzle'+str(j)]       # json노즐
            if nozzle==drink:
                try:
                    drink_amount = int(recipe_dict['drink'+str(i)+'_amount'])
                    if not((drink_amount >= 0) and (drink_amount <= 600)):
                        print('try')
                        no_nozzle = 2
                        break
                    else:
                        cmd = cmd + str(j) + len3(drink_amount)
                        no_nozzle = 0
                        break
                except:
                    print('except')
                    no_nozzle = 2
                    break
                
        if no_nozzle == 1:
            err = err + f'''{drink} 노즐없음, '''
        if no_nozzle == 2:
            # 조작함
            return manipulated()
    
    alert = ''
    if err != '':
        msg = err[:-2]
        print(msg)
        alert = msg
    else:
        try:
            # my_serial(cmd)
            cmd = len16(cmd)
            alert = esp32_tcp(cmd)

            # if err=='':     # 에러가 없는 경우
            #     # alert = f'''{recipe_name} 제작완료'''
            #     alert = f'''{cmd}'''
            # else:
            #     alert = err[:-2]    
        except:
            alert = '사용할수 없는 상태'

    
    recipe_dict = my_pysql.show_recipe_url(recipe_dict['url'])      # 조금 조잡하긴한데 옛날코드와 호환이 달라서 재갱신 코드가 필요
    flash(alert)
    return render_template('./main/show_recipe.html', login_state=True, user_id=session['session_id'] , recipe_dict = recipe_dict)



@app.route('/sharing/')
def sharing_home():
    recipes = my_pysql.show_all_sharings()
    if 'session_id' in session:
        return render_template('./main/sharing.html', login_state=True, user_id=session['session_id'], recipes=recipes)
    else:
        return render_template('./login/login.html', login_state = False)
    

@app.route('/sharing_read/<url>/', methods=['GET','POST'])
def sharing_read(url):
    try:
        recipe = my_pysql.show_recipe_url(url)
        if recipe['share'] != '1':
            flash('비공개됐거나 삭제된 레시피 입니다.')
            return redirect('/recipe/')
    except:
        flash('비공개됐거나 삭제된 레시피 입니다.')
        return redirect('/recipe/')

    comments = my_pysql.fetch_comments(url)
    if 'session_id' in session:
        return render_template('./main/sharing_read.html', login_state=True, user_id=session['session_id'], recipe=recipe, comments=comments)
    else:
        return render_template('./login/login.html', login_state = False)



@app.route('/sharing_page/', methods=['POST'])
def sharing_page():

    comments = my_pysql.fetch_comments(request.form['url'])

    recipe = my_pysql.show_recipe_url(request.form['url'])
    print(recipe)
    if recipe['share'] == '0': 
        return render_template('./main/sharing_page.html', login_state=True, user_id=session['session_id'], recipe=recipe, comments=comments)
    elif recipe['share'] == '1':
        flash('이미공유중')
    elif recipe['share'] == '2':
        flash('타인의 레시피는 공개불가')
    return render_template('./main/show_recipe.html', login_state=True, user_id=session['session_id'] , recipe_dict = recipe)
    

@app.route('/sharing_hide/<url>/', methods=['POST'])
def sharing_hide(url):
    flash(my_pysql.sharing_hide(url))
    recipe_dict = my_pysql.show_recipe_url(url)
    return render_template('./main/show_recipe.html', login_state=True, user_id=session['session_id'] , recipe_dict = recipe_dict)



@app.route('/sharing_process/<url>/', methods=['POST'])
def sharing_process(url):    
    title = request.form['title']
    content = request.form['content']
    flash(my_pysql.sharing(url, title, content))
    return redirect(f'/sharing_read/{url}/')




@app.route('/comment/<url>/', methods=['post'])
def comment(url):
    req_dict = dict(request.form)
    if len(req_dict['content'])>25:
        flash('글자수초과')
    else:
        req_dict['id'] = session['session_id']          # 댓글에 id 추가
        print(my_pysql.new_comments(req_dict,url))
    return redirect(f'/sharing_read/{url}/')


@app.route('/delete_comment/<comment_id>/', methods=['post'])
def delete_comment(comment_id):
    url = request.form['url']
    print(my_pysql.delete_comment(url, comment_id))
    return redirect(f'/sharing_read/{url}/')



@app.route('/sharing_copy/<url>/', methods=['post'])
def sharing_copy(url):
    if my_pysql.copy_check(session['session_id'], url) == 'available':
        flash(my_pysql.sharing_copy(session['session_id'], url))
    elif my_pysql.copy_check(session['session_id'], url) == 'unavailable':
        # else 써도 되지만 직관적이게 'unavailable' 적었음
        flash('이미 존재하는 레시피입니다.')    
    return redirect(f'/sharing_read/{url}/')
























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
    result = my_pysql.new_recipe(session['session_id'],request.form)
    if(result=='manipulated'):
        return manipulated()
    flash(result)
    return redirect('/recipe/')

@app.route('/delete_recipe_process/', methods=['POST'])
def delete_recipe_process():
    flash(my_pysql.delete_recipe(session['session_id'], request.form['recipe_name']))
    return redirect('/recipe/')


@app.route('/update_recipe_process/', methods=['POST'])
def update_recipe_process():
    # {'recipe_name': '아메리카노', 'drink0': '물', 'drink0_amount': '200', 'drink1': '에스프레소', 'drink1_amount': '25'}
    req_dict= dict(request.form)
    print(req_dict)

    url = req_dict['url']

    cmd = ''
    for i in range(8):
        try:
            drink_amount = 'drink' + str(i) +'_amount'
            drink_amount_num = req_dict[drink_amount]
            cmd = cmd + f'''{drink_amount}='{drink_amount_num}', '''
        except:
            # 노즐이 없는경우 오류가 발생하는데 그러면 break를 통해서 for문 탈출
            break
    cmd = cmd[:-2]
    print(cmd)

    flash(my_pysql.update_recipe(cmd ,url))
    
    recipe_dict = my_pysql.show_detail_recipe(session['session_id'],req_dict['url'])
    return render_template('./main/show_recipe.html', login_state=True, user_id=session['session_id'] , recipe_dict = recipe_dict)


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
            flash(sql_result)
            return redirect('/')
        # 로그인 성공
        else:
            session['session_id'] = user_id    # 세션에 현재 아이디 입력
            return redirect('/')
    elif user_id == 'admin':
        if user_pw == local()['admin_pw']:
            session['session_id'] = user_id    # 성공
            return redirect('/')
        else:
            flash('로그인에 실패했습니다.')
            return redirect('/')

    

@app.route('/register_process/', methods=['POST'])
def register_process():
    print(request.form)
    user_id = request.form['user_id']
    user_pw = request.form['user_pw']
    user_sex = request.form['user_sex']
    user_yb = request.form['user_yb']
    result = my_pysql.register(user_id, user_pw, user_sex, user_yb)      # return값을 반환하기 때문('이미 존재하는 회원', '회원가입 완료')
    if result == 'manipulated':
        result = '조작감지'
    flash(result)
    return redirect('/')

@app.route('/drop_process/', methods=['post'])
def drop_process():
    if session['session_id'] == 'dbadmin':
        # 체크가 안돼있으면 에러 발생 따라서 try/except 이용
        try:
            if request.form['selcetd_user'] == '1':
                if request.form['user_id'] != 'dbadmin':
                    sql_message = my_pysql.drop_user(request.form['user_id'])
                    flash(sql_message)
        except:
            pass
        return render_template('./login/admin.html', login_state=True, user_id=session['session_id'], all_users=my_pysql.all_users())  
    else:
        my_pysql.drop_user(request.form['user_id'])
        session.pop('session_id')      # session에서 제거
        return redirect('/')

@app.route('/pw_clear_process/', methods=['post'])
def pw_clear_process():
    # 체크가 안돼있으면 에러 발생 따라서 try/except 이용
    try:
        if request.form['selcetd_user'] == '1':
            sql_message = my_pysql.pw_clear(request.form['user_id'])
            flash(sql_message)
    except:
        pass
    return render_template('./login/admin.html', login_state=True, user_id=session['session_id'], all_users=my_pysql.all_users())  


@app.route('/recovery_process/', methods=['post'])
def recovery_process():
    # 체크가 안돼있으면 에러 발생 따라서 try/except 이용
    try:
        if request.form['selcetd_user'] == '1':
            sql_message = my_pysql.recovery(request.form['user_id'])
            flash(sql_message)
    except:
        pass
    return render_template('./login/admin.html', login_state=True, user_id=session['session_id'], all_users=my_pysql.all_users())  





@app.route('/update_process/', methods=['post'])      
def update_process():
    new_sex = request.form['user_sex']
    new_yb = request.form['user_yb']
    new_pw = request.form['user_pw']
    if(my_pysql.update_profile(new_sex, new_yb, new_pw, session['session_id']) == 'manipulated'):
        return manipulated()
    return redirect('/managing/')

############################################################### errs ###############################################################
@app.errorhandler(404)
def page_not_found(error):
    flash('페이지없음')
    return redirect('/')

@app.errorhandler(405)
def page_not_found(error):
    flash('잘못된접근')
    return redirect('/')
####################################################################################################################################
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)