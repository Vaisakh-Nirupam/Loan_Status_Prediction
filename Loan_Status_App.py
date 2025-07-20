# Model Setting
import pickle
import pandas as pd
import numpy as np

# App Creation
from flask import Flask, render_template, request, flash, session, redirect, url_for

# Mailing
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os


# Model Import
with open('model/Loan_Status_Model.pkl','rb') as f:
    model_dict = pickle.load(f)


# App Creation
app = Flask(__name__)

# Loading .env
load_dotenv()

# Mail Config
app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER")
app.config['MAIL_PORT'] = int(os.getenv("MAIL_PORT"))
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_RECEIVER'] = os.getenv("MAIL_RECEIVER")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_USE_TLS'] = os.getenv("MAIL_USE_TLS") == "True"
app.config['MAIL_USE_SSL'] = False
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# Mail Setup
mail = Mail(app)

# Home Page
@app.route('/')
def index():
    return render_template('home.html',active='home')

# Input Page
@app.route('/input', methods=['GET', 'POST'])
def input():
    show = request.args.get("show", default=1, type=int)

    if request.method == 'POST':
        if show == 1:
            session['name'] = request.form.get('name')
            session['age'] = request.form.get('age')
            session['gender'] = request.form.get('gender')
            return redirect(url_for('input', show=2))
        
        elif show == 2:
            session['education'] = request.form.get('education')
            session['income'] = request.form.get('income')
            session['experience'] = request.form.get('experience')
            return redirect(url_for('input', show=3))
        
        elif show == 3:
            session['loan_amount'] = request.form.get('loan_amount')
            session['loan_intent'] = request.form.get('loan_intent')
            session['interest'] = request.form.get('interest')
            return redirect(url_for('input', show=4))

        elif show == 4:
            session['home_ownership'] = request.form.get('home_ownership')
            session['credit_history'] = request.form.get('credit_history')
            session['credit_score'] = request.form.get('credit_score')

            inputs = [
                int(session['age']),
                session['gender'],
                session['education'],
                int(session['income']),
                int(session['experience']),
                session['home_ownership'],
                int(session['loan_amount']),
                session['loan_intent'],
                int(session['interest']),
                int(session['credit_history']),
                int(session['credit_score']),
            ]

            cols = ['age', 'gender', 'education', 'income', 'experience', 'home_ownership',
                    'loan_amount', 'loan_intent', 'loan_int_rate', 'credit_history', 'credit_score']

            df_inps = pd.DataFrame([inputs], columns=cols)
            print(df_inps)

            df_inps['gender'] = model_dict['gender'].transform(df_inps['gender'])
            df_inps['education'] = model_dict['education'].transform(df_inps['education'])
            df_inps['home_ownership'] = model_dict['home_ownership'].transform(df_inps['home_ownership'])
            df_inps['loan_intent'] = model_dict['loan_intent'].transform(df_inps['loan_intent'])

            df_scaled = model_dict['scaler'].transform(df_inps)
            pred = model_dict['model'].predict_proba(df_scaled)[0][1]
            pred_percent = round(pred*100)

            name = session.get('name', 'User')
            session['prediction'] = pred_percent
            
            return redirect(url_for('prediction'))
    
    return render_template('input.html', active='predict', show=show)

# Prediction Page
@app.route('/prediction')
def prediction():
    name = session.get('name', 'User')
    prediction = session.get('prediction', None)
    session.clear()

    if prediction is None:
        return redirect(url_for('input'))

    return render_template('prediction.html', active='predict', name=name, prediction=prediction)

# About Page
@app.route('/about', methods=['GET','POST'])
def about():
    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        msg = Message(
            subject="Loan Status Prediction App Contact Message",
            sender=app.config['MAIL_USERNAME'],
            recipients=[app.config['MAIL_RECEIVER']],
            body=f"Name: {name}\n\nEmail: {email}\n\nMessage: {message}"
        )

        mail.send(msg)
        flash("Your Message Sent Successfully!", "success")

    return render_template('about.html',active='about')

if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
