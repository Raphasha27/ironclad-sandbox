<div align="center">
  <a href="https://raphasha27.github.io/ironclad-sandbox/">
    <img src="https://img.shields.io/badge/LIVE_DEPLOYMENT-View_App-0EA5E9?style=for-the-badge&logo=github&logoColor=white" alt="Live Deployment" />
  </a>
</div>

<br/>

[![CI](https://github.com/Raphasha27/ironclad-sandbox/actions/workflows/ci.yml/badge.svg)](https://github.com/Raphasha27/ironclad-sandbox/actions/workflows/ci.yml)

# Ironclad Sandbox

> **The future of AI agent code execution** -- No Docker, no containers, no cloud sandboxes. Just pure, secure, blazing-fast Python execution powered by Rust.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Monty](https://img.shields.io/badge/Powered%20by-Pydantic%20Monty-red.svg)](https://github.com/pydantic/monty)
[![Rust](https://img.shields.io/badge/Security-Rust%20Microinterpreter-orange.svg)](https://rust-lang.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Made in SA](https://img.shields.io/badge/Made%20in-South%20Africa%20%F0%9F%87%BF%F0%9F%87%A6-brightgreen.svg)](https://github.com/Raphasha27)

## The Problem with Docker-Based Agent Sandboxes

Traditional AI agent code execution requires spinning up Docker containers:

| Metric | Docker Container | Ironclad Sandbox |
|--------|-----------------|------------------|
| **Startup Time** | ~200ms | **0.06ms** |
| **Speed Factor** | 1x | **3,000x faster** |
| **Memory Overhead** | ~50MB+ per container | **< 1MB** |
| **Requires Daemon** | Yes (dockerd) | **No** |
| **Container Images** | Required | **None** |
| **Cloud Dependencies** | Often | **Zero** |
| **Cost** | Pay per container | **Free & OSS** |

## Powered by Pydantic Monty

Ironclad Sandbox is built on top of [Pydantic Monty](https://github.com/pydantic/monty) -- a **minimal, secure Python interpreter written in Rust**, designed specifically for AI agents.

Instead of running code in a Docker container, Ironclad runs Python directly in your process -- controlled, locked, and secured by a Rust-based microinterpreter that monitors and blocks unauthorized access to:

- **File system** -- No reading/writing files unless explicitly allowed
- **Network** -- No HTTP calls, socket connections, or DNS lookups
- **Environment variables** -- No access to secrets or config
- **System calls** -- Restricted kernel interaction

### Key Features

- **Instant snapshots** -- Save execution state to bytes, resume later
- **Resource tracking** -- Memory, stack depth, and execution time limits
- **CodeMode pattern** -- Agents write full scripts instead of sequential tool calls
- **Async support** -- Run async/sync code natively
- **100% open source** -- MIT licensed, community-audited

## Architecture

```
+----------------------------------+
|        AI Agent (LLM)            |
|   (GPT-4o / Gemini / Claude)     |
+----------------------------------+
              |
              | Generates Python code
              v
+----------------------------------+
|     Ironclad Sandbox          |
|  +----------------------------+  |
|  |   Rust Microinterpreter    |  |
|  |   - FS blocked            |  |
|  |   - Network blocked       |  |
|  |   - Env vars blocked      |  |
|  |   - Resource limits set   |  |
|  +----------------------------+  |
|              |                   |
|  +----------------------------+  |
|  |   Allowed Functions        |  |
|  |   (Explicitly injected)   |  |
|  |   - get_data()            |  |
|  |   - calculate()           |  |
|  |   - format_output()       |  |
|  +----------------------------+  |
+----------------------------------+
              |
              v
+----------------------------------+
|     Structured Output            |
|   (JSON / Pydantic models)       |
+----------------------------------+
```

## Quick Start

### Installation

```bash
pip install monty-python pydantic-ai
```

### Basic Usage

```python
from monty import Monty

# Create a sandboxed interpreter
sandbox = Monty()

# Execute LLM-generated code safely
result = sandbox.run("""
data = [45, 23, 67, 89, 12, 34, 78, 56]
sorted_data = sorted(data, reverse=True)
mean = sum(data) / len(data)
output = {
    "sorted": sorted_data,
    "mean": round(mean, 2),
    "max": max(data),
    "min": min(data),
    "count": len(data)
}
""")

print(result["output"])
# {"sorted": [89, 78, 67, 56, 45, 34, 23, 12], "mean": 50.5, ...}
```

### With Pydantic AI Agent

```python
from pydantic_ai import Agent
from monty import Monty

# Initialize Monty sandbox
sandbox = Monty()

# Create an AI agent with code execution capability
agent = Agent('openai:gpt-4o')

@agent.tool
def execute_code(code: str) -> dict:
    """Execute Python code in a secure Monty sandbox."""
    result = sandbox.run(code)
    return {"output": result.output, "execution_time_ms": result.duration_ms}

@agent.tool
def analyze_data(data: list[float]) -> dict:
    """Analyze numerical data using sandboxed computation."""
    code = f"""
import statistics
data = {data}
result = {{
    "mean": round(statistics.mean(data), 4),
    "median": statistics.median(data),
    "stdev": round(statistics.stdev(data), 4),
    "variance": round(statistics.variance(data), 4),
    "range": max(data) - min(data),
}}
"""
    return sandbox.run(code)

# Run the agent
result = agent.run_sync(
    "Analyze this security log data and find anomalies: [12, 15, 14, 13, 98, 12, 14, 13, 99, 15]"
)
print(result.data)
```

### Snapshot & Resume

```python
from monty import Monty

sandbox = Monty()

# Run some code
sandbox.run("counter = 0")
sandbox.run("counter += 1")

# Snapshot the state to bytes
state = sandbox.snapshot()
print(f"State size: {len(state)} bytes")

# Later: restore from snapshot
restored = Monty.from_snapshot(state)
restored.run("counter += 1")
result = restored.run("counter")
print(result)  # 2
```

## SOC Integration Example

This sandbox integrates with the [CyberShield SOC](https://github.com/Raphasha27/cybershield_soc) platform for secure threat analysis:

```python
from monty import Monty

def analyze_threat_log(log_entries: list[dict]) -> dict:
    """Use Monty to safely analyze potentially malicious log data."""
    sandbox = Monty()

    # Inject only the data -- no file/network access
    sandbox.set_global("logs", log_entries)

    result = sandbox.run("""
ips = {}
for entry in logs:
    ip = entry.get("source_ip", "unknown")
    ips[ip] = ips.get(ip, 0) + 1

# Find IPs with suspicious frequency
threshold = len(logs) * 0.3
suspicious = {ip: count for ip, count in ips.items() if count > threshold}

output = {
    "total_entries": len(logs),
    "unique_ips": len(ips),
    "suspicious_ips": suspicious,
    "threat_level": "HIGH" if suspicious else "LOW"
}
""")
    return result["output"]
```

## Benchmarks

```
Sandbox Startup Latency:
  Docker:     ~200ms
  Firecracker: ~125ms  
  gVisor:      ~50ms
  Monty:       ~0.06ms  (3,333x faster than Docker)

Memory per sandbox:
  Docker:     ~50MB
  Firecracker: ~25MB
  Monty:       ~0.5MB   (100x less than Docker)

Cost per 1M executions:
  Docker:     ~$150 (compute)
  Cloud Sandbox: ~$200 (API fees)
  Monty:       $0 (local, open source)
```

## Project Structure

```
ironclad-sandbox/
+-- src/
|   +-- sandbox/
|   |   +-- __init__.py       # Sandbox configuration
|   |   +-- executor.py       # Code execution engine
|   |   +-- policies.py       # Security policies
|   |   +-- snapshots.py      # State management
|   +-- agents/
|   |   +-- code_agent.py     # Pydantic AI agent with Monty
|   |   +-- soc_agent.py      # SOC threat analysis agent
|   |   +-- data_agent.py     # Data processing agent
|   +-- examples/
|       +-- basic_execution.py
|       +-- snapshot_demo.py
|       +-- soc_integration.py
+-- tests/
|   +-- test_sandbox.py
|   +-- test_security.py
+-- requirements.txt
+-- pyproject.toml
```

## Why Ironclad Over Docker for AI Agents?

1. **Speed** -- AI agents make dozens of code execution calls per task. 200ms Docker startup x 50 calls = 10 seconds of pure overhead. Ironclad: 3ms total.
2. **Cost** -- No container orchestration, no cloud sandbox APIs, no billing surprises.
3. **Security** -- Sandboxed by design at the interpreter level, not at the OS level. Every syscall is controlled.
4. **Simplicity** -- `pip install monty-python` and you're done. No Dockerfile, no compose, no daemon.
5. **Snapshots** -- Pause and resume execution state. Perfect for long-running agent workflows.

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**Built by [Koketso Raphasha](https://github.com/Raphasha27) | Kirov Dynamics Technology**

*Pioneering AI agent infrastructure from Johannesburg, South Africa*

## Contributors

This project is developed and maintained together with the team:
- [Raphasha27](https://github.com/Raphasha27) — Project lead & maintainer
- [DkMash](https://github.com/DkMash) — Teammate
