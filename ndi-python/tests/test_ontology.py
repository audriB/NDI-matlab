"""
Tests for NDI ontology lookup functionality.

These tests require internet access to query external ontology APIs (EBI OLS).
They are marked as 'integration' tests and can be skipped with: pytest -m "not integration"

Note: External API tests may fail due to rate limiting, API changes, or network issues.
Such failures are marked as xfail for tests that depend on external services.
"""

import pytest
import json
import os
from pathlib import Path
from ndi.ontology import Ontology


# Check if external APIs are available
def _check_api_available():
    """Check if external OLS API is accessible."""
    try:
        import urllib.request
        req = urllib.request.Request('https://www.ebi.ac.uk/ols4/api/ontologies')
        req.add_header('Accept', 'application/json')
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status == 200
    except Exception:
        return False


# Cache the API availability check
_API_AVAILABLE = None
def api_available():
    global _API_AVAILABLE
    if _API_AVAILABLE is None:
        _API_AVAILABLE = _check_api_available()
    return _API_AVAILABLE


# Load test cases from JSON file
def load_ontology_test_cases():
    """Load ontology test cases from JSON file."""
    test_dir = Path(__file__).parent
    json_file = test_dir / 'ontology_lookup_tests.json'

    with open(json_file, 'r') as f:
        data = json.load(f)

    test_cases = data['ontology_lookup_tests']

    # Create test IDs for better test output
    test_ids = [f"{case['ontology']}:{case['lookup_string'].replace(':', '_')}"
                for case in test_cases]

    return test_cases, test_ids


# Load all test cases
ALL_TEST_CASES, TEST_IDS = load_ontology_test_cases()

# Ontologies that use external APIs (EBI OLS)
EXTERNAL_API_ONTOLOGIES = {'NCBITaxon', 'CL', 'CHEBI', 'PATO', 'OM', 'Uberon', 'NCIm', 'PubChem', 'RRID', 'NCIT', 'WBStrain'}

# Ontologies that are local-only
LOCAL_ONTOLOGIES = {'NDIC', 'EMPTY'}


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.parametrize('test_case', ALL_TEST_CASES, ids=TEST_IDS)
def test_ontology_lookup(test_case):
    """
    Test ontology lookup functionality with various ontologies.

    This is a parameterized test that loads test cases from a JSON file.
    Each test case specifies:
    - lookup_string: The string to look up
    - should_succeed: Whether the lookup should succeed or fail
    - expected_id: The expected ID returned (if success)
    - expected_name: The expected name returned (if success)
    """
    ontology = test_case['ontology']
    lookup_str = test_case['lookup_string']
    should_succeed = test_case['should_succeed']
    expected_id = test_case['expected_id']
    expected_name = test_case['expected_name']

    # Skip external API tests if APIs are unavailable
    if ontology in EXTERNAL_API_ONTOLOGIES and not api_available():
        pytest.skip(f"External OLS API unavailable, skipping {ontology} test")

    if should_succeed:
        # Test case expected to succeed
        try:
            result_id, result_name, _, _, _, _ = Ontology.lookup(lookup_str)

            # Verify ID matches (handle both prefixed and unprefixed formats)
            id_matches = (
                result_id == expected_id or  # Exact match
                result_id.endswith(f':{expected_id}') or  # Prefixed returned, unprefixed expected
                expected_id.endswith(f':{result_id}')  # Unprefixed returned, prefixed expected
            )
            assert id_matches, \
                f'ID mismatch for "{lookup_str}". Expected "{expected_id}", got "{result_id}"'

            # Verify name matches (case-insensitive)
            assert result_name.lower() == expected_name.lower(), \
                f'Name mismatch for "{lookup_str}". Expected "{expected_name}", got "{result_name}"'

        except Exception as e:
            # If external API error, mark as xfail
            error_str = str(e).lower()
            if ontology in EXTERNAL_API_ONTOLOGIES and any(x in error_str for x in ['403', 'forbidden', 'timeout', 'connection']):
                pytest.xfail(f'External API unavailable: {str(e)}')
            pytest.fail(f'Expected success for "{lookup_str}", but got error: {str(e)}')

    else:
        # Test case expected to fail
        try:
            Ontology.lookup(lookup_str)
            pytest.fail(f'Expected failure for "{lookup_str}", but lookup succeeded')
        except Exception:
            pass  # Expected to fail


# Create a separate test for a quick smoke test that doesn't require all API calls
@pytest.mark.integration
def test_ontology_lookup_basic():
    """
    Quick smoke test for ontology lookup with local ontologies.

    Tests NDIC and EMPTY which don't require external API calls.
    """
    # Test NDIC lookup (local file)
    try:
        result_id, result_name, _, _, _, _ = Ontology.lookup('NDIC:8')
        assert result_id == '8', f'Expected NDIC ID "8", got "{result_id}"'
        assert 'cricket' in result_name.lower(), f'Expected name containing "cricket", got "{result_name}"'
    except FileNotFoundError:
        pytest.skip("NDIC.txt file not found")

    # Test EMPTY lookup (local OBO file)
    result_id, result_name, _, _, _, _ = Ontology.lookup('EMPTY:00000090')
    assert result_id == 'EMPTY:00000090', f'Expected EMPTY ID "EMPTY:00000090", got "{result_id}"'


@pytest.mark.integration
def test_ontology_lookup_invalid():
    """Test that invalid lookups raise an error."""
    with pytest.raises(Exception):
        Ontology.lookup('InvalidOntology:NoSuchTerm')
