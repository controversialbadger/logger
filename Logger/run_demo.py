#!/usr/bin/env python3
import os
import sys
import subprocess
import time

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)

def run_command(command, description):
    """Run a command and print its output."""
    print_header(description)
    print(f"Running: {command}\n")
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               universal_newlines=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        print(e.stdout)
        return False

def check_logs():
    """Check and display log files."""
    print_header("Checking Log Files")
    
    log_dir = "./logs"
    if not os.path.exists(log_dir):
        print(f"Log directory {log_dir} not found!")
        return
        
    print(f"Log files in {os.path.abspath(log_dir)}:")
    
    for file in os.listdir(log_dir):
        file_path = os.path.join(log_dir, file)
        file_size = os.path.getsize(file_path)
        print(f"- {file} ({file_size} bytes)")
        
        # Show a preview of each log file
        print(f"\nPreview of {file}:")
        try:
            with open(file_path, 'r') as f:
                # Read first 5 lines
                lines = [next(f) for _ in range(5)]
                for line in lines:
                    print(f"  {line.strip()}")
            print("  ...")
        except Exception as e:
            print(f"  Error reading file: {e}")
        print()

def main():
    """Run the demo and tests."""
    print_header("Secure Logger Demo")
    print("This script will demonstrate the Secure Logger functionality")
    print("by running the example script and tests.")
    
    # Run the example script
    if run_command("python example.py", "Running Example Script"):
        # Wait a moment for logs to be written
        time.sleep(1)
        check_logs()
    
    # Run the tests
    run_command("python test_security.py", "Running Security Tests")
    
    print_header("Demo Complete")
    print("The Secure Logger has been demonstrated.")
    print("Check the README.md file for more information on how to use the logger.")

if __name__ == "__main__":
    main()