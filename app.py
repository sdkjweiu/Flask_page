from flask import Flask, render_template, request, redirect
import pymysql

import sys
sys.path.append('d:/Sourcetree_account')
import pymysql_con

app = Flask(__name__)



@app.route('/')     # 클라이언트에서 보내온 request를 받는 역할
def index():
    return '''index page'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    # print(request.form['email'])        #request.form : 딕셔너리 구조로 서버에서부터 값을 넣는다
    # print(request.form['password'])
    conn = pymysql.connect(host='192.168.182.128', port=3306, user=pymysql_con.user, passwd=pymysql_con.passwd, database='page')
    cur = conn.cursor()
    if request.method == 'POST':                      # 어떤 방식(method)으로 보냈는지 확인
        print(request.form.get('email'))
        print(request.form.get('password'))
        print(request.form['email'])
        print(request.form['password'])
        if cur.execute('select email, password from users where email="%s" and password="%s"' %(request.form.get('email'), request.form.get('password'))):
            cur.close()
            conn.close()
            print('ABCDEF')
            return redirect('/')

        cur.close()
        conn.close()
    return render_template('login.html')


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


if __name__ == '__main__':      # 파이썬이 이 파일을 인터프리팅할때 해당 조건문의 실행문을 실행시키는(True) 조건 내용, 이 파일을 직접 불러올때만 True로 바뀌고 그 밑에 코드를 실행,
                                # 다른 파일에서 불러와 쓸 수 없다(변수 등등)
    app.run(debug=True)         # debug=True : 서버 껐다 킬 필요없이 코드를 수정하면 자동적으로 재실행해줌, 에러 발생시 원인을 알려줌