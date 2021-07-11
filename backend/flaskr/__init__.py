import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
# from sqlalchemy import func

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions


def create_app(test_config=None):
  app = Flask(__name__)
  setup_db(app)
  # CORS(app)
  '''
  Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  '''
  Use the after_request decorator to set Access-Control-Allow
  '''

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  ''' 
  DONE : Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def retrieve_categories():
    categories = Category.query.order_by(Category.id).all()
    # categories_list = [category.format() for category in categories]

    if len(categories) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'categories': {category.id: category.type for category in categories}
    })


  '''
  DONE : Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route('/questions')
  def retrieve_questions():
    questions = Question.query.order_by(Question.id).all()
    questions_list = paginate_questions(request, questions)

    categories = Category.query.all()

    if len(questions_list) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': questions_list,
      'total_questions': len(questions_list),
    # 'current_category' : ,
      'categories' : {category.id: category.type for category in categories}
    })


  '''
  DONE : Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
    try:
      question = Question.query.filter(Question.id == id).one_or_none()

      if question is None:
        abort(404)

      question.delete()

      return jsonify({
        'success': True,
        # 'deleted': id,
        # 'total_questions': len(Question.query.all())
      })

    except:
      abort(422)


  '''
  DONE : Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()

    new_question = body.get('question')
    insert_answer = body.get('answer')
    insert_difficulty = body.get('difficulty')
    insert_category = body.get('category')
    
    try:
      question = Question(question=new_question, answer=insert_answer,difficulty=insert_difficulty, category=insert_category)
      question.insert()

      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)
    
      return jsonify({
        'success': True,
        'created': question.id,
        'questions': current_questions,
        'total_questions': len(Question.query.all())
        })

    except:
      abort(400)

  '''
  DONE : Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

# run successfully in curl
  @app.route('/questions/search', methods=['POST'])
  def search():
    body = request.get_json()
    search = body.get('searchTerm', None)

    try:
        current_questions = Question.query.filter(Question.question.ilike('%{}%'.format(search))).all()

        return jsonify({
          'success': True,
          'questions': [questions.format() for questions in current_questions]
        })

    except:
      abort(404)

  '''
  DONE : Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route('/categories/<int:id>/questions', methods=['GET'])
  def get_questions(id):
    questions = Question.query.filter(Question.category == id).all()
    questions_list = paginate_questions(request, questions)

    if len(questions_list) == 0:
      abort(404)

    category = Category.query.filter_by(id=id).one_or_none()

    return jsonify({
      'success': True,
      'questions': questions_list,
      'total_questions': len(questions_list),
      'current_category' : category.type
    })



  '''
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def quiz():
    body = request.get_json()

    category = body.get('quiz_category')
    previous_question = body.get('previous_questions')

    category_id = int(category.get('id'))

    randomquestion = None

    if (category_id != 0):
      questions = Question.query.filter(Question.id.notin_(previous_question),Question.category == category_id).all()
      randomquestion = random.choice(questions)
    else:
      # questions = Question.query.order_by(func.random())
      questions = Question.query.filter(Question.id.notin_(previous_question),Question.category != category_id).all()
      randomquestion = random.choice(questions)

    
    return jsonify({
      'success': True,
      'question': randomquestion.format()
      })



  '''
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "resource not found"
      }), 404
  
  @app.errorhandler(405)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 405,
      "message": "method not allowed"
      }), 405

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "bad request"
      }), 400

  @app.errorhandler(500)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 500,
      "message": "internal server error"
      }), 500
  
  return app

    