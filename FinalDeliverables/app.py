from distutils.log import debug
from flask import Flask, request,redirect,render_template, url_for, session
import ibm_db
import base64
import re
import sendgrid
import os
from dotenv import load_dotenv
from sendgrid.helpers.mail import Mail, Email, To, Content
from apiflask import APIFlask

try:
    conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=ba99a9e6-d59e-4883-8fc0-d6a8c9f7a08f.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=31321;SECURITY=SSL;UID=lln42240;PWD=G8UYVe0Mkl6SW8nE",'','')
    print(conn)
    print("connection successfull")
except:
    print("Error in connection, sqlstate = ")
    errorState = ibm_db.conn_error()
    print(errorState)

load_dotenv()
app = APIFlask(__name__ , spec_path='/spec')
app.secret_key = 'smartfashionrecommender'

app.config['SERVERS'] = [
    {
        'description': 'Heroku deployment',
        'url': 'https://smart-fashion-recommender06745.herokuapp.com',
        'variables':
        {
            "appname":
            {
                "default": "SmartFashion",
                "description": "SmartFashion is an web application with AI chat bot."
            }
        }
    },
    {
        'description': 'local test',
        'url': 'http://127.0.0.1:{port}',
        'variables':
        {
            'port':
            {
                'default': "5000",
                'description': 'local port to use'
            }
        }
    }
]

@app.get('/user_profile')
def userprofile():
    if 'loggedin' in session:
        sql = "SELECT USERS.USERNAME, USERS.EMAIL FROM USERS WHERE email = ?"
        stmt1 = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt1,1,session['email'])
        ibm_db.execute(stmt1)
        account = ibm_db.fetch_tuple(stmt1)
        return {
            'name': account[0],
            'email': account[1]
        }
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        def getTrendy():
            prods = []
            sql = "SELECT PRODUCTS.ID, PRODUCTS.NAME, PRODUCTS.PRICE, PROD_IMGS.IMAGE FROM PRODUCTS INNER JOIN PROD_IMGS ON PRODUCTS.ID = PROD_IMGS.PROD_ID LIMIT 8"
            stmt = ibm_db.exec_immediate(conn,sql)
            result = ibm_db.fetch_assoc(stmt)
            while result != False:
                # print("The ID is : ", result["ID"])
                # print("The name is : ", result["NAME"])
                # print("The image is :",result['IMAGE'])
                image=base64.b64encode(result["IMAGE"]).decode("utf-8")
                result.update({"IMAGE":image})
                prods.append(result)
                result = ibm_db.fetch_assoc(stmt)
            return prods
        data = getTrendy()
        return render_template('home.html', username=session['username'],Trendy_prod=data)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/shop')
def shop():
    return render_template('shop.html')

@app.route('/shop-details')
def shopDetails():
    return render_template('shop_detail.html')

@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')
    
@app.route('/login',methods=['GET','POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        checkuser = "SELECT * FROM USERS WHERE email=? AND password=?"
        stmt1 = ibm_db.prepare(conn,checkuser)
        ibm_db.bind_param(stmt1,1,email)
        ibm_db.bind_param(stmt1,2,password)
        ibm_db.execute(stmt1)
        account = ibm_db.fetch_tuple(stmt1)
        if account:
            #user has an account
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            session['email'] = account[3]
            print(session['email'])
            # msg = "logged in successfull" ( Need to set timoeout to display this message )
            return redirect(url_for('home'))
        else:
            msg = "Invalid email-id or password!"
    return render_template("sign_in.html",msg=msg)

# http://localhost:5000/python/logout - this will be the logout page
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

@app.route('/signup',methods=['GET','POST'])
def sign_up():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        print(username,email,password)
        checkuser = "SELECT email FROM USERS WHERE email=?"
        stmt1 = ibm_db.prepare(conn,checkuser)
        ibm_db.bind_param(stmt1,1,email)
        ibm_db.execute(stmt1)
        account = ibm_db.fetch_tuple(stmt1)
        print(account)
        account= False
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            sql = "INSERT INTO USERS(username,password,email) VALUES(?,?,?)"
            stmt = ibm_db.prepare(conn,sql)
            ibm_db.bind_param(stmt, 1, username)
            ibm_db.bind_param(stmt, 2, password)
            ibm_db.bind_param(stmt, 3, email)
            ibm_db.execute(stmt)
            print(username,email,password)
            msg = 'You have successfully registered!'
            sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
            from_email = Email("smartfashionproject@gmail.com")  # Change to your verified sender
            to_email = To(email)  # Change to your recipient
            subject = "Welcome to SmartFashion"
            content = Content("text/plain", "You have Successfully registered in SmartFashion!!!")
            mail = Mail(from_email, to_email, subject, content)

            # Get a JSON-ready representation of the Mail object
            mail_json = mail.get()

            # Send an HTTP POST request to /mail/send
            response = sg.client.mail.send.post(request_body=mail_json)
            print(response.status_code)
            print(response.headers)

            return redirect(url_for('home'))
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('sign_up.html', msg=msg)

    
if __name__ == '__main__':
    app.run(debug=True)