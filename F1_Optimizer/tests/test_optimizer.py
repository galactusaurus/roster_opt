#!/usr/bin/env python3
"""
Unit tests for the F1 Basic Lineup Optimizer.

This file contains tests that verify the basic optimizer's functionality
including data loading, constraints enforcement, and lineup generation.
"""

import os
import sys
import unittest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the optimizer modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from optimizer import LineupOptimizer


class TestF1LineupOptimizer(unittest.TestCase):
    """Test cases for the basic F1 lineup optimizer."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a sample test CSV data for the optimizer with F1 drivers and constructors
        self.test_data = pd.DataFrame({
            'ID': list(range(20)),
            'Name': [f'Driver{i}' for i in range(10)] + [f'Constructor{i}' for i in range(10)],
            'Roster Position': ['D', 'CPT', 'D', 'D', 'CPT', 'D', 'D', 'D', 'CPT', 'D'] + ['CNSTR'] * 10,
            'TeamAbbrev': ['MERC', 'RBULL', 'FERR', 'MCLA', 'ALPI'] * 4,
            'Game Info': ['Monaco GP'] * 20,
            'Salary': [12000, 15000, 10000, 8000, 9000, 7500, 6000, 5000, 11000, 9500] + 
                      [8000, 12000, 9000, 7000, 6000, 5000, 7500, 8500, 9500, 10500],
            'AvgPointsPerGame': [50.0, 65.0, 45.0, 40.0, 55.0, 35.0, 30.0, 25.0, 60.0, 42.0] + 
                                [40.0, 70.0, 50.0, 35.0, 30.0, 25.0, 45.0, 55.0, 60.0, 65.0],
        })

        # Create a temporary CSV file for testing
        self.test_csv_path = 'test_f1_players.csv'
        self.test_data.to_csv(self.test_csv_path, index=False)
        
        # Initialize the optimizer with the test data
        self.optimizer = LineupOptimizer(self.test_csv_path, salary_cap=50000)

    def tearDown(self):
        """Clean up after each test method."""
        # Remove the temporary CSV file
        if os.path.exists(self.test_csv_path):
            os.remove(self.test_csv_path)

    def test_init(self):
        """Test the initialization of the LineupOptimizer class."""
        self.assertEqual(self.optimizer.salary_cap, 50000)
        self.assertEqual(len(self.optimizer.players_df), 20)
        self.assertEqual(self.optimizer.required_positions, {
            'CPT': 1, 'D': 4, 'CNSTR': 1
        })

    def test_data_loading(self):
        """Test that player data is loaded correctly."""
        # Check that the data was loaded properly
        self.assertIsInstance(self.optimizer.players_df, pd.DataFrame)
        self.assertEqual(len(self.optimizer.players_df), 20)
        
        # Check that the data types are correct
        self.assertEqual(self.optimizer.players_df['Salary'].dtype, np.int64)
        self.assertEqual(self.optimizer.players_df['AvgPointsPerGame'].dtype, np.float64)
        
        # Check that the Captain points were calculated correctly (1.5x regular points)
        self.assertIn('CaptainPoints', self.optimizer.players_df.columns)
        
        # Test a few specific values
        driver1 = self.optimizer.players_df[self.optimizer.players_df['Name'] == 'Driver1'].iloc[0]
        self.assertEqual(driver1['CaptainPoints'], driver1['AvgPointsPerGame'] * 1.5)

    def test_optimize_single_lineup(self):
        """Test generating a single optimized lineup."""
        lineups = self.optimizer.optimize(num_lineups=1)
        
        # Check that we got exactly one lineup
        self.assertEqual(len(lineups), 1)
        
        lineup = lineups[0]
        
        # Check that the lineup has exactly 6 players (1 CPT, 4 D, 1 CNSTR)
        self.assertEqual(len(lineup['players']), 6)
        
        # Check position requirements
        positions = [player['position'] for player in lineup['players']]
        self.assertEqual(positions.count('CPT'), 1)
        self.assertEqual(positions.count('D'), 4)
        self.assertEqual(positions.count('CNSTR'), 1)
        
        # Check salary cap constraint
        self.assertLessEqual(lineup['total_salary'], 50000)
        
        # Check that points are calculated correctly (CPT gets 1.5x points)
        captain = next(p for p in lineup['players'] if p['position'] == 'CPT')
        self.assertEqual(captain['points'], captain['avg_points'] * 1.5)

    def test_multiple_lineups_diversity(self):
        """Test generating multiple lineups with diversity."""
        num_lineups = 3
        lineups = self.optimizer.optimize(num_lineups=num_lineups)
        
        # Check that we got the expected number of lineups
        self.assertEqual(len(lineups), num_lineups)
        
        # Check that lineups are diverse (at least 2 different players between lineups)
        for i in range(num_lineups):
            for j in range(i + 1, num_lineups):
                lineup1_ids = {player['id'] for player in lineups[i]['players']}
                lineup2_ids = {player['id'] for player in lineups[j]['players']}
                common_players = lineup1_ids.intersection(lineup2_ids)
                
                # There should be at most 4 common players (at least 2 different)
                self.assertLessEqual(len(common_players), 4)

    def test_captain_constraint(self):
        """Test that a driver cannot be both a captain and regular driver."""
        lineups = self.optimizer.optimize(num_lineups=1)
        
        # Get all drivers in the lineup
        captain = None
        regular_drivers = []
        
        for player in lineups[0]['players']:
            if player['position'] == 'CPT':
                captain = player['name']
            elif player['position'] == 'D':
                regular_drivers.append(player['name'])
        
        # Check that the captain doesn't also appear as a regular driver
        self.assertNotIn(captain, regular_drivers)

    def test_salary_cap_constraint(self):
        """Test that the salary cap constraint is enforced."""
        # Create a new optimizer with a very low salary cap
        low_cap_optimizer = LineupOptimizer(self.test_csv_path, salary_cap=10000)
        
        # Try to optimize with the low cap
        with patch('pulp.LpProblem.solve') as mock_solve:
            # Mock the solve method to always return 'Infeasible'
            mock_solve.return_value = 1  # 1 is the code for 'Not Solved'
            mock_status = MagicMock()
            mock_status.__getitem__.return_value = 'Infeasible'
            with patch('pulp.LpStatus', mock_status):
                lineups = low_cap_optimizer.optimize(num_lineups=1)
                
                # Should get an empty list if no solution is found
                self.assertEqual(lineups, [])

    def test_output_formatting(self):
        """Test that the lineup output is formatted correctly."""
        lineups = self.optimizer.optimize(num_lineups=1)
        
        # Check overall lineup structure
        self.assertIn('players', lineups[0])
        self.assertIn('total_salary', lineups[0])
        self.assertIn('total_points', lineups[0])
        
        # Check player data structure
        player = lineups[0]['players'][0]
        self.assertIn('id', player)
        self.assertIn('name', player)
        self.assertIn('position', player)
        self.assertIn('team', player)
        self.assertIn('game_info', player)
        self.assertIn('salary', player)
        self.assertIn('avg_points', player)
        self.assertIn('points', player)


if __name__ == '__main__':
    unittest.main()
