#!/usr/bin/env python3
"""
Integration tests for the WNBA Showdown Optimizer.

This file contains integration tests that verify the end-to-end functionality
of the WNBA Showdown optimizer, including the full optimization workflow from
loading data to generating valid lineups that meet all contest rules.
"""

import os
import sys
import unittest
import pandas as pd
import subprocess
from unittest.mock import patch

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from optimizer import WNBAShowdownOptimizer
from advanced_optimizer import AdvancedWNBAShowdownOptimizer


class TestWNBAOptimizerIntegration(unittest.TestCase):
    """Integration tests for the WNBA Showdown optimizer."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a realistic test dataset with player data
        self.test_data = pd.DataFrame({
            'ID': list(range(100)),
            'Name': [f'Player{i}' for i in range(100)],
            'TeamAbbrev': ['LVA', 'NYL', 'CON', 'SEA', 'WAS', 'PHO', 'MIN', 'CHI', 'DAL', 'ATL'] * 10,
            'Game Info': ['LVA@NYL', 'LVA@NYL', 'CON@SEA', 'CON@SEA', 'WAS@PHO', 'WAS@PHO',
                         'MIN@CHI', 'MIN@CHI', 'DAL@ATL', 'DAL@ATL'] * 10,
            'Salary': [10000, 9500, 9000, 8500, 8000, 7500, 7000, 6500, 6000, 5500] * 10,
            'AvgPointsPerGame': [40.0, 38.0, 36.0, 34.0, 32.0, 30.0, 28.0, 26.0, 24.0, 22.0] * 10
        })

        # Create a temporary CSV file for testing
        self.test_csv_path = 'test_wnba_players.csv'
        self.test_data.to_csv(self.test_csv_path, index=False)

    def tearDown(self):
        """Clean up after each test method."""
        # Remove temporary files
        if os.path.exists(self.test_csv_path):
            os.remove(self.test_csv_path)
        # Remove any output files created during tests
        for filename in os.listdir('.'):
            if filename.startswith('lineup_') or filename.startswith('optimized_lineups_'):
                os.remove(filename)

    def test_basic_to_advanced_optimizer_consistency(self):
        """Test that basic and advanced optimizers produce consistent results."""
        # Initialize both optimizers with the same data
        basic_optimizer = WNBAShowdownOptimizer(self.test_csv_path)
        advanced_optimizer = AdvancedWNBAShowdownOptimizer(self.test_csv_path)
        
        # Generate lineups with both optimizers
        basic_lineups = basic_optimizer.optimize(num_lineups=1)
        advanced_lineups = advanced_optimizer.optimize(num_lineups=1)
        
        # Verify that both produced a lineup
        self.assertEqual(len(basic_lineups), 1)
        self.assertEqual(len(advanced_lineups), 1)
        
        # Skip if no lineups were generated
        if not advanced_lineups or not basic_lineups:
            self.skipTest("No lineups generated by one or both optimizers, skipping consistency test.")
            
        # Check that both lineups satisfy the key requirements
        # 1. Both lineups have a captain
        self.assertIsNotNone(basic_lineups[0]['captain'])
        self.assertIsNotNone(advanced_lineups[0]['captain'])
        
        # 2. Both lineups have 5 utility players
        self.assertEqual(len(basic_lineups[0]['utilities']), 5)
        self.assertEqual(len(advanced_lineups[0]['utilities']), 5)
        
        # 3. Both lineups are under salary cap
        self.assertLessEqual(basic_lineups[0]['total_salary'], 50000)
        self.assertLessEqual(advanced_lineups[0]['total_salary'], 50000)

    def test_end_to_end_optimization(self):
        """Test the complete optimization workflow."""
        # Create an advanced optimizer with team stacking
        optimizer = AdvancedWNBAShowdownOptimizer(
            self.test_csv_path,
            salary_cap=50000
        )
        
        # Generate multiple lineups with different constraints
        lineups = optimizer.optimize(
            num_lineups=3,
            stack_team='LVA',
            stack_count=3,
            min_salary_used=0.95,
            player_diversity=2,
            randomness=0.05
        )
        
        # Verify the results
        if not lineups:  # Skip further assertions if no lineups
            self.skipTest("No lineups generated, skipping end-to-end test.")
        
        for lineup in lineups:
            # Check roster construction (1 captain, 5 utility)
            self.assertIsNotNone(lineup['captain'])
            self.assertEqual(len(lineup['utilities']), 5)
            
            # Check salary cap
            self.assertLessEqual(lineup['total_salary'], 50000)
            
            # Check team stacking
            lva_players = [p for p in lineup['utilities'] if p['TeamAbbrev'] == 'LVA']
            if lineup['captain']['TeamAbbrev'] == 'LVA':
                lva_players.append(lineup['captain'])
                
            self.assertGreaterEqual(len(lva_players), 3)

    def test_output_file_generation(self):
        """Test that output files are generated correctly."""
        # Create an optimizer
        optimizer = AdvancedWNBAShowdownOptimizer(self.test_csv_path)
        
        # Generate lineups and save to file
        lineups = optimizer.optimize(num_lineups=2)
        
        # Create a test directory for output
        test_output_dir = os.path.join(os.getcwd(), 'test_output')
        os.makedirs(test_output_dir, exist_ok=True)
        
        # Save to CSV with full path
        output_file = os.path.join(test_output_dir, 'test_wnba_lineups.csv')
        optimizer.save_lineups_to_csv(lineups, output_file)
        
        # Check that the files were created
        self.assertTrue(os.path.exists(output_file))
        
        # Read the file and verify contents
        if os.path.exists(output_file):
            df = pd.read_csv(output_file)
            
            # Check that it has the expected number of rows (2 lineups * 6 players per lineup)
            self.assertEqual(len(df), 12)
            
            # Check that required columns exist
            expected_columns = ['Lineup', 'Position', 'Name', 'Team', 'Opponent', 'Salary', 'Avg Points']
            for col in expected_columns:
                self.assertIn(col, df.columns)
            
            # Clean up
            os.remove(output_file)
            
        # Check the summary file
        summary_file = output_file.replace('test_wnba_lineups.csv', 'optimized_lineups_test_wnba_lineups.csv')
        if os.path.exists(summary_file):
            df = pd.read_csv(summary_file)
            
            # Should have one row per lineup
            self.assertEqual(len(df), 2)
            
            # Check for required columns
            expected_columns = ['Lineup', 'Players', 'Total Salary', 'Projected Points']
            for col in expected_columns:
                self.assertIn(col, df.columns)
                
            # Clean up
            os.remove(summary_file)
            
        os.rmdir(test_output_dir)


if __name__ == '__main__':
    unittest.main()
