#!/bin/bash

echo "Creating a Python $PYTHON_VERSION environment"
conda create -n stemming python=$PYTHON_VERSION || exit 1
source activate stemming

echo "Installing packages..."
conda install flask flake8 pytest
