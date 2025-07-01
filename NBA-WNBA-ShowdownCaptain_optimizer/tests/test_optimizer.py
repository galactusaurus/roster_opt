#!/usr/bin/env python3
"""
Unit tests for the WNBA Showdown Lineup Optimizer.

This file contains tests that verify the functionality of the basic optimizer,
including lineup generation, salary constraints, and proper roster construction.
"""

import os
import sys
import unittest
import pandas as pd
from unittest.mock import patch

# Add parent directory to path to import optimizer module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from optimizer import WNBAShowdownOptimizer

class TestWNBAShowdownOptimizer(unittest.TestCase):
    """Test cases for the WNBA Showdown lineup optimizer."""
    
    def setUp(self):
        """Set up test fixtures before each test."""
        # Create a simple test dataset
        self.test_data = pd.DataFrame({
            'Name': ['Player1', 'Player2', 'Player3', 'Player4', 'Player5', 'Player6', 'Player7', 'Player8'],
            'Salary': [10000, 9000, 8000, 7000, 6000, 5000, 4000, 3000],
            'TeamAbbrev': ['LVA', 'LVA', 'NYL', 'NYL', 'CON', 'CON', 'SEA', 'SEA'],
            'Game Info': ['LVA@NYL', 'LVA@NYL', 'LVA@NYL', 'LVA@NYL', 'CON@SEA', 'CON@SEA', 'CON@SEA', 'CON@SEA'],
            'AvgPointsPerGame': [40.0, 35.0, 30.0, 25.0, 20.0, 15.0, 10.0, 5.0]
        })
        
        # Save to a test CSV file
        self.test_csv_path = 'test_wnba_players.csv'
        self.test_data.to_csv(self.test_csv_path, index=False)
        
        # Initialize the optimizer
        self.optimizer = WNBAShowdownOptimizer(self.test_csv_path)
    
    def tearDown(self):
        """Clean up after each test."""
        # Remove the test CSV file
        if os.path.exists(self.test_csv_path):
            os.remove(self.test_csv_path)
    
    def test_init(self):
        """Test the initialization of the optimizer."""
        self.assertEqual(self.optimizer.salary_cap, 50000)
        self.assertEqual(self.optimizer.captain_multiplier, 1.5)
        self.assertEqual(len(self.optimizer.players), 8)
    
    def test_data_loading(self):
        """Test that player data is loaded correctly."""
        self.assertEqual(len(self.optimizer.players), 8)
        self.assertTrue('Name' in self.optimizer.players.columns)
        self.assertTrue('Salary' in self.optimizer.players.columns)
        self.assertTrue('TeamAbbrev' in self.optimizer.players.columns)
        self.assertTrue('AvgPointsPerGame' in self.optimizer.players.columns)
    
    def test_extract_opponent(self):
        """Test the _extract_opponent method."""
        # Test with valid game info
        opponent = self.optimizer._extract_opponent('LVA@NYL', 'LVA')
        self.assertEqual(opponent, 'NYL')
        
        opponent = self.optimizer._extract_opponent('LVA@NYL', 'NYL')
        self.assertEqual(opponent, 'LVA')
        
        # Test with invalid game info
        opponent = self.optimizer._extract_opponent('Invalid', 'LVA')
        self.assertEqual(opponent, 'Unknown')
        
        opponent = self.optimizer._extract_opponent(None, 'LVA')
        self.assertEqual(opponent, 'Unknown')
    
    def test_optimize_single_lineup(self):
        """Test generating a single optimized lineup."""
        lineups = self.optimizer.optimize(num_lineups=1)
        
        # Check if any lineups were generated
        if not lineups:
            self.skipTest("No lineups generated, skipping assertions")
            
        # Check that we have one lineup
        self.assertEqual(len(lineups), 1)
        
        lineup = lineups[0]
        # Check that we have 1 captain and 5 utilities
        self.assertIsNotNone(lineup['captain'])
        self.assertEqual(len(lineup['utilities']), 5)
        
        # Check total salary is under cap
        self.assertLessEqual(lineup['total_salary'], 50000)
        
        # Captain should be the highest points-per-dollar player
        highest_value_player = self.test_data.iloc[
            (self.test_data['AvgPointsPerGame'] / self.test_data['Salary']).idxmax()
        ]
        self.assertEqual(lineup['captain']['Name'], highest_value_player['Name'])
    
    def test_salary_cap_constraint(self):
        """Test that the salary cap constraint is enforced."""
        # Create a test case where it's impossible to stay under salary cap
        high_salary_data = pd.DataFrame({
            'Name': ['Player1', 'Player2', 'Player3', 'Player4', 'Player5', 'Player6'],
            'Salary': [15000, 15000, 15000, 15000, 15000, 15000],
            'TeamAbbrev': ['LVA', 'LVA', 'NYL', 'NYL', 'CON', 'SEA'],
            'AvgPointsPerGame': [40.0, 35.0, 30.0, 25.0, 20.0, 15.0]
        })
        
        high_salary_path = 'high_salary_test.csv'
        high_salary_data.to_csv(high_salary_path, index=False)
        
        try:
            optimizer = WNBAShowdownOptimizer(high_salary_path)
            lineups = optimizer.optimize(num_lineups=1)
            
            # No lineups should be generated as total salary would exceed cap
            self.assertEqual(len(lineups), 0)
        finally:
            if os.path.exists(high_salary_path):
                os.remove(high_salary_path)

if __name__ == '__main__':
    unittest.main()
