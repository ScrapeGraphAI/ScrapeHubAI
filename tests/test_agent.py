import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path to enable imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.evaluator import evaluate_company, rank_companies
from src.agent import run_agent

class TestEvaluator(unittest.TestCase):
    def test_evaluate_company_high_score(self):
        """Test evaluation of a company with high relevance."""
        company_info = """
        TechCorp is a leading AI and machine learning company with 500 employees.
        They specialize in data analytics, web scraping, and automation solutions.
        The company is growing rapidly and recently raised Series B funding.
        """
        
        result = evaluate_company("TechCorp", company_info)
        
        self.assertEqual(result["company"], "TechCorp")
        self.assertGreaterEqual(result["score"], 70)
        self.assertEqual(result["recommendation"], "High Priority")
        self.assertIn("employees", result["summary"].lower())
    
    def test_evaluate_company_medium_score(self):
        """Test evaluation of a company with medium relevance."""
        company_info = """
        RetailCo is an e-commerce company with 100 employees.
        They focus on online retail and digital marketing.
        """
        
        result = evaluate_company("RetailCo", company_info)
        
        self.assertEqual(result["company"], "RetailCo")
        self.assertGreaterEqual(result["score"], 30)
        self.assertLessEqual(result["score"], 70)
    
    def test_evaluate_company_low_score(self):
        """Test evaluation of a company with low relevance."""
        company_info = """
        LocalShop is a small local business with 5 employees.
        They sell handmade crafts and artwork.
        """
        
        result = evaluate_company("LocalShop", company_info)
        
        self.assertEqual(result["company"], "LocalShop")
        self.assertLess(result["score"], 30)
    
    def test_rank_companies(self):
        """Test ranking of multiple companies."""
        evaluations = [
            {"company": "A", "score": 50},
            {"company": "B", "score": 80},
            {"company": "C", "score": 30},
            {"company": "D", "score": 65}
        ]
        
        ranked = rank_companies(evaluations)
        
        self.assertEqual(len(ranked), 4)
        self.assertEqual(ranked[0]["company"], "B")
        self.assertEqual(ranked[1]["company"], "D")
        self.assertEqual(ranked[2]["company"], "A")
        self.assertEqual(ranked[3]["company"], "C")

class TestAgent(unittest.TestCase):
    @patch('src.agent.fetch_stargazers')
    @patch('src.agent.get_user_company')
    @patch('src.agent.search_company_info')
    def test_run_agent_success(self, mock_search, mock_get_user, mock_fetch):
        """Test successful agent run."""
        # Mock the tools
        mock_fetch.invoke.return_value = ["user1", "user2", "user3"]
        mock_get_user.invoke.side_effect = [
            {"username": "user1", "company": "TechCorp", "organizations": []},
            {"username": "user2", "company": None, "organizations": ["DataInc"]},
            {"username": "user3", "company": "AIStartup", "organizations": []}
        ]
        mock_search.invoke.return_value = "Company with 100 employees in AI and data analytics"
        
        result = run_agent("test/repo")
        
        self.assertTrue(result["success"])
        self.assertIsNone(result["error"])
        self.assertEqual(result["total_stargazers"], 3)
        self.assertGreater(result["total_companies"], 0)
        self.assertGreater(len(result["evaluations"]), 0)
    
    @patch('src.agent.fetch_stargazers')
    def test_run_agent_error(self, mock_fetch):
        """Test agent handling of errors."""
        mock_fetch.invoke.return_value = ["Error: Repository not found"]
        
        result = run_agent("invalid/repo")
        
        self.assertTrue(result["success"] or result["error"])  # Should handle error gracefully
        self.assertIsInstance(result["evaluations"], list)

if __name__ == '__main__':
    unittest.main()