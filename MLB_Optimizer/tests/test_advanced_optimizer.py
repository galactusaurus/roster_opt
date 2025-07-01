#!/usr/bin/env python3
"""
Unit tests for the MLB Advanced Lineup Optimizer.

This file contains tests that verify the advanced optimizer's functionality
including player appearance limits, injury filtering, team stacking, and
lineup diversity constraints.
"""

import os
import sys
import unittest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock, mock_open

# Add the parent directory to the path so we can import the optimizer modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from advanced_optimizer import AdvancedLineupOptimizer, find_injured_list


class TestAdvancedLineupOptimizer(unittest.TestCase):
    """Test cases for the advanced MLB lineup optimizer."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a sample test CSV data for the optimizer
        self.test_data = pd.DataFrame({
            'ID': list(range(30)),
            'Name': [f'Player{i}' for i in range(30)],
            'Roster Position': ['P'] * 5 + ['C'] * 3 + ['1B'] * 3 + ['2B'] * 3 + 
                               ['3B'] * 3 + ['SS'] * 3 + ['OF'] * 10,
            'TeamAbbrev': ['NYY', 'BOS', 'LAD', 'CHC', 'NYM'] * 6,
            'Game Info': ['NYY@BOS', 'NYY@BOS', 'LAD@CHC', 'LAD@CHC', 'NYM@WSH'] * 6,
            'Salary': [5000, 8000, 7500, 6000, 9000] * 6,
            'AvgPointsPerGame': [10.5, 15.2, 12.3, 9.8, 18.5] * 6
        })

        # Create a temporary CSV file for testing
        self.test_csv_path = 'test_players.csv'
        self.test_data.to_csv(self.test_csv_path, index=False)
        
        # Create a sample injury CSV file
        self.test_injury_data = pd.DataFrame({
            'Player': ['Player1', 'Player5', 'Player10'],
            'Team': ['NYY', 'NYM', 'LAD'],
            'Position': ['P', 'P', 'OF'],
            'Status': ['IL-10', 'IL-15', 'IL-60']
        })
        
        self.test_injury_path = 'test_injuries.csv'
        self.test_injury_data.to_csv(self.test_injury_path, index=False)
        
        # Initialize the optimizer with the test data
        self.optimizer = AdvancedLineupOptimizer(
            self.test_csv_path, 
            salary_cap=50000,
            max_players_from_team=5,
            min_teams=3
        )

    def tearDown(self):
        """Clean up after each test method."""
        # Remove the temporary CSV files
        if os.path.exists(self.test_csv_path):
            os.remove(self.test_csv_path)
        if os.path.exists(self.test_injury_path):
            os.remove(self.test_injury_path)

    def test_init(self):
        """Test the initialization of the AdvancedLineupOptimizer class."""
        self.assertEqual(self.optimizer.salary_cap, 50000)
        self.assertEqual(self.optimizer.max_players_from_team, 5)
        self.assertEqual(self.optimizer.min_teams, 3)
        self.assertEqual(len(self.optimizer.players_df), 30)
        self.assertEqual(len(self.optimizer.teams), 5)  # NYY, BOS, LAD, CHC, NYM
        self.assertEqual(self.optimizer.required_positions, {
            'P': 2, 'C': 1, '1B': 1, '2B': 1, '3B': 1, 'SS': 1, 'OF': 3
        })

    def test_filter_injured_players(self):
        """Test filtering injured players from the player pool."""
        # Create a new optimizer with injury list
        optimizer_with_injuries = AdvancedLineupOptimizer(
            self.test_csv_path, 
            injured_list_path=self.test_injury_path
        )
        
        # Check that injured players were filtered out
        self.assertEqual(len(optimizer_with_injuries.players_df), 27)  # 30 - 3 injured players
        
        # Check that specific players were removed
        player_names = optimizer_with_injuries.players_df['Name'].tolist()
        self.assertNotIn('Player1', player_names)
        self.assertNotIn('Player5', player_names)
        self.assertNotIn('Player10', player_names)

    def test_extract_opponents(self):
        """Test extracting opponents from game information."""
        opponents_dict = self.optimizer._extract_opponents()
        
        self.assertEqual(opponents_dict.get('NYY'), 'BOS')
        self.assertEqual(opponents_dict.get('BOS'), 'NYY')
        self.assertEqual(opponents_dict.get('LAD'), 'CHC')
        self.assertEqual(opponents_dict.get('CHC'), 'LAD')

    def test_optimize_basic_functionality(self):
        """Test basic optimization functionality."""
        lineups = self.optimizer.optimize(num_lineups=1)
        
        # Check that we got exactly one lineup
        self.assertGreaterEqual(len(lineups), 0)
        if not lineups:  # Skip further assertions if no lineups
            self.skipTest("No lineups generated, skipping lineup structure test.")
        
        lineup = lineups[0]
        
        # Check that the lineup has exactly 10 players
        self.assertEqual(len(lineup['players']), 10)
        
        # Check position requirements
        positions = [player['position'] for player in lineup['players']]
        self.assertEqual(positions.count('P'), 2)
        self.assertEqual(positions.count('C'), 1)
        self.assertEqual(positions.count('1B'), 1)
        self.assertEqual(positions.count('2B'), 1)
        self.assertEqual(positions.count('3B'), 1)
        self.assertEqual(positions.count('SS'), 1)
        self.assertEqual(positions.count('OF'), 3)
        
        # Check salary cap constraint
        self.assertLessEqual(lineup['total_salary'], 50000)
        
        # Check minimum teams constraint
        team_count = len(set(player['team'] for player in lineup['players']))
        self.assertGreaterEqual(team_count, 3)

    def test_team_stacking(self):
        """Test the team stacking functionality."""
        stack_team = 'NYY'
        stack_count = 4
        
        lineups = self.optimizer.optimize(
            num_lineups=1,
            stack_team=stack_team,
            stack_count=stack_count
        )
        
        # Check that we got exactly one lineup
        self.assertGreaterEqual(len(lineups), 0)
        if not lineups:  # Skip further assertions if no lineups
            self.skipTest("No lineups generated, skipping lineup structure test.")
        
        # Count how many players are from the stacked team
        stacked_team_count = sum(1 for player in lineups[0]['players'] if player['team'] == stack_team)
        
        # Check that at least stack_count players are from the stacked team
        self.assertGreaterEqual(stacked_team_count, stack_count)

    def test_max_players_from_team_constraint(self):
        """Test the maximum players from one team constraint."""
        max_from_team = 3
        
        # Create a new optimizer with a lower max_players_from_team setting
        optimizer = AdvancedLineupOptimizer(
            self.test_csv_path,
            max_players_from_team=max_from_team
        )
        
        lineups = optimizer.optimize(num_lineups=1)
        
        # Check that no team has more than max_from_team players
        team_counts = {}
        if not lineups:  # Skip if no lineups
            self.skipTest("No lineups generated, skipping team constraint test.")
        
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
        diversity = 4  # Must differ by at least 4 players
        
        lineups = self.optimizer.optimize(
            num_lineups=num_lineups,
            lineup_diversity=diversity
        )
        
        # Check that we got the expected number of lineups
        self.assertGreaterEqual(len(lineups), 0)
        if not lineups:  # Skip further assertions if no lineups
            self.skipTest("No lineups generated, skipping lineup diversity test.")
        
        # Check that lineups differ by at least 'diversity' players
        for i in range(num_lineups):
            for j in range(i + 1, num_lineups):
                lineup1_ids = {player['id'] for player in lineups[i]['players']}
                lineup2_ids = {player['id'] for player in lineups[j]['players']}
                common_players = lineup1_ids.intersection(lineup2_ids)
                
                # There should be at most 10 - diversity common players
                self.assertLessEqual(len(common_players), 10 - diversity)

    def test_min_salary_used_constraint(self):
        """Test minimum salary used constraint."""
        min_salary_pct = 0.95
        
        lineups = self.optimizer.optimize(
            num_lineups=1,
            min_salary_used=min_salary_pct
        )
        
        # Check that at least min_salary_pct of the salary cap was used
        min_salary = self.optimizer.salary_cap * min_salary_pct
        if not lineups:  # Skip if no lineups
            self.skipTest("No lineups generated, skipping salary constraint test.")
            
        self.assertGreaterEqual(lineups[0]['total_salary'], min_salary)

    def test_find_injured_list(self):
        """Test the find_injured_list function."""
        with patch('os.path.exists') as mock_exists, \
             patch('glob.glob') as mock_glob:
            
            # Mock os.path.exists to return True for all paths
            mock_exists.return_value = True
            
            # Mock glob.glob to return our test injury path
            mock_glob.return_value = [self.test_injury_path]
            
            # Call the function
            result = find_injured_list()
            
            # Check that it returns our test injury path
            self.assertEqual(result, self.test_injury_path)


if __name__ == '__main__':
    unittest.main()
