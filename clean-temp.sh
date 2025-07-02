#!/bin/bash

# Clean __pycache__ files and directory
find . -name "__pycache__" -exec rm -r "{}" \;
echo "Clean __pycache__ done"

# Clean .coverage files and directory
find . -name ".coverage" -exec rm -r "{}" \;
find . -name "htmlcov" -exec rm -r "{}" \;
echo "clean coverage done"

echo "Done"
