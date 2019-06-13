from flask import request, redirect, render_template, session, flash
from app import app, db
from models import User, Blog
from hashutils import check_pw_hash

@app.route('/login', methods = ['POST','GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_pw_hash(password, user.pw_hash):
            session['user']= email
            flash("Logged in")
            return redirect('/')
        else:
            
            flash("User password incorrect or user does not exist", 'error')

    return render_template('login.html')

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        if not is_email(email):
            flash('zoiks! "' + email + '" does not seem like an email address')
            return redirect('/signup')
        email_db_count = User.query.filter_by(email=email).count()
        if email_db_count > 0:
            flash('yikes! "' + email + '" is already taken and password reminders are not implemented')
            return redirect('/signup')
        if password != verify:
            flash('passwords did not match')
            return redirect('/signup')
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        session['user'] = user.email
        return redirect("/newpost")
    else:
        return render_template('signup.html')

def is_email(string):
    atsign_index = string.find('@')
    atsign_present = atsign_index >= 0
    if not atsign_present:
        return False
    else:
        domain_dot_index = string.find('.', atsign_index)
        domain_dot_present = domain_dot_index >= 0
        return domain_dot_present

@app.route("/logout", methods=['POST'])
def logout():
    del session['user']
    return redirect("/")

def get_blog():
    return Blog.query.all()

def get_authors():
    return User.query.all()

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if request.method == 'POST':
        
        blog_title = request.form['title']
        blog_body = request.form['blog-entry']
        if blog_body.strip() =="" or blog_title.strip() =="":
            flash('Please enter content into both text areas')
            return redirect('/newpost')
        new_entry = Blog(blog_title,blog_body,logged_in_user())
        db.session.add(new_entry)
        db.session.commit()
        post_id = new_entry.id

        return redirect('/blog/{0}'.format(post_id))

    return render_template('newpost.html')

#This is a really clean way to do this using flask variable rule
@app.route('/blog/<int:post_id>')
def post(post_id):
    return render_template('blog.html', posts=Blog.query.filter_by(id=post_id))

@app.route('/singleUser/<int:author_id>')
def singleUser(author_id):
    return render_template('singleUser.html', posts=Blog.query.filter_by(owner_id=author_id))
 
@app.route('/blog/')
def blog():
    return render_template('blog.html', posts=get_blog())

@app.route('/')
def index():
    return render_template('index.html',authors=get_authors())

def logged_in_user():
    owner = User.query.filter_by(email=session['user']).first()
    return owner

endpoints_without_login = ['login', 'signup', 'index']

@app.before_request
def require_login():
    if not ('user' in session or request.endpoint in endpoints_without_login):
        return redirect("/signup")

#!!!!!!!!!!!!!!!secret key not for production!!!!!!!!!!!!!!!
app.secret_key = 'Welcome_to_my_blog'

if __name__ == "__main__":
    app.run()
