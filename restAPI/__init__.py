import os
from flask import Flask
from flask import jsonify
from werkzeug.exceptions import HTTPException

def create_app(test_config=None):
	app = Flask(__name__,instance_relative_config=True)
	app.config.from_mapping(
		SECRET_KEY="dev",
		DATABASE="sqlite:///"+os.path.join(app.instance_path,"restAPI.db")
	)
	
	if test_config is None:
		app.config.from_pyfile("config.py", silent=True)
	else:
		app.config.update(test_config)
	
	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass
	
	# adding objects database
	from restAPI.models import bcrypt, db, init_db_command
	app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///"+os.path.join(app.instance_path,"restAPI.db")
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
	bcrypt.init_app(app)
	db.init_app(app)
	app.cli.add_command(init_db_command)
	
	# adding blueprints
	from restAPI import users,todos
	app.register_blueprint(users.bp)
	app.register_blueprint(todos.bp)
	
	
	# Handles all invalid usage
	@app.errorhandler(Exception) 
	def handle_invalid_usage(error):
		code=500
		if isinstance(error,HTTPException):
			code=error.code
		return jsonify(error=str(error)),code
	
	return app
