import os
import sqlite3

from flask import Flask, flash, render_template, g, request, redirect, url_for, session
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename

app = Flask(__name__)
Bootstrap(app)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'mysite.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default',
    UPLOAD_FOLDER='static/uploads',
    ALLOWED_EXTENSIONS=set(['jpg', 'jpeg'])
))
app.config.from_envvar('FLASKR_SETTINGS',silent=True)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
        db.commit()

def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def index():

    return render_template('index.html')

@app.route('/gallery',methods=['GET','POST'])
def gallery():
    error = None
    existing_files = []
    #List containing all files in the directory
    file_list = os.listdir(app.config['UPLOAD_FOLDER'])

    for file in file_list:
        path = os.path.join("uploads/",file)
        existing_files.append(path)

    if request.method == "POST":
        if 'file' not in request.files:
            flash("No file part")
            return redirect(request.url)

        file = request.files['file']
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        flash('File uploaded successfully.')
        return redirect(request.url)

    return render_template('gallery.html',existing_files=existing_files)

@app.route('/projects', methods=['GET','POST'])
def projects():
    error = None
    db = get_db()
    projects = db.execute('SELECT * FROM projects_entries').fetchall()
    #content = db.execute('SELECT project_content FROM projects_entries').fetchall()

    if request.method == "POST":
        if request.form['title'] != "":
            if request.form['content'] != "":
                db.execute('INSERT INTO projects_entries (project_title,project_content) VALUES (?,?)',[request.form['title'],request.form['content']])
                db.commit()
                flash("Submitted data")
                return redirect(url_for('projects'))

            else:
                print "Didn't work"

    return render_template('projects.html',projects=projects)

@app.route('/<junk>')
def err404(junk):
    flash("Not found. Took you back to the homepage.")
    return redirect(url_for('index'))


@app.route('/gallery/<image>')
def image_link(image):
    return "You clicked a " + image

@app.route('/delete/<postID>')
def delete(postID):
    if 'logged_in' in session:
        db = get_db()
        db.execute("DELETE FROM projects_entries WHERE id = " + postID)
        db.commit()
        flash("Deleted post")
        return redirect(url_for('projects'))
    else:
        return "You do not have permission to do that."

@app.route('/contact',methods=['GET','POST'])
def contact():
    error = None
    if request.method == "POST":
        #init_db()
        if request.form['message_data'] != "":
            db = get_db()
            db.execute('INSERT INTO admin_messages (content) VALUES (?)',[request.form['message_data']])
            db.commit()
            flash("Thanks for your submission!")
        else:
            error = "Invalid input."

    return render_template('contact.html',error=error)

@app.route('/admin',methods=['GET', 'POST'])
def admin():
    error = None
    #Get all messages that users sent
    db = get_db()
    cur = db.execute('SELECT content FROM admin_messages')
    entries = cur.fetchall()

    if request.method == "POST":
        if request.form['username'] != app.config['USERNAME']:
            error = "Invalid username"
        elif request.form['password'] != app.config['PASSWORD']:
            error = "Invalid password"
        else:
            session['logged_in'] = True
            flash('You were logged in.')
            #return render_template('login.html',entries=entries)
            return redirect(url_for('admin'))
    return render_template('login.html',error=error,entries=entries)

@app.route('/logout')
def logout():
    session.pop('logged_in',None)
    flash("You logged out.")
    return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run(host='0.0.0.0')
    #app.run()