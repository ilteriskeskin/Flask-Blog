from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, StringField, PasswordField, validators
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "linuxdegilgnulinux"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/ilteriskeskin/Belgeler/Flask-Blog/blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(80))
    content = db.Column(db.Text)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    password = db.Column(db.String(80))

class RegistrationForm(Form):
    username = StringField('Kullanıcı Adı', [validators.Length(min=1, max=25)])
    password = PasswordField('Parola', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Parolalar uyuşmuyor, tekrar deneyin!')
    ])
    confirm = PasswordField('Tekrar Giriniz')

@app.route('/')
def home():
    articles = Article.query.all()
    users = User.query.all()
    return render_template("index.html", users = users, articles = articles)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']

        data = User.query.filter_by(username = username).first()

        if data is not None and check_password_hash(data.password, password):
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            flash('Kullanıcı adı veya parola hatalı, tekrar deneyin.', category='danger')
            return redirect(url_for('login'))

@app.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        
        try:
            newUser = User(username = username, password = generate_password_hash(password))
            db.session.add(newUser)
            db.session.commit()
            flash('Kayıt işleminiz tamamlnamıştır.')
            return redirect(url_for("login"))
        except:
            flash('Teknik bir aksaklık oldu, tekrar deneyin.', category='danger')
            return redirect(url_for('register'))
    else:
        return render_template('register.html', form = form)

@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect(url_for('home'))

@app.route('/add', methods=['GET','POST'])
def add():
    if session['logged_in'] == True:
        if request.method == 'POST':
            title = request.form.get("title")
            content = request.form.get("content")
            newArticle = Article(title = title, content = content)
            db.session.add(newArticle)
            db.session.commit()
            return redirect(url_for("home"))
        else:
            return render_template('add_article.html')
    else:
        return redirect(url_for('login'))

class Article(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(80))
    content = db.Column(db.Text)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/private')
def private():
    return render_template('private.html')

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)