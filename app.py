from datetime import datetime
import os
from flask import Flask, render_template, url_for, request, redirect, session
from flask_wtf import FlaskForm
from wtforms import  StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired ,EqualTo, ValidationError
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.engine import Engine
from sqlalchemy import event

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Migrate(app, db)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password
    
    def __repr__(self):
        return f"Username: {self.username}"

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=True)
    due_date = db.Column(db.Date)
    details = db.Column(db.Text)
    category = db.Column(db.String, nullable=True)
    is_completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', backref='tasks', lazy='select')

    def __init__(self, title, due_date, details, category, is_completed, user_id):
        self.title = title
        self.due_date = due_date
        self.details = details
        self.category = category
        self.is_completed = is_completed
        self.user_id = user_id
    
    def __repr__(self):
        return f"Title: {self.title}, due_date: {self.due_date}, details: {self.details}, category: {self.category}, is_completed: {self.is_completed}, user_id: {self.user_id}, user: {self.user}"

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = None
    if form.validate_on_submit():
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password==password:
            session['user_id'] = user.id
            return redirect(url_for('task'))
        else:
            error = 'ユーザー名またはパスワードが正しくありません'
            print(error)
            return render_template('/login.html', form=form, error=error)
        
    return render_template('/login.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    error_password = None

    if form.validate_on_submit():
        print("Form is valid!")
        
        username = form.username.data
        password = form.password.data
        pass_confirm = form.pass_confirm.data

        if password != pass_confirm:
            error_password = 'パスワードが一致しません'
            print("Error: Passwords do not match.")
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))

    error_username = form.username.errors[0] if form.username.errors else None
    return render_template('/register.html', form=form, error_username=error_username, error_password=error_password)


@app.route('/task', methods=['GET'])
def task():
    # if 'user_id' not in session:
    #     return redirect(url_for('login'))
    
    user_id = session['user_id']
    user_tasks = Task.query.filter_by(user_id=user_id, is_completed=False).all()

    return render_template('/task.html', tasks=user_tasks)


@app.route('/completed', methods=['GET'])
def completed():
    # if 'user_id' not in session:
    #     return redirect(url_for('login'))
    
    user_id = session['user_id']
    completed_tasks = Task.query.filter_by(user_id=user_id, is_completed=True).all()
    return render_template('completed.html', tasks=completed_tasks)

@app.route('/add_task', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    title = request.form.get('title')
    due_date_str = request.form.get('due_date')
    details = request.form.get('details')
    category = request.form.get('category')

    due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
    
    new_task = Task(
        title=title,
        due_date=due_date,
        details=details,
        category=category,
        is_completed=False,
        user_id=user_id
    )
    
    db.session.add(new_task)
    db.session.commit()
    
    return redirect(url_for('task'))

@app.route('/complete_task', methods=['POST'])
def complete_task():
    task_id = request.form.get('task_id')
    task = Task.query.get(task_id)

    if task:
        task.is_completed = True
        db.session.commit()
    return redirect(url_for('task'))

@app.route('/uncomplete_task',methods=['POST'])
def uncomplete_task():
    task_id = request.form.get('task_id')
    task = Task.query.get(task_id)

    if task:
        task.is_completed = False
        db.session.commit()
    return redirect(url_for('completed'))

@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('task'))


class LoginForm(FlaskForm):
    username = StringField(label='ユーザー名', validators=[DataRequired()])
    password = PasswordField(label='パスワード', validators=[DataRequired()])
    submit = SubmitField(label='ログイン')

class RegisterForm(FlaskForm):
    username = StringField(label='ユーザー名', validators=[DataRequired()])
    password = PasswordField(label='パスワード', validators=[DataRequired()])
    pass_confirm = PasswordField(label='パスワード（確認）', validators = [DataRequired(), EqualTo('password', message = 'パスワードが一致しません')])
    submit = SubmitField(label='登録')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('このユーザー名は既に使用されています。 \n別のユーザー名を設定してください')



if __name__ == '__main__':
    app.run(debug=True)