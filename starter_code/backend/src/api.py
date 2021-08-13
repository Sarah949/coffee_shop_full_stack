import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# Initialize the datbase

db_drop_and_create_all()

# ROUTES
'''
GET /drinks
    - a public endpoint
    - contain only the drink.short() data representation
    - returns status code 200 and
    json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
    or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
def get_drinks():
    drinkList = Drink.query.all()

    drinks = [drink.short() for drink in drinkList]

    return jsonify({
        'success': True,
        'drinks': drinks,
    }), 200


'''
GET /drinks-detail
    - require the 'get:drinks-detail' permission
    - contain the drink.long() data representation
    - returns status code 200 and
    json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
    or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_details():
    drinkList = Drink.query.all()

    drinks = [drink.long() for drink in drinkList]

    return jsonify({
        'success': True,
        'drinks': drinks,
    }), 200

'''

POST /drinks
    - create a new row in the drinks table
    - require the 'post:drinks' permission
    - contain the drink.long() data representation
    - returns status code 200 and
    json {"success": True, "drinks": drink}
    where drink an array containing only the newly created drink
    or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink():
    body = request.get_json()

    addtitle = body.get('title', None)
    addrecipe = body.get('recipe', None)

    adddrink = Drink(title=addtitle, recipe=json.dumps(addrecipe))
    adddrink.insert()

    drinkqu = Drink.query.all()
    drink = [drink.long() for drink in drinkqu]

    return jsonify({
        "success": True,
        "drinks": drink,
      })


'''
PATCH /drinks/<id>
    - where <id> is the existing model id
    - respond with a 404 error if <id> is not found
    - update the corresponding row for <id>
    - require the 'patch:drinks' permission
    - contain the drink.long() data representation
    - returns status code 200 and
    json {"success": True, "drinks": drink}
    where drink an array containing only the updated drink
    or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def replace_drink(id):

    drinkqu = Drink.query.filter(Drink.id == id).one_or_none()
    if drinkqu is None:
        abort(404)
    else:
        body = request.get_json()
        new_title = body.get('title', None)
        new_recipe = body.get('recipe', None)
        drinkqu.title = new_title
        drinkqu.recipe = json.dumps(new_recipe)
        drinkqu.update()

        drink = [drink.long() for drink in drinkqu]

    return jsonify({
        'success': True,
        "drinks": drink,
    })

'''
DELETE /drinks/<id>
    - where <id> is the existing model id
    - respond with a 404 error if <id> is not found
    - delete the corresponding row for <id>
    - require the 'delete:drinks' permission
    - returns status code 200 and
    json {"success": True, "delete": id}
    where id is the id of the deleted record
    or appropriate status code indicating reason for failure
'''


@app.route("/drinks/<int:drink_id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(id):

    drinkqu = Drink.query.filter(Drink.id == id).one_or_none()

    if drinkqu is None:
        abort(404)

    drinkqu.delete()

    return jsonify({
        'success': True,
        'delete': id,
    }), 200


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

'''
Example error handling for not found entity
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found",
    }), 404


'''
Error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error,
    }), 401
