#!/usr/bin/env python3
"""
Unit tests for the MLB Injury Manager.

This file contains tests that verify the functionality of the injury manager
including finding injury files, previewing content, and handling different
file formats.
"""

import os
import sys
import unittest
import pandas as pd
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from injury_manager import list_all_injury_files, preview_injury_file


class TestInjuryManager(unittest.TestCase):
    """Test cases for the MLB injury manager."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a sample injury CSV file
        self.test_injury_data = pd.DataFrame({
            'Player': ['John Doe', 'Jane Smith', 'Bob Johnson'],
            'Team': ['NYY', 'LAD', 'BOS'],
            'Position': ['OF', 'P', 'C'],
            'Status': ['IL-10', 'IL-15', 'IL-60']
        })
        
        self.test_injury_path = 'test_mlb-injury-report.csv'
        self.test_injury_data.to_csv(self.test_injury_path, index=False)

    def tearDown(self):
        """Clean up after each test method."""
        # Remove the temporary CSV file
        if os.path.exists(self.test_injury_path):
            os.remove(self.test_injury_path)

    def test_list_all_injury_files(self):
        """Test finding all injury files."""
        with patch('os.getcwd') as mock_getcwd, \
             patch('os.path.dirname') as mock_dirname, \
             patch('os.path.expanduser') as mock_expanduser, \
             patch('os.path.exists') as mock_exists, \
             patch('glob.glob') as mock_glob, \
             patch('os.path.getsize') as mock_getsize, \
             patch('os.path.getmtime') as mock_getmtime:
            
            # Set up the mocks
            mock_getcwd.return_value = '/test/current'
            mock_dirname.return_value = '/test'
            mock_expanduser.return_value = '/home/user'
            mock_exists.return_value = True
            
            # Mock glob to return our test file
            mock_glob.return_value = [self.test_injury_path]
            
            # Mock file stats
            mock_getsize.return_value = 1024
            mock_getmtime.return_value = 1593532800.0  # July 1, 2020
            
            # Call the function
            result = list_all_injury_files()
            
            # Check that it found our test file
            self.assertGreaterEqual(len(result), 1)  # Updated to handle variable number of injury files
            self.assertEqual(result[0][0], self.test_injury_path)
            self.assertEqual(result[0][1], 1024)  # Size

    @patch('builtins.print')
    def test_preview_injury_file(self, mock_print):
        """Test previewing injury file contents."""
        # Create a test file and write directly to it to ensure it exists
        test_file_path = "test_injuries.csv"
        with open(test_file_path, 'w', newline='') as f:
            f.write("Player,Team,Position,Status\n")
            f.write("John Doe,NYY,P,IL60\n")
            f.write("Jane Smith,BOS,OF,IL10\n")
            f.write("Bob Johnson,LAD,1B,Day-to-Day\n")
        
        try:
            # Call the function with our test file
            preview_injury_file(test_file_path)
            
            # Check that it printed the expected information
            mock_print.assert_any_call(f"\nPreview of: {test_file_path}")
            
            # Just verify that print was called multiple times
            self.assertGreater(mock_print.call_count, 1)
        finally:
            # Clean up
            if os.path.exists(test_file_path):
                os.remove(test_file_path)

    @patch('builtins.print')
    def test_preview_injury_file_error(self, mock_print):
        """Test handling errors when previewing invalid files."""
        # Try to preview a non-existent file
        preview_injury_file('non_existent_file.csv')
        
        # Check that it printed an error message
        error_msg = mock_print.mock_calls[0]
        self.assertTrue("Error reading the file" in str(error_msg))


if __name__ == '__main__':
    unittest.main()
