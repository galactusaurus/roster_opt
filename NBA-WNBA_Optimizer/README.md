# NBA/WNBA Basketball Lineup Optimizer

This optimizer creates optimal lineups for NBA/WNBA fantasy contests, with current focus on WNBA Showdown format.

## Features

- Creates lineups for WNBA Showdown contests (1 Captain, 5 Utility players)
- Captain gets 1.5x points but costs 1.5x salary
- Salary cap of $50,000
- Supports multiple lineup generation with enforced diversity
- Advanced differentiation features:
  - Team stacking (multiple players from the same team)
  - Player exposure limits
  - Randomization for lineup variety
  - Minimum salary usage requirements
  - Team fading (reducing exposure to specific teams)

## Usage

### Basic Usage

```
python optimizer.py [data_file] [num_lineups]
```

Example:
```
python optimizer.py DKSalaries.csv 10
```

### Advanced Usage

```
python advanced_optimizer.py [data_file] [num_lineups] [stack_team]
```

Example with team stacking:
```
python advanced_optimizer.py DKSalaries.csv 10 LVA
```

### Using the Batch File

```
run_optimizer.bat [data_file] [num_lineups] [stack_team]
```

Example:
```
run_optimizer.bat DKSalaries.csv 15 LVA
```

## Input Data

The optimizer expects a CSV file with DraftKings salary data. Download this from the DraftKings contest page and save it as `DKSalaries.csv` in the same directory as the optimizer.

Required columns:
- Name (or "Name + ID")
- Salary
- TeamAbbrev
- AvgPointsPerGame
- Game Info (optional, but recommended for opponent extraction)

## Output

The optimizer creates two CSV files in the "Outputs" directory:

1. `lineup_[timestamp].csv` - Detailed lineup information with all players
2. `optimized_lineups_[timestamp].csv` - Summary of lineups with projected points

## Customization

You can customize the optimization by modifying parameters in the Python script:

- `player_diversity`: Minimum number of different players between lineups
- `exposure_constraints`: Dictionary of player name to maximum exposure (0-1)
- `stack_team`: Team abbreviation to stack
- `stack_count`: Minimum number of players to include from stack team
- `fade_teams`: List of team abbreviations to reduce exposure to
- `randomness`: Factor of randomness to add to projections (0-1)
- `min_salary_used`: Minimum fraction of salary cap that must be used
