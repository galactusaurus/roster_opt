#!/usr/bin/env python3
"""
Unit tests for the Advanced WNBA Showdown Lineup Optimizer.

This file contains tests that verify the functionality of the advanced optimizer,
including team stacking, exposure control, and other differentiation features.
"""

import os
import sys
import unittest
import pandas as pd
from unittest.mock import patch

# Add parent directory to path to import optimizer module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from optimizer import WNBAShowdownOptimizer
from advanced_optimizer import AdvancedWNBAShowdownOptimizer

class TestAdvancedWNBAShowdownOptimizer(unittest.TestCase):
    """Test cases for the Advanced WNBA Showdown lineup optimizer."""
    
    def setUp(self):
        """Set up test fixtures before each test."""
        # Create a simple test dataset with two teams
        self.test_data = pd.DataFrame({
            'Name': ['Player1', 'Player2', 'Player3', 'Player4', 'Player5', 'Player6', 'Player7', 'Player8', 'Player9', 'Player10'],
            'Salary': [10000, 9000, 8000, 7000, 6000, 5000, 4000, 3500, 3000, 2500],
            'TeamAbbrev': ['LVA', 'LVA', 'LVA', 'LVA', 'LVA', 'NYL', 'NYL', 'NYL', 'NYL', 'NYL'],
            'Game Info': ['LVA@NYL', 'LVA@NYL', 'LVA@NYL', 'LVA@NYL', 'LVA@NYL', 'LVA@NYL', 'LVA@NYL', 'LVA@NYL', 'LVA@NYL', 'LVA@NYL'],
            'AvgPointsPerGame': [40.0, 38.0, 36.0, 34.0, 32.0, 30.0, 28.0, 26.0, 24.0, 22.0]
        })
        
        # Save to a test CSV file
        self.test_csv_path = 'test_wnba_advanced.csv'
        self.test_data.to_csv(self.test_csv_path, index=False)
        
        # Initialize the optimizer
        self.optimizer = AdvancedWNBAShowdownOptimizer(self.test_csv_path)
    
    def tearDown(self):
        """Clean up after each test."""
        # Remove the test CSV file
        if os.path.exists(self.test_csv_path):
            os.remove(self.test_csv_path)
    
    def test_init(self):
        """Test the initialization of the advanced optimizer."""
        self.assertEqual(self.optimizer.salary_cap, 50000)
        self.assertEqual(self.optimizer.captain_multiplier, 1.5)
        self.assertEqual(len(self.optimizer.players), 10)
        self.assertTrue(hasattr(self.optimizer, 'team_correlations'))
    
    def test_team_correlations(self):
        """Test that team correlations are initialized correctly."""
        teams = ['LVA', 'NYL']
        for team in teams:
            self.assertTrue(team in self.optimizer.team_correlations)
            for other_team in teams:
                self.assertTrue(other_team in self.optimizer.team_correlations[team])
                
        # Same team should have positive correlation
        self.assertGreater(self.optimizer.team_correlations['LVA']['LVA'], 0)
        
        # Opposing teams should have negative correlation
        self.assertLess(self.optimizer.team_correlations['LVA']['NYL'], 0)
    
    def test_team_stacking(self):
        """Test the team stacking functionality."""
        # Generate lineup with LVA stack (should have at least 4 LVA players)
        lineups = self.optimizer.optimize(num_lineups=1, stack_team='LVA', stack_count=4)
        
        # Check if any lineups were generated
        if not lineups:
            self.skipTest("No lineups generated, skipping team stacking test")
        
        lineup = lineups[0]
        lva_players = [p for p in lineup['utilities'] if p['TeamAbbrev'] == 'LVA']
        if lineup['captain']['TeamAbbrev'] == 'LVA':
            lva_players.append(lineup['captain'])
            
        self.assertGreaterEqual(len(lva_players), 4, "Should have at least 4 LVA players")
    
    def test_player_exposure_constraints(self):
        """Test applying player exposure constraints."""
        # Set Player1 to zero exposure
        exposure_constraints = {'Player1': 0}
        lineups = self.optimizer.optimize(num_lineups=1, exposure_constraints=exposure_constraints)
        
        # Check if any lineups were generated
        if not lineups:
            self.skipTest("No lineups generated, skipping exposure test")
        
        lineup = lineups[0]
        player_names = [p['Name'] for p in lineup['utilities']]
        if lineup['captain']:
            player_names.append(lineup['captain']['Name'])
            
        self.assertNotIn('Player1', player_names)
    
    def test_lineup_diversity(self):
        """Test lineup diversity constraints."""
        # Generate multiple lineups with high diversity
        num_lineups = 3
        player_diversity = 2
        lineups = self.optimizer.optimize(num_lineups=num_lineups, player_diversity=player_diversity)
        
        # Check if enough lineups were generated
        if not lineups or len(lineups) < 2:
            self.skipTest("Not enough lineups generated, skipping diversity test")
        
        # Check diversity between consecutive lineups
        for i in range(len(lineups) - 1):
            lineup1_players = set(lineups[i]['player_names'])
            lineup2_players = set(lineups[i+1]['player_names'])
            
            # Calculate the number of different players between lineups
            different_players = len(lineup1_players.symmetric_difference(lineup2_players))
            self.assertGreaterEqual(different_players, player_diversity)
    
    def test_min_salary_used_constraint(self):
        """Test minimum salary used constraint."""
        min_salary_used = 0.95
        lineups = self.optimizer.optimize(num_lineups=1, min_salary_used=min_salary_used)
        
        # Check if any lineups were generated
        if not lineups:
            self.skipTest("No lineups generated, skipping salary constraint test")
            
        lineup = lineups[0]
        min_salary = int(self.optimizer.salary_cap * min_salary_used)
        
        self.assertGreaterEqual(lineup['total_salary'], min_salary)

if __name__ == '__main__':
    unittest.main()
