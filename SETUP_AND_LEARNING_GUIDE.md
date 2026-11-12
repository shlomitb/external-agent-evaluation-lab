# External Agent Evaluation Lab — Setup and Learning Guide

## 1. Project Purpose

The **External Agent Evaluation Lab** is a hands-on learning project focused on evaluating an existing AI agent from the outside.

The goal is to learn how to assess an agent's behavior and reliability without building the agent itself.

Areas we intend to evaluate include:

- Whether the agent understands and completes assigned tasks.
- Whether it selects appropriate tools.
- Whether it uses tools with correct arguments.
- How it handles errors and unexpected situations.
- Whether it follows instructions and respects constraints.
- Whether it produces correct, verifiable results.
- Whether it recovers appropriately when something goes wrong.

The emphasis is on independent evaluation: we should not assume that an agent's own claims about its work are correct. We need ways to verify its actions and outputs.

## 2. Development Environment

The project was set up and tested using the following environment:

| Component | Version / Details |
|---|---|
| Operating system | Windows 11 Home |
| Linux environment | WSL2 |
| Linux distribution | Ubuntu 24.04.1 |
| Python | 3.12.3 |
| IDE | PyCharm Community Edition 2025.3.1.1 |
| Version control | Git and GitHub |
| Agent under investigation | Open Interpreter 0.0.60 |
| LLM provider | Google Gemini API |
| Model used for initial tests | Gemini 3.5 Flash-Lite |

### Project location

The project is stored inside the WSL2 Linux filesystem:

```text
/home/shlomit/projects/external-agent-evaluation-lab
```

The agent workspace is:

```text
/home/shlomit/projects/external-agent-evaluation-lab/agent_workspace
```

### Python virtual environment

The project uses a Python virtual environment named `.venv`.

Activate it from the Ubuntu terminal:

```bash
cd ~/projects/external-agent-evaluation-lab
source .venv/bin/activate
```

To leave the virtual environment:

```bash
deactivate
```

### Development workflow

- Edit project files in PyCharm on Windows.
- Run Python commands and project tools in the Ubuntu terminal through WSL2.
- Keep the project and its virtual environment in the WSL2 filesystem.
- Use Git for version control and GitHub for the remote repository.

PyCharm Community Edition does not provide the same WSL interpreter integration as PyCharm Professional. The project can still be edited in PyCharm and executed from the Ubuntu terminal.

## 3. Open Interpreter

Open Interpreter was selected as a candidate existing agent to investigate and evaluate.

Installed version:

```text
Open Interpreter 0.0.60
```

It was installed in the WSL2 environment. Its executable is available at:

```text
~/.local/bin/interpreter
```

The intention was to interact with an existing agent through its command-line interface and eventually evaluate its behavior using repeatable test scenarios.

Open Interpreter was run in an ephemeral, read-only sandbox during the initial integration experiment.

Example command options used:

```bash
interpreter exec \
  --sandbox read-only \
  --ephemeral \
  "Reply with exactly: TEST"
```

The initial investigation focused on getting a model provider working before beginning agent evaluation.

**Important:** The Open Interpreter integration with Gemini has not yet been verified as working. See Section 6.

## 4. Gemini API and Local Compatibility Proxy

### Why a proxy was created

Open Interpreter was configured to use an OpenAI-compatible chat-completions interface.

Google Gemini provides an OpenAI-compatible API endpoint, but the initial integration required a small local proxy to adapt requests and remove an unsupported OpenAI-specific field.

The proxy is implemented in:

```text
gemini_proxy.py
```

It uses:

- FastAPI to expose a local HTTP endpoint.
- Uvicorn to run the local server.
- HTTPX to forward requests to Gemini.
- python-dotenv to load the Gemini API key from a `.env` file.

The proxy exposes:

```text
GET  /health
POST /v1/chat/completions
```

The upstream Gemini endpoint is:

```text
https://generativelanguage.googleapis.com/v1beta/openai/chat/completions
```

The proxy removes the `store` field from incoming requests before forwarding them to Gemini.

### Python dependencies

The proxy requires:

- `fastapi`
- `uvicorn`
- `httpx`
- `python-dotenv`

These dependencies are installed in the project's virtual environment.

## 5. Running the Local Gemini Proxy

The proxy runs in one Ubuntu terminal. Open Interpreter or other clients can be run in a second terminal.

### Terminal 1 — Start the proxy

Activate the virtual environment:

```bash
cd ~/projects/external-agent-evaluation-lab
source .venv/bin/activate
```

### Gemini API key configuration

The Gemini API key is stored in a `.env` file in the project root:

```env
GEMINI_API_KEY=your_actual_gemini_api_key
```

Replace the example value with your actual API key.

The `.env` file is excluded from Git through `.gitignore` and must never be committed to GitHub.

The proxy uses `python-dotenv` to load the key automatically when it starts.

The Python code reads the key through:

```python
api_key = os.environ.get("GEMINI_API_KEY")
```

### Start the proxy

Run:

```bash
python -m uvicorn gemini_proxy:app --host 127.0.0.1 --port 8000
```

Leave this terminal running.

### Verify the proxy

From another Ubuntu terminal:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

### Test a simple Gemini request through the proxy

```bash
curl -sS -X POST http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3.5-flash-lite",
    "messages": [
      {"role": "user", "content": "Reply with exactly: PROXY_LITE_OK"}
    ],
    "store": true
  }'
```

The test succeeded and Gemini returned:

```text
PROXY_LITE_OK
```

This verified that a simple request could travel through the local proxy to Gemini and receive a response.

## 6. Open Interpreter + Gemini Integration Experiment

### Intended configuration

Open Interpreter was configured to use the local proxy as a custom model provider.

The local proxy URL was:

```text
http://127.0.0.1:8000/v1
```

In Terminal 2, the following placeholder key was used for the provider configuration:

```bash
export PROXY_API_KEY="local-proxy-token"
```

This is a local configuration value, not the Gemini API key.

**Important:** The proxy currently does not validate this incoming bearer token. It is only being supplied to satisfy the Open Interpreter provider configuration.

### Open Interpreter command

The command used was:

```bash
interpreter exec \
  -c 'model_provider="gemini_proxy"' \
  -c 'model="gemini-3.5-flash-lite"' \
  -c 'model_providers.gemini_proxy.name="Local Gemini Proxy"' \
  -c 'model_providers.gemini_proxy.base_url="http://127.0.0.1:8000/v1"' \
  -c 'model_providers.gemini_proxy.env_key="PROXY_API_KEY"' \
  -c 'model_providers.gemini_proxy.wire_api="chat"' \
  --chat-completions \
  --sandbox read-only \
  --ephemeral \
  "Reply with exactly: OPEN_INTERPRETER_LITE_OK"
```

### Results

The following results were observed:

| Test | Result |
|---|---|
| Direct Gemini 3.5 Flash-Lite API request | Successful |
| Simple request through local proxy | Successful |
| Proxy health check | Successful |
| Open Interpreter request reaching the local proxy | Confirmed |
| Open Interpreter receiving a successful Gemini response | Not achieved |

Open Interpreter sent a substantially larger request than the simple proxy test. The request included:

- A system prompt of approximately 17,000 characters.
- Additional instructions and environment context.
- 13 tool definitions.

The integration produced repeated errors, and Gemini returned:

```text
429 RESOURCE_EXHAUSTED
```

This indicates that the available Gemini free-tier quota was a blocker during the experiment.

### Conclusion

The direct API and simple proxy tests demonstrated that Gemini 3.5 Flash-Lite could respond to basic requests.

However, the Open Interpreter integration did not complete successfully.

We have not established whether the failure was caused by request size, free-tier quota limits, tool definitions, or a combination of factors. We should not conclude that Open Interpreter and Gemini are inherently incompatible.

Further integration testing was paused to avoid repeatedly consuming the available API quota.

**Current status: experimental integration, not verified as working.**

## 7. API Key and Security Practices

- Never commit API keys to GitHub.
- Never paste API keys into source code or chat messages.
- Store the Gemini API key in the project-root `.env` file.
- Keep `.env` excluded through `.gitignore`.
- The `PROXY_API_KEY` used by Open Interpreter is currently a local placeholder; it is not a substitute for securing the proxy.
- The proxy listens on `127.0.0.1`, limiting access to the local machine.
- Do not expose the proxy to a network or the internet in its current configuration.
- Temporary diagnostic logging that prints message previews is commented out because prompts may contain private information.

Before using the proxy beyond local experiments, review its authentication and security behavior.

## 8. Current Project Status and Next Steps

The environment and initial provider investigation are documented.

### Completed

- Created the project repository.
- Set up the WSL2 Ubuntu development environment.
- Created and activated the Python virtual environment.
- Installed Open Interpreter.
- Tested direct Gemini API access.
- Implemented a small FastAPI compatibility proxy.
- Configured the proxy to load the Gemini API key from `.env`.
- Verified that `.env` is excluded from Git.
- Verified a simple request through the proxy.
- Investigated Open Interpreter's custom provider configuration.
- Documented the quota-related integration blocker.

### Not yet completed

- A successful Open Interpreter + Gemini integration.
- Selection and setup of a suitable external agent for evaluation.
- Definition of repeatable agent evaluation scenarios.
- Independent verification of agent actions and results.
- Integration of an evaluation framework such as Promptfoo, if appropriate.

### Learning direction

The next phase should focus on selecting an accessible existing agent and designing controlled evaluation scenarios.

The goal is to learn how to evaluate agent behavior systematically, rather than spend excessive time troubleshooting one particular model-provider integration.

Potential evaluation areas include:

1. Task completion and correctness.
2. Tool selection and tool arguments.
3. Handling of missing or incorrect information.
4. Error recovery.
5. Compliance with explicit instructions and constraints.
6. Verification of outputs and side effects.

The evaluation framework and agent should be selected based on the learning objectives, practical accessibility, and ability to observe and verify agent behavior.