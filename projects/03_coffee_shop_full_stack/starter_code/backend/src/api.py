import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from jose import jwt

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
#db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['GET'])
def get_drinks():
    all_drinks = Drink.query.order_by(Drink.id).all()
    formatted_drinks = [Drink.short() for Drink in all_drinks]
    return jsonify({
        'success': True,
        'drinks': formatted_drinks
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    all_drinks = Drink.query.order_by(Drink.id).all()
    formatted_drinks_details = [Drink.long() for Drink in all_drinks]
    return jsonify({
        'success': True,
        'drinks': formatted_drinks_details
    })

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drinks(jwt):
    body = request.get_json()
    new_drink_title = body.get('title', None)
    new_drink_recipe = body.get('recipe', None)
    print(new_drink_recipe)

    if not new_drink_title or not new_drink_recipe:
        abort(400)
    try:
        drink = Drink(title=new_drink_title, recipe=json.dumps(new_drink_recipe))
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })

    except BaseException:
        abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(jwt,id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404)
    body = request.get_json()
    updated_drink_title = body.get('title', None)
    updated_drink_recipe = body.get('recipe', None)

    if updated_drink_title is None and updated_drink_recipe is None:
        abort(400)
    
    try:
        if not updated_drink_title is None:
            drink.title = updated_drink_title
        if not updated_drink_recipe is None:
            drink.recipe = updated_drink_recipe
        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })

    except BaseException:
        abort(422)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(jwt,id):

    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if drink is None:
        abort(404)
    
    try:
        drink.delete()

        return jsonify({
            'success': True,
            'delete': drink.id
        })

    except BaseException:
        abort(422)


## Error Handling
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
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(400)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400
'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
