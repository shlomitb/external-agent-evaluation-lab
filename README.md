# External Agent Evaluation Lab

A hands-on learning and engineering project focused on independently evaluating AI agents built by others.

The goal is to develop practical skills in agent evaluation, reliability testing, behavioral assessment, and MCP testing — without relying on access to an agent's internal implementation.

## Project Goals

- Evaluate an existing external AI agent through its exposed interface.
- Design repeatable test scenarios with clearly defined expected outcomes.
- Assess whether an agent selects appropriate tools and uses them correctly.
- Verify actual task completion independently of the agent's own claims.
- Evaluate error handling, constraint adherence, and recovery from failures.
- Learn to distinguish agent failures from integration and environment failures.
- Develop an evidence-based approach to deciding whether an agent is reliable.

## Guiding Principles

1. **Independent verification:** Never assume an agent completed a task just because it says it did.
2. **Objective checks first:** Prefer observable outcomes and deterministic assertions wherever possible.
3. **Black-box evaluation:** Test the agent through its public interface rather than relying on its internal code.
4. **Reproducibility:** Keep test cases, configurations, and results version-controlled.
5. **Meaningful failures:** Design tests that expose weaknesses, not just demonstrate successful behavior.
6. **Understand the evidence:** Learn what each metric tells us, what it does not tell us, and how much confidence we should place in the results.

## Planned Technology

- **Promptfoo:** Evaluation orchestration, test cases, assertions, and reporting.
- **Open Interpreter:** Candidate external agent under evaluation.
- **Ollama:** Local model runtime, where practical.
- **Python / pytest:** Independent verification of observable outcomes.
- **MCP:** A later learning and evaluation milestone covering MCP servers and agent-server integration.

Technology choices will be validated before installation. Preference is given to free, local tools.

## Evaluation Scope

The initial evaluation will focus on an agent interacting with a controlled, disposable workspace.

Potential evaluation dimensions:

- Task completion and correctness.
- Tool selection and tool arguments.
- Action sequence and unnecessary actions.
- Error handling and recovery.
- Compliance with task constraints.
- Side effects and unintended changes.
- Agreement between the agent's final response and the actual resulting state.

## Learning Milestones

1. Establish the local development environment.
2. Learn Promptfoo's evaluation model and configuration.
3. Select and configure an external agent.
4. Design a controlled black-box evaluation environment.
5. Build baseline behavioral evaluations.
6. Add independent verification and negative test cases.
7. Analyze results, limitations, and reliability.
8. Learn MCP fundamentals.
9. Evaluate an MCP server independently.
10. Evaluate an agent's use of an MCP server.

## Learning Approach

This is a step-by-step learning project.

Each milestone should include:

- The engineering problem and why it matters.
- A small implementation task.
- Tests and evidence.
- Review of the results and limitations.
- A concise record of what was learned.

The emphasis is on understanding evaluation quality, not simply running evaluation tools.

## Environment

- Windows 11
- Ubuntu 24.04.1 through WSL2
- Python 3.12.3
- Project-local Python virtual environment
- PyCharm (free edition)
- Git and GitHub

## Background

This project builds on prior hands-on work with:

- AI agent implementation and tool authorization.
- Deterministic and mocked testing.
- DeepEval and LLM-as-a-judge evaluation.
- RAG pipeline implementation and retrieval metrics.

The intention is to explore a different problem: how to evaluate an agent that we did not build.