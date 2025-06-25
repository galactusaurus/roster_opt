#!/usr/bin/env python3
"""
Advanced Daily Fantasy Baseball Lineup Optimizer

This script provides enhanced optimization for Daily Fantasy Baseball contests using linear programming.
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


class AdvancedLineupOptimizer:
    """Advanced class for optimizing Daily Fantasy Baseball lineups with additional features."""

    def __init__(
        self, 
        csv_path: str, 
        salary_cap: int = 50000,
        max_players_from_team: int = 5,
        min_teams: int = 3,
        injured_list_path: Optional[str] = None
    ):
        """
        Initialize the lineup optimizer with player data and constraints.
        
        Args:
            csv_path: Path to the CSV file containing player data
            salary_cap: Maximum salary allowed for the roster (default: $50,000)
            max_players_from_team: Maximum number of players allowed from a single team
            min_teams: Minimum number of different teams that must be represented in a lineup
            injured_list_path: Optional path to CSV file containing injured players
        """
        self.salary_cap = salary_cap
        self.max_players_from_team = max_players_from_team
        self.min_teams = min_teams
        self.players_df = self._load_data(csv_path)
        
        # If injured list is provided, filter out injured players
        if injured_list_path and os.path.exists(injured_list_path):
            self._filter_injured_players(injured_list_path)
            
        self.teams = self.players_df['TeamAbbrev'].unique().tolist()
        
        # Required positions for a valid lineup
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
        # Ensure we use the correct data types
        df['Salary'] = df['Salary'].astype(int)
        df['AvgPointsPerGame'] = df['AvgPointsPerGame'].astype(float)
        
        # Add a unique ID column if needed
        if 'ID' not in df.columns:
            df['ID'] = df.index
            
        return df
    
    def _filter_injured_players(self, injured_list_path: str) -> None:
        """
        Filter out players on the injured list.
        
        Args:
            injured_list_path: Path to the CSV file containing injured players
        """
        try:
            # Load injured players data
            injured_df = pd.read_csv(injured_list_path)
            
            # Create a set of player names that are on the injured list
            injured_players = set(injured_df['Player'].str.strip().tolist())
            initial_player_count = len(self.players_df)
            
            # Check if a player's name is in the injured list
            def is_not_injured(player_name):
                # Handle variations in name formatting
                name = player_name.strip()
                return name not in injured_players
            
            # Filter the players dataframe to exclude injured players
            self.players_df = self.players_df[self.players_df['Name'].apply(is_not_injured)]
            
            filtered_count = initial_player_count - len(self.players_df)
            print(f"Filtered out {filtered_count} injured players from the player pool.")
            
        except Exception as e:
            print(f"Error processing injured list: {str(e)}")
            print("Continuing with all players (no injury filtering)")
        
    def _extract_opponents(self) -> Dict[str, str]:
        """
        Extract all team opponents from game information.
        
        Returns:
            Dictionary mapping teams to their opponents
        """
        opponents = {}
        games = {}
        
        # First, collect all game information
        for _, row in self.players_df.iterrows():
            if '@' in row['Game Info']:
                game_info = row['Game Info'].split(' ')[0]  # Get "TEAM1@TEAM2" part
                team1, team2 = game_info.split('@')
                games[team1] = team2
                games[team2] = team1
                
        return games

    def optimize(
        self, 
        num_lineups: int = 10, 
        stack_team: Optional[str] = None,
        stack_count: int = 4,
        min_salary_used: float = 0.95,
        lineup_diversity: int = 3
    ) -> List[Dict]:
        """
        Generate optimized lineups with advanced constraints.
        
        Args:
            num_lineups: Number of different lineups to generate
            stack_team: Team abbreviation to stack (if desired)
            stack_count: Number of players to include from stacked team
            min_salary_used: Minimum fraction of salary cap that must be used
            lineup_diversity: Minimum number of different players between lineups
            
        Returns:
            List of dictionaries, each containing a lineup with player details
        """
        lineups = []
        opponents_dict = self._extract_opponents()
        previous_lineups_players = []
        
        for i in range(num_lineups):
            # Create a new linear programming problem
            prob = plp.LpProblem(f"DFS_Lineup_{i+1}", plp.LpMaximize)
            
            # Create a binary variable for each player
            player_vars = {row['ID']: plp.LpVariable(f"player_{row['ID']}", cat='Binary') 
                           for _, row in self.players_df.iterrows()}
            
            # Create binary variables for each team (1 if any player from that team is selected)
            team_vars = {team: plp.LpVariable(f"team_{team}", cat='Binary') 
                        for team in self.teams}
            
            # Objective function: Maximize total average points
            prob += plp.lpSum(row['AvgPointsPerGame'] * player_vars[row['ID']] 
                             for _, row in self.players_df.iterrows())
            
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
            
            # Constraint 4: Exactly 10 players in total
            prob += plp.lpSum(player_vars.values()) == sum(self.required_positions.values())
            
            # Constraint 5: Team constraints (connect player_vars to team_vars)
            for team in self.teams:
                # If any player from this team is selected, team_var must be 1
                team_players = self.players_df[self.players_df['TeamAbbrev'] == team]
                for _, player in team_players.iterrows():
                    prob += player_vars[player['ID']] <= team_vars[team]
                
                # If no players from this team are selected, team_var must be 0
                prob += plp.lpSum(player_vars[player['ID']] for _, player in team_players.iterrows()) >= team_vars[team]
            
            # Constraint 6: Maximum players from one team
            for team in self.teams:
                team_players = self.players_df[self.players_df['TeamAbbrev'] == team]
                prob += plp.lpSum(player_vars[player['ID']] for _, player in team_players.iterrows()) <= self.max_players_from_team
            
            # Constraint 7: Minimum teams represented
            prob += plp.lpSum(team_vars.values()) >= self.min_teams
            
            # Constraint 8: Team stacking if requested
            if stack_team and stack_team in self.teams:
                stack_team_players = self.players_df[self.players_df['TeamAbbrev'] == stack_team]
                prob += plp.lpSum(player_vars[player['ID']] for _, player in stack_team_players.iterrows()) >= stack_count
            
            # Constraint 9: Ensure uniqueness from previous lineups
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
            
            # Create lineup data
            lineup_data = {
                'players': [],
                'total_salary': 0,
                'total_points': 0,
                'teams_used': set()
            }
            
            for player_id in selected_player_ids:
                player = self.players_df[self.players_df['ID'] == player_id].iloc[0]
                opponent = opponents_dict.get(player['TeamAbbrev'], "Unknown")
                
                lineup_data['players'].append({
                    'name': player['Name'],
                    'position': player['Roster Position'],
                    'team': player['TeamAbbrev'],
                    'opponent': opponent,
                    'salary': player['Salary'],
                    'avg_points': player['AvgPointsPerGame'],
                    'game_info': player['Game Info']
                })
                
                lineup_data['total_salary'] += player['Salary']
                lineup_data['total_points'] += player['AvgPointsPerGame']
                lineup_data['teams_used'].add(player['TeamAbbrev'])
            
            # Sort players by position in the required order
            position_order = {'P': 0, 'C': 1, '1B': 2, '2B': 3, '3B': 4, 'SS': 5, 'OF': 6}
            lineup_data['players'].sort(key=lambda x: (position_order[x['position']], -x['avg_points']))
            
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
            print(f"{'POS':<5}{'NAME':<30}{'TEAM':<6}{'OPP':<6}{'SALARY':<10}{'POINTS':<10}{'GAME INFO':<20}")
            print(f"{'-'*80}")
            
            # Group players by team to see stacks
            team_counts = defaultdict(int)
            for player in lineup['players']:
                team_counts[player['team']] += 1
            
            for player in lineup['players']:
                team_indicator = f"{player['team']}*" if team_counts[player['team']] >= 3 else player['team']
                print(f"{player['position']:<5}{player['name']:<30}{team_indicator:<6}"
                      f"{player['opponent']:<6}${player['salary']:<9}{player['avg_points']:<10.2f}"
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
        
        with open(output_path, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['Lineup', 'Position', 'Name', 'Team', 'Opponent', 
                               'Salary', 'Avg Points', 'Game Info'])
            
            for i, lineup in enumerate(lineups, 1):
                for player in lineup['players']:
                    csvwriter.writerow([
                        i, 
                        player['position'], 
                        player['name'], 
                        player['team'],
                        player['opponent'],
                        player['salary'], 
                        player['avg_points'],
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
                        # Get player ID
                        player_data = {
                            'id': self.players_df[(self.players_df['Name'] == player['name']) & 
                                                 (self.players_df['Roster Position'] == pos)]['ID'].values[0],
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

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Optimize Daily Fantasy Baseball lineups')
    
    parser.add_argument('--csv', type=str, help='Path to the CSV file with player data')
    parser.add_argument('--salary-cap', type=int, default=50000, 
                        help='Salary cap for the lineup (default: 50000)')
    parser.add_argument('--num-lineups', type=int, default=10, 
                        help='Number of lineups to generate (default: 10)')
    parser.add_argument('--stack-team', type=str, 
                        help='Team abbreviation to stack (e.g., HOU, NYY)')
    parser.add_argument('--stack-count', type=int, default=4, 
                        help='Number of players to include from stacked team (default: 4)')
    parser.add_argument('--max-from-team', type=int, default=5, 
                        help='Maximum players from a single team (default: 5)')
    parser.add_argument('--min-teams', type=int, default=3, 
                        help='Minimum number of teams in a lineup (default: 3)')
    parser.add_argument('--min-salary-used', type=float, default=0.95, 
                        help='Minimum fraction of salary cap to use (default: 0.95)')
    parser.add_argument('--lineup-diversity', type=int, default=3, 
                        help='Minimum number of different players between lineups (default: 3)')
    parser.add_argument('--injured-list', type=str,
                        help='Path to CSV file containing injured players')
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

def find_injured_list():
    """Find the path to the injured list CSV file, always returning the latest version."""
    # Look for common injury file patterns
    injury_patterns = ["mlb-injury*.csv", "*injury*.csv", "*injured*.csv", "*-IL-*.csv"]
    
    # First check the downloads directory
    user_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
    current_dir = os.getcwd()
    search_dirs = [current_dir, user_downloads]
    
    all_matches = []
    import glob
    
    # Find all matching files across directories
    for directory in search_dirs:
        if os.path.exists(directory):
            for pattern in injury_patterns:
                matches = glob.glob(os.path.join(directory, pattern))
                all_matches.extend(matches)
    
    # Sort by modification time (newest first)
    all_matches.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    if all_matches:
        return all_matches[0]  # Return the most recent file
    
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
    
    # Find injured list if not provided - only if we're explicitly asked to use it via command-line argument
    injured_list_path = args.injured_list
    
    try:
        # Create optimizer with parameters from command line or defaults
        optimizer = AdvancedLineupOptimizer(
            csv_path=csv_path,
            salary_cap=args.salary_cap,
            max_players_from_team=args.max_from_team,
            min_teams=args.min_teams,
            injured_list_path=args.injured_list
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
                    args.stack_count = int(input(f"Enter number of players to stack (default {args.stack_count}): ") or args.stack_count)
                
                args.max_from_team = int(input(f"Enter maximum players from one team (default {args.max_from_team}): ") or args.max_from_team)
                args.min_teams = int(input(f"Enter minimum number of teams (default {args.min_teams}): ") or args.min_teams)
                
                # Injured list handling is now managed by the batch file before launching the script
                
                # Update optimizer with new parameters
                optimizer.salary_cap = args.salary_cap
                optimizer.max_players_from_team = args.max_from_team
                optimizer.min_teams = args.min_teams
        
        # Generate lineups
        lineups = optimizer.optimize(
            num_lineups=args.num_lineups,
            stack_team=args.stack_team,
            stack_count=args.stack_count,
            min_salary_used=args.min_salary_used,
            lineup_diversity=args.lineup_diversity
        )
        
        if not lineups:
            print("Failed to generate any valid lineups with the given constraints.")
            return
        
        # Display the results
        optimizer.display_lineups(lineups)
        
        # Save results to CSV
        # Generate timestamp for unique filenames
        from datetime import datetime
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
