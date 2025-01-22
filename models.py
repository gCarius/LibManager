from myapp import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(144), unique=False)
    password = db.Column(db.String(144), nullable = False)
    first_name = db.Column(db.String(144), nullable = False)
    notes = db.relationship('Note', backref = 'notes')


class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.String(1440), nullable = False)
    user_id  = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    register_number = db.Column(db.Integer)
    title = db.Column(db.String(300))
    entry_date = db.Column(db.String(50))
    author = db.Column(db.String(144))    
    editor = db.Column(db.String(144))
    edition = db.Column(db.String(144))
    method_aq = db.Column(db.String(144))
    notes = db.Column(db.String(144))
    borrows = db.relationship('Borrowed', backref = 'books')
    is_available = db.Column(db.Boolean, default = True, nullable = False)


class Borrowed(db.Model):
    __tablename__ = 'borrows'
    id = db.Column(db.Integer, primary_key=True)
    who = db.Column(db.String(144), nullable = False)
    req_date = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    end_date = db.Column(db.DateTime())
    email = db.Column(db.String(144))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable = False)

