from flask import Flask, render_template, request, redirect, url_for, session, render_template_string, abort
from flask_sqlalchemy import SQLAlchemy
import re, datetime, threading, time, logging, os, sqlite3

app = Flask(__name__)
app.secret_key = 'ахуенно секретный ключ'

# DB config
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    isadmin = db.Column(db.Boolean, default=False)

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(80), nullable=False)

with app.app_context():
        db.create_all()

def login_required(f):
    def wrap(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

@app.route('/')
@login_required
def index():
    posts = Posts.query.all()
    return render_template('index.html', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Users.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = user.username
            session['isadmin'] = user.isadmin
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/write', methods=['GET', 'POST'])
@login_required
def write():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        author = session.get('username')

        if 'preview' in request.form:
            rendered_body = render_template_string(body)
            return render_template('write.html', title=title, body=rendered_body, author=author, preview=True)

        if 'edit' in request.form:
            return render_template('write.html', title=title, body=body)
        # TODO
        return redirect(url_for('index'))
    
    return render_template('write.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('isadmin', None)
    return redirect(url_for('index'))

@app.route('/post/<int:post_id>')
@login_required
def post(post_id):
    post = Posts.query.get_or_404(post_id)
    return render_template('post.html', post=post)

@app.route('/error')
def trigger_error():
    raise Exception("Generic 500 error.")

@app.errorhandler(403)
def forbidden(error):
    return render_template('403.html'), 403

if __name__ == '__main__':
    app.run(debug=True)