#import module(s)
from os import access
from tabnanny import check
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import validators
from flasgger import swag_from
from src.database import User, db
from .constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity

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

@auth.post('/login')
@swag_from('./docs/auth/login.yaml')
def login():
    email = request.json.get('email', '')
    password = request.json.get('password', '')

    #check if user exists
    user=User.query.filter_by(email=email).first()

    #check password validity
    if user:
        is_pass_correct=check_password_hash(user.password, password)
    
        if is_pass_correct:
            refresh=create_refresh_token(identity=user.id)
            access = create_access_token(identity=user.id)

            return jsonify({
                'user':{
                    'refresh':refresh,
                    'access':access,
                    'username':user.username,
                    'email':user.email
                }
            }
            ), HTTP_200_OK
    return jsonify({'error':'Wrong credentials'}), HTTP_401_UNAUTHORIZED


@auth.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()

    user=User.query.filter_by(id=user_id).first()
    return jsonify({
        'username':user.username,
        'email':user.email
    }), HTTP_200_OK

@auth.post('/token/refresh')
@jwt_required(refresh=True)
def refresh_users_token():
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)

    return jsonify({
        'access':access
    }), HTTP_200_OK