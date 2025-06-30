# MLB Daily Fantasy Lineup Optimizer

This folder contains Python scripts to optimize lineups for Daily Fantasy Baseball contests on DraftKings. The optimizer uses linear programming to find the highest-scoring lineup possible within the given constraints.

## Requirements

- Python 3.7+
- Required Python packages:
  - pandas
  - pulp

## Installation

Run the setup batch file to install the required packages:
```
setup.bat
```

## Usage

You can run the optimizer using the batch file:
```
run_optimizer_new.bat
```

This will provide options for using:
1. The basic optimizer
2. The advanced optimizer with stacking and diversity features
3. The advanced optimizer with injured player filtering (auto-detected)
4. The advanced optimizer with both injury filtering and player appearance limits
5. A utility to copy the latest DraftKings CSV file from your Downloads folder

### Advanced Optimizer Command Line Arguments

```bash
python advanced_optimizer.py --csv "path/to/DKSalaries.csv" --num-lineups 15 --stack-team HOU --stack-count 4
```

Available arguments:
- `--csv`: Path to the CSV file with player data
- `--salary-cap`: Salary cap for the lineup (default: 50000)
- `--num-lineups`: Number of lineups to generate (default: 10)
- `--stack-team`: Team abbreviation to stack (e.g., HOU, NYY)
- `--stack-count`: Number of players to include from stacked team (default: 4)
- `--max-from-team`: Maximum players from a single team (default: 5)
- `--min-teams`: Minimum number of teams in a lineup (default: 3)
- `--min-salary-used`: Minimum fraction of salary cap to use (default: 0.95)
- `--lineup-diversity`: Minimum number of different players between lineups (default: 3)
- `--max-player-appearances`: Maximum number of times a player can appear across all lineups
- `--injured-list`: Path to CSV file containing injured players to exclude
- `--auto-detect-injury`: Automatically detect and use the most recent injury list file
- `--output`: Output CSV file name (default: optimized_lineups.csv)

## Automatic Injury Detection

The optimizer can automatically detect and use the most recent MLB injury list file with the `--auto-detect-injury` flag. This feature:

1. Searches common locations for injury CSV files (current directory, parent directory, Downloads folder)
2. Selects the most recently modified injury file
3. Provides detailed feedback about the search process
4. Falls back to recursive search in Documents if no file is found in standard locations

Example usage:
```bash
python advanced_optimizer.py --auto-detect-injury --max-player-appearances 5
```

This allows you to run the optimizer with both injury filtering and player appearance limits without manually specifying the injury file path.

## MLB Lineup Rules

The optimizer creates lineups following DraftKings MLB rules:
- Each valid roster must consist of the following positions: P, P, C, 1B, 2B, 3B, SS, OF, OF, OF
- Total salary cannot exceed $50,000
- Maximum of 5 players from the same MLB team
- Minimum of 3 different teams represented

## Input File Format

The optimizer expects a CSV file in DraftKings format with the following columns:
- Position (actual position: SP, RP, 1B, etc.)
- Name + ID
- Name
- ID
- Roster Position (for our purposes: P, C, 1B, 2B, 3B, SS, OF)
- Salary
- Game Info
- TeamAbbrev
- AvgPointsPerGame

### Injured List File

The optimizer can filter out injured players using an injury report CSV file. The file should contain at least a column named 'Player' with the player names.
