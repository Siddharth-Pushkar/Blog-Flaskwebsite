from flask import Flask,render_template, request, session,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import json
from datetime import datetime




with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = 'True'
app = Flask(__name__)
app.secret_key = 'super-secrete-key'

app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD = params['gmail-password']
)


mail = Mail(app)

if(local_server):
    app.config["SQLALCHEMY_DATABASE_URI"] = params["local_uri"]
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params["prod_uri"]

db = SQLAlchemy(app)



class Contacts(db.Model):

    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone_num = db.Column(db.String(10), nullable=False)
    msg = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(12), nullable=True)

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    tagline = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)



@app.route("/dashboard")
def dashboard():
    posts = Posts.query.all()
    return render_template("dashboard.html", params=params,posts = posts)




@app.route("/")
def home():
    posts = Posts.query.filter_by().all()[0:params['no_of_posts']]
    return render_template('index.html', params=params, posts=posts)

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/contact", methods = ['GET','POST'])
def contact():
    if (request.method == 'POST'):
        name = request.form.get('name')
        email = request.form.get('email_id')
        phone = request.form.get('phone_num')
        message = request.form.get('message')
        entry = Contacts(name = name, phone_num = phone, date = datetime.now(), email = email, msg = message)
        db.session.add(entry)
        db.session.commit()
        mail.send_message("New message from user " + name ,
                          sender = email ,
                          recipients = [params ['gmail-user']]  ,
                          body = message + "\n" + phone)



    return render_template('contact.html')

@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)


@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    if request.method == 'POST':
        box_title = request.form.get('title')
        tline = request.form.get('tline')
        slug = request.form.get('slug')
        content = request.form.get('content')
        date = datetime.now()

        if sno == '0':
            post = Posts(title=box_title, slug=slug, content=content, tagline=tline, date=date)
            db.session.add(post)
            db.session.commit()
        else:
            post = Posts.query.filter_by(sno = sno).first()
            post.title = box_title
            post.tline = tline
            post.slug = slug
            post.content = content
            post.date = date
            db.session.commit()
            return redirect('/edit/'+ sno)
    post = Posts.query.filter_by(sno=sno).first()
    return render_template('edit.html', params=params, post= post, sno = sno)

@app.route("/delete/<string:sno>" , methods=['GET', 'POST'])
def delete(sno):
    post = Posts.query.filter_by(sno=sno).first()
    db.session.delete(post)
    db.session.commit()
    return redirect("/dashboard")


app.run(debug=True)