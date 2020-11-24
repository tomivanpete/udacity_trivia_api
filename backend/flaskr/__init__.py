import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import sys

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r'/api/*': {'origins': '*'}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE,OPTIONS')
    return response
  
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/api/categories')
  def get_categories():
    try:
      categories = Category.query.order_by('id').all()
      formatted_categories = {category.id : category.type for category in categories}

      return jsonify({
        'success': True,
        'categories': formatted_categories,
      })
    except:
      abort(500)

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
  @app.route('/api/questions')
  def get_questions():
    try:
      page = request.args.get('page', 1, type=int)
      start = (page - 1) * QUESTIONS_PER_PAGE
      end = start + QUESTIONS_PER_PAGE

      questions = Question.query.all()
      formatted_questions = [question.format() for question in questions]
      if start > len(formatted_questions):
        raise IndexError

      categories = Category.query.all()
      formatted_categories = {category.id : category.type for category in categories}

      return jsonify({
        'success': True,
        'questions': formatted_questions[start:end],
        'categories': formatted_categories,
        'current_category': None,
        'total_questions': len(questions)
      })
    # Return a 404 error for an invalid page number
    except IndexError:
      abort(404)
    except:
      abort(500)

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/api/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.get(question_id)
      question.delete()

      return jsonify({
        'success': True,
        'deleted': question_id
      })
    except:
      abort(404)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/api/questions', methods=['POST'])
  def create_question():
    try:
      request_body = request.get_json()
      question = request_body['question']
      answer = request_body['answer']
      category = request_body['category']
      difficulty = request_body['difficulty']

      if (type(question) != str) or (type(answer) != str) or (type(difficulty) != int):
        raise TypeError

      new_question = Question(
        question=question,
        answer=answer,
        category=category,
        difficulty=difficulty
      )
      new_question.insert()

      return jsonify({
        'success': True,
        'created': new_question.id
      }), 201
    # Return a 400 error if any required fields are not present in the request body
    except KeyError:
      abort(400)
    # Return a 422 error if question, answer, or difficulty are not the correct data types
    except TypeError:
      abort(422)
    except:
      abort(500)


  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/api/questions/search', methods=['POST'])
  def search_questions():
    try:
      request_body = request.get_json()
      search_term = request_body['searchTerm']
      questions = Question.query.filter(Question.question.ilike('%'+search_term+'%'))
      formatted_questions = [question.format() for question in questions]

      return jsonify({
        'success': True,
        'questions': formatted_questions
      })
    except:
      abort(400)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/api/categories/<int:category_id>/questions')
  def get_questions_by_category(category_id):
    try:
      questions = Question.query.filter(Question.category == category_id).all()
      formatted_questions = [question.format() for question in questions]

      return jsonify({
        'success': True,
        'questions': formatted_questions
      })
    except:
      abort(404)

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
  @app.route('/api/quizzes', methods=['POST'])
  def play_quiz():
    try:
      request_body = request.get_json()
      previous_questions = request_body['previous_questions']
      quiz_category_id = request_body['quiz_category']['id']

      # Category 0 should include questions from all existing categories
      if quiz_category_id == 0:
        questions = Question.query.all()
      else:
        questions = Question.query.filter(Question.category == quiz_category_id).all()
      formatted_questions = [question.format() for question in questions]

      # If there are no previous questions, then we can return a random choice from all available questions
      if len(previous_questions) == 0:
        return jsonify({
          'success': True,
          'question': random.choice(formatted_questions)
          })
      else:
        # Remove previous questions from the selection of possible new questions
        for id in previous_questions:
          for question in formatted_questions:
            if id == question['id']:
              formatted_questions.remove(question)
        # If all questions have been removed, then return None for question
        if len(formatted_questions) == 0:
          return jsonify({
            'success': True,
            'question': None
            })
        # Return a random choice from the remaining possible questions
        else:
          return jsonify({
            'success': True,
            'question': random.choice(formatted_questions)
            })
    except:
      abort(400)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'Bad request'
    }), 400
  
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'Not Found'
    }), 404
  
  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      'success': False,
      'error': 405,
      'message': 'Method not allowed'
    }), 405
  
  @app.errorhandler(422)
  def unprocessable_entity(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'Unprocessable entity'
    }), 422

  @app.errorhandler(500)
  def server_error(error):
    return jsonify({
      'success': False,
      'error': 500,
      'message': 'Internal server error'
    }), 500
  
  return app

    