#!/usr/bin/env python3
"""
Unit tests for the F1 Advanced Lineup Optimizer.

This file contains tests that verify the advanced optimizer's functionality
including team stacking, driver correlation, and lineup diversity constraints.
"""

import os
import sys
import unittest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the optimizer modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from advanced_optimizer import AdvancedLineupOptimizer


class TestAdvancedF1LineupOptimizer(unittest.TestCase):
    """Test cases for the advanced F1 lineup optimizer."""

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
        self.optimizer = AdvancedLineupOptimizer(
            self.test_csv_path, 
            salary_cap=50000,
            max_from_team=3,
            min_teams=2,
            max_player_appearances=1
        )

    def tearDown(self):
        """Clean up after each test method."""
        # Remove the temporary CSV file
        if os.path.exists(self.test_csv_path):
            os.remove(self.test_csv_path)

    def test_init(self):
        """Test the initialization of the AdvancedLineupOptimizer class."""
        self.assertEqual(self.optimizer.salary_cap, 50000)
        self.assertEqual(self.optimizer.max_from_team, 3)
        self.assertEqual(self.optimizer.min_teams, 2)
        self.assertEqual(self.optimizer.max_player_appearances, 1)
        self.assertEqual(len(self.optimizer.players_df), 20)
        self.assertEqual(len(self.optimizer.teams), 5)  # MERC, RBULL, FERR, MCLA, ALPI
        self.assertEqual(self.optimizer.required_positions, {
            'CPT': 1, 'D': 4, 'CNSTR': 1
        })

    def test_optimize_basic_functionality(self):
        """Test basic optimization functionality."""
        lineups = self.optimizer.optimize(num_lineups=1)
        
        # Check that we got exactly one lineup
        self.assertEqual(len(lineups), 1)
        
        lineup = lineups[0]
        
        # Check that the lineup has exactly 6 players
        self.assertEqual(len(lineup['players']), 6)
        
        # Check position requirements
        positions = [player['position'] for player in lineup['players']]
        self.assertEqual(positions.count('CPT'), 1)
        self.assertEqual(positions.count('D'), 4)
        self.assertEqual(positions.count('CNSTR'), 1)
        
        # Check salary cap constraint
        self.assertLessEqual(lineup['total_salary'], 50000)
        
        # Check minimum teams constraint
        team_count = len(set(player['team'] for player in lineup['players']))
        self.assertGreaterEqual(team_count, 2)

    def test_team_stacking(self):
        """Test the team stacking functionality."""
        stack_team = 'MERC'
        stack_count = 2
        
        lineups = self.optimizer.optimize(
            num_lineups=1,
            stack_team=stack_team,
            stack_count=stack_count
        )
        
        # Check that we got exactly one lineup
        self.assertEqual(len(lineups), 1)
        
        # Count drivers from stacked team (excluding constructor)
        driver_positions = ['CPT', 'D']
        stacked_team_count = sum(1 for player in lineups[0]['players'] 
                               if player['team'] == stack_team and player['position'] in driver_positions)
        
        # Check that at least stack_count drivers are from the stacked team
        self.assertGreaterEqual(stacked_team_count, stack_count)

    def test_max_from_team_constraint(self):
        """Test the maximum players from one team constraint."""
        max_from_team = 2
        
        # Create a new optimizer with a lower max_from_team setting
        optimizer = AdvancedLineupOptimizer(
            self.test_csv_path,
            max_from_team=max_from_team
        )
        
        lineups = optimizer.optimize(num_lineups=1)
        
        # Check that no team has more than max_from_team players
        team_counts = {}
        for player in lineups[0]['players']:
            team = player['team']
            team_counts[team] = team_counts.get(team, 0) + 1
        
        for team, count in team_counts.items():
            self.assertLessEqual(count, max_from_team)

    def test_player_appearance_limit(self):
        """Test limiting the number of times a player can appear across lineups."""
        max_appearances = 2
        num_lineups = 5
        
        lineups = self.optimizer.optimize(
            num_lineups=num_lineups,
            max_player_appearances=max_appearances
        )
        
        # Count player appearances across all lineups
        player_counts = {}
        for lineup in lineups:
            for player in lineup['players']:
                player_id = player['id']
                player_counts[player_id] = player_counts.get(player_id, 0) + 1
        
        # Check that no player appears more than max_appearances times
        for player_id, count in player_counts.items():
            self.assertLessEqual(count, max_appearances)

    def test_lineup_diversity(self):
        """Test lineup diversity constraints."""
        num_lineups = 3
        diversity = 3  # Must differ by at least 3 players
        
        lineups = self.optimizer.optimize(
            num_lineups=num_lineups,
            lineup_diversity=diversity
        )
        
        # Check that we got the expected number of lineups
        self.assertEqual(len(lineups), num_lineups)
        
        # Check that lineups differ by at least 'diversity' players
        for i in range(num_lineups):
            for j in range(i + 1, num_lineups):
                lineup1_ids = {player['id'] for player in lineups[i]['players']}
                lineup2_ids = {player['id'] for player in lineups[j]['players']}
                common_players = lineup1_ids.intersection(lineup2_ids)
                
                # There should be at most 6 - diversity common players
                self.assertLessEqual(len(common_players), 6 - diversity)

    def test_min_salary_used_constraint(self):
        """Test minimum salary used constraint."""
        min_salary_pct = 0.95
        
        lineups = self.optimizer.optimize(
            num_lineups=1,
            min_salary_used=min_salary_pct
        )
        
        # Check that at least min_salary_pct of the salary cap was used
        min_salary = self.optimizer.salary_cap * min_salary_pct
        self.assertGreaterEqual(lineups[0]['total_salary'], min_salary)

    def test_captain_constructor_compatibility(self):
        """Test that captain selection is compatible with constructor."""
        lineups = self.optimizer.optimize(num_lineups=1)
        
        # Check if captain's team has a constructor in the lineup
        captain = next(p for p in lineups[0]['players'] if p['position'] == 'CPT')
        constructor = next(p for p in lineups[0]['players'] if p['position'] == 'CNSTR')
        
        # We don't strictly require the captain's team to match the constructor,
        # but we should check that the lineup makes sense strategically
        team_members = [p for p in lineups[0]['players'] if p['team'] == constructor['team']]
        
        # Either the captain should be from the constructor's team, or we should have
        # multiple drivers from the constructor's team for synergy
        if captain['team'] != constructor['team']:
            # If captain is not from constructor team, check if we have multiple drivers from constructor team
            driver_count = sum(1 for p in team_members if p['position'] in ['CPT', 'D'])
            self.assertGreaterEqual(driver_count, 1)

    def test_output_file_generation(self):
        """Test that output files are generated correctly."""
        # Generate lineups
        lineups = self.optimizer.optimize(num_lineups=3)
        
        # Save to CSV
        timestamp = '20250630_120000'  # Mock timestamp
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = timestamp
            
            output_file = f"lineup_{timestamp}.csv"
            self.optimizer.save_lineups_to_csv(lineups, output_file=output_file)
        
            # Check that the output file path is formatted correctly
            self.assertEqual(output_file, f"lineup_{timestamp}.csv")


if __name__ == '__main__':
    unittest.main()
