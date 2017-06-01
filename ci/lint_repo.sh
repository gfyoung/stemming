#!/bin/bash

echo "Linting repository..."
source activate stemming
flake8
