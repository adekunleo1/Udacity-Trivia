import os
import random

from flask import Flask, abort, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from models import Category, Question, setup_db
from sqlalchemy.sql.expression import func

QUESTIONS_PER_PAGE = 10

# function to paginate the questions
def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


# function to format the categories to a dictionary
def format_categories(categories):
    categories_dict = {}
    for category in categories:
        categories_dict[category.id] = category.type
    return categories_dict

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

     # Set up CORS. Allow '*' for origins.
    CORS(app, resources={r"/api/v1/": {"origins": "https://127.0.0.1:5000"}})

    # Use the after_request decorator to set Access-Control-Allow
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    # Endpoint to handle GET requests
    # for all available categories.
    @app.route('/api/v1/categories')
    def get_categories():
        categories = Category.query.order_by(Category.id).all()
        if len(categories) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': format_categories(categories)
        })

    # Endpoint to handle GET request to get all the questions and the categories
    @app.route('/api/v1/questions')
    def get_questions():
        questions = Question.query.order_by(Question.id).all()
        categories = Category.query.order_by(Category.id).all()
        current_questions = paginate_questions(request, questions)

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'total_questions': len(questions),
            'categories': format_categories(categories),
            'questions': current_questions
        })

    # Endpoint to DELETE question using a question ID.
    @app.route('/api/v1/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()
            if question is None:
                abort(404)

            question.delete()

            return jsonify({
                'success': True,
                'deleted': question_id,
                'total_questions': len(Question.query.all())
            })
        except:
            abort(422)

    # endpoint to POST a new question
    @app.route('/api/v1/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        question = body.get('question', None)
        answer = body.get('answer', None)
        difficulty = body.get('difficulty', None)
        category = body.get('category', None)
        search = body.get('searchTerm', None)
        try:
            if search:
                if search == "":
                    abort(400)
                selection = Question.query.order_by(Question.id).filter(
                    Question.question.ilike('%{}%'.format(search)))
                questions = [question.format() for question in selection]

                return jsonify({
                    'success': True,
                    'questions': questions,
                    'total_questions': len(selection.all()),
                })
            else:
                if (question is None) or (answer is None) or (difficulty is None) or (category is None):
                    abort(422)

                question = Question(
                    question=question,
                    answer=answer,
                    difficulty=difficulty,
                    category=category
                )
                question.insert()

                return jsonify({
                    'success': True,
                    'created': question.id,
                    'total_questions': len(Question.query.all())
                })
        except:
            abort(422)

    # GET endpoint to get questions based on category.
    @app.route('/api/v1/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        category = Category.query.filter_by(id=category_id).one_or_none()
        if category is None:
            abort(422)

        selected_questions = Question.query.filter(Question.category == category_id)
        current_questions = paginate_questions(request, selected_questions)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selected_questions.all()),
            'current_category': category.format()
        })

    # POST endpoint to get questions to play the quiz.
    @app.route('/api/v1/quizzes', methods=['POST'])
    def get_quiz_questions():
        previous_questions = request.json.get('previous_questions')
        quiz_category = request.json.get('quiz_category')
        category_id = int(quiz_category.get('id'))

        category = Category.query.filter_by(id=category_id).one_or_none()
        
        if category_id:
            questions = Question.query.filter(
                Question.category == category_id,
                ~Question.id.in_(previous_questions))
        else:
            questions = Question.query.filter(~Question.id.in_(previous_questions))

        question = questions.order_by(func.random()).first()

        if not question:
            return jsonify({
                'success': True,
                'question': None
            })

        return jsonify({
            'success': True,
            'question': question.format()
        })

    # Error handlers for 400, 404, 422 and 500
    @app.errorhandler(400)
    def error_not_found(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400

    @app.errorhandler(404)
    def error_not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not Found"
        }), 404

    @app.errorhandler(422)
    def error_not_found(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422

    @app.errorhandler(500)
    def error_not_found(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        }), 500

    return app

