AgentCI

Trust, but verify AI agent actions.

AgentCI is an open-source evaluation and reliability harness for AI agents. It helps determine whether an AI-generated code repair actually works instead of trusting the model's claim that it is correct.

AgentCI combines local AI-powered code repair using Gemma 4 with independent, deterministic checks and behavioral tests. It evaluates proposed changes in an isolated temporary workspace and produces a structured report showing whether the repair passed or failed.

Why AgentCI?

A basic test runner executes tests against code. AgentCI focuses on verifying AI-generated actions and their outcomes.

Independent verification: A model's proposed fix is accepted only when the configured checks and behavioral tests pass.

Local AI inference: Uses the gemma4:e2b model through Ollama to generate code repair suggestions locally.

Isolated repair evaluation: Tests proposed code in a temporary copy of the project, preserving the original target file.

Structured reports: Records check results, test output, timestamps, and the final evaluation status in JSON.

Tool permissions and traces: Includes a tool registry that restricts calls to allowed tools and records tool-call attempts for inspection.

The goal is to make agent behavior more measurable, reproducible, and auditable.

How It Works

Identify a task: AgentCI loads a task definition containing the expected checks.

Generate a repair: Gemma 4 receives the task description and buggy code and proposes a correction.

Create an isolated workspace: AgentCI copies the project into a temporary directory.

Apply the proposal: The proposed code is written to the target file inside that temporary copy.

Evaluate independently: AgentCI runs configured text checks and behavioral tests against the proposed code.

Report the outcome: The repair is accepted only if all configured checks pass. Otherwise, the evaluation fails.

A proposed fix is not a verified fix. The model generates a candidate; AgentCI determines whether that candidate satisfies the configured requirements.

Technology Stack

Python

Gemma 4 (gemma4:e2b)

Ollama for local model inference

pytest and Python unittest for testing

JSON task definitions and evaluation reports

Requirements

Python 3.10 or newer

Ollama installed and running

The gemma4:e2b model available locally

Git (optional for running locally; required for Git-based collaboration)

Setup

1. Clone the repository

git clone https://github.com/srihithsumukha-dev/AgentCI.git
cd AgentCI

2. Install dependencies

Install the Python packages used by the project:

python -m pip install ollama pytest

3. Download the Gemma 4 model

ollama pull gemma4:e2b

Ensure Ollama is running before invoking the repair command. Depending on your installation, you may need to start the Ollama application separately.

Run the Demo

Run these commands from the repository root.

Example A: Evaluate the intentionally buggy implementation

python -m agentci.runner --project . --task tasks/empty_input_broken.json --test "python -m unittest tests.test_parse_items_broken -v"

The evaluation should fail because the implementation accesses items[0] without checking whether the list is empty. The report should show "passed": false.

Example B: Ask Gemma 4 to repair the bug

python -m agentci.repair --project . --task tasks/empty_input_broken.json --target benchmarks/sample_project/parse_items_broken.py --test "python -m unittest tests.test_parse_items_broken -v"

AgentCI asks Gemma 4 for a proposed repair, evaluates it in a temporary workspace, and reports the result.

A successful run should include:

"repair_accepted": true

"original_preserved": true

Passing text and behavioral checks

Model output may vary, so acceptance depends on the evaluation results rather than the model's explanation.

Run the Tests

Run the evaluator, runner, and tool-registry tests:

python -m pytest tests/test_evaluator.py tests/test_runner.py tests/test_tools.py -v

Run the working sample's behavioral tests:

python -m unittest tests.test_parse_items -v

The test_parse_items_broken.py test intentionally fails when run against the original buggy file. During repair evaluation, the proposed code is tested in a temporary workspace instead.

Safety and Scope

AgentCI evaluates proposed repairs without automatically replacing the original target file. The repair workflow uses a temporary project copy and reports whether the original file remained unchanged.

AgentCI's checks are only as comprehensive as the task definition and test suite. Passing the configured checks does not guarantee that code is free of every bug or security vulnerability. Review and additional testing are still recommended before deploying a repair.

The current project demonstrates this workflow using a small Python empty-input bug. More benchmarks, stronger sandboxing, richer trace analysis, and additional agent tools are possible future improvements.

Project Goal

AgentCI aims to help developers evaluate AI agents based on verified outcomes rather than unverified claims. By combining open-weight AI models with independent checks, behavioral tests, and traceable results, it provides a foundation for building more reliable tool-using agents.
