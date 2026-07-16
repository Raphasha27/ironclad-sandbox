"""Tests for Ironclad Sandbox."""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sandbox.executor import Sandbox, SecurityPolicy, MontyAgentExecutor


class TestSandbox:
    def test_basic_execution(self):
        sandbox = Sandbox()
        result = sandbox.execute("output = 2 + 2")
        assert result.success
        assert result.output == 4

    def test_list_operations(self):
        sandbox = Sandbox()
        result = sandbox.execute("""
data = [5, 3, 8, 1, 9, 2]
output = sorted(data)
""")
        assert result.success
        assert result.output == [1, 2, 3, 5, 8, 9]

    def test_dict_operations(self):
        sandbox = Sandbox()
        result = sandbox.execute("""
output = {"mean": sum([1, 2, 3]) / 3, "count": 3}
""")
        assert result.success
        assert result.output["mean"] == 2.0

    def test_global_injection(self):
        sandbox = Sandbox()
        sandbox.set_global("input_data", [10, 20, 30])
        result = sandbox.execute("output = sum(input_data)")
        assert result.success
        assert result.output == 60

    def test_error_handling(self):
        sandbox = Sandbox()
        result = sandbox.execute("output = 1 / 0")
        assert not result.success
        assert "ZeroDivisionError" in result.error

    def test_dangerous_builtins_blocked(self):
        sandbox = Sandbox()
        result = sandbox.execute("__import__('os').system('whoami')")
        assert not result.success

    def test_execution_stats(self):
        sandbox = Sandbox()
        sandbox.execute("x = 1")
        sandbox.execute("y = 2")
        stats = sandbox.get_stats()
        assert stats["total_executions"] == 2


class TestMontyAgentExecutor:
    def test_run_agent_code(self):
        executor = MontyAgentExecutor()
        result = executor.run_agent_code(
            "output = [x**2 for x in range(5)]"
        )
        assert result["success"]
        assert result["output"] == [0, 1, 4, 9, 16]

    def test_run_with_context(self):
        executor = MontyAgentExecutor()
        result = executor.run_agent_code(
            "output = sum(values) / len(values)",
            context={"values": [10, 20, 30, 40, 50]}
        )
        assert result["success"]
        assert result["output"] == 30.0

    def test_threat_log_analysis(self):
        executor = MontyAgentExecutor()
        logs = [
            {"source_ip": "192.168.1.100", "severity": "HIGH"},
            {"source_ip": "192.168.1.100", "severity": "HIGH"},
            {"source_ip": "192.168.1.100", "severity": "CRITICAL"},
            {"source_ip": "10.0.0.1", "severity": "LOW"},
            {"source_ip": "10.0.0.2", "severity": "LOW"},
        ]
        result = executor.analyze_threat_logs(logs)
        assert result.success
        assert result.output["suspicious_ips"]["192.168.1.100"] == 3

