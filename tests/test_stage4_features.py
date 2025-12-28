import pytest
from swarm_mcp.core.task_scoring import TaskScorer, ScoredTask
from swarm_mcp.core.verification import VerificationHarness, VerificationResult, VerificationType
from swarm_mcp.core.recovery import RecoveryManager, FailureEvent

class TestTaskScoring:
    def test_roi_calculation(self):
        t1 = ScoredTask("1", "High Value", value=10, urgency=10, effort=1, risk=1, dependencies=[])
        # ROI = (10*10)/(1*1*1) = 100
        assert t1.roi_score == 100.0
        
        t2 = ScoredTask("2", "Hard/Risky", value=10, urgency=10, effort=10, risk=10, dependencies=[])
        # ROI = (10*10)/(10*10*1) = 1.0
        assert t2.roi_score == 1.0

    def test_dependency_penalty(self):
        t1 = ScoredTask("1", "Solo", dependencies=[])
        t2 = ScoredTask("2", "Blocked", dependencies=["a", "b"])
        # default value=5, urg=5, eff=5, risk=1
        # t1 ROI = 25 / 5 = 5.0
        # t2 ROI = 25 / (5 * 1 * (1 + 2*0.5)) = 25 / (5 * 2) = 2.5
        assert t2.roi_score < t1.roi_score

    def test_metadata_parsing(self):
        scorer = TaskScorer()
        attrs = scorer.parse_task_metadata("Fix critical bug [v=9 u=10 e=2 r=1]")
        assert attrs["value"] == 9.0
        assert attrs["urgency"] == 10.0
        assert attrs["effort"] == 2.0
        assert attrs["risk"] == 1.0

    def test_selection(self):
        scorer = TaskScorer()
        t1 = ScoredTask("1", "Low", value=1)
        t2 = ScoredTask("2", "High", value=10)
        selected = scorer.select_next_task([t1, t2])
        assert selected.id == "2"

class TestVerification:
    def test_file_exists(self, tmp_path):
        harness = VerificationHarness(workspace_root=str(tmp_path))
        (tmp_path / "test.txt").touch()
        
        res = harness.verify_file_exists("test.txt")
        assert res.passed is True
        assert res.type == VerificationType.FILE_EXISTS
        
        res_fail = harness.verify_file_exists("missing.txt")
        assert res_fail.passed is False

    def test_unit_test_run(self, tmp_path):
        harness = VerificationHarness(workspace_root=str(tmp_path))
        # Create a passing test
        test_file = tmp_path / "test_pass.py"
        test_file.write_text("def test_ok(): assert True")
        
        # We need pytest installed in environment, assuming it is since we are running tests
        res = harness.verify_unit_test(str(test_file))
        assert res.passed is True
        assert res.type == VerificationType.UNIT_TEST

class TestRecovery:
    def test_analyze_failure(self):
        manager = RecoveryManager()
        log = "Traceback... ImportError: No module named 'foo'"
        event = manager.analyze_failure(log)
        assert event.component == "dependencies"
        
        strategy = manager.propose_strategy(event)
        assert strategy == "reinstall_dependencies"

    def test_analyze_syntax_error(self):
        manager = RecoveryManager()
        log = "File 'x.py', line 1\nSyntaxError: invalid syntax"
        event = manager.analyze_failure(log)
        assert event.component == "code_integrity"
        
        strategy = manager.propose_strategy(event)
        assert strategy == "rollback_last_commit"
