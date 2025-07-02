#!/bin/bash
echo "Build Documentation files"
doxygen Doxyfile

echo "Build Package files"
python3 -m build
