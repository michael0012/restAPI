from flask import Blueprint
from flask import request
from flask import jsonify
from flask import abort
from flask import g
from restAPI.models import User,TodoItem,db
from restAPI.validators import jsonrequestrequired,jwttokenrequired,validtodorequest
from datetime import datetime

bp = Blueprint("todos",__name__)

@bp.route("/todos", methods=["GET","POST"])
@jsonrequestrequired
@jwttokenrequired
def show_create():
	user = g.user
	if request.method == "GET":
		result = {'todos':TodoItem.myTodos(user_id=user),'message':'all todo items sent' }
		return (jsonify(result),200)
	else:
		jsonrequest = request.get_json()
		errors = validtodorequest(jsonrequest)
		if errors:
			return (jsonify(dict(errors=errors)),400)
		name = jsonrequest.get("name",None)
		description = jsonrequest.get("description",None)
		due = jsonrequest.get('due',None)
		if due is not None:
			due = datetime.strptime(due,"%Y-%m-%dT%H:%M:%S.%fZ")
		if (name is None) or (description is None):
			return (jsonify({"error":"name or description missing from request"}),400)
		todoItem = TodoItem(name=name,description=description,due=due,owner=user.id_)
		db.session.add(todoItem)
		db.session.commit()
		id_ = todoItem.id_
		return (jsonify({"message":"todo item created","id_":id_}),201)


@bp.route("/todos/<int:id_>", methods=["GET","PUT","DELETE"])
@jsonrequestrequired
@jwttokenrequired
def todo_item(id_):
	user = g.user
	todoItem = TodoItem.myTodo(user_id=user,todo_id=id_)
	if todoItem is None:
		abort(404)
	if request.method == "GET":
		return (jsonify({"message":"todo item send","todo":todoItem.sanitize}),200)
	elif request.method == "DELETE":
		db.session.delete(todoItem)
		db.session.commit()
		return (jsonify({"message":"todo item deleted"}),200)
	jsonrequest = request.get_json()
	errors = validtodorequest(jsonrequest)
	if errors:
		return (jsonify(dict(errors=errors)),400)
	name = jsonrequest.get('name',None)
	description = jsonrequest.get('description',None)
	due = jsonrequest.get('due',None)
	completed = jsonrequest.get('completed',None)
	itemchanged = False
	if name is not None:
		todoItem.name = name
		itemchanged =True
	if description is not None:
		todoItem.description = description
		itemchanged =True
	if due is not None:
		todoItem.due = datetime.strptime(due,"%Y-%m-%dT%H:%M:%S.%fZ")
		itemchanged =True
	if completed is not None:
		todoItem.completed = completed
		itemchanged =True
	if itemchanged:
		db.session.commit()
		return (jsonify({"message":"todo item updated"}),200)
	return (jsonify({"message":"todo item not updated"}),200)

