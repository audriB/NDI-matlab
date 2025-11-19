"""
PyTest configuration and fixtures for NDI tests.

This file contains fixtures and mock data for testing, particularly
for mocking external API calls to ontology services.
"""

import pytest
import json
import urllib.error
from unittest.mock import Mock, patch
from io import BytesIO


# Ontology mock data based on test cases
ONTOLOGY_MOCK_DATA = {
    # Cell Ontology (CL)
    'CL:0000000': {
        'obo_id': 'CL:0000000',
        'label': 'cell',
        'description': ['A material entity of anatomical origin'],
        'iri': 'http://purl.obolibrary.org/obo/CL_0000000'
    },
    'CL:0000540': {
        'obo_id': 'CL:0000540',
        'label': 'neuron',
        'description': ['An electrically active cell'],
        'iri': 'http://purl.obolibrary.org/obo/CL_0000540'
    },

    # CHEBI (Chemical Entities of Biological Interest)
    'CHEBI:15377': {
        'obo_id': 'CHEBI:15377',
        'label': 'water',
        'description': ['An oxygen hydride'],
        'iri': 'http://purl.obolibrary.org/obo/CHEBI_15377'
    },
    'CHEBI:16236': {
        'obo_id': 'CHEBI:16236',
        'label': 'ethanol',
        'description': ['A primary alcohol'],
        'iri': 'http://purl.obolibrary.org/obo/CHEBI_16236'
    },

    # UBERON (Uber Anatomy Ontology)
    'UBERON:0000948': {
        'obo_id': 'UBERON:0000948',
        'label': 'heart',
        'description': ['A myogenic muscular circulatory organ'],
        'iri': 'http://purl.obolibrary.org/obo/UBERON_0000948'
    },
    'UBERON:0002107': {
        'obo_id': 'UBERON:0002107',
        'label': 'liver',
        'description': ['An exocrine gland which secretes bile'],
        'iri': 'http://purl.obolibrary.org/obo/UBERON_0002107'
    },

    # PATO (Phenotype and Trait Ontology)
    'PATO:0000384': {
        'obo_id': 'PATO:0000384',
        'label': 'male',
        'description': ['A biological sex quality'],
        'iri': 'http://purl.obolibrary.org/obo/PATO_0000384'
    },
    'PATO:0000383': {
        'obo_id': 'PATO:0000383',
        'label': 'female',
        'description': ['A biological sex quality'],
        'iri': 'http://purl.obolibrary.org/obo/PATO_0000383'
    },

    # OM (Ontology of Units of Measure)
    'OM:MolarVolumeUnit': {
        'label': 'molar volume unit',
        'iri': 'http://www.ontology-of-units-of-measure.org/resource/om-2/MolarVolumeUnit'
    },
    'OM:Acidity': {
        'label': 'acidity',
        'iri': 'http://www.ontology-of-units-of-measure.org/resource/om-2/Acidity'
    },
    'OM:Period': {
        'label': 'period',
        'iri': 'http://www.ontology-of-units-of-measure.org/resource/om-2/Period'
    },

    # NCBITaxon
    'NCBITaxon:9606': {
        'obo_id': 'NCBITaxon:9606',
        'label': 'Homo sapiens',
        'description': ['Human species'],
        'iri': 'http://purl.obolibrary.org/obo/NCBITaxon_9606'
    },

    # NCIm (NCI Metathesaurus)
    'NCIm:C0018787': {
        'label': 'Heart',
        'iri': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C0018787'
    },
    'NCIm:C0009450': {
        'label': 'Infectious Disorder',
        'iri': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C0009450'
    },

    # PubChem
    'PubChem:2244': {
        'label': 'aspirin',
        'iri': 'http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID2244'
    },

    # RRID (Research Resource Identifiers)
    'RRID:SCR_006472': {
        'label': 'NCBI',
        'iri': 'https://scicrunch.org/resolver/SCR_006472'
    },
    'RRID:RGD_70508': {
        'label': 'SD',
        'iri': 'https://scicrunch.org/resolver/RGD_70508'
    },
}


# Label to ID mappings for search queries
LABEL_TO_ID_MAP = {
    'cell': 'CL:0000000',
    'neuron': 'CL:0000540',
    'water': 'CHEBI:15377',
    'ethanol': 'CHEBI:16236',
    'heart': 'UBERON:0000948',
    'liver': 'UBERON:0002107',
    'male': 'PATO:0000384',
    'female': 'PATO:0000383',
    'molar volume unit': 'OM:MolarVolumeUnit',
    'acidity': 'OM:Acidity',
    'period': 'OM:Period',
    'homo sapiens': 'NCBITaxon:9606',
    'aspirin': 'PubChem:2244',
}


def mock_urlopen(request, timeout=30):
    """
    Mock urllib.request.urlopen for ontology API calls.

    Returns appropriate mock responses based on the URL being requested.
    """
    url = request.full_url if hasattr(request, 'full_url') else str(request)

    # Check if this is an OLS search or term lookup
    if '/api/search' in url:
        # This is a search request
        return _mock_ols_search(url)
    elif '/api/ontologies/' in url and '/terms/' in url:
        # This is a term lookup request
        return _mock_ols_term_lookup(url)
    else:
        # Unknown URL - raise 404
        raise urllib.error.HTTPError(url, 404, 'Not Found', {}, None)


def _mock_ols_search(url):
    """Mock OLS search API responses."""
    # Extract query parameters from URL
    from urllib.parse import urlparse, parse_qs

    parsed = urlparse(url)
    params = parse_qs(parsed.query)

    query = params.get('q', [''])[0]
    ontology = params.get('ontology', [''])[0]
    query_fields = params.get('queryFields', [''])[0]

    # Find matching entry
    results = []

    if query_fields == 'obo_id':
        # ID search - match case-insensitively
        # Try exact match first
        for key, value in ONTOLOGY_MOCK_DATA.items():
            if key.upper() == query.upper():
                results = [value]
                break
    elif query_fields == 'label':
        # Label search - case insensitive
        query_lower = query.lower()
        if query_lower in LABEL_TO_ID_MAP:
            ontology_id = LABEL_TO_ID_MAP[query_lower]
            if ontology_id in ONTOLOGY_MOCK_DATA:
                results = [ONTOLOGY_MOCK_DATA[ontology_id]]

    # Build search response
    search_response = {
        'response': {
            'numFound': len(results),
            'docs': results
        }
    }

    response_data = json.dumps(search_response).encode('utf-8')
    return _create_mock_response(response_data)


def _mock_ols_term_lookup(url):
    """Mock OLS term lookup API responses."""
    from urllib.parse import unquote

    # Extract the term IRI from the URL (it's double-encoded)
    # URL format: /api/ontologies/{ontology}/terms/{double_encoded_iri}
    parts = url.split('/terms/')
    if len(parts) < 2:
        raise urllib.error.HTTPError(url, 404, 'Not Found', {}, None)

    # The IRI is double URL-encoded, so decode twice
    encoded_iri = parts[1].split('?')[0] if '?' in parts[1] else parts[1]
    decoded_once = unquote(encoded_iri)
    decoded_iri = unquote(decoded_once)

    # Find matching entry by IRI
    for entry_id, entry_data in ONTOLOGY_MOCK_DATA.items():
        if entry_data.get('iri') == decoded_iri:
            response_data = json.dumps(entry_data).encode('utf-8')
            return _create_mock_response(response_data)

    # Not found
    raise urllib.error.HTTPError(url, 404, 'Not Found', {}, None)


def _create_mock_response(data):
    """Create a mock HTTP response object."""
    mock_response = Mock()
    mock_response.read.return_value = data
    mock_response.__enter__ = Mock(return_value=mock_response)
    mock_response.__exit__ = Mock(return_value=False)
    return mock_response


@pytest.fixture(autouse=True)
def mock_ontology_api():
    """
    Automatically mock ontology API calls for all tests.

    This fixture patches urllib.request.urlopen to return mock responses
    instead of making real HTTP requests to external ontology APIs.
    """
    with patch('urllib.request.urlopen', side_effect=mock_urlopen):
        yield


@pytest.fixture
def sample_session_dir(tmp_path):
    """
    Create a temporary session directory for testing.

    Returns:
        Path: Path to temporary session directory
    """
    session_path = tmp_path / "test_session"
    session_path.mkdir()
    return session_path
