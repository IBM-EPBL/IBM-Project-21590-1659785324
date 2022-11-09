from distutils.log import debug
from flask import Flask
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
    return "hello flask"
if __name__ == '__main__':
    app.run(debug=True)