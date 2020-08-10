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
        self.database_path = "postgresql://{}/{}".format('postgres:123456@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'New Question Test Case ?',
            'answer': 'Answer Test Case',
            'difficulty': 1,
            'category': 1
        }

        self.invalid_new_question = {
            'question': 'New Question Test Case ?'
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
        """Test categories"""
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['categories']))
        self.assertEqual(data['success'], True)

    def test_get_questions_per_page(self):
        """Test questions per page"""
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['total_questions'] > 0)
        self.assertTrue(len(data['questions']) > 0)
        self.assertTrue(len(data['categories']))
        self.assertEqual(data['success'], True)

    def test_get_questions_for_invalid_page(self):
        """Test questions per page"""
        res = self.client().get('/questions/page=300')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_delete_question(self):
        """Test questions per page"""
        question_to_delete = Question.query.first()
        res = self.client().delete('/questions/'+str(question_to_delete.id))
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == question_to_delete.id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(question, None)
        self.assertEqual(data['deleted'], question_to_delete.id)

    def test_delete_not_exist_question(self):
        """Test questions per page"""
        res = self.client().delete('/questions/1')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 1).one_or_none()

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    def test_create_new_question(self):
        """Test create new questions"""
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_create_new_invalid_question(self):
        """Test create new invalid questions"""
        res = self.client().post('/questions', json=self.invalid_new_question)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()