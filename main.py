from flask import Flask, render_template, request, redirect, url_for
from google.appengine.ext import db
import jinja2
import pdb

app = Flask(__name__)

@app.route('/new', methods=['GET', 'POST'])
def get_or_post():
    if request.method == 'GET':
        return show_new_form()
    else:
        return save_form_info()

@app.route('/') 
def home():
    articles = db.GqlQuery("select * from Article order by created desc")
    return render_template("index.html", articles = articles)

def show_new_form():
    return render_template("new.html")

def save_form_info():
    title = request.form.get("title")
    text  = request.form.get("text")

    if title and text:
        a = Article(title = title, text = text)
        a.put()

        return redirect(url_for('home'))
    else:
        error = "Oh, oh! We need title and text, baby ;)"
        return render_template("new.html", title = title, text = text, error = error)

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404

class Article(db.Model):
    title   = db.StringProperty(required = True)
    text    = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
