#!venv/bin/python
# ------------------------------------------------------------------------------
#  Copyright (c) 2020. Anas Abu Farraj.
# ------------------------------------------------------------------------------
"""Learning along Reading Flask Web Development Second Edition.

[X]: TODO: Add type notations
[ ]: TODO: Add Documentation
[ ]: TODO: Change reCAPTCHA and all Secret keys. Since mistakenly pushed to repo.
[ ]: TODO: Store data in database.
[X]: TODO: Turn-off 'DEBUG' on production server.
[ ]: TODO: Turn-off 'TESTING' on production server.
[ ]: TODO: Never guess, add ... or 'hard to guess secret'
"""

import os
from datetime import datetime
from threading import Thread

from flask import Flask, render_template, redirect, url_for, session, flash
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_mail import Message
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.csrf import CSRFError
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, AnyOf


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['WTF_CSRF_SECRET_KEY'] = os.getenv('WTF_CSRF_SECRET_KEY')
app.config['WTF_CSRF_TIME_LIMIT'] = 3600
app.config['WTF_CSRF_ENABLED'] = True
app.config['DEBUG'] = True
app.config['TESTING'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = os.getenv('RECAPTCHA_PUBLIC_KEY')
app.config['RECAPTCHA_PRIVATE_KEY'] = os.getenv('RECAPTCHA_PRIVATE_KEY')
app.config['RECAPTCHA_DATA_ATTRS'] = {'theme': 'light'}
app.config['UPLOADS_DEFAULT_DEST'] = 'static'
app.config['SQLALCHEMY_DATABASE_URI'] = os.path.join('sqlite:///' + os.getcwd(), 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEBUG'] = app.debug
app.config['MAIL_SUPPRESS_SEND'] = app.testing
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = ('Me', os.getenv('MAIL_DEFAULT_SENDER'))
app.config['MAIL_MAX_EMAILS'] = 5
app.config['MAIL_ASCII_ATTACHMENTS'] = False

# ------------------------------------------------------------------------------
# Application Settings Initialization:
# ------------------------------------------------------------------------------
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)

# TODO: Store date in database instead.
NAMES = ['john', 'jane', 'tomas']

# ------------------------------------------------------------------------------
# Database Models Setup (SQLite):
# ------------------------------------------------------------------------------
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')  # 'role' is not a real table column

    def __repr__(self):
        return f'<Role {self.name}>'


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return f'<User {self.username}>'


# ------------------------------------------------------------------------------
# Automatic Imports in Application Shell Context:
# ------------------------------------------------------------------------------
@app.shell_context_processor
def make_shell_context() -> dict:
    return dict(db=db, Role=Role, User=User, mail=mail, Message=Message)


# ------------------------------------------------------------------------------
# Asynchronous Email Sending Setup:
# ------------------------------------------------------------------------------
def async_email(msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject: object, recipients: object, template_name: str) -> object:
    msg = Message(subject, recipients=recipients)
    assert msg.sender == 'Me <goyoomed@gmail.com>'
    msg.body = render_template(template_name + '.txt')
    msg.html = render_template(template_name + '.html')
    thread = Thread(target=async_email, args=[msg])
    thread.start()
    return thread


# ------------------------------------------------------------------------------
# Application WTForms Setup:
# ------------------------------------------------------------------------------
class RegisterForm(FlaskForm):
    """Registration form fields."""
    name = StringField('Name', validators=[DataRequired('Username is required!')])
    username = StringField('Username',
                           validators=[
                               DataRequired('Username is required!'),
                               Length(min=6, message='Minimum is 6 characters.')
                           ])
    password = PasswordField(
        'Password',
        validators=[DataRequired('Password is required!'),
                    AnyOf(values=['secret', '123'])])
    recaptcha = RecaptchaField()
    selects = SelectField('Gender', choices=[('0', '--Choose--'), ('1', 'Male'), ('2', 'Female')])
    submit = SubmitField('Submit')


class PhotoUpload(FlaskForm):
    """Photo upload fields."""
    file_type = UploadSet('images', IMAGES)
    configure_uploads(app, file_type)
    photo = FileField('File Upload',
                      validators=[
                          FileRequired('Choose an image file to upload.'),
                          FileAllowed(file_type, "Only image files allowed!")
                      ])
    submit = SubmitField('Upload')


# ------------------------------------------------------------------------------
# Application Errors Handlers:
# ------------------------------------------------------------------------------
@app.errorhandler(404)
def page_not_found(error):
    """Returns error template 404"""
    return render_template('404.html', reason=error.description), 404


@app.errorhandler(500)
def internal_server_error(error):
    """Returns error template 500"""
    return render_template('500.html', reason=error.description), 500


@app.errorhandler(CSRFError)
def csrf_error(error):
    """Returns error template CSRF Error."""
    return render_template('csrf_error.html', reason=error.description), 400


# ------------------------------------------------------------------------------
# Application Routing:
# ------------------------------------------------------------------------------
@app.route('/')
def index():
    """Returns index page."""
    return render_template('index.html', NAMES=NAMES, now=datetime.utcnow())


@app.route('/thanks')
def thanks():
    """Returns thank you page."""
    return render_template('thanks.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Returns a register page. If valid upon submission, returns
    a thank you page."""
    form = RegisterForm()
    if form.validate_on_submit():
        username = session.get('username')
        if username is not None and form.username.data != username:
            flash('Your new settings has been updated!')
        session['username'] = form.username.data
        send_email(subject=f'Hello, {form.name.data}',
                   recipients=[form.username.data],
                   template_name='confirm')
        return render_template('thanks.html',
                               username=form.username.data,
                               password=form.password.data)
    return render_template('register.html', form=form)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Returns an upload form. Check the file and returns a secure version.
    If valid upon submission,returns a thank you page."""
    form = PhotoUpload()
    if form.validate_on_submit():
        file = form.photo.data
        filename = secure_filename(file.filename)
        basedir = os.path.abspath(os.path.dirname(__file__))
        file.save(os.path.join(basedir, 'static/uploads', filename))
        return redirect(url_for('thanks'))
    return render_template('upload.html', form=form)
