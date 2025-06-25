#!/usr/bin/env python3
"""
Daily Fantasy Baseball Lineup Optimizer

This script optimizes lineups for Daily Fantasy Baseball contests using linear programming.
It selects the highest-scoring possible lineup while respecting position requirements and
salary constraints.
"""

import os
import csv
import pandas as pd
import pulp as plp
from typing import List, Dict, Tuple


class LineupOptimizer:
    """Class to handle the optimization of Daily Fantasy Baseball lineups."""

    def __init__(self, csv_path: str, salary_cap: int = 50000):
        """
        Initialize the lineup optimizer with player data and constraints.
        
        Args:
            csv_path: Path to the CSV file containing player data
            salary_cap: Maximum salary allowed for the roster (default: $50,000)
        """
        self.salary_cap = salary_cap
        self.players_df = self._load_data(csv_path)
        self.required_positions = {
            'P': 2,
            'C': 1,
            '1B': 1,
            '2B': 1,
            '3B': 1,
            'SS': 1,
            'OF': 3
        }

    def _load_data(self, csv_path: str) -> pd.DataFrame:
        """
        Load player data from CSV file.
        
        Args:
            csv_path: Path to the CSV file
            
        Returns:
            DataFrame containing player information
        """
        df = pd.read_csv(csv_path)
        # Ensure we use the Roster Position for our optimization
        # and that the data types are correct
        df['Salary'] = df['Salary'].astype(int)
        df['AvgPointsPerGame'] = df['AvgPointsPerGame'].astype(float)
        return df

    def optimize(self, num_lineups: int = 10) -> List[Dict]:
        """
        Generate optimized lineups.
        
        Args:
            num_lineups: Number of different lineups to generate
            
        Returns:
            List of dictionaries, each containing a lineup with player details
        """
        lineups = []
        
        # Create a list to store previously used player combinations
        previous_lineups_players = []
        
        for i in range(num_lineups):
            # Create a new linear programming problem
            prob = plp.LpProblem(f"DFS_Lineup_{i+1}", plp.LpMaximize)
            
            # Create a binary variable for each player
            player_vars = {row['ID']: plp.LpVariable(f"player_{row['ID']}", cat='Binary') 
                           for _, row in self.players_df.iterrows()}
            
            # Objective function: Maximize total average points
            prob += plp.lpSum(row['AvgPointsPerGame'] * player_vars[row['ID']] 
                             for _, row in self.players_df.iterrows())
            
            # Constraint 1: Salary cap
            prob += plp.lpSum(row['Salary'] * player_vars[row['ID']] 
                             for _, row in self.players_df.iterrows()) <= self.salary_cap
            
            # Constraint 2: Position requirements
            for position, count in self.required_positions.items():
                prob += plp.lpSum(player_vars[row['ID']] 
                                 for _, row in self.players_df.iterrows() 
                                 if row['Roster Position'] == position) == count
            
            # Constraint 3: Exactly 10 players in total
            prob += plp.lpSum(player_vars.values()) == sum(self.required_positions.values())
            
            # Constraint 4: Ensure uniqueness from previous lineups
            for prev_lineup in previous_lineups_players:
                # Add constraint that the new lineup must differ from each previous lineup by at least 3 players
                prob += plp.lpSum(player_vars[player_id] for player_id in prev_lineup) <= len(prev_lineup) - 3
            
            # Solve the problem
            prob.solve(plp.PULP_CBC_CMD(msg=False))
            
            # Check if a solution was found
            if plp.LpStatus[prob.status] != 'Optimal':
                print(f"Could not find optimal solution for lineup {i+1}")
                continue
                
            # Extract the selected players
            selected_player_ids = [int(p_id) for p_id, var in player_vars.items() 
                                 if plp.value(var) == 1]
            previous_lineups_players.append(selected_player_ids)
            
            # Create lineup data
            lineup_data = {
                'players': [],
                'total_salary': 0,
                'total_points': 0
            }
            
            for player_id in selected_player_ids:
                player = self.players_df[self.players_df['ID'] == player_id].iloc[0]
                lineup_data['players'].append({
                    'id': player['ID'],
                    'name': player['Name'],
                    'position': player['Roster Position'],
                    'team': player['TeamAbbrev'],
                    'opponent': self._extract_opponent(player['Game Info'], player['TeamAbbrev']),
                    'salary': player['Salary'],
                    'avg_points': player['AvgPointsPerGame']
                })
                lineup_data['total_salary'] += player['Salary']
                lineup_data['total_points'] += player['AvgPointsPerGame']
            
            # Sort players by position in the required order
            position_order = {'P': 0, 'C': 1, '1B': 2, '2B': 3, '3B': 4, 'SS': 5, 'OF': 6}
            lineup_data['players'].sort(key=lambda x: (position_order[x['position']], -x['avg_points']))
            
            lineups.append(lineup_data)
        
        # Sort lineups by total points in descending order
        lineups.sort(key=lambda x: x['total_points'], reverse=True)
        return lineups

    def _extract_opponent(self, game_info: str, team: str) -> str:
        """
        Extract opponent team from game information.
        
        Args:
            game_info: String containing game details (e.g. "PHI@HOU 06/25/2025 08:10PM ET")
            team: Team abbreviation for the player
            
        Returns:
            Opponent team abbreviation
        """
        if '@' not in game_info:
            return "Unknown"
        
        teams = game_info.split(' ')[0].split('@')
        return teams[1] if teams[0] == team else teams[0]
    
    def display_lineups(self, lineups: List[Dict]) -> None:
        """
        Display the optimized lineups in a readable format.
        
        Args:
            lineups: List of lineup dictionaries
        """
        for i, lineup in enumerate(lineups, 1):
            print(f"\n{'='*60}")
            print(f"LINEUP #{i} - Total Points: {lineup['total_points']:.2f} - Total Salary: ${lineup['total_salary']}")
            print(f"{'-'*60}")
            print(f"{'POS':<5}{'NAME':<30}{'TEAM':<6}{'OPP':<6}{'SALARY':<10}{'POINTS':<10}")
            print(f"{'-'*60}")
            
            for player in lineup['players']:
                print(f"{player['position']:<5}{player['name']:<30}{player['team']:<6}"
                      f"{player['opponent']:<6}${player['salary']:<9}{player['avg_points']:<10.2f}")
            print(f"{'='*60}")

    def save_lineup_to_csv(self, lineups: List[Dict], output_file: str = "lineup.csv") -> None:
        """
        Save the optimized lineup to a CSV file in position-based format.
        One row per lineup with player IDs in a comma-separated format.
        
        Args:
            lineups: List of lineup dictionaries
            output_file: Path to the output CSV file
        """
        if not lineups:
            print("No lineups to save.")
            return
        
        # Handle special case when output_file is already a full path with directory
        if os.path.dirname(output_file) and os.path.exists(os.path.dirname(output_file)):
            output_path = output_file
        else:
            # Ensure the Outputs directory exists
            output_dir = os.path.join(os.getcwd(), "Outputs")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Generate timestamp for unique filenames if not already in the filename
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create output path - if a filename is provided, use it with timestamp
            base_name = os.path.basename(output_file)
            name_parts = os.path.splitext(base_name)
            # Only add timestamp if not already included in the filename
            if timestamp not in base_name:
                timestamped_name = f"{name_parts[0]}_{timestamp}{name_parts[1]}"
                output_path = os.path.join(output_dir, timestamped_name)
            else:
                output_path = os.path.join(output_dir, base_name)
        
        # Define the positions in the order they should appear in the CSV
        positions = ['P', 'P', 'C', '1B', '2B', '3B', 'SS', 'OF', 'OF', 'OF']
        
        with open(output_path, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            
            # Write the header row
            csvwriter.writerow(positions)
            
            # Process each lineup
            for lineup in lineups:
                # Create a dictionary to organize players by position
                players_by_position = {pos: [] for pos in positions}
                
                # Sort players into their positions
                for player in lineup['players']:
                    pos = player['position']
                    if pos in players_by_position:
                        # Get player ID (already stored in player data)
                        player_data = {
                            'id': player['id'],
                            'avg_points': player['avg_points']
                        }
                        players_by_position[pos].append(player_data)
                
                # Sort players by average points within each position
                for pos in players_by_position:
                    if len(players_by_position[pos]) > 0:
                        players_by_position[pos].sort(key=lambda x: x['avg_points'], reverse=True)
                
                # Build the roster row with IDs in the correct position order
                roster_row = []
                for pos in positions:
                    if players_by_position[pos] and len(players_by_position[pos]) > 0:
                        # Take the highest-scoring player for this position
                        roster_row.append(str(players_by_position[pos].pop(0)['id']))
                    else:
                        # If no player found for this position (shouldn't happen in a valid lineup)
                        roster_row.append('')
                
                # Write the roster row
                csvwriter.writerow(roster_row)
        
        print(f"\nLineups saved to {output_path} in position-based format")


def main():
    """Main function to run the optimization process."""
    # First look for the CSV in the downloads directory
    user_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
    csv_filename = "DKSalaries (34).csv"
    
    # Check in common locations for the CSV file
    possible_paths = [
        os.path.join(user_downloads, csv_filename),  # User's Downloads folder
        os.path.join(os.getcwd(), csv_filename),     # Current working directory
        csv_filename                                 # Just the filename (if in current directory)
    ]
    
    csv_path = None
    for path in possible_paths:
        if os.path.exists(path):
            csv_path = path
            break
    
    if not csv_path:
        csv_path = input("Please enter the full path to the DKSalaries CSV file: ")
        if not os.path.exists(csv_path):
            print(f"Error: Could not find CSV file at {csv_path}")
            return
    
    try:
        # Create optimizer and generate lineups
        optimizer = LineupOptimizer(csv_path)
        num_lineups = 10  # Default number of lineups to generate
        
        # Check if user wants to customize parameters
        customize = input("Do you want to customize optimization parameters? (y/n): ").lower()
        if customize == 'y':
            salary_cap = int(input("Enter salary cap (default 50000): ") or 50000)
            num_lineups = int(input("Enter number of lineups to generate (default 10): ") or 10)
            optimizer.salary_cap = salary_cap
        
        lineups = optimizer.optimize(num_lineups)
        
        # Display the results
        optimizer.display_lineups(lineups)
        
        # Optionally save results to a CSV file
        save_to_csv = input("\nDo you want to save these lineups to CSV files? (y/n): ").lower()
        if save_to_csv == 'y':
            # Save detailed output
            output_file = input("Enter filename for detailed output (default: optimized_lineups.csv): ") or "optimized_lineups.csv"
            
            # Ensure the Outputs directory exists
            output_dir = os.path.join(os.getcwd(), "Outputs")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Generate timestamp for unique filenames
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create output path with timestamp
            base_name = os.path.basename(output_file)
            name_parts = os.path.splitext(base_name)
            timestamped_name = f"{name_parts[0]}_{timestamp}{name_parts[1]}"
            output_path = os.path.join(output_dir, timestamped_name)
            
            with open(output_path, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(['Lineup', 'Position', 'Name', 'Team', 'Opponent', 'Salary', 'Avg Points'])
                
                for i, lineup in enumerate(lineups, 1):
                    for player in lineup['players']:
                        csvwriter.writerow([
                            i, 
                            player['position'], 
                            player['name'], 
                            player['team'],
                            player['opponent'],
                            player['salary'], 
                            player['avg_points']
                        ])
            
            # Also save to the standard filename in the base directory for compatibility
            with open(output_file, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(['Lineup', 'Position', 'Name', 'Team', 'Opponent', 'Salary', 'Avg Points'])
                
                for i, lineup in enumerate(lineups, 1):
                    for player in lineup['players']:
                        csvwriter.writerow([
                            i, 
                            player['position'], 
                            player['name'], 
                            player['team'],
                            player['opponent'],
                            player['salary'], 
                            player['avg_points']
                        ])
            
            print(f"\nDetailed lineups saved to {output_path}")
            
            # Save lineup in position-based format (roster format)
            lineup_file = input(f"Enter filename for position-based roster format (default: lineup.csv): ") or "lineup.csv"
            num_lineups_to_save = int(input(f"How many lineups to save in roster format? (1-{len(lineups)}, default: {len(lineups)}): ") or len(lineups))
            num_lineups_to_save = min(num_lineups_to_save, len(lineups))
            optimizer.save_lineup_to_csv(lineups[:num_lineups_to_save], lineup_file)
            
    except Exception as e:
        print(f"Error during optimization: {e}")


if __name__ == "__main__":
    main()
