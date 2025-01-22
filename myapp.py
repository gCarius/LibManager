from flask import Flask
from flask import session
from flask_sqlalchemy import SQLAlchemy

from os import path

    
def create_app():
    SECRET_KEY = 'mUiTo ScReTo'    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sql'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    return app

def create_database():
    db.drop_all()   
    db.create_all()
    print('Created Database!')    


app = create_app()
db = SQLAlchemy(app)


db.drop_all()   
db.create_all()


create_database()

import models as ORM
from views import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
