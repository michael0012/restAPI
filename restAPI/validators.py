from functools import wraps
import re
from datetime import datetime
from flask import request
from flask import jsonify
from flask import abort
from flask import g
from restAPI.models import User

def jsonrequestrequired(f):
	@wraps(f)
	def decorator(*args,**kwargs):
		if not (request.is_json):
			return (jsonify({'error':'error code 400, invalid content-type'}),400)
		return f(*args,**kwargs)
	return decorator

def jwttokenrequired(f):
	@wraps(f)
	def decorator(*args,**kwargs):
		auth_header = request.headers.get("Authorization",None)
		if not auth_header or not auth_header.startswith('Bearer '):
			return ( jsonify({"error":"401 error Authorization token not provided"}),401 )
		auth_token = auth_header[7:]
		del auth_header
		if not auth_token:
			abort(401)
		user = User.verify_auth_token(auth_token)
		if not user:
			return ( jsonify({"error":"401 error Authorization token not valid"}),401 )
		g.user = user
		return f(*args,**kwargs)
	return decorator

def check_signup(jsondic):
	email = jsondic.get('email',None)
	password = jsondic.get('password',None)
	errors = {}
	if email is not None:
		if not isinstance(email, str):
			errors['email'] = "Invalid email data type"
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email) or (len(email) >254): 
			errors['email'] = "Invalid email format"
	if password is not None:
		if not isinstance(password,str):
			errors['password'] = "Invalid password data type"
		elif not re.match(r'[A-Za-z0-9_@$]{8,32}', password):
			errors['password'] = "Invalid password format"
	
	return errors
	
def validtodorequest(jsondic):
	name = jsondic.get('name',None)
	description = jsondic.get('description',None)
	due = jsondic.get('due',None)
	completed = jsondic.get('completed',None)
	errors={}
	if name is not None:
		if (not isinstance(name, str) ):
			errors['name'] = "name is invalid type"
		elif len(name) > 120:
			errors['name'] = "The length of name is over 120"
	if description is not None:
		if not isinstance(description, str):
			errors['description'] = "description is invalid type"
		elif len(description) > 500:
			errors['description'] = "The length of the decription is over 500"
	if completed is not None:
		if not isinstance(completed, bool): 
			errors['completed'] = "completed is invalid type"
	if due is not None:
		if not isinstance(due,str):
			errors['due'] = "due is invalid type"
		elif len(due) > 27:
			errors['due'] = "due is invalid length"
		else:
			try:
				test_due = datetime.strptime(due,"%Y-%m-%dT%H:%M:%S.%fZ")
				if test_due <= datetime.now():
					errors['due'] = "due's datetime has passed."
			except ValueError:
				errors['due'] = "due is invalid format"
	return errors
	