#!/usr/bin/env bash
cd "$(dirname "$0")/starter/phase_1"
mkdir -p ../../outputs/phase_1

python direct_prompt_agent.py              | tee ../../outputs/phase_1/direct_prompt_agent_output.txt
python augmented_prompt_agent.py           | tee ../../outputs/phase_1/augmented_prompt_agent_output.txt
python knowledge_augmented_prompt_agent.py | tee ../../outputs/phase_1/knowledge_augmented_prompt_agent_output.txt
python rag_knowledge_prompt_agent.py       | tee ../../outputs/phase_1/rag_knowledge_prompt_agent_output.txt
python evaluation_agent.py                 | tee ../../outputs/phase_1/evaluation_agent_output.txt
python routing_agent.py                    | tee ../../outputs/phase_1/routing_agent_output.txt
python action_planning_agent.py            | tee ../../outputs/phase_1/action_planning_agent_output.txt
