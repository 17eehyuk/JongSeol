from flask import Flask, render_template, request, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import app_sql

# StringField : text박스
# SubmitField : submit 버튼
# DataRequired : 유효성검사

manager = {'id':'3jo', 'pw':'whdtjf123'}

app = Flask(__name__)
app.config['SECRET_KEY'] = "super secret"   #보안용

# Form 생성
class NameForm(FlaskForm):
    form_name = StringField('이름라벨', validators=[DataRequired()])    #validators에 의해서 값이 없으면 안됨
    form_submit = SubmitField('제출라벨')

@app.route('/')
def index():
    return render_template('index.html',html_title='메인')

@app.route('/login/', methods=['POST'])
def login():
    return render_template('login.html',html_title='로그인')


@app.route('/managing/', methods=['GET', 'POST'])
def managing():
    nozzles = app_sql.fetchall_data('nozzles')
    if request.method == 'POST':
        app_sql.clear_table_data('nozzles')
        new_drinks = list(dict(request.form).values())
        drinks_list = ''
        for i in range(8):
            drinks_list = drinks_list + f'''({i}, '{new_drinks[i]}'), '''
        drinks_list = drinks_list[:-2]
        app_sql.insert_datas('nozzles', drinks_list)
        return redirect('/managing/')       #GET으로 전송시키기
    elif request.method == 'GET':
        return render_template('managing.html',html_title='관리', html_nozzles=nozzles, html_update=0)

@app.route('/managing_process/', methods=['POST'])
def managing_process():
    id = request.form['id']
    pw = request.form['pw']
    #로그인
    if manager['id']==id and manager['pw']==pw:
        nozzles = app_sql.fetchall_data('nozzles')
        return render_template('managing.html',html_title='관리', html_nozzles=nozzles, html_update=1)
    else:
        return render_template('login_failed.html',html_title='로그인실패')


    


@app.route('/making/')
def making():
    return render_template('making.html',html_title='제조')

@app.route('/editing/')
def editing():
    return render_template('editing.html',html_title='편집')

@app.route('/sharing/')
def sharing():
    return render_template('sharing.html',html_title='공유')






#요청한 페이지를 찾을 수 없음
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html')


app.run(host='0.0.0.0', port=5000, debug=True)