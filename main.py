import os
import urllib.parse
from datetime import datetime
from decouple import Config, RepositoryEnv
config = Config(RepositoryEnv('config.cfg'))

from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy.orm
from cockroachdb.sqlalchemy import run_transaction


def get_uri():
    conn_string = config('SQLALCHEMY_DATABASE_URI', default='guess_me')

    try:
        db_uri = os.path.expandvars(conn_string)
        db_uri = urllib.parse.unquote(db_uri)
        psycopg_uri = db_uri.replace(
            'postgresql://', 'cockroachdb://').replace('26257/defaultdb?', '26257/test?')

    except Exception as e:
        print('Failed to connect to database.')
        print('{0}'.format(e))

    return psycopg_uri


psycopg_uri = get_uri()
app = Flask('app')
app.config['SQLALCHEMY_DATABASE_URI'] = psycopg_uri
app.config['SECRET_KEY'] = config('SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config(
    'SQLALCHEMY_TRACK_MODIFICATIONS')
app.config['DEBUG'] = config('DEBUG')


db = SQLAlchemy(app)
sessionmaker = sqlalchemy.orm.sessionmaker(db.engine)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column('user_id', db.Integer, primary_key=True)
    username = db.Column(db.String(60))
    email = db.Column(db.String)
    password = db.Column(db.String)
    create_date = db.Column(db.DateTime)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        self.create_date = datetime.utcnow()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/login-register')
def login_register():
    return render_template('login-register.html')

@app.route('/image-classification')
def image_recognition():
    return render_template('img-classification.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if not request.form['username']:
            flash('username is required', 'error')
        elif not request.form['email']:
            flash('email is required', 'error')
        elif not request.form['password']:
            flash('password is required', 'error')
        else:
            def callback(session):
                user = User(
                    request.form['username'], request.form['email'], request.form['password'])
                session.add(user)
            run_transaction(sessionmaker, callback)
            flash(u'User was successfully created')
            return redirect(url_for('index'))
    return redirect(url_for('signuplogin'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if not request.form['username']:
            flash('username is required', 'error')
        elif not request.form['password']:
            flash('password is required', 'error')
        else:
            def callback(session):
                username = request.form['username']
                user = session.query(User).filter(
                    User.username.in_([username])).all()
                if len(user) == 0:
                    flash('User not registered', 'error')
                elif user[0].password != request.form['password']:
                    flash('Incorrect password entered', 'error')
                else:
                    return True
                return False
            check = run_transaction(sessionmaker, callback)
            if check:
                flash(u'User successfully logged in')
                return redirect(url_for('index'))
    return redirect(url_for('signuplogin'))


app.run(host='0.0.0.0', port=8080)