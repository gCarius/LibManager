from functools import wraps
from tracemalloc import start #DOCUMENTAÇÃO
from flask import request, redirect, url_for, render_template, flash
from sqlalchemy import delete

from markupsafe import escape #https://flask.palletsprojects.com/en/2.0.x/quickstart/#a-minimal-application
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import pandas as pd
from datetime import datetime, timedelta

from myapp import app, db
from myapp import session
import models as ORM



#This function is the mechnism that stablish the login statment of the website
#It uses the wraps module
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        from_url = request.path
        if 'AUTH' in session:
            return f(*args, **kwargs)
        else:
            if from_url != '/':
                flash('Para entrar em {}, precisa fazer o login primeiro.'.format(from_url[1:]), 'danger')
            else:
                flash('Precisa fazer o Login primeiro.', 'info')
            return redirect(url_for('login', next=from_url))
    return wrap


#
#=================From this part forward the fuctions are designed to manage all the pages on the website=================
#


#These three fisrt functions are exclusively destinated to user management functions
#This page takes the credentials that the users submit, search the database and update the status depending on the response
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if not session.get('AUTH'):
        session["AUTH"] = False
    if request.method == 'POST':
        visitor = request.form.get('vist')
        email = request.form.get('email')
        password = request.form.get('password')
        user = ORM.User.query.filter_by(email=email).first()

        if visitor:
            if visitor == 'student' or visitor == 'visit':
                flash('Logged in successfully!', category='success')
                session['AUTH'] = True
                return redirect(url_for('home',user = session['AUTH']))
            else:
                flash('An option must be selected', category='error')
        elif user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                session['AUTH'] = True
                session['USER'] = user.id
                print(session['USER'])
                return redirect(url_for('home',user = session['AUTH']))
            else:
                flash('Incorrect password, try again.', category='error')
                return render_template("login.html", user = session['AUTH'])
        else:
            flash('Email does not exist.', category='error')
        return render_template("login.html", user = session['AUTH'])
    else:
        return render_template("login.html", user = session['AUTH'])


#This page creates new users, it requires a special key, hardcoded
@app.route('/sign-up/', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        control = 'oceano12'
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        admin_key = (request.form.get('admin_key'))

        user = ORM.User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        elif admin_key != control:
            flash('Admin key do not match', category='error')
        else:
            new_user = ORM.User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            session['AUTH'] = True
            flash('Account created!', category='success')
            return redirect(url_for('home'))
    return render_template("sign_up.html", user=session['AUTH'])


#This is exclusively designed to update the status of the user to "session['AUTH'] = False"
@app.route('/logout/')
@login_required
def logout():
    session['AUTH'] = False
    session['USER'] = ""
    return redirect(url_for('login'))



#From tis point on the functions are pages that are designed to show content or to the logistics management
#This is the main route of the website, it shows some information and notes about the library
@app.route('/', methods=['GET', 'POST'])
def home():
    if not session.get('AUTH'):
        session["AUTH"] = False
    data = ORM.Note.query.all()
    return render_template("home.html", data=data, user=session.get('AUTH'))


#The purpose of this page is to show the list of books, and let the user search among the collection
@app.route("/books/", methods=["GET", "POST"])
def books():
    if not session.get('AUTH'):
        session["AUTH"] = False
    data = ORM.Book.query.filter_by(is_available = True).all()
    data = data[0:19]
    if request.method == 'POST':
        rq = request.form.get('quest', None)
        if rq:
            rq = escape(rq)
            rq.lower().strip()
            rq = "%{}%".format(rq)
            data = ORM.Book.query.filter(ORM.Book.title.like(rq)).filter_by(is_available = True).all() + \
                   ORM.Book.query.filter(ORM.Book.author.like(rq)).filter_by(is_available = True).all() + \
                   ORM.Book.query.filter(ORM.Book.editor.like(rq)).filter_by(is_available = True).all()
    return render_template('books.html', user = session['AUTH'], data = data)


#The purpose of this page is to add a book to the collection
@app.route("/add_book/", methods=["GET","POST"])
@login_required
def add_book():
    if request.method == 'POST':
        last_book = ORM.Book.query.order_by(ORM.Book.register_number.desc()).first()
        register_number = last_book.register_number + 1
        title = request.form.get('title')
        author = request.form.get('author')
        editor = request.form.get('editor')
        edition = request.form.get('edition')
        method_aq = request.form.get('method_aq')
        entry_date = request.form.get('entry_date')
        notes = request.form.get('notes')
        if title and author and editor and edition and method_aq and entry_date:
            new_book = ORM.Book(register_number=register_number,entry_date=entry_date,author=author,title=title,editor=editor,edition=edition,method_aq=method_aq,notes=notes)
            db.session.add(new_book)
            db.session.commit()
            flash('Book added!', category='success')
        else:
            flash('Missing information', category='error')
    return render_template("add_book.html", user=session['AUTH'])


#The purpose of this page is to delete books
@app.route("/delete_book/<int:book_id>", methods=["GET","POST"])
@login_required
def delete_book(book_id=None):
    if book_id is None:
        return url_for('/books')
    else:
        book_d = ORM.Book.query.filter_by(id = book_id).first()
        db.session.delete(book_d)
        db.session.commit()
        flash('Book deleted', category='error')
        return redirect('/books/')


#The purpose of this page is to load books into the SQL
@app.route("/load/")
@login_required
def load_books():
    data = pd.read_excel("livros.xlsx")
    for i in (range(len(data))):
        register_number = str(data.iloc[i]['N.º de registo ']) #mudar isso para tamanho +1
        entry_date = str(data.iloc[i]['Data de entrada '])
        author = str(data.iloc[i]['Autor '])
        title = str(data.iloc[i]['Título'])
        editor = str(data.iloc[i]['Editora'])
        edition = str(data.iloc[i]['Edição '])
        method_aq = str(data.iloc[i]['Aquisição'])
        notes = str(data.iloc[i]['Observações'])

        new_book = ORM.Book(register_number=register_number,entry_date=entry_date,author=author,title=title,editor=editor,edition=edition,method_aq=method_aq,notes=notes)
        db.session.add(new_book)
        db.session.commit()
    print("Books created!")
    return None


#The purpose of this page is to add a note
@app.route("/add_note/", methods=["GET","POST"])
@login_required
def add_note():
    if request.method == 'POST':
        note = request.form.get('note')
        if note:
            new_book = ORM.Note(note=note, user_id = session['USER'] )
            db.session.add(new_book)
            db.session.commit()
            flash('Note added!', category='success')
        else:
            flash('Missing information', category='error')
    return render_template("add_note.html", user=session['AUTH'])


#The purpose of this page is to open the manager page
@app.route("/manage_info/", methods=["GET","POST"])
@login_required
def manage_res():
    data = ORM.Note.query.all()
    all = ORM.Borrowed.query.all()

    borrows = []
    today = datetime.now()
    for r in all:
        turn_in = r.end_date
        number_of_days =  turn_in - today
        alert_colors = {"00": "", "01": "table-warning", "10": "table-danger"}
        color = "{:d}{:d}".format(turn_in <= today,  (today + timedelta(days=4)) > turn_in > today)
        ra = (r, alert_colors.get(color, ""), number_of_days)
        borrows.append(ra)
    return render_template('manage_info.html', user = session['AUTH'], data = data, borrows=borrows)


#The purpose of this page is to delete information
@app.route("/manage_info/delete/", methods=["GET","POST"])
@login_required
def manage_res_delete():
    if request.method == 'POST':
        id = request.form.get('id')
        n = ORM.Note.query.filter_by(id=id).first()
        db.session.delete(n)
        db.session.commit()
    return(redirect('/manage_info/'))


#The purpose of this page is to delete a borrow
@app.route("/manage_info/delete_borrow/", methods=["GET","POST"])
@login_required
def manage_res_delete_borrow():
    if request.method == 'POST':
        id = request.form.get('id')
        n = ORM.Borrowed.query.filter_by(id=id).first()
        book = ORM.Book.query.filter_by(id = n.book_id).first()
        book.is_available = True
        db.session.delete(n)
        db.session.commit()
    return(redirect('/manage_info/'))


#The purpose of this page is to borrow a book
@app.route("/borrow_book/<int:book_id>", methods=["GET","POST"])
@login_required
def borrow_book(book_id = None):
    if book_id is None:
        return render_template("borrow_book.html", user=session['AUTH'])

    if request.method == 'POST':
        start_borrow =  request.form.get('start_borrow' , '')
        print(start_borrow)
        if start_borrow != '':
            book = ORM.Book.query.filter_by(id = start_borrow).first()
            return render_template("borrow_book.html", user=session['AUTH'], book = book)
        else:

            book = ORM.Book.query.filter_by(id = book_id).first()
            print(book)
            who = request.form.get('who')
            end_date_day = int(request.form.get('end_date_day'))
            end_date_month = int(request.form.get('end_date_month'))
            end_date_year = int(request.form.get('end_date_year'))
            end_date = datetime(end_date_year, end_date_month, end_date_day)
            email = request.form.get('email')
            if who and end_date:
                book.is_available = False
                new_borrow = ORM.Borrowed(who = who,end_date=end_date,email=email,book_id = book.id)
                db.session.add(new_borrow)
                db.session.commit()
                flash('Book borrowed!', category='success')
            else:
                flash('Missing information', category='error')
    return render_template("borrow_book.html", user=session['AUTH'], book = None)
