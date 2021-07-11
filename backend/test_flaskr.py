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
        self.database_path = 'postgresql://postgres:admin@localhost:5432/trivia_test'
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
    Write at least one test for each test for successful 
    operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_if_questions_based_category_allowed(self):
        res = self.client().get("categories/2/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertIn("questions", data)
        self.assertIn("total_questions", data)
        self.assertIn("current_category", data)

    def test_405_if_questions_based_category_not_allowed(self):
        res = self.client().post('/categories/9/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')
    
    def test_422_if_book_does_not_exist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_delete_book(self):
        res = self.client().delete('/questions/4')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_get_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertIn("questions", data)
        self.assertIn("total_questions", data)

    def test_404_get_questions(self):
        res = self.client().get("/questions?page=999")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_search_questions(self):
        res=self.client().post('/questions/search',json={'searchTerm': 'are'})
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn("questions",data)


    def test_create_question(self):
        res = self.client().post('/questions',json={'question': 'Udacity Nanodgree ?', 'answer': 'Yes it is FSND ', 'difficulty': '4', 'category': '1'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn("created", data)
        self.assertIn("questions", data)
        self.assertIn("total_questions", data)

    def test_400_create_question(self):
        res = self.client().post('/questions',json={'question': 'Udacity Nanodgree ?','answer': 'Yes it is FSND','category': 'Not integer','difficulty': 'Not integer',})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

    def test_quizzes(self):
        res = self.client().post('/quizzes',json={"quiz_category": {"id": 1}, "previous_questions": [12]})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn("question", data)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()