#!/bin/bash
# Simple script to fix ALL id column issues (solarpump, controller, meters)
# Run this on your server: bash run_fix.sh

cd /home/anujdeshmukh24/DBSolar_19_09_2023/DBSolar_19_09_2023
source /home/anujdeshmukh24/env/bin/activate
python fix_all_id_columns.py

echo ""
echo "========================================="
echo "Fix completed! Please RESTART your Django server now."
echo "========================================="

