#!/usr/bin/env python3
"""
NBA/WNBA Showdown Captain Lineup Optimizer

This module provides functionality for optimizing NBA/WNBA Showdown Captain lineups.
Supports both traditional NBA lineups and WNBA Showdown contests.
WNBA Showdown contests require 1 Captain and 5 Utility players.
The salary cap for lineups is typically $50,000.
"""

import os
import sys
import csv
import time
import pandas as pd
import numpy as np
from datetime import datetime
from pulp import LpProblem, LpMaximize, LpVariable, LpStatus, PULP_CBC_CMD, lpSum, LpInteger

class WNBAShowdownOptimizer:
    """Optimizer for NBA/WNBA Showdown Captain contests (currently optimized for WNBA Showdown format)."""
    
    def __init__(self, data_file, salary_cap=50000, captain_multiplier=1.5):
        """
        Initialize the NBA/WNBA Showdown Captain lineup optimizer.
        
        Args:
            data_file: Path to CSV file containing player data
            salary_cap: Salary cap for lineup (default: 50000)
            captain_multiplier: Points multiplier for captain (default: 1.5, WNBA Showdown format)
        """
        self.data_file = data_file
        self.salary_cap = salary_cap
        self.captain_multiplier = captain_multiplier
        self.players = self._load_player_data()
        
    def _load_player_data(self):
        """
        Load player data from the CSV file.
        
        Returns:
            DataFrame with player information
        """
        try:
            df = pd.read_csv(self.data_file)
            
            # Make sure required columns exist
            required_cols = ['Name', 'Salary', 'TeamAbbrev', 'AvgPointsPerGame']
            
            # Check if we have Name or Name + ID
            if 'Name + ID' in df.columns and 'Name' not in df.columns:
                # Extract name from "Name + ID" format
                df['Name'] = df['Name + ID'].apply(lambda x: x.split('(')[0].strip())
            
            # Check for missing columns
            missing = [col for col in required_cols if col not in df.columns]
            if missing:
                print(f"Warning: Missing columns in data file: {missing}")
                # Try to map common alternative column names
                col_mapping = {
                    'Roster Position': 'Position',
                    'TeamAbbrev': 'Team',
                    'AvgPointsPerGame': 'FPPG'
                }
                for req_col, alt_col in col_mapping.items():
                    if req_col in missing and alt_col in df.columns:
                        df[req_col] = df[alt_col]
            
            # Add player index for tracking
            df['PlayerIndex'] = range(len(df))
            
            print(f"Loaded {len(df)} players from {self.data_file}")
            return df
            
        except Exception as e:
            print(f"Error loading player data: {str(e)}")
            return pd.DataFrame()
    
    def _extract_opponent(self, game_info, team):
        """
        Extract opponent from game information.
        
        Args:
            game_info: String in format "TEAM1@TEAM2"
            team: Current player's team
            
        Returns:
            Opponent team abbreviation
        """
        try:
            if not isinstance(game_info, str) or '@' not in game_info:
                return "Unknown"
                
            teams = game_info.split('@')
            if teams[0] == team:
                return teams[1]
            else:
                return teams[0]
        except:
            return "Unknown"
    
    def optimize(self, num_lineups=1, player_diversity=3, exposure_constraints=None):
        """
        Optimize WNBA Showdown lineups.
        
        Args:
            num_lineups: Number of lineups to generate
            player_diversity: Minimum player differences between lineups
            exposure_constraints: Dict of {player_name: max_exposure} where max_exposure is 0-1
            
        Returns:
            List of optimized lineups
        """
        if not self._validate_data():
            return []
            
        all_lineups = []
        previous_lineups = []
        
        for i in range(num_lineups):
            print(f"\nGenerating lineup {i+1} of {num_lineups}")
            
            # Create optimization model
            prob = LpProblem(f"NBA_WNBA_ShowdownCaptain_Lineup_{i+1}", LpMaximize)
            
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
            
            # Objective function: maximize projected points
            prob += lpSum([
                # Captain points (1.5x multiplier)
                captain_vars[i] * self.players.iloc[i]['AvgPointsPerGame'] * self.captain_multiplier +
                # Utility points (normal)
                utility_vars[i] * self.players.iloc[i]['AvgPointsPerGame']
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
            
            # Constraint 5: Player diversity from previous lineups
            for j, prev_lineup in enumerate(previous_lineups):
                prob += lpSum([
                    captain_vars[i] + utility_vars[i]
                    for i in range(len(self.players))
                    if self.players.iloc[i]['Name'] in prev_lineup['player_names']
                ]) <= (6 - player_diversity), f"Diversity_From_Lineup_{j}_Iteration_{i}"
            
            # Constraint 6: Apply exposure constraints
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
                    'player_names': []
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
                
                all_lineups.append(lineup)
                previous_lineups.append(lineup)
                
                print(f"Lineup {i+1} optimization complete:")
                print(f"Captain: {lineup['captain']['Name']} ({lineup['captain']['TeamAbbrev']})")
                print("Utility players:")
                for util in lineup['utilities']:
                    print(f"- {util['Name']} ({util['TeamAbbrev']})")
                print(f"Total salary: ${lineup['total_salary']}")
                print(f"Projected points: {lineup['total_projected_points']:.2f}")
            else:
                print(f"Could not find optimal solution for lineup {i+1}")
        
        return all_lineups
    
    def _validate_data(self):
        """Validate that we have enough player data to create valid lineups."""
        if len(self.players) < 6:
            print("Error: Not enough players to create a valid lineup (need at least 6)")
            return False
        return True
    
    def save_lineups_to_csv(self, lineups, output_file=None):
        """
        Save optimized lineups to a CSV file in DraftKings submission format.
        
        Args:
            lineups: List of lineup dictionaries
            output_file: Path to output file (default: generate timestamped file)
        """
        if not lineups:
            print("No lineups to save")
            return
            
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Outputs")
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f"lineup_{timestamp}.csv")
        
        try:
            with open(output_file, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Write header for WNBA Showdown positions: 1 Captain + 5 Utilities
                writer.writerow(['CPT', 'UTIL', 'UTIL', 'UTIL', 'UTIL', 'UTIL'])
                
                # Write lineup data - each row is one complete lineup
                for lineup in lineups:
                    if 'captain' in lineup and 'utilities' in lineup:
                        # Create lineup row with player IDs
                        lineup_row = []
                        
                        # Add captain ID
                        lineup_row.append(lineup['captain']['ID'])
                        
                        # Add utility player IDs
                        for player in lineup['utilities']:
                            lineup_row.append(player['ID'])
                        
                        # Ensure we have exactly 6 players (1 CPT + 5 UTIL)
                        while len(lineup_row) < 6:
                            lineup_row.append('')  # Add empty if missing players
                        
                        writer.writerow(lineup_row[:6])  # Only take first 6 players
            
            print(f"Lineups saved to {output_file}")
            
            # Also save detailed lineups in a separate format for analysis
            summary_file = output_file.replace('lineup_', 'optimized_lineups_')
            with open(summary_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Lineup', 'Position', 'Name', 'Team', 'Opponent', 'Salary', 'Avg Points', 'Projected Points'])
                
                # Write detailed player data
                for i, lineup in enumerate(lineups, 1):
                    # Captain first
                    writer.writerow([
                        i,
                        'CPT',
                        lineup['captain']['Name'],
                        lineup['captain']['TeamAbbrev'],
                        lineup['captain']['opponent'],
                        lineup['captain']['Salary'] * 1.5,  # Captain costs 1.5x
                        lineup['captain']['AvgPointsPerGame'],
                        lineup['captain']['projected_points']
                    ])
                    
                    # Then utilities
                    for player in lineup['utilities']:
                        writer.writerow([
                            i,
                            'UTIL',
                            player['Name'],
                            player['TeamAbbrev'],
                            player['opponent'],
                            player['Salary'],
                            player['AvgPointsPerGame'],
                            player['projected_points']
                        ])
            
            print(f"Detailed lineups saved to {summary_file}")
            
        except Exception as e:
            print(f"Error saving lineups: {e}")
            raise
                    
            print(f"Summary saved to {summary_file}")
                
        except Exception as e:
            print(f"Error saving lineups to CSV: {str(e)}")

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
    
    # Create optimizer and generate lineups
    optimizer = WNBAShowdownOptimizer(data_file)
    lineups = optimizer.optimize(num_lineups=num_lineups, player_diversity=2)
    
    # Save lineups to CSV
    if lineups:
        optimizer.save_lineups_to_csv(lineups)
