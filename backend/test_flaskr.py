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

        self.quiz_request = {
            'previous_questions': [],
            'quiz_category': {
                'type': 'Science',
                'id': 1
            }
        }
        self.new_question = {
            'question': 'Does this API work?',
            'answer': 'We will find out after this test runs.',
            'category': 1,
            'difficulty': 5
        }

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
        """ Test that GET for /api/categories endpoint returns a 200 and a list of categories """
        res = self.client().get('/api/categories')
        res_body = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(res_body['success'])
        self.assertTrue(res_body['categories'])

    def test_get_questions(self):
        """ Test that GET for /api/questions endpoint returns a 200 and a list of questions """
        res = self.client().get('/api/questions')
        res_body = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(res_body['success'])
        self.assertTrue(res_body['questions'])

    def test_create_question(self):
        """ Test that POST for /api/questions endpoint returns a 201 and creates a new question """
        res = self.client().post('/api/questions', json=self.new_question)
        res_body = json.loads(res.data)

        self.assertEqual(res.status_code, 201)
        self.assertTrue(res_body['success'])
        self.assertTrue(res_body['created'])
        
        new_question = Question.query.filter(Question.id == res_body['created']).one_or_none()
        self.assertTrue(new_question)

    def test_delete_question(self):
        """ Test that DELETE for /api/questions/<int:question_id> endpoint returns a 200 and deletes a question """
        res = self.client().get('/api/questions')
        res_body = json.loads(res.data)
        question_id = res_body['questions'][0]['id']
        
        res = self.client().delete('/api/questions/' + str(question_id))
        res_body = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(res_body['success'])
        self.assertTrue(res_body['deleted'])

    def test_search_questions_with_results(self):
        """ Test that POST for /api/questions/search endpoint returns a 200 and a list of matching questions """
        res = self.client().post('/api/questions/search', json={'searchTerm': 'what'})
        res_body = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(res_body['success'])
        self.assertTrue(len(res_body['questions']))

    def test_search_questions_without_results(self):
        """ Test that POST for /api/questions/search endpoint returns a 200 and no matching questions """
        res = self.client().post('/api/questions/search', json={'searchTerm': 'string_with_no_results'})
        res_body = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(res_body['success'])
        self.assertEqual(len(res_body['questions']), 0)

    def test_get_questions_by_category(self):
        """ Test that GET for /api/categories/1/questions endpoint returns a 200 list of matching questions """
        res = self.client().get('/api/categories/1/questions')
        res_body = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(res_body['success'])
        self.assertTrue(res_body['questions'])

    def test_play_quiz(self):
        """ Test playing the quiz for 5 questions. """
        for i in range(5):
            res = self.client().post('/api/quizzes', json=self.quiz_request)
            res_body = json.loads(res.data)

            self.assertEqual(res.status_code, 200)
            self.assertTrue(res_body['success'])

            if res_body['question']:
                self.quiz_request['previous_questions'].append(res_body['question']['id'])

    def test_404_get_questions(self):
        """ Test that sending an invalid page to /api/questions should return a 404 error """
        res = self.client().get('/api/questions?page=1000')
        res_body = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(res_body['success'])
        self.assertEqual(res_body['message'], 'Not Found')

    def test_400_create_question(self):
        """ Test sending a POST with incomplete question data should return a 400 error """
        res = self.client().post('/api/questions', json={'question': 'This should fail'})
        res_body = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(res_body['success'])
        self.assertEqual(res_body['message'], 'Bad request')

    def test_400_invalid_search(self):
        """ Test sending a POST with incomplete an invalid search body should return a 400 error """
        res = self.client().post('/api/questions/search', json={'search': 'This should fail'})
        res_body = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(res_body['success'])
        self.assertEqual(res_body['message'], 'Bad request')

    def test_405_post_category(self):
        """ Test sending a POST to /api/categories should return a 405 error """
        res = self.client().post('/api/categories', json={'type': 'New Category'})
        res_body = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertFalse(res_body['success'])
        self.assertEqual(res_body['message'], 'Method not allowed')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()