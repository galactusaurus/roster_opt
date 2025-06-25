# Daily Fantasy Sports Lineup Optimizer

This repository contains tools to optimize lineups for various Daily Fantasy Sports contests. Currently, it supports MLB (Baseball) and Formula 1 with plans to add NFL, NBA, and NHL in the future. The optimizer uses linear programming to find the highest-scoring lineup possible within the given constraints.

## Requirements

- Python 3.7+
- Required Python packages:
  - pandas
  - pulp

## Project Structure

The project is organized into sport-specific subdirectories:

- `MLB_Optimizer/` - MLB baseball lineup optimizer
- `F1_Optimizer/` - Formula 1 lineup optimizer
- `NFL_Optimizer/` - (Coming soon) NFL football lineup optimizer
- `NBA_Optimizer/` - (Coming soon) NBA basketball lineup optimizer
- `NHL_Optimizer/` - (Coming soon) NHL hockey lineup optimizer

Each sport's subfolder contains its own specific optimization code and requirements.

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/roster_opt.git
   cd roster_opt
   ```

2. Run the setup batch file to install the required packages:
   ```
   setup.bat
   ```

## Usage

Simply run the main batch file to select which sport's optimizer you want to use:

```bash
optimize.bat
```

This will present a menu where you can choose which sport's optimizer to run:

1. MLB (Baseball)
2. Formula 1
3. NFL (Football) - Coming soon
4. NBA (Basketball) - Coming soon
5. NHL (Hockey) - Coming soon
6. Exit

### Sport-Specific Documentation

For detailed information on how to use a particular sport's optimizer, please refer to the README.md file in that sport's directory:

- [MLB Optimizer Documentation](./MLB_Optimizer/README.md)
- [Formula 1 Optimizer Documentation](./F1_Optimizer/README.md)

## Output

Each optimizer will generate optimized lineups and save them to CSV files within their respective sport directories.

## Contributing

If you'd like to contribute to this project, please feel free to submit pull requests or open issues on GitHub.

## Future Plans

- Add NFL (Football) lineup optimizer
- Add NBA (Basketball) lineup optimizer  
- Add NHL (Hockey) lineup optimizer
- Improve optimization algorithms
- Add web interface

The script generates multiple optimized lineups and displays them in the console, showing:
- Player names, positions, teams, and opponents
- Individual player salaries and average points
- Total salary and projected points for each lineup

Optionally, the results can be saved to a CSV file for further analysis.

## Example

```
===================================================================
LINEUP #1 - Total Points: 145.26 - Total Salary: $49900 - Teams Used: 7
-------------------------------------------------------------------
POS  NAME                          TEAM  OPP   SALARY    POINTS     GAME INFO        
-------------------------------------------------------------------
P    Hunter Brown                  HOU   PHI   $10500    24.47      PHI@HOU 06/25/2025 08:10PM ET
P    Logan Webb                    SF    MIA   $10000    22.48      MIA@SF 06/25/2025 09:45PM ET
C    Adley Rutschman               BAL   CWS   $4700     8.24       BAL@CWS 06/25/2025 08:10PM ET
1B   Matt Olson                    ATL   NYM   $5600     8.50       ATL@NYM 06/25/2025 07:10PM ET
2B   Jorge Polanco                 SEA   MIN   $4200     7.58       SEA@MIN 06/25/2025 07:40PM ET
3B   Isaac Paredes                 TB    KC    $3800     7.24       TB@KC 06/25/2025 07:40PM ET
SS   Bobby Witt Jr.                KC    TB    $5500     9.28       TB@KC 06/25/2025 07:40PM ET
OF   Kyle Schwarber                PHI   HOU   $5600     9.87       PHI@HOU 06/25/2025 08:10PM ET
OF   Daulton Varsho                TOR   BOS   $4200     8.23       TOR@BOS 06/25/2025 07:10PM ET
OF   Lane Thomas                   WAS   NYY   $3900     7.45       WAS@NYY 06/25/2025 07:05PM ET
===================================================================
```