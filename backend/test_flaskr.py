import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path ='postgresql://postgres:ade@127.0.0.1:5432/trivia'
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_retrieve_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200) 

    def test_retrieve_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)


    def test_delete_book(self):
        res = self.client().delete('/questions/50') # check that question with id=50 exists
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 48).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted_id'], 50)
        
        
    def test_delete_question_error_404(self):      
        res = self.client().delete('/questions/100')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)

    def test_create_question(self):
        res = self.client().post('/questions/add', 
        json={'question':'TestQuestion', 
              'answer':'TestAnswer', 
              'category':'5', 
              'difficulty':5})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)

    def test_create_question_error_405(self):
        res = self.client().post('/questions', 
        json={})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)

    def test_get_question_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)

    def test_get_question_by_category_error_404(self):
        res = self.client().get('/categories/100/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()