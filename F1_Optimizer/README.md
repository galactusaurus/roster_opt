# Formula 1 DFS Lineup Optimizer

A tool to optimize DraftKings Formula 1 fantasy lineups using linear programming.

## Overview

This optimizer helps create optimal lineups for DraftKings Formula 1 contests. It uses linear programming to maximize projected points while respecting roster construction rules and salary constraints. It includes both a basic and an advanced version with additional features.

## Roster Construction

The tool optimizes for DraftKings Formula 1 rosters, which consist of:

- 1 Captain (CPT): A driver whose cost and point output is 1.5x
- 4 Drivers (D): Regular drivers
- 1 Constructor (CNSTR): A Formula 1 team

## Features

### Basic Optimizer (`optimizer.py`)
- Creates optimal lineups based on projected points
- Respects salary cap constraints
- Ensures correct position allocation
- Prevents using both the captain and regular version of the same driver

### Advanced Optimizer (`advanced_optimizer.py`)
- All features from the basic optimizer
- Team stacking capabilities
- Control maximum drivers from a single team
- Set minimum number of different teams
- Control lineup diversity when generating multiple lineups
- Minimum salary utilization

## Installation

1. Make sure you have Python 3.6+ installed
2. Clone or download this repository
3. Install required packages:

```
pip install -r requirements.txt
```

## Usage

### Basic Usage

1. Download the DraftKings salary file (CSV format) for a Formula 1 contest
2. Run the optimizer:

```
python optimizer.py
```

3. The script will guide you through the process and ask for your preferences

### Advanced Usage

```
python advanced_optimizer.py --csv path/to/DKSalaries.csv --num-lineups 10 --stack-team MCL
```

### Command Line Arguments (Advanced)

- `--csv`: Path to the CSV file with player data
- `--salary-cap`: Salary cap for the lineup (default: 50000)
- `--num-lineups`: Number of lineups to generate (default: 10)
- `--stack-team`: Team abbreviation to stack (e.g., MCL, RB)
- `--stack-count`: Number of drivers to include from stacked team (default: 2)
- `--max-from-team`: Maximum drivers from a single team (default: 3)
- `--min-teams`: Minimum number of teams in a lineup (default: 2)
- `--min-salary-used`: Minimum fraction of salary cap to use (default: 0.95)
- `--lineup-diversity`: Minimum number of different players between lineups (default: 2)
- `--output`: Output CSV file name (default: optimized_lineups.csv)

## Output Files

The optimizer creates two types of output files in the Outputs directory:

1. Detailed lineups (optimized_lineups_{timestamp}.csv):
   - Shows all players in each lineup with their details

2. Position-based format (lineup_{timestamp}.csv):
   - Format suitable for mass-importing lineups into DraftKings
   - Shows each lineup as a row with player IDs in position order

## Requirements

- pandas
- pulp
- numpy
