from flask import Flask, render_template, redirect, url_for, request
from google.appengine.ext import db
import jinja2
import re
import pdb

app = Flask(__name__)

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404

#
# Home
#
@app.route('/')
def home():
    articles = db.GqlQuery("select * from Article order by created desc")
    return render_template("index.html", articles = articles)

#
# Sign Up
#
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
def valid_email(email):
    return not email or EMAIL_RE.match(email)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        return save_signup_info()
    else:
        return show_signup_form()

def show_signup_form():
    return render_template("signup.html")

def save_signup_info():
    have_error = False
    username = request.form.get("username")
    password = request.form.get("password")
    verify   = request.form.get("verify")
    email    = request.form.get("email")

    params = dict(username = username,
                  email = email)

    if not valid_username(username):
        params["error_username"] = "That was an invalid username"
        have_error = True

    if not valid_password(password):
        params["error_password"] = "That was an invalid password"
        have_error = True
    elif password != verify:
        params["error_verify"] = "Passwords don't match"
        have_error = True

    if not valid_email(email):
        params["error_email"] = "That was an invalid email"
        have_error = True

    if have_error:
        return render_template("signup.html", **params)
    else:
        return render_template("welcome.html", username = username)

#
# Post
#
@app.route('/new', methods=['GET', 'POST'])
def get_or_post():
    if request.method == 'GET':
        return show_new_form()
    else:
        return save_form_info()

def show_new_form():
    return render_template("new.html")

def save_form_info():
    title = request.form.get("title")
    text  = request.form.get("text")
    text  = text.replace("\n", "<br>")

    if title and text:
        article = Article(title = title, text = text)
        article.put()

        article_id = str(article.key().id())

        return redirect(url_for('show_article', article_id = article_id))
    else:
        error = "Oh, oh! We need title and text, baby ;)"
        return render_template("new.html", title = title, text = text, error = error)

@app.route('/<int:article_id>')
def show_article(article_id):
    article = Article.get_by_id(article_id)
    return render_template("show.html", article = article)

class Article(db.Model):
    title   = db.StringProperty(required = True)
    text    = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
