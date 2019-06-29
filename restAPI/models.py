import click
from datetime import datetime
from flask.cli import with_appcontext
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import(TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

bcrypt = Bcrypt()
db = SQLAlchemy()

# TODO get better secret_key
secret_key = "dfhusiuhiu9djsf9vsj"
class User(db.Model):
	id_ = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(80), unique=True, nullable=False)
	password = db.Column(db.String(255), unique=False, nullable=False)
	confirmed = db.Column(db.Boolean, nullable=False, default=True)
	last_login = db.Column(db.DateTime(timezone=True),default=None,nullable=True)
	token_version = db.Column(db.Integer,nullable=False,default=1)
	
	def set_password(self,password):
		self.__hash_password(password)

	def __hash_password(self,password):
		self.password = bcrypt.generate_password_hash(password)
	
	def verify_password(self, password):
		return bcrypt.check_password_hash(self.password,password)
	
	def generate_auth_token(self,expiration=3600):
		s = Serializer(secret_key,expires_in=expiration)
		return s.dumps({'id_': self.id_,'token_version':self.token_version})
	
	def __repr__(self):
		return '<User %r>' % self.email
	
	
	@classmethod
	def createUser(cls,**kwargs):
		email = kwargs['email'].lower()
		password = kwargs['password']
		user = cls(email=email,password="password")
		user.set_password(password)
		return user
	
	@classmethod
	def emailExist(cls,email):
		email = email.lower()
		return cls.query.filter_by(email=email).first()
	
	#returns user if email and password combination is valid or None if it is't valid	
	@classmethod
	def validLogin(cls,email,password):
		user = cls.query.filter_by(email=email.lower()).first()
		if user is None or not user.verify_password(password):
			return None
		return user
	
	@classmethod
	def verify_auth_token(cls,token):
		s = Serializer(secret_key)
		try:
			data = s.loads(token)
		except SignatureExpired:
			return None
		except BadSignature:
			return None
		try:
			user_id = int(data['id_'])
		except ValueError:
			return None
		user_token_version = int(data['token_version'])
		user = cls.query.get(user_id)
		if user is None or user.token_version != user_token_version:
			return None
		return user
		


class TodoItem(db.Model):
	id_ = db.Column(db.Integer, primary_key=True)
	owner = db.Column(db.Integer, db.ForeignKey('user.id_'),nullable=False)
	name = db.Column(db.String(80),nullable=False)
	description = db.Column(db.String(255),nullable=False,default="")
	created = db.Column(db.DateTime(timezone=True),nullable=False,default=datetime.utcnow())
	completed = db.Column(db.Boolean,nullable=False,default=False)
	due = db.Column(db.DateTime(timezone=True),nullable=True)

	@classmethod
	def myTodos(cls,**kwargs):
		user_id = kwargs['user_id']
		if isinstance(user_id, User):
			user_id = user_id.id_
		alltodos = cls.query.filter_by(owner=user_id)
		return [item.sanitize for item in alltodos]
	
	@classmethod
	def myTodo(cls,*args,**kwargs):
		user_id = kwargs.get('user_id',None)
		todo_id = kwargs.get('todo_id',None)
		assert user_id, "user_id arg missing in myTodos method"
		assert todo_id, "todo_id arg missing in myTodos method"
		if isinstance(user_id, User):
			user_id = user_id.id_
		todoItem = cls.query.filter_by(owner=user_id,id_=todo_id).first()
		return todoItem
	
	@property
	def sanitize(self):
		return {
		'id_':self.id_,
		'name':self.name,
		'description':self.description,
		'created':str(self.created),
		'due':str(self.due),
		'completed':self.completed
		}

	def __repr__(self):
		return '<TodoItem %r>' % self.name	
	
# TODO: finish todo model 
@click.command("init-db")
@with_appcontext
def init_db_command():
	db.create_all()

