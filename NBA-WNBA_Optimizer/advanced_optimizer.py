#!/usr/bin/env python3
"""
Advanced NBA/WNBA Basketball Lineup Optimizer

This module provides enhanced functionality for optimizing NBA/WNBA lineups
with additional differentiation factors such as:
- Team stacking
- Player correlation
- Matchup targeting
- Advanced exposure control
"""

import os
import sys
import csv
import time
import random
import pandas as pd
import numpy as np
from datetime import datetime
from pulp import LpProblem, LpMaximize, LpVariable, LpStatus, PULP_CBC_CMD, lpSum, LpInteger

# Import the base optimizer to extend its functionality
from optimizer import WNBAShowdownOptimizer

class AdvancedWNBAShowdownOptimizer(WNBAShowdownOptimizer):
    """Advanced optimizer for NBA/WNBA Basketball contests with differentiation features."""
    
    def __init__(self, data_file, salary_cap=50000, captain_multiplier=1.5):
        """
        Initialize the advanced NBA/WNBA Basketball lineup optimizer.
        
        Args:
            data_file: Path to CSV file containing player data
            salary_cap: Salary cap for lineup (default: 50000)
            captain_multiplier: Points multiplier for captain (default: 1.5, WNBA Showdown format)
        """
        super().__init__(data_file, salary_cap, captain_multiplier)
        self._init_correlations()
    
    def _init_correlations(self):
        """
        Initialize player correlation matrices.
        Correlation between players on same team is positive.
        Correlation between players on opposing teams is negative.
        """
        self.team_correlations = {}
        teams = self.players['TeamAbbrev'].unique()
        
        # Create a simple correlation matrix based on teams
        for team in teams:
            self.team_correlations[team] = {}
            for other_team in teams:
                if team == other_team:
                    self.team_correlations[team][other_team] = 0.3  # Positive correlation for same team
                else:
                    # Get all games involving both teams to see if they play each other
                    team_games = self.players[self.players['TeamAbbrev'] == team]['Game Info'].unique()
                    opponents = []
                    
                    for game in team_games:
                        if isinstance(game, str) and '@' in game:
                            teams_in_game = game.split('@')
                            if team in teams_in_game:
                                opponents.append([t for t in teams_in_game if t != team][0])
                    
                    if other_team in opponents:
                        self.team_correlations[team][other_team] = -0.1  # Negative correlation for opponents
                    else:
                        self.team_correlations[team][other_team] = 0  # No correlation
    
    def optimize(self, num_lineups=1, player_diversity=3, exposure_constraints=None,
                 stack_team=None, stack_count=3, fade_teams=None, randomness=0.0,
                 min_salary_used=0.95):
        """
        Optimize WNBA Showdown lineups with advanced options.
        
        Args:
            num_lineups: Number of lineups to generate
            player_diversity: Minimum player differences between lineups
            exposure_constraints: Dict of {player_name: max_exposure} where max_exposure is 0-1
            stack_team: Team abbreviation to stack (include multiple players from)
            stack_count: Minimum number of players to include from stacked team
            fade_teams: List of team abbreviations to fade (minimize exposure)
            randomness: Factor of randomness to add to projections (0-1)
            min_salary_used: Minimum fraction of salary cap that must be used
            
        Returns:
            List of optimized lineups
        """
        if not self._validate_data():
            return []
            
        all_lineups = []
        previous_lineups = []
        
        # Prepare a copy of projections to add randomness
        randomized_projections = self.players['AvgPointsPerGame'].copy()
        
        # Apply fade teams by reducing player projections
        if fade_teams:
            for team in fade_teams:
                mask = self.players['TeamAbbrev'] == team
                self.players.loc[mask, 'AvgPointsPerGame'] *= 0.8
                print(f"Applied 20% fade to players from {team}")
        
        for i in range(num_lineups):
            print(f"\nGenerating lineup {i+1} of {num_lineups}")
            
            # Apply randomness to projections if specified
            if randomness > 0:
                for idx in range(len(randomized_projections)):
                    random_factor = 1.0 + (random.uniform(-randomness, randomness))
                    randomized_projections.iloc[idx] = self.players['AvgPointsPerGame'].iloc[idx] * random_factor
            else:
                randomized_projections = self.players['AvgPointsPerGame'].copy()
            
            # Create optimization model
            prob = LpProblem(f"WNBA_Showdown_Lineup_{i+1}", LpMaximize)
            
            # Create variables for captain and utility positions
            captain_vars = []
            utility_vars = []
            
            for idx, player in self.players.iterrows():
                # Variable for player as captain (1 if selected, 0 otherwise)
                captain_vars.append(
                    LpVariable(f"Captain_{player['PlayerIndex']}", cat=LpInteger, lowBound=0, upBound=1)
                )
                
                # Variable for player as utility (1 if selected, 0 otherwise)
                utility_vars.append(
                    LpVariable(f"Utility_{player['PlayerIndex']}", cat=LpInteger, lowBound=0, upBound=1)
                )
            
            # Objective function: maximize projected points using randomized projections
            prob += lpSum([
                # Captain points (1.5x multiplier)
                captain_vars[i] * randomized_projections.iloc[i] * self.captain_multiplier +
                # Utility points (normal)
                utility_vars[i] * randomized_projections.iloc[i]
                for i in range(len(self.players))
            ])
            
            # Constraint 1: Exactly 1 captain
            prob += lpSum(captain_vars) == 1, "Exactly_1_Captain"
            
            # Constraint 2: Exactly 5 utility players
            prob += lpSum(utility_vars) == 5, "Exactly_5_Utility_Players"
            
            # Constraint 3: A player can't be both captain and utility
            for i in range(len(self.players)):
                prob += captain_vars[i] + utility_vars[i] <= 1, f"No_Duplicate_Player_{i}"
            
            # Constraint 4: Salary cap
            prob += lpSum([
                captain_vars[i] * self.players.iloc[i]['Salary'] * 1.5 +  # Captain costs 1.5x
                utility_vars[i] * self.players.iloc[i]['Salary']
                for i in range(len(self.players))
            ]) <= self.salary_cap, "Salary_Cap"
            
            # Constraint 5: Minimum salary used
            min_salary = int(self.salary_cap * min_salary_used)
            prob += lpSum([
                captain_vars[i] * self.players.iloc[i]['Salary'] * 1.5 +  # Captain costs 1.5x
                utility_vars[i] * self.players.iloc[i]['Salary']
                for i in range(len(self.players))
            ]) >= min_salary, "Minimum_Salary_Used"
            
            # Constraint 6: Team stacking if specified
            if stack_team:
                stack_indices = self.players.index[self.players['TeamAbbrev'] == stack_team].tolist()
                if stack_indices:
                    # Ensure we have at least stack_count players from the specified team
                    prob += lpSum([
                        captain_vars[self.players.loc[idx, 'PlayerIndex']] + utility_vars[self.players.loc[idx, 'PlayerIndex']]
                        for idx in stack_indices
                    ]) >= stack_count, f"Stack_{stack_team}"
                    print(f"Added constraint to include at least {stack_count} players from {stack_team}")
                else:
                    print(f"Warning: Stack team {stack_team} not found in player data")
            
            # Constraint 7: Player diversity from previous lineups
            for j, prev_lineup in enumerate(previous_lineups):
                prob += lpSum([
                    captain_vars[i] + utility_vars[i]
                    for i in range(len(self.players))
                    if self.players.iloc[i]['Name'] in prev_lineup['player_names']
                ]) <= (6 - player_diversity), f"Diversity_From_Previous_Lineups_{j}"
            
            # Constraint 8: Apply exposure constraints
            if exposure_constraints:
                for player_name, max_exposure in exposure_constraints.items():
                    player_indices = self.players.index[self.players['Name'] == player_name].tolist()
                    for idx in player_indices:
                        i = self.players.loc[idx, 'PlayerIndex']
                        if max_exposure == 0:  # Exclude player completely
                            prob += captain_vars[i] + utility_vars[i] == 0, f"Exclude_{player_name}"
                        else:
                            # Calculate current exposure
                            current_exposure = sum(1 for lineup in previous_lineups if player_name in lineup['player_names'])
                            max_allowed = int(max_exposure * num_lineups)
                            if current_exposure >= max_allowed:
                                prob += captain_vars[i] + utility_vars[i] == 0, f"Max_Exposure_{player_name}"
            
            # Solve the problem
            prob.solve(PULP_CBC_CMD(msg=False))
            
            if prob.status == 1:  # Optimal solution found
                # Extract the lineup
                lineup = {
                    'captain': None,
                    'utilities': [],
                    'total_salary': 0,
                    'total_projected_points': 0,
                    'player_names': [],
                    'teams': {}
                }
                
                # Extract captain
                for i in range(len(self.players)):
                    if captain_vars[i].value() == 1:
                        player = self.players.iloc[i].to_dict()
                        player['position'] = 'CPT'
                        player['is_captain'] = True
                        player['projected_points'] = player['AvgPointsPerGame'] * self.captain_multiplier
                        player['opponent'] = self._extract_opponent(player.get('Game Info', ''), player['TeamAbbrev'])
                        lineup['captain'] = player
                        lineup['total_salary'] += player['Salary'] * 1.5
                        lineup['total_projected_points'] += player['projected_points']
                        lineup['player_names'].append(player['Name'])
                        
                        # Track teams
                        team = player['TeamAbbrev']
                        lineup['teams'][team] = lineup['teams'].get(team, 0) + 1
                
                # Extract utility players
                for i in range(len(self.players)):
                    if utility_vars[i].value() == 1:
                        player = self.players.iloc[i].to_dict()
                        player['position'] = 'UTIL'
                        player['is_captain'] = False
                        player['projected_points'] = player['AvgPointsPerGame']
                        player['opponent'] = self._extract_opponent(player.get('Game Info', ''), player['TeamAbbrev'])
                        lineup['utilities'].append(player)
                        lineup['total_salary'] += player['Salary']
                        lineup['total_projected_points'] += player['projected_points']
                        lineup['player_names'].append(player['Name'])
                        
                        # Track teams
                        team = player['TeamAbbrev']
                        lineup['teams'][team] = lineup['teams'].get(team, 0) + 1
                
                all_lineups.append(lineup)
                previous_lineups.append(lineup)
                
                # Print lineup details
                print(f"Lineup {i+1} optimization complete:")
                print(f"Captain: {lineup['captain']['Name']} ({lineup['captain']['TeamAbbrev']})")
                print("Utility players:")
                for util in lineup['utilities']:
                    print(f"- {util['Name']} ({util['TeamAbbrev']})")
                    
                # Print team breakdown
                print("Team breakdown:")
                for team, count in lineup['teams'].items():
                    print(f"- {team}: {count} players")
                    
                print(f"Total salary: ${lineup['total_salary']} of ${self.salary_cap}")
                print(f"Projected points: {lineup['total_projected_points']:.2f}")
            else:
                print(f"Could not find optimal solution for lineup {i+1}")
                
                # Try to identify constraints causing the issue
                if stack_team and i > 0:
                    print("Hint: The team stack constraint might be too restrictive.")
                if player_diversity > 3 and i > 2:
                    print("Hint: Try reducing the player_diversity requirement.")
        
        return all_lineups
    
    def save_correlation_matrix(self, file_path="team_correlations.csv"):
        """
        Save the team correlation matrix to a CSV file.
        
        Args:
            file_path: Path to output file
        """
        teams = list(self.team_correlations.keys())
        df = pd.DataFrame(index=teams, columns=teams)
        
        for team1 in teams:
            for team2 in teams:
                df.loc[team1, team2] = self.team_correlations[team1].get(team2, 0)
        
        df.to_csv(file_path)
        print(f"Team correlation matrix saved to {file_path}")


if __name__ == "__main__":
    # Example usage
    if len(sys.argv) > 1:
        data_file = sys.argv[1]
    else:
        data_file = "DKSalaries.csv"
        
    if not os.path.exists(data_file):
        print(f"Error: Data file '{data_file}' not found.")
        sys.exit(1)
        
    num_lineups = 10
    if len(sys.argv) > 2:
        try:
            num_lineups = int(sys.argv[2])
        except:
            print(f"Warning: Invalid number of lineups '{sys.argv[2]}', using default {num_lineups}")
    
    # Example configuration
    stack_team = None
    player_diversity = 2
    randomness = 0.05
    
    # Parse optional command-line arguments
    if len(sys.argv) > 3:
        stack_team = sys.argv[3]
    
    # Create optimizer and generate lineups
    optimizer = AdvancedWNBAShowdownOptimizer(data_file)
    
    # Optional: Define exposure constraints
    exposure_constraints = {}  # Example: {'Player Name': 0.5} for 50% max exposure
    
    lineups = optimizer.optimize(
        num_lineups=num_lineups,
        player_diversity=player_diversity,
        stack_team=stack_team,
        randomness=randomness,
        exposure_constraints=exposure_constraints
    )
    
    # Save lineups to CSV
    if lineups:
        optimizer.save_lineups_to_csv(lineups)
