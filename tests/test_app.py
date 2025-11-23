"""
Basic tests for ContractGuardian frontend
Run with: pytest tests/
"""
import pytest
from utils.api_client import MockWatsonXClient
from utils.validators import (
    validate_file_upload,
    validate_risk_score,
    validate_analysis_results
)
from config.settings import get_risk_level


class MockFile:
    """Mock file object for testing"""
    def __init__(self, name, size, file_type):
        self.name = name
        self.size = size
        self.type = file_type

    def read(self):
        return b"x" * self.size


def test_mock_client_upload():
    """Test mock client upload functionality"""
    client = MockWatsonXClient()
    response = client.upload_contract(b"test content", "test.pdf")

    assert 'job_id' in response
    assert response['status'] == 'processing'


def test_mock_client_status():
    """Test mock client status retrieval"""
    client = MockWatsonXClient()
    status = client.get_agent_status("mock-job-12345")

    assert 'status' in status
    assert 'progress' in status
    assert 'current_agent' in status


def test_mock_client_results():
    """Test mock client results"""
    client = MockWatsonXClient()
    results = client.get_analysis_results("mock-job-12345")

    assert 'risk_score' in results
    assert 'entities' in results
    assert 'high_risk_clauses' in results
    assert 'debate' in results


def test_file_validation_valid():
    """Test file validation with valid file"""
    mock_file = MockFile("contract.pdf", 1024 * 1024, "application/pdf")
    is_valid, error = validate_file_upload(mock_file)

    assert is_valid
    assert error is None


def test_file_validation_too_large():
    """Test file validation with oversized file"""
    mock_file = MockFile("large.pdf", 20 * 1024 * 1024, "application/pdf")
    is_valid, error = validate_file_upload(mock_file, max_size_mb=10)

    assert not is_valid
    assert "exceeds maximum" in error


def test_file_validation_wrong_type():
    """Test file validation with wrong file type"""
    mock_file = MockFile("document.txt", 1024, "text/plain")
    is_valid, error = validate_file_upload(mock_file)

    assert not is_valid
    assert "not supported" in error


def test_risk_score_validation_valid():
    """Test risk score validation with valid scores"""
    for score in range(1, 11):
        is_valid, error = validate_risk_score(score)
        assert is_valid
        assert error is None


def test_risk_score_validation_invalid():
    """Test risk score validation with invalid scores"""
    invalid_scores = [0, 11, -1, 100]

    for score in invalid_scores:
        is_valid, error = validate_risk_score(score)
        assert not is_valid
        assert "out of valid range" in error


def test_get_risk_level():
    """Test risk level classification"""
    # Ultra risky
    level = get_risk_level(10)
    assert level['label'] == 'Ultra Risky'

    # High risk
    level = get_risk_level(7)
    assert level['label'] == 'High Risk'

    # Medium risk
    level = get_risk_level(5)
    assert level['label'] == 'Medium Risk'

    # Low risk
    level = get_risk_level(2)
    assert level['label'] == 'Low Risk'

    # Ideal
    level = get_risk_level(1)
    assert level['label'] == 'Ideal'


def test_analysis_results_validation():
    """Test complete analysis results validation"""
    valid_results = {
        'job_id': 'test-123',
        'risk_score': 7,
        'risk_level': 'High Risk',
        'recommendation': 'NEGOTIATE',
        'entities': {},
        'high_risk_clauses': []
    }

    is_valid, error = validate_analysis_results(valid_results)
    assert is_valid
    assert error is None


def test_analysis_results_validation_missing_fields():
    """Test analysis results validation with missing fields"""
    invalid_results = {
        'job_id': 'test-123'
        # Missing required fields
    }

    is_valid, error = validate_analysis_results(invalid_results)
    assert not is_valid
    assert "Missing required fields" in error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
