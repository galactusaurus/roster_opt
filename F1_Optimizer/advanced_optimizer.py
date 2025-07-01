#!/usr/bin/env python3
"""
Advanced Daily Fantasy Formula 1 Lineup Optimizer

This script provides enhanced optimization for Daily Fantasy Formula 1 contests using linear programming.
It supports advanced features like team stacking, player correlation, and multiple lineup generation
with customizable diversity.
"""

import os
import csv
import pandas as pd
import pulp as plp
from typing import List, Dict, Tuple, Set, Optional
from collections import defaultdict
import argparse
from datetime import datetime


class AdvancedLineupOptimizer:
    """Advanced class for optimizing Daily Fantasy Formula 1 lineups with additional features."""

    def __init__(
        self, 
        csv_path: str, 
        salary_cap: int = 50000,
        max_from_team: int = 3,
        min_teams: int = 2,
        max_player_appearances: int = 1
    ):
        """
        Initialize the lineup optimizer with driver/constructor data and constraints.
        
        Args:
            csv_path: Path to the CSV file containing player data
            salary_cap: Maximum salary allowed for the roster (default: $50,000)
            max_from_team: Maximum number of drivers allowed from a single team
            min_teams: Minimum number of different teams that must be represented in a lineup
        """
        self.salary_cap = salary_cap
        self.max_from_team = max_from_team
        self.min_teams = min_teams
        self.players_df = self._load_data(csv_path)
        self.teams = self.players_df['TeamAbbrev'].unique().tolist()
        self.max_player_appearances = max_player_appearances
        
        # Required positions for a valid lineup
        self.required_positions = {
            'CPT': 1,  # Captain (1.5x points)
            'D': 4,    # Drivers
            'CNSTR': 1 # Constructor
        }

    def _load_data(self, csv_path: str) -> pd.DataFrame:
        """
        Load driver/constructor data from CSV file.
        
        Args:
            csv_path: Path to the CSV file
            
        Returns:
            DataFrame containing player information
        """
        df = pd.read_csv(csv_path)
        # Ensure we use the correct data types
        df['Salary'] = df['Salary'].astype(int)
        df['AvgPointsPerGame'] = df['AvgPointsPerGame'].astype(float)
        
        # Calculate Captain points (1.5x the regular points)
        df['CaptainPoints'] = df['AvgPointsPerGame'] * 1.5
        
        # Add a unique ID column if needed
        if 'ID' not in df.columns:
            df['ID'] = df.index
            
        return df

    def optimize(
        self, 
        num_lineups: int = 10, 
        stack_team: Optional[str] = None,
        stack_count: int = 2,
        min_salary_used: float = 0.95,
        lineup_diversity: int = 2,
        max_player_appearances: Optional[int] = None
    ) -> List[Dict]:
        """
        Generate optimized lineups with advanced constraints.
        
        Args:
            num_lineups: Number of different lineups to generate
            stack_team: Team abbreviation to stack (if desired)
            stack_count: Number of drivers to include from stacked team
            min_salary_used: Minimum fraction of salary cap that must be used
            lineup_diversity: Minimum number of different players between lineups
            max_player_appearances: Maximum number of times a player can appear across all lineups
            
        Returns:
            List of dictionaries, each containing a lineup with player details
        """
        lineups = []
        previous_lineups_players = []
        
        # Keep track of how many times each player appears across lineups
        player_appearances = {player_id: 0 for player_id in self.players_df['ID'].values}
        
        for i in range(num_lineups):
            # Create a new linear programming problem
            prob = plp.LpProblem(f"DFS_Lineup_{i+1}", plp.LpMaximize)
            
            # Create a binary variable for each player
            player_vars = {row['ID']: plp.LpVariable(f"player_{row['ID']}", cat='Binary') 
                           for _, row in self.players_df.iterrows()}
            
            # Create binary variables for each team (1 if any driver from that team is selected)
            team_vars = {team: plp.LpVariable(f"team_{team}", cat='Binary') 
                        for team in self.teams}
            
            # Objective function: Maximize total points
            # Note: Captain points are 1.5x
            prob += plp.lpSum(
                row['CaptainPoints'] * player_vars[row['ID']] if row['Roster Position'] == 'CPT' 
                else row['AvgPointsPerGame'] * player_vars[row['ID']]
                for _, row in self.players_df.iterrows()
            )
            
            # Constraint 1: Salary cap
            prob += plp.lpSum(row['Salary'] * player_vars[row['ID']] 
                             for _, row in self.players_df.iterrows()) <= self.salary_cap
            
            # Constraint 2: Minimum salary used
            prob += plp.lpSum(row['Salary'] * player_vars[row['ID']] 
                             for _, row in self.players_df.iterrows()) >= self.salary_cap * min_salary_used
            
            # Constraint 3: Position requirements
            for position, count in self.required_positions.items():
                prob += plp.lpSum(player_vars[row['ID']] 
                                 for _, row in self.players_df.iterrows() 
                                 if row['Roster Position'] == position) == count
            
            # Constraint 4: Total number of roster spots
            prob += plp.lpSum(player_vars.values()) == sum(self.required_positions.values())
            
            # Constraint 5: Team constraints (connect player_vars to team_vars)
            for team in self.teams:
                # If any driver from this team is selected, team_var must be 1
                team_players = self.players_df[(self.players_df['TeamAbbrev'] == team) & 
                                             (self.players_df['Roster Position'] != 'CNSTR')]
                
                if not team_players.empty:  # Only add constraints if there are drivers for this team
                    for _, player in team_players.iterrows():
                        prob += player_vars[player['ID']] <= team_vars[team]
                    
                    # If no drivers from this team are selected, team_var must be 0
                    prob += plp.lpSum(player_vars[player['ID']] for _, player in team_players.iterrows()) >= team_vars[team]
            
            # Constraint 6: Maximum drivers from one team
            for team in self.teams:
                team_players = self.players_df[(self.players_df['TeamAbbrev'] == team) & 
                                             (self.players_df['Roster Position'] != 'CNSTR')]
                
                if not team_players.empty:  # Only add constraints if there are drivers for this team
                    prob += plp.lpSum(player_vars[player['ID']] for _, player in team_players.iterrows()) <= self.max_from_team
            
            # Constraint 7: Minimum teams represented
            prob += plp.lpSum(team_vars.values()) >= self.min_teams
            
            # Constraint 8: Team stacking if requested
            if stack_team and stack_team in self.teams:
                stack_team_players = self.players_df[(self.players_df['TeamAbbrev'] == stack_team) & 
                                                  (self.players_df['Roster Position'] != 'CNSTR')]
                
                if not stack_team_players.empty:  # Only add constraints if there are drivers for this team
                    prob += plp.lpSum(player_vars[player['ID']] for _, player in stack_team_players.iterrows()) >= min(stack_count, len(stack_team_players))
            
            # Constraint 9: Can't pick both captain and regular versions of same driver
            driver_names = self.players_df[self.players_df['Roster Position'] != 'CNSTR']['Name'].unique()
            
            for driver_name in driver_names:
                # Get IDs for both versions of this driver (CPT and D)
                driver_ids = self.players_df[self.players_df['Name'] == driver_name]['ID'].tolist()
                
                if len(driver_ids) > 1:  # If driver has both CPT and regular version
                    # Constraint: Can only choose at most one version of this driver
                    prob += plp.lpSum(player_vars[id] for id in driver_ids) <= 1
            
            # Constraint 10: Limit on player appearances across lineups
            if max_player_appearances is not None:
                excluded_count = 0
                for player_id, appearances in player_appearances.items():
                    if appearances >= max_player_appearances:
                        # If player has reached maximum allowed appearances, exclude them from this lineup
                        prob += player_vars[player_id] == 0
                        excluded_count += 1
                
                if excluded_count > 0 and i > 0:  # Only print for second lineup onwards
                    print(f"Lineup {i+1}: Excluded {excluded_count} drivers/constructors who reached the max appearance limit of {max_player_appearances}")
                        
            # Constraint 11: Ensure uniqueness from previous lineups
            for prev_lineup in previous_lineups_players:
                # New lineup must differ from each previous lineup by at least lineup_diversity players
                prob += plp.lpSum(player_vars[player_id] for player_id in prev_lineup) <= len(prev_lineup) - lineup_diversity
            
            # Solve the problem
            prob.solve(plp.PULP_CBC_CMD(msg=False))
            
            # Check if a solution was found
            if plp.LpStatus[prob.status] != 'Optimal':
                print(f"Could not find optimal solution for lineup {i+1}")
                if i == 0:  # First lineup must be successful
                    return []
                break
                
            # Extract the selected players
            selected_player_ids = [int(p_id) for p_id, var in player_vars.items() 
                                 if plp.value(var) == 1]
            previous_lineups_players.append(selected_player_ids)
            
            # Update player appearance counts
            for player_id in selected_player_ids:
                player_appearances[player_id] += 1
            
            # Create lineup data
            lineup_data = {
                'players': [],
                'total_salary': 0,
                'total_points': 0,
                'teams_used': set()
            }
            
            for player_id in selected_player_ids:
                player = self.players_df[self.players_df['ID'] == player_id].iloc[0]
                
                # Calculate points based on position
                points = player['CaptainPoints'] if player['Roster Position'] == 'CPT' else player['AvgPointsPerGame']
                
                lineup_data['players'].append({
                    'id': player['ID'],
                    'name': player['Name'],
                    'position': player['Roster Position'],
                    'team': player['TeamAbbrev'],
                    'salary': player['Salary'],
                    'avg_points': player['AvgPointsPerGame'],  # Base points
                    'points': points,  # Calculated points (with captain multiplier if applicable)
                    'game_info': player['Game Info']
                })
                
                lineup_data['total_salary'] += player['Salary']
                lineup_data['total_points'] += points
                
                # Add team to teams_used if it's a driver (not a constructor)
                if player['Roster Position'] != 'CNSTR':
                    lineup_data['teams_used'].add(player['TeamAbbrev'])
            
            # Sort players by position in the required order (CPT first, then D, then CNSTR)
            position_order = {'CPT': 0, 'D': 1, 'CNSTR': 2}
            lineup_data['players'].sort(key=lambda x: (position_order[x['position']], -x['points']))
            
            lineups.append(lineup_data)
        
        # Sort lineups by total points in descending order
        lineups.sort(key=lambda x: x['total_points'], reverse=True)
        return lineups

    def display_lineups(self, lineups: List[Dict]) -> None:
        """
        Display the optimized lineups in a readable format.
        
        Args:
            lineups: List of lineup dictionaries
        """
        for i, lineup in enumerate(lineups, 1):
            print(f"\n{'='*80}")
            print(f"LINEUP #{i} - Total Points: {lineup['total_points']:.2f} - "
                  f"Total Salary: ${lineup['total_salary']} - "
                  f"Teams Used: {len(lineup['teams_used'])}")
            print(f"{'-'*80}")
            print(f"{'POS':<6}{'NAME':<30}{'TEAM':<8}{'SALARY':<10}{'POINTS':<10}{'GAME INFO':<20}")
            print(f"{'-'*80}")
            
            # Group players by team to see stacks
            team_counts = defaultdict(int)
            for player in lineup['players']:
                if player['position'] != 'CNSTR':  # Only count drivers, not constructors
                    team_counts[player['team']] += 1
            
            for player in lineup['players']:
                # Highlight teams with multiple drivers
                team_indicator = f"{player['team']}*" if team_counts[player['team']] > 1 and player['position'] != 'CNSTR' else player['team']
                print(f"{player['position']:<6}{player['name']:<30}{team_indicator:<8}"
                      f"${player['salary']:<9}{player['points']:<10.2f}"
                      f"{player['game_info']:<20}")
            
            print(f"{'='*80}")
            
    def save_lineups_to_csv(self, lineups: List[Dict], output_file: str = "optimized_lineups.csv") -> None:
        """
        Save the optimized lineups to a CSV file.
        
        Args:
            lineups: List of lineup dictionaries
            output_file: Path to the output CSV file
        """
        # Handle special case when output_file is already a full path with directory
        if os.path.dirname(output_file) and os.path.exists(os.path.dirname(output_file)):
            output_path = output_file
        else:
            # Ensure the Outputs directory exists
            output_dir = os.path.join(os.getcwd(), "Outputs")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Generate timestamp for unique filenames if not already in the filename
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
        
        with open(output_path, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['Lineup', 'Position', 'Name', 'Team', 'Salary', 'Avg Points', 'Game Info'])
            
            for i, lineup in enumerate(lineups, 1):
                for player in lineup['players']:
                    csvwriter.writerow([
                        i, 
                        player['position'], 
                        player['name'], 
                        player['team'],
                        player['salary'], 
                        player['points'],  # Use calculated points for CSV output
                        player['game_info']
                    ])
        
        print(f"\nLineups saved to {output_path}")
        
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
        positions = ['CPT', 'D', 'D', 'D', 'D', 'CNSTR']
        
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
                        # Get player ID
                        player_data = {
                            'id': player['id'],
                            'points': player['points']  # Use calculated points
                        }
                        players_by_position[pos].append(player_data)
                
                # Sort players by average points within each position
                for pos in players_by_position:
                    if len(players_by_position[pos]) > 0:
                        players_by_position[pos].sort(key=lambda x: x['points'], reverse=True)
                
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
    
    def summarize_player_usage(self, lineups: List[Dict], max_player_appearances: Optional[int] = None) -> None:
        """
        Print a summary of how many times each driver/constructor appears across all lineups.
        
        Args:
            lineups: List of lineup dictionaries
            max_player_appearances: The maximum allowed appearances, if any
        """
        if not lineups:
            return
            
        # Count appearances for each player
        player_usage = defaultdict(int)
        player_ids = {}  # To map names to IDs
        
        for lineup in lineups:
            for player in lineup['players']:
                player_id = player['id']
                player_name = player['name']
                player_usage[player_name] += 1
                player_ids[player_name] = player_id
                
        # Print summary
        print(f"\n{'='*80}")
        print(f"DRIVER/CONSTRUCTOR USAGE SUMMARY (Total lineups: {len(lineups)})")
        print(f"{'-'*80}")
        print(f"{'NAME':<30}{'POSITION':<10}{'APPEARANCES':<15}{'% OF LINEUPS':<15}")
        print(f"{'-'*80}")
        
        # Get position for each player
        player_positions = {}
        for lineup in lineups:
            for player in lineup['players']:
                player_positions[player['name']] = player['position']
        
        # Sort players by number of appearances (descending)
        sorted_players = sorted(player_usage.items(), key=lambda x: x[1], reverse=True)
        
        for player_name, count in sorted_players:
            position = player_positions.get(player_name, "")
            percentage = (count / len(lineups)) * 100
            
            # Highlight players at the appearance limit
            if max_player_appearances and count >= max_player_appearances:
                print(f"{player_name:<30}{position:<10}{count:<15}{percentage:.1f}% **MAX**")
            else:
                print(f"{player_name:<30}{position:<10}{count:<15}{percentage:.1f}%")
                
        print(f"{'='*80}")

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Optimize Daily Fantasy Formula 1 lineups')
    
    parser.add_argument('--csv', type=str, help='Path to the CSV file with driver/constructor data')
    parser.add_argument('--salary-cap', type=int, default=50000, 
                        help='Salary cap for the lineup (default: 50000)')
    parser.add_argument('--num-lineups', type=int, default=10, 
                        help='Number of lineups to generate (default: 10)')
    parser.add_argument('--stack-team', type=str, 
                        help='Team abbreviation to stack (e.g., MCL, RB)')
    parser.add_argument('--stack-count', type=int, default=2, 
                        help='Number of drivers to include from stacked team (default: 2)')
    parser.add_argument('--max-from-team', type=int, default=3, 
                        help='Maximum drivers from a single team (default: 3)')
    parser.add_argument('--min-teams', type=int, default=2, 
                        help='Minimum number of teams in a lineup (default: 2)')
    parser.add_argument('--min-salary-used', type=float, default=0.95, 
                        help='Minimum fraction of salary cap to use (default: 0.95)')
    parser.add_argument('--lineup-diversity', type=int, default=2, 
                        help='Minimum number of different players between lineups (default: 2)')
    parser.add_argument('--max-player-appearances', type=int, 
                        help='Maximum number of times a player can appear across all lineups')
    parser.add_argument('--output', type=str, default='optimized_lineups.csv', 
                        help='Output CSV file name (default: optimized_lineups.csv)')
    
    return parser.parse_args()


def find_csv_path(file_pattern="DKSalaries*.csv"):
    """
    Find the path to a CSV file matching the given pattern.
    
    Args:
        file_pattern: A glob pattern to match files (default: DKSalaries*.csv)
        
    Returns:
        The path to the first matching file, or None if not found
    """
    # First look in the downloads directory
    user_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
    
    # Then look in the current directory
    current_dir = os.getcwd()
    
    # Create a list of directories to search
    search_dirs = [current_dir, user_downloads]
    
    # Loop through each directory
    for directory in search_dirs:
        if os.path.exists(directory):
            # Get all files matching the pattern
            import glob
            matching_files = glob.glob(os.path.join(directory, file_pattern))
            
            # Sort by modification time (newest first)
            matching_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            if matching_files:
                return matching_files[0]  # Return the most recent file
    
    return None


def main():
    """Main function to run the optimization process."""
    # Parse command-line arguments
    args = parse_args()
    
    # Find CSV path if not provided
    csv_path = args.csv
    if not csv_path:
        csv_path = find_csv_path()
        
    if not csv_path:
        csv_path = input("Please enter the full path to the DKSalaries CSV file: ")
        
    if not os.path.exists(csv_path):
        print(f"Error: Could not find CSV file at {csv_path}")
        return
    
    try:
        # Create optimizer with parameters from command line or defaults
        optimizer = AdvancedLineupOptimizer(
            csv_path=csv_path,
            salary_cap=args.salary_cap,
            max_from_team=args.max_from_team,
            min_teams=args.min_teams
        )
        
        # Check if running interactively or from command line
        if __name__ == "__main__" and len(os.sys.argv) <= 1:
            # Running interactively, ask for customization
            customize = input("Do you want to customize optimization parameters? (y/n): ").lower()
            if customize == 'y':
                args.salary_cap = int(input(f"Enter salary cap (default {args.salary_cap}): ") or args.salary_cap)
                args.num_lineups = int(input(f"Enter number of lineups to generate (default {args.num_lineups}): ") or args.num_lineups)
                args.stack_team = input("Enter team to stack (leave blank for no stacking): ") or args.stack_team
                
                if args.stack_team:
                    args.stack_count = int(input(f"Enter number of drivers to stack (default {args.stack_count}): ") or args.stack_count)
                
                args.max_from_team = int(input(f"Enter maximum drivers from one team (default {args.max_from_team}): ") or args.max_from_team)
                args.min_teams = int(input(f"Enter minimum number of teams (default {args.min_teams}): ") or args.min_teams)
                
                # Ask about max player appearances
                max_appearances_input = input(f"Enter maximum times a player can appear across all lineups (leave blank for no limit): ")
                if max_appearances_input:
                    args.max_player_appearances = int(max_appearances_input)
                
                # Update optimizer with new parameters
                optimizer.salary_cap = args.salary_cap
                optimizer.max_from_team = args.max_from_team
                optimizer.min_teams = args.min_teams
        
        # Generate lineups
        lineups = optimizer.optimize(
            num_lineups=args.num_lineups,
            stack_team=args.stack_team,
            stack_count=args.stack_count,
            min_salary_used=args.min_salary_used,
            lineup_diversity=args.lineup_diversity,
            max_player_appearances=args.max_player_appearances
        )
        
        if not lineups:
            print("Failed to generate any valid lineups with the given constraints.")
            return
        
        # Display the results
        optimizer.display_lineups(lineups)
        
        # If max player appearances was set, display the player usage summary
        if args.max_player_appearances:
            optimizer.summarize_player_usage(lineups, args.max_player_appearances)
        
        # Save results to CSV
        # Generate timestamp for unique filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Ensure the Outputs directory exists
        output_dir = os.path.join(os.getcwd(), "Outputs")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        if __name__ == "__main__" and len(os.sys.argv) <= 1:
            # When running interactively, ask if user wants to save
            save_to_csv = input("\nDo you want to save these lineups to CSV files? (y/n): ").lower()
            if save_to_csv == 'y':
                # Save detailed output
                output_base = input(f"Enter filename for detailed output (default: optimized_lineups): ") or "optimized_lineups"
                output_file = f"{output_base}_{timestamp}.csv"
                detailed_output = os.path.join(output_dir, output_file)
                optimizer.save_lineups_to_csv(lineups, detailed_output)
                
                # Save the position-based lineup format (roster format)
                lineup_base = input(f"Enter filename for position-based roster format (default: lineup): ") or "lineup"
                lineup_file = f"{lineup_base}_{timestamp}.csv"
                lineup_output = os.path.join(output_dir, lineup_file)
                
                num_lineups_to_save = int(input(f"How many lineups to save in roster format? (1-{len(lineups)}, default: {len(lineups)}): ") or len(lineups))
                num_lineups_to_save = min(num_lineups_to_save, len(lineups))
                optimizer.save_lineup_to_csv(lineups[:num_lineups_to_save], lineup_output)
                
                # Also save to the standard filenames for compatibility
                optimizer.save_lineups_to_csv(lineups, args.output)
                optimizer.save_lineup_to_csv(lineups[:num_lineups_to_save], "lineup.csv")
                
                print(f"\nOutputs saved in folder: {output_dir}")
                print(f"Detailed lineups: {output_file}")
                print(f"Roster format: {lineup_file}")
        else:
            # When running from command line with args, save automatically with timestamp
            # Create output filenames with timestamp
            detailed_output = os.path.join(output_dir, f"optimized_lineups_{timestamp}.csv")
            lineup_output = os.path.join(output_dir, f"lineup_{timestamp}.csv")
            
            # Save both file formats
            optimizer.save_lineups_to_csv(lineups, detailed_output)
            optimizer.save_lineup_to_csv(lineups, lineup_output)
            
            # Also save to the standard filenames for compatibility
            optimizer.save_lineups_to_csv(lineups, args.output)
            optimizer.save_lineup_to_csv(lineups, "lineup.csv")
            
            print(f"\nOutputs saved in folder: {output_dir}")
            print(f"Detailed lineups: {os.path.basename(detailed_output)}")
            print(f"Roster format: {os.path.basename(lineup_output)}")
            
    except Exception as e:
        print(f"Error during optimization: {e}")


if __name__ == "__main__":
    main()
