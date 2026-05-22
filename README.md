# AI-Powered Agentic Workflow for Project Management

This is my submission for the project. It is split into two phases. Detailed instructions are inside `starter/phase_1/README.md` and `starter/phase_2/README.md`.

## Structure

```
starter/
  phase_1/   reusable agent library (workflow_agents/base_agents.py)
             and seven test scripts (one per agent)
  phase_2/   agentic_workflow.py — the Email Router workflow
outputs/
  phase_1/   text output from each Phase 1 test script
  phase_2/   text output from the full Phase 2 workflow run
run_phase_1.sh   runs the seven Phase 1 tests and saves outputs
run_phase_2.sh   runs the Phase 2 workflow and saves the output
```

## Dependencies

Install with `pip install -r requirements.txt` (pandas, openai, python-dotenv).

## Setup

Create a `.env` file with your OpenAI API key:

```
OPENAI_API_KEY=your_key_here
```

If you use the Vocareum workspace, also set:

```
OPENAI_BASE_URL=https://openai.vocareum.com/v1
```

## Run

```bash
bash run_phase_1.sh   # runs all seven Phase 1 tests
bash run_phase_2.sh   # runs the Phase 2 Email Router workflow
```

Outputs are written to `outputs/phase_1/` and `outputs/phase_2/`.
