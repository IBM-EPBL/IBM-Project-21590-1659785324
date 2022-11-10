from distutils.log import debug
from flask import Flask, request, render_template, url_for
import ibm_db

try:
    conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=b1bc1829-6f45-4cd4-bef4-10cf081900bf.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32304;SECURITY=SSL;UID=mkb48397;PWD=4joZwnJswX0BRnwT",'','')
    print(conn)
    print("connection successfull")
except:
    print("Error in connection, sqlstate = ")
    errorState = ibm_db.conn_error()
    print(errorState)

app = Flask(__name__,static_url_path='/static')

@app.route('/')
def home():
    return render_template("home_body.html")

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        sql = "INSERT INTO USERS(email,password) VALUES(?,?)"
        stmt = ibm_db.prepare(conn,sql)
        email = request.form['uname']
        password = request.form['pswd']
        ibm_db.bind_param(stmt, 1, email)
        ibm_db.bind_param(stmt, 2, password)
        ibm_db.execute(stmt)
        print(email,password)
        return render_template("home_body.html")
    elif request.method == 'GET':
        return render_template("sign_in.html")


@app.route('/signup')
def sign_up():
    return render_template("sign_up.html")

    
if __name__ == '__main__':
    app.run(debug=True)