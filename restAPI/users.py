from flask import Blueprint
from flask import request
from flask import jsonify
from flask import abort
from flask import g
from restAPI.models import User,db
from restAPI.validators import jsonrequestrequired,jwttokenrequired,check_signup
from datetime import datetime

bp = Blueprint("users",__name__)


@bp.route("/signup",methods=["POST"])
@jsonrequestrequired
def signup():
	jsonrequest = request.get_json()
	errors = check_signup(jsonrequest)
	if errors:
		return (jsonify(dict(errors=errors)),400)
	email = jsonrequest.get('email',None)
	password = jsonrequest.get('password',None)
	if email is None or password is None:
		abort(400)
	if User.emailExist(email) is not None:
		return (jsonify({"error":"email exist"}),400)
	user = User.createUser(email=email,password=password)
	db.session.add( user )
	db.session.commit()
	return (jsonify({"message":"You have suggestful signed up."}), 200)


@bp.route("/login",methods=["POST"])
@jsonrequestrequired
def login():
	jsonrequest = request.get_json()
	email = jsonrequest.get('email',None)
	password = jsonrequest.get('password',None)
	if not isinstance(email, str):
		email = None
	if not isinstance(password, str):
		password = None
	if email is None or (len(email) > 254) or password is None or (len(password) > 32):
		abort(400)
	user = User.validLogin(email,password)
	if not user:
		return jsonify({"error":"Wrong email and password combination"})
	user.last_login = datetime.utcnow()
	db.session.commit()
	token = user.generate_auth_token().decode('ascii')
	return jsonify({"message":"You have logged in!","token":token})
	
@bp.route("/user/update",methods=["POST"])
@jsonrequestrequired
@jwttokenrequired
def update():
	user = g.user
	jsonrequest = request.get_json()
	errors = check_signup(jsonrequest)
	if errors:
		return (jsonify(dict(errors=errors)),400)
	email = jsonrequest.get('email',None)
	password = jsonrequest.get('password',None)
	if password is None and email:
		if User.emailExist(email) is not None:
			return jsonify({"error":"email exist"})
		user.email = email.lower()
		db.session.commit()
		return jsonify({"message": "Email has been updated"})
	elif password:
		user.set_password(password)
		db.session.commit()
		return jsonify({"message":"Password has been updated"})
	abort(400)

@bp.route("/token/refresh",methods=["POST"])
@jsonrequestrequired
@jwttokenrequired
def refresh():
	user = g.user
	token = user.generate_auth_token().decode('ascii')
	return jsonify({"message":"Here is your new token.","token":token})

@bp.route("/token/revoke",methods=["POST"])
@jsonrequestrequired
def revoke():
	jsonrequest = request.get_json()
	email = jsonrequest.get('email',None)
	password = jsonrequest.get('password',None)
	if not isinstance(email, str):
		email = None
	if not isinstance(password, str):
		password = None
	if email is None or (len(email) > 254) or password is None or (len(password) > 32):
		abort(400)
	user = User.validLogin(email,password)
	if not user:
		return jsonify({"error":"Wrong email and password combination"})
	user.token_version = user.token_version + 1
	db.session.commit()
	return (jsonify({"message":"Tokens have been revoked."}),200)
