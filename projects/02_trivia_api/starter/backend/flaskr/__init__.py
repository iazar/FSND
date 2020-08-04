import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/": {"origins": "*"}})
  
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers','Content-Type')
    response.headers.add('Access-Control-Allow-Methods','*')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    all_categories = Category.query.order_by(Category.id).all()
    formatted_categories = {Category.id: Category.type for Category in all_categories}

    return jsonify({
      'categories': formatted_categories
    })


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_questions():
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    all_categories = Category.query.order_by(Category.id).all()
    formatted_categories = {Category.id: Category.type for Category in all_categories}

    all_questions = Question.query.order_by(Question.id).all()
    formatted_questions = [Question.format() for Question in all_questions]
    formatted_current_selection = formatted_questions[start:end]

    return jsonify({
      'questions': formatted_current_selection,
      'total_questions': len(all_questions),
      'categories': formatted_categories,
      'current_category': ''
    })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods = ['DELETE'])
  def delete_question(question_id):

    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()
      
      if question is None:
        abort(404)

      question.delete()

      return jsonify({
      'success': True,
      'deleted': question.id
    })

    except:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods = ['POST'])
  def create_question():

    body = request.get_json()

    if 'searchTerm' in body:
      search_term = body.get('searchTerm',None)
      page = request.args.get('page', 1, type=int)
      start = (page - 1) * QUESTIONS_PER_PAGE
      end = start + QUESTIONS_PER_PAGE

      search_term_questions = Question.query.filter(Question.question.ilike('%'+search_term+'%')).order_by(Question.id).all()
      formatted_search_term_questions = [Question.format() for Question in search_term_questions]
      formatted_current_selection = formatted_search_term_questions[start:end]

      all_categories = Category.query.order_by(Category.id).all()
      formatted_categories = {Category.id: Category.type for Category in all_categories}

      return jsonify({
        'questions': formatted_current_selection,
        'total_questions': len(search_term_questions),
        'categories': formatted_categories,
        'current_category': ''
      })
    else:
      new_question = body.get('question',None)
      new_question_answer = body.get('answer',None)
      new_question_difficulty = body.get('difficulty',None)
      new_question_category = body.get('category',None)
      if not new_question or  not new_question_answer or not new_question_difficulty or not new_question_category:
        abort(400)
      try:
          question = Question(new_question, new_question_answer, new_question_category, new_question_difficulty)
          question.insert()

          return jsonify({
            'success': True,
            'created': question.id
          })

      except:
        abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def get_category_questions(category_id):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    current_category = Category.query.filter(Category.id == category_id).one_or_none()
    if current_category is None:
      abort(404)

    category_questions = Question.query.filter(Question.category == category_id).all()
    formatted_category_questions = [Question.format() for Question in category_questions]
    formatted_current_selection = formatted_category_questions[start:end]

    return jsonify({
      'questions': formatted_current_selection,
      'total_questions': len(category_questions),
      'current_category': current_category.type
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  @app.route('/quizzes', methods=['POST'])
  def play():

    body = request.get_json()

    previous_questions = body.get('previous_questions', None)
    quiz_category = body.get('quiz_category', None)

    if quiz_category['id'] == 0:
      all_questions = Question.query.filter(~Question.id.in_(previous_questions)).all()
      all_questions_ids = [Question.id for Question in all_questions]
      if len(all_questions_ids) == 0:
        return jsonify({
      'question': None,
      'success': True
      })
      formatted_random_question = Question.query.get(random.choice(all_questions_ids)).format()
      return jsonify({
      'question': formatted_random_question,
      'success': True
    })
    else:
      category_questions = Question.query.filter(Question.category == quiz_category['id'], ~Question.id.in_(previous_questions)).all()
      category_questions_ids = [Question.id for Question in category_questions]
      if len(category_questions_ids) == 0:
        return jsonify({
      'question': None,
      'success': True
      })
      random_question = Question.query.get(random.choice(category_questions_ids)).format()
      return jsonify({
      'question': random_question,
      'success': True
    })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          "success": False, 
          "error": 404,
          "message": "Not found"
          }), 404
  
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422

  @app.errorhandler(400)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "Bad Request"
      }), 400
  return app

    