from flask import Flask, render_template, request, redirect, session, flash
from datetime import datetime
import pymysql

import sys
sys.path.append('d:/Sourcetree_account')
import pymysql_con

app = Flask(__name__)

app.config['SECRET_KEY'] = 'test'

@app.route('/')     # 클라이언트에서 보내온 request를 받는 역할
def index():
    conn = pymysql.connect(host='192.168.182.128', port=3306, user=pymysql_con.user, passwd=pymysql_con.passwd, database='page')
    cur = conn.cursor()
    cur.execute('select p.title, u.nickname, p.stampdate, p.post_id from post p, users u where p.user_id = u.user_id')
    post = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', post=post)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # print(request.form['email'])        #request.form : 딕셔너리 구조로 서버에서부터 값을 넣는다
    # print(request.form['password'])
    conn = pymysql.connect(host='192.168.182.128', port=3306, user=pymysql_con.user, passwd=pymysql_con.passwd, database='page')
    cur = conn.cursor()
    if request.method == 'POST':                      # 어떤 방식(method)으로 보냈는지 확인
        if cur.execute('select email, password, nickname, user_id from users where email="%s" and password="%s"' %(request.form.get('email'), request.form.get('password'))):
            user = cur.fetchone()
            session['user'] = user[3]
            cur.close()
            conn.close()
            
            return redirect('/')

        cur.close()
        conn.close()
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/regis', methods=['GET', 'POST'])
def regis():
    if request.method == 'POST':
        conn = pymysql.connect(host='192.168.182.128', port=3306, user=pymysql_con.user, passwd=pymysql_con.passwd, database='page')
        cur = conn.cursor()
        cur.execute('insert into users (email, password, nickname) values ("%s", "%s", "%s")' %(request.form.get('regis_email'), request.form.get('regis_password'), request.form.get('regis_nickname')))
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/login')
    return render_template('regis.html')

@app.route('/body_edit', methods=['GET', 'POST'])
def body_edit():
    if session.get('user') == None:
        flash("로그인을 해야합니다")
        return redirect('/')
    if request.method == 'POST':
        conn = pymysql.connect(host='192.168.182.128', port=3306, user=pymysql_con.user, passwd=pymysql_con.passwd, database='page')
        cur = conn.cursor()
        cur.execute('insert into post (title, body, stampdate, user_id) values ("%s","%s","%s","%s")' %(request.form.get('title'), request.form.get('body'), datetime.now().strftime('%Y-%m-%d %H:%M'), session.get('user')))
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/')
    return render_template('body_edit.html')

@app.route('/body_update/<po_st>', methods=['GET','POST'])
def body_update(po_st):
    if session.get('user') == session.get('p.user_id'): # 검증, 작성자랑 수정하려는 사람이 같은지
        conn = pymysql.connect(host='192.168.182.128', port=3306, user=pymysql_con.user, passwd=pymysql_con.passwd, database='page')
        cur = conn.cursor() 
        if request.method == 'POST':        # submit을 눌렀을 때 작동하는 함수
            cur.execute('update post set title="%s", body="%s" where post_id = "%s"' %(request.form.get('udt_title'), request.form.get('udt_body'),po_st))
            conn.commit()
            cur.close()
            conn.close()
            return redirect('/body/'+po_st)

        cur.execute('select title, body from post where post_id = "%s" ' %(po_st))      # submit을 안 눌렀을때, 수정버튼 클릭 전
        p_post = cur.fetchone()
        cur.close()
        conn.close()
        
    return render_template('body_update.html', p_post=p_post, po_st=po_st)



@app.route('/body/<text>')
def body(text):
    conn = pymysql.connect(host='192.168.182.128', port=3306, user=pymysql_con.user, passwd=pymysql_con.passwd, database='page')
    cur = conn.cursor()
    cur.execute('select p.title, p.body, p.stampdate, u.nickname, p.post_id, p.user_id from post p, users u where p.user_id = u.user_id and p.post_id="%s"  ' %(text)) #게시물 보여주기용으로 데이터 조회
    body=cur.fetchone()
    session['p.user_id'] = body[5]
    cur.execute('select u.nickname, c.contents, c.stampdate from comment c, users u where u.user_id = c.user_id and c.post_id = "%s"' %(body[4])) #어느 게시물의 해당하는 댓글인지 확인하기 위해서 아까 body[4](post_id)를 이용
    comment=cur.fetchall()
    cur.close()
    conn.close()
    return render_template('body.html', body=body, ment=comment, text=text)

@app.route('/ment/<abc>', methods=['POST'])
def ment(abc):
    if session.get('user') == None:
        flash("로그인을 해야합니다")
        return redirect('/')
    if request.method == 'POST':
        conn = pymysql.connect(host='192.168.182.128', port=3306, user=pymysql_con.user, passwd=pymysql_con.passwd, database='page')
        cur = conn.cursor()
        cur.execute('insert into comment (user_id, contents, stampdate, post_id) values ("%s","%s","%s","%s")' %(session.get('user'),request.form.get('co_ment'), datetime.now().strftime('%Y-%m-%d %H:%M'), abc))
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/body/'+abc)


if __name__ == '__main__':      # 파이썬이 이 파일을 인터프리팅할때 해당 조건문의 실행문을 실행시키는(True) 조건 내용, 이 파일을 직접 불러올때만 True로 바뀌고 그 밑에 코드를 실행,
                                # 다른 파일에서 불러와 쓸 수 없다(변수 등등)
    app.run(debug=True)         # debug=True : 서버 껐다 킬 필요없이 코드를 수정하면 자동적으로 재실행해줌, 에러 발생시 원인을 알려줌