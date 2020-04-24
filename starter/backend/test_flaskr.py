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
    def test_get_categories_success(self):
        """
        test get categories success
        """
        response = self.client().get('/categories')
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["success"], True)
        self.assertEqual(len(response_data["categories"]), 6)

    def test_get_categories_failure(self):
        response = self.client().get('/categories/1')
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_data["success"], False)
        self.assertEqual(response_data["message"], "resource not found")

    def test_paginate_questions_success(self):
        """
        test get paginated questions success
        """
        response = self.client().get('/questions')
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["success"], True)
        self.assertTrue(len(response_data['questions']), int(response_data['total_questions']))

    def test_paginate_questions_failure(self):
        """
        test get paginated questions failure
        """
        response = self.client().get('/questions?page=1000')
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_data["success"], False)
        self.assertEqual(response_data["message"], "resource not found")

    def test_questions_by_category_success(self):
        """
        test get get questions by category success
        """
        response = self.client().get('/categories/1/questions')
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["success"], True)

    def test_questions_by_category_failure(self):
        """
        test get get questions by category failure
        """
        response = self.client().get('/categories/10/questions')
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response_data["success"], False)
        self.assertEqual(response_data["message"], "request unprocessable")

    def test_delete_question_success(self):
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

    def test_delete_question_failure(self):
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

    def test_quizzes_success(self):
        """
        test quizzes success
        """
        new_quiz_question = {
            'previous_questions': [],
            'quiz_category': {
                'id': '1',
                'type': 'Science'
            }
        }
        response = self.client().post('/quizzes', json=new_quiz_question)
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["success"], True)

    def test_quizzes_failure(self):
        """
        test quizzes failure
        """
        new_quiz_question = {
            'previous_questions': [],
            'quiz_category': {}
        }
        response = self.client().post('/quizzes', json=new_quiz_question)
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data["success"], False)
        self.assertEqual(response_data["message"], "bad request")

    def test_post_questions_success(self):
        """
        test post questions success
        """
        new_question = {
            'question': 'question to be deleted',
            'answer': 'no answer',
            'category': 1,
            'difficulty': 1
        }
        response = self.client().post('/questions', json=new_question)
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["success"], True)
    
    def test_post_questions_failure(self):
        """
        test post questions failure
        """
        new_question = {
            'question': 'question to be deleted',
        }
        response = self.client().post('/questions', json=new_question)
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response_data["success"], False)
        self.assertEqual(response_data["success"], False)
        self.assertEqual(response_data["message"], "request unprocessable")

    def test_search_questions_success(self):
        """
        test search questions success
        """
        new_search = {
            'searchTerm': 'What movie earned Tom Hanks his third straight Oscar nomination, in 1996?'
        }
        res = self.client().post('/questions', json=new_search)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])

    def test_search_questions_failure(self):
        """
        test search questions success
        """
        new_search = {
            'searchTerm': 'lol'
        }
        response = self.client().post('/questions', json=new_search)
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_data["success"], False)
        self.assertEqual(response_data["message"], "resource not found")



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()