from flask import Flask,render_template,redirect,url_for,session,flash
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,FloatField
from wtforms.validators import DataRequired,ValidationError,Email,InputRequired
import bcrypt
from flask_mysqldb import MySQL
from flask import request
import pandas as pd
import numpy as np
import joblib

app=Flask(__name__)
#mysql_config
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='mydatabase'
app.secret_key='the_secret_key'

mysql=MySQL(app)
model=joblib.load("best_random_forest_model.joblib")

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

class InputForm(FlaskForm):

    sepal_length = FloatField('Sepal Length (cm)', validators=[InputRequired()])
    sepal_width = FloatField('Sepal Width (cm)', validators=[InputRequired()])
    petal_length = FloatField('Petal Length (cm)', validators=[InputRequired()])
    petal_width = FloatField('Petal Width (cm)', validators=[InputRequired()])
    submit = SubmitField('Predict')

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

@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
    if 'user_id' in session:
        user_id=session['user_id']
        cursor=mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id=%s",(user_id,))
        user =cursor.fetchone()
        cursor.close()

        if user:#let the user use the ML model
            form =InputForm()
            pred=None
            if form.validate_on_submit():
                x_new=np.array(pd.DataFrame({
                    "SepalLengthCm":[form.sepal_length.data],
                    "SepalWidthCm":[form.sepal_width.data],
                    "PetalLengthCm":[form.petal_length.data],
                    "PetalWidthCm":[form.petal_width.data]
                }))

                pred=model.predict(x_new).item()
                classes=['Iris-setosa', 'Iris-versicolor', 'Iris-virginica']
                for i in range(len(classes)):
                    if pred==i:
                        pred=classes[i]
                        message=f"the predicted class: {pred}"
                        break
                return render_template('dashboard.html',user=user,form=form,output=message)
            
            elif request.method == 'POST':
                flash("Please provide valid feature values.")
            
            return render_template('dashboard.html',user=user,form=form)
        
    #flash("No registered user found")
    return redirect(url_for("login"))

@app.route('/logout')
def logout():
    session.pop('user_id',None)
    flash("You have logged out successfully")
    return redirect(url_for('login'))

if __name__=="__main__":#if this script runs then only the app runs and the debugging happens in the webpage itself
    app.run(debug=True)
