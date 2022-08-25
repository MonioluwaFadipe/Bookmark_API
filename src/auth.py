#import module(s)
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import validators
from src.database import User, db
from .constants.http_status_codes import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT

auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

@auth.post('/register')
def register():
    username=request.json['username']
    email=request.json['email']
    password=request.json['password']

    #validate password
    if len(password)<6:
        return jsonify({'error': "Password is too short"}), HTTP_400_BAD_REQUEST

    #validate username
    if len(username)<3:
        return jsonify({'error': "Username is too short"}), HTTP_400_BAD_REQUEST

    if not username.isalnum() or " " in username:
        return jsonify({'error': "Username should be alphanumeric, also no spaces"}), HTTP_400_BAD_REQUEST

    #validate email
    if not validators.email(email):
        return jsonify({'error': "Email is not valid"}), HTTP_400_BAD_REQUEST

    #Check for multiple emails
    if User.query.filter_by(email=email).first() is not None:
        return jsonify({'Error': "Email is already in use"}), HTTP_409_CONFLICT

    #Check for multiple usernames
    if User.query.filter_by(username=username).first() is not None:
        return jsonify({'Error': "Username is already in use"}), HTTP_409_CONFLICT


    #Hash password
    pwd_hash=generate_password_hash(password)


    #save to database
    user=User(username=username,password=pwd_hash,email= email)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': "User created", 
                    'user': {
                        'username':username, "email":email
                    }}), HTTP_201_CREATED


    return "User created"


@auth.get("/me")
def me():
    return {"user":"me"}