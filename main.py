from flask import Flask, render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_wtf.file import FileField, FileAllowed
import os
import csv

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smuh.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = 'some_secret_key'
app.config['UPLOAD_FOLDER'] = 'documents'


class Volunteer(db.Model):
    user = db.Column(db.String(30), primary_key=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    image_path = db.Column(db.String(255))
    phone = db.Column(db.String(20))


class Elder(db.Model):
    elder_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(100), nullable=False)

    def _repr_(self):
        return '<Elder %r>' % self.elder_id


class Order(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    elder_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def _repr_(self):
        return '<Order %r>' % self.order_id


class VolunteerRegistrationForm(FlaskForm):
    user = StringField('User', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    image = FileField('Image', validators=[FileAllowed(['png', 'jpg', 'jpeg', 'gif'], 'Images only!')])
    submit = SubmitField('Register')


class VolunteerLoginForm(FlaskForm):
    user = StringField('User', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    submit = SubmitField('Login')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        phone_number = request.form.get('phone_number')

        if phone_number:
            save_to_csv(phone_number)

    return render_template('HTMLPage1.html')


@app.route('/prof', methods=['GET'])
def prof():
    phone_numbers = read_phone_numbers_from_csv('numbers.csv')
    return render_template('prof.html', phone_numbers=phone_numbers)


def read_phone_numbers_from_csv(file_path):
    phone_numbers = []
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            phone_numbers.append(row[0])
    return phone_numbers


def save_to_csv(phone_number):
    filename = 'numbers.csv'
    fieldnames = ['Phone Number']
    file_exists = os.path.isfile(filename)

    with open(filename, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({'Phone Number': phone_number})


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = VolunteerRegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data).decode('utf-8')

        if form.image.data:
            image_path = save_image(form.image.data)
        else:
            image_path = None

        volunteer = Volunteer(user=form.user.data, phone=form.phone.data, password=hashed_password, image=image_path)
        db.session.add(volunteer)
        db.session.commit()
        return redirect('prof.hrml')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = VolunteerLoginForm()
    if form.validate_on_submit():
        volunteer = Volunteer.query.filter_by(user=form.user.data).first()
        if volunteer and check_password_hash(volunteer.password, form.password.data):
            return redirect(url_for('index'))
    return render_template('login.html', form=form)


def save_image(image):
    filename = secure_filename(image.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(image_path)
    return image_path


if __name__ == '__main__':
    app.run(debug=True)