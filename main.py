from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True      # displays runtime errors in the browser, too
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:hello@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
#!!!!!!!!!!!!!!!secret key not for production!!!!!!!!!!!!!!!
app.secret_key = 'Welcome_to_my_blog'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True)
    body = db.Column(db.String(1000))

    def __init__(self,title,body):
        self.title = title
        self.body = body

    def __repr__(self):
        return '<Blog %r>' % self.title

def get_blog():
    return Blog.query.all()

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if request.method == 'POST':
        
        blog_title = request.form['title']
        blog_body = request.form['blog-entry']
        if blog_body.strip() =="" or blog_title.strip() =="":
            flash('Please enter content into both text areas')
            return redirect('/newpost')
        new_entry = Blog(blog_title,blog_body)
        db.session.add(new_entry)
        db.session.commit()
        post_id = new_entry.id

        return redirect('/blog/{0}'.format(post_id))

    return render_template('newpost.html')

#This is a really clean way to do this
@app.route('/blog/<int:post_id>')
def blog(post_id):
    return render_template('blog.html', posts=Blog.query.filter_by(id=post_id))
 
@app.route('/blog/')
def index():    
    return render_template('blog.html', posts=get_blog())

@app.route('/')
def start():
    return redirect('/blog/')

if __name__ == "__main__":
    app.run()
