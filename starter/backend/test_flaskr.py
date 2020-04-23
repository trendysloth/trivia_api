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
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        # sample question for use in tests

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
    def test_get_categories(self):
        """
        test get categories success
        """
        response = self.client().get('/categories')
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["success"], True)
        self.assertEqual(len(response_data["categories"]), 6)

    def test_get_categories_error(self):
        response = self.client().get('/categories/1')
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_data["success"], False)
        self.assertEqual(response_data["message"], "resource not found")
        
    def test_paginate_questions(self):
        """
        test get paginated questions success
        """
        response = self.client().get('/questions')
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["success"], True)
        self.assertTrue(len(response_data['questions']), int(response_data['total_questions']))

    def test_paginate_questions_error(self):
        response = self.client().get('/questions?page=1000')
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_data["success"], False)
        self.assertEqual(response_data["message"], "resource not found")

    def test_delete_question(self):
        """
        test delete a question
        """
        question = Question(
            question='question to be deleted',
            answer='no answer',
            category=1,
            difficulty=1
        )
        question.insert()
        question_id = question.id
        response = self.client().delete('/questions/{}'.format(question_id))
        response_data = json.loads(response.data)
        deleted_question = Question.query.filter(Question.id == question.id).one_or_none()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["success"], True)
        self.assertEqual(response_data["deleted"], str(question_id))
        self.assertEqual(deleted_question, None)

    def test_delete_question_error(self):
        question = Question(
            question='question to be deleted',
            answer='no answer',
            category=1,
            difficulty=1
        )
        question.insert()
        question_id = question.id
        self.client().delete('/questions/{}'.format(question_id))
        response = self.client().delete('/questions/{}'.format(question_id))
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response_data["success"], False)
        self.assertEqual(response_data["message"], "request unprocessable")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()