#!/usr/bin/env bash
cd "$(dirname "$0")/starter/phase_2"
mkdir -p ../../outputs/phase_2

python agentic_workflow.py | tee ../../outputs/phase_2/agentic_workflow_output.txt
