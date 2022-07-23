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
        self.database_name = "trivia_test"
        self.database_path = 'postgresql://ade:@127.0.0.1:5000/trivia_test'
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

    def test_get_paginated_questions(self):
        res = self.client().get('/api/v1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        # self.assertEqual(len(data['questions']), 18)
        self.assertTrue(len(data['questions']))

    def test_404_requesting_beyond_valid_page(self):
        res = self.client().get('/api/v1/questions?page=1000', json={'difficulty': 1})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')

    def test_get_categories(self):
        res = self.client().get('/api/v1/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['categories']))

    def test_get_questions_by_category(self):
        res = self.client().get('/api/v1/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])

    def test_404_get_questions_by_category(self):
        res = self.client().get('/api/v1/categories/100/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')

    def test_add_question(self):
        res = self.client().post('/api/v1/questions', json=self.new_question)
        self.assertTrue(res.status_code, 200)

        data = json.loads(res.data)
        self.assertTrue(data['success'])

    def test_delete_question(self):
        res = self.client().delete('/api/v1/questions/2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 2)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_422_if_question_to_delete_does_not_exist(self):
        res = self.client().delete('/api/v1/questions/100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Processable')

    def test_search_question(self):
        res = self.client().post('/api/v1/questions', json={'searchTerm': 'question'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertEqual(len(data['questions']), 10)

    def test_get_quiz(self):
        res = self.client().post('/api/v1/quizzes',
                                 json={'previous_questions': [],
                                       'quiz_category':
                                       {'id': '5', 'type': 'Entertainment'}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])
        self.assertEqual(data['question']['category'], 5)

    def test_422_get_quiz(self):
        res = self.client().post('/api/v1/quizzes',
                                 json={
                                     'previous_questions': []
                                 })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Processable')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()