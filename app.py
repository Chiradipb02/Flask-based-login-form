from flask import Flask,render_template,redirect,url_for,session,flash
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import DataRequired,ValidationError,Email
import bcrypt
from flask_mysqldb import MySQL

app=Flask(__name__)
#mysql_config
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='mydatabase'
app.secret_key='the_secret_key'

mysql=MySQL(app)

class RegisterForm(FlaskForm):
    name=StringField("Name: ",validators=[DataRequired()])
    email=StringField("Email: ",validators=[DataRequired(),Email()])
    password=PasswordField("Password: ",validators=[DataRequired()])
    submit=SubmitField("Sign up")

    #the WTForms allows you to define custom validation logic by creating a method named validate_<fieldname>.
    def validate_email(self,field): #automatically called by wtforms when submit is pressed
        cursor=mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s",(field.data,))#the last comma is important
        user=cursor.fetchone()
        cursor.close()

        if(user):
            raise ValidationError('Email already taken')
        
class LoginForm(FlaskForm):
    #name=StringField("Name: ",validators=[DataRequired()])
    email=StringField("Email: ",validators=[DataRequired(),Email()])
    password=PasswordField("Password: ",validators=[DataRequired()])
    submit=SubmitField("Login")

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/login',methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        #name=form.name.data
        email=form.email.data
        password=form.password.data

        #hashed_password=bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
        #store the user info to the database
        cursor=mysql.connection.cursor()#helps to establish connection tothe database
        cursor.execute("SELECT * FROM users WHERE email=%s",(email,))
        user=cursor.fetchone()
        cursor.close()

        if(user and bcrypt.checkpw(password.encode('utf-8'),user[3].encode('utf-8'))):
            session['user_id']=user[0]
            
            return redirect(url_for('dashboard'))
        else:
            flash("login failed check the password or email")
            return redirect(url_for("login"))
    
    return render_template('login.html',form=form)

@app.route('/register',methods=['GET','POST'])
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        name=form.name.data
        email=form.email.data
        password=form.password.data

        hashed_password=bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
        #store the user info to the database
        cursor=mysql.connection.cursor()#helps to establish connection tothe database
        cursor.execute("INSERT INTO users (name,email,password) VALUES (%s, %s, %s)",(name, email, hashed_password))
        mysql.connection.commit() #to see the changes in database commit should be done
        cursor.close()

        return redirect(url_for('dashboard'))
    
    return render_template('register.html',form=form)

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id=session['user_id']
        cursor=mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id=%s",(user_id,))
        user =cursor.fetchone()
        cursor.close()

        if user:
            return render_template('dashboard.html',user=user)
    
    return redirect(url_for("login"))

@app.route('/logout')
def logout():
    session.pop('user_id',None)
    flash("You have logged out successfully")
    return redirect(url_for('login'))

if __name__=="__main__":#if this script runs then only the app runs and the debugging happens in the webpage itself
    app.run(debug=True)