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
  CORS(app)
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  def paginate_responses(queries):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * 10
    end = start + 10
    formatted_queries = [query.format() for query in queries]
    current_formatted_queries = formatted_queries[start:end]
    return current_formatted_queries

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, PUT, POST, DELETE, OPTIONS')
    return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def get_categories():
    categories = Category.query.all()
    categories_to_return = {}
    if len(categories) == 0:
      abort(404)

    for category in categories:
      categories_to_return[category.id] = category.type
    return jsonify({
        'success': True,
        'categories': categories_to_return
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
  @app.route('/questions', methods=['GET'])
  def get_questions():
    questions = Question.query.all()
    categories = Category.query.all()

    if (len(paginate_responses(questions)) == 0):
      abort(404)

    return jsonify({
      'success': True,
      'questions': paginate_responses(questions),
      'total_questions': len(questions),
      'current_category': None,
      'categories': {category.id: category.type for category in categories}
    })
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.get(question_id)
      question.delete()
      return jsonify({
        'success': True,
        'deleted': question_id
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
  @app.route('/questions', methods=['POST'])
  def post_questions():
    body = request.get_json()
    # print(body)
    # if search term is present
    if (body.get('searchTerm')):
      search_term = body.get('searchTerm')

      # query the database using search term
      selection = Question.query.filter(Question.question.ilike('%' + search_term + '%')).all()

      # 404 if no results found
      if (len(selection) == 0):
        abort(404)

      # paginate the results
      paginated = paginate_responses(selection)

      # return results
      return jsonify({
        'success': True,
        'questions': paginated,
        'total_questions': len(Question.query.all())
      })
    else:
      if not ('question' in body and 'answer' in body and 'difficulty' in body and 'category' in body):
        abort(422)
      new_question = body.get('question')
      new_answer = body.get('answer')
      new_difficulty = body.get('difficulty')
      new_category = body.get('category')
      try:
        question = Question(question=new_question, answer=new_answer,
                            difficulty=new_difficulty, category=new_category)
        question.insert()
        return jsonify({
            'success': True,
            'created': question.id,
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
  
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):
    try:
      selected_questions = Question.query.filter(Question.category == str(category_id)).all()
      if (len(selected_questions) == 0):
        abort(404)
      
      return jsonify({
        'success': True,
        'questions': paginate_responses(selected_questions),
        'total_questions': len(selected_questions),
        'current_category': None,
        'categories': category_id
      })
    except:
      abort(422)

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
  def generate_random_question(all_questions, previous_questions):
    random_question = all_questions[random.randrange(0, len(all_questions), 1)]
    used = False
    if previous_questions == []:
      return random_question
    while (not used):
      for prev_q in previous_questions:
        if (prev_q != random_question.id):
          used = True
        else:
          random_question = all_questions[random.randrange(0, len(all_questions), 1)]
    return random_question

  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    body = request.get_json()
    previous = body.get('previous_questions')
    category = body.get('quiz_category')
    # print(previous, category) 
    try:
      questions = Question.query.filter_by(category=category['id']).all()
      random_question = generate_random_question(questions, previous)
      # print(random_question)
      return jsonify({
        'success': True,
        'question': random_question.format()
      })
    except:
      abort(400)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "request unprocessable"
    }), 422
  
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "resource not found"
    }), 404

  @app.errorhandler(400)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "bad request"
    }), 400

  return app