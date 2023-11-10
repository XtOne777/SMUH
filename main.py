from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_wtf.file import FileField, FileAllowed
import os

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


@app.route('/')
def index():
    return render_template('HTMLPage1.html')


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
        return redirect(url_for('index'))
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