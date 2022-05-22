from flask import Flask, render_template, redirect, request, flash
import pymysql
import json
import time, datetime

#MySQL 접속
mydb = pymysql.connect(
    user='tmp',
    database='tmpdb',
    passwd='1234',
    host='localhost',
    charset='utf8'
)

app = Flask(__name__)
app.secret_key = 'jiqwejioqjweoijqwoiej'        # flash를 사용하기 위해서는 필요 (아무값이나 가능)

@app.route('/')
def index():
    # SQL
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    sql_cmd = f'''
    SELECT * FROM articles ORDER BY time DESC;
    '''
    sql_cursor.execute(sql_cmd)
    articles = sql_cursor.fetchall()   # 없는경우는 tuple임    # 있는경우는 list임
    sql_cursor.close()

    if articles == ():
        articles = 'empty'

    return render_template('index.html', articles=articles)


@app.route('/new_article')
def new_article():
    return render_template('new_article.html')

@app.route('/save', methods=['post'])
def save():
    url = str(time.time())[1:16].replace('.','0')
    title = request.form['title'].replace("'","''")     # ' 을 '' 으로 바꿔줌 (안그러면 오류남)
    author = request.form['author']
    if author.isalnum() == False:        # 특수문자 존재
        flash('작성자에 특수문자 넣으면 안됨')
        return redirect('/')
    pw = request.form['pw'].replace("'","''")     # ' 을 '' 으로 바꿔줌 (안그러면 오류남)
    content = request.form['content'].replace("'","''")     # ' 을 '' 으로 바꿔줌 (안그러면 오류남)

    # SQL
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    sql_cmd = f'''
    INSERT INTO articles(url, title, author, pw, content, comments) VALUES ('{url}', '{title}', '{author}', '{pw}', '{content}', '{{}}');
    '''
    sql_cursor.execute(sql_cmd)
    mydb.commit()
    sql_cursor.close()

    flash('추가완료!')
    return redirect(f'/{url}/read')



@app.route('/<url>/read')
def read(url):
    # 본문
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    sql_cmd = f'''
    SELECT * FROM articles WHERE url='{url}';
    '''
    sql_cursor.execute(sql_cmd)
    article = sql_cursor.fetchone()
    sql_cursor.close()

    # 댓글
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    sql_cmd = f'''
    SELECT comments FROM articles WHERE url='{url}';
    '''
    sql_cursor.execute(sql_cmd)
    comments = sql_cursor.fetchone()['comments']
    sql_cursor.close()
    comments = json.loads(comments)
    

    return render_template('read.html', article=article , comments=comments)

@app.route('/<url>/delete', methods=['post'])
def delete(url):
    # SQL
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    sql_cmd = f'''
    SELECT pw FROM articles WHERE url='{url}';
    '''
    sql_cursor.execute(sql_cmd)
    pw = sql_cursor.fetchone()['pw']
    input_pw =request.form['pw']

    if pw == input_pw:
        sql_cmd = f'''
        DELETE FROM articles WHERE url='{url}';
        '''
        sql_cursor.execute(sql_cmd)
        mydb.commit()
        flash('삭제성공')
    else:
        flash('비밀번호가 다름')
    sql_cursor.close()
    return redirect(f'/{url}/read')


@app.route('/<url>/comment', methods=['post'])
def comment(url):

    # 댓글가져오기
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    sql_cmd = f'''
    SELECT comments FROM articles WHERE url='{url}';
    '''
    sql_cursor.execute(sql_cmd)
    old_comments = sql_cursor.fetchone()['comments']
    sql_cursor.close()
    old_comments = json.loads(old_comments)         # json -> dict

    # 새댓글
    comment_id = str(time.time())[1:16].replace('.','0')
    now = datetime.datetime.now()
    nowDatetime = now.strftime('%Y-%m-%d %H:%M:%S')

    req_dict = dict(request.form)
    req_dict['time'] = nowDatetime
    
    nickname = req_dict['nickname']
    if nickname.isalnum() == False:        # 특수문자 존재
        flash('닉네임에 특수문자 넣으면 안됨')
        return redirect(f'/{url}/read')
    pw = req_dict['pw']
    if pw.isalnum() == False:        # 특수문자 존재
        flash('비밀번호에 특수문자 넣으면 안됨')
        return redirect(f'/{url}/read')

    req_dict['content'] = req_dict['content'].strip('"')
    req_dict['content'] = req_dict['content'].strip("'")
    req_dict['content'] = req_dict['content'].strip('\\')

    new_comment = {comment_id : req_dict}


    # 합치기
    comments = dict(old_comments, **new_comment)
    comments = json.dumps(comments, ensure_ascii=False)  # dict -> json 변환

    # SQL
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    sql_cmd = f'''
    UPDATE articles SET comments = '{comments}' WHERE url='{url}';
    '''
    sql_cursor.execute(sql_cmd)
    mydb.commit()
    sql_cursor.close()
    #수정하기#

    return redirect(f'/{url}/read')



@app.route('/<url>/comment_delete', methods=['post'])
def comment_delete(url):

    comment_id = request.form['comment_id']     # hidden을 통해 가져와짐
    input_pw = request.form['pw']

    # 댓글
    sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
    sql_cmd = f'''
    SELECT comments FROM articles WHERE url='{url}';
    '''
    sql_cursor.execute(sql_cmd)
    comments = sql_cursor.fetchone()['comments']
    sql_cursor.close()
    comments = dict(json.loads(comments))

    for key, value in comments.items():
        if key == comment_id:
            if value['pw'] == input_pw:
                
                del comments[comment_id]

                comments = json.dumps(comments, ensure_ascii=False)  # dict -> json 변환

                sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)
                sql_cmd = f'''
                UPDATE articles SET comments = '{comments}' WHERE url='{url}';
                '''
                sql_cursor.execute(sql_cmd)
                mydb.commit()
                sql_cursor.close()
                flash('삭제성공')
                break
            else:
                flash('비밀번호가 다름')
                break
    return redirect(f'/{url}/read')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)



