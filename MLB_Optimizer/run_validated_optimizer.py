#!/usr/bin/env python
"""
Run the optimizer with guaranteed valid arguments.
This script wraps advanced_optimizer.py and ensures valid parameters.
"""

import sys
import subprocess
import os

def run_optimizer():
    """Run the optimizer with validated parameters."""
    # Get command-line arguments
    args = sys.argv[1:]

    # Check if --max-player-appearances is provided
    max_appearances_index = -1
    for i, arg in enumerate(args):
        if arg == '--max-player-appearances' and i < len(args) - 1:
            max_appearances_index = i + 1
            break

    # If we found the flag, validate the argument
    if max_appearances_index >= 0:
        try:
            # Try to convert to integer
            value = int(args[max_appearances_index])
            if value <= 0:
                print("Warning: max-player-appearances must be positive. Using default of 5.")
                args[max_appearances_index] = '5'
        except ValueError:
            print("Warning: Invalid max-player-appearances value. Using default of 5.")
            args[max_appearances_index] = '5'

    # Build the command to run the optimizer
    cmd = ['python', 'advanced_optimizer.py'] + args
    print("Running optimizer with arguments:", ' '.join(cmd[1:]))
    
    # Run the optimizer
    subprocess.run(cmd)

if __name__ == '__main__':
    run_optimizer()
