"""
NDI Metadata Manager - Automated metadata extraction and validation.

This module provides utilities for extracting, validating, and managing
metadata from NDI documents, sessions, and datasets.

MATLAB Equivalent: Various metadata functions in NDI-MATLAB database utilities
"""

from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime
import re


class MetadataExtractor:
    """
    Extract metadata from NDI documents and sessions.

    Provides automated extraction of common metadata fields from various
    document types, sessions, and experimental setups.

    Examples:
        >>> extractor = MetadataExtractor()
        >>> metadata = extractor.extract_from_document(doc)
        >>> metadata['creation_date']
        '2025-11-17T00:00:00'
    """

    def __init__(self):
        """Initialize metadata extractor."""
        self.extractors = {
            'base': self._extract_base_metadata,
            'element': self._extract_element_metadata,
            'probe': self._extract_probe_metadata,
            'stimulus': self._extract_stimulus_metadata,
            'app': self._extract_app_metadata,
        }

    def extract_from_document(self, document: Any) -> Dict[str, Any]:
        """
        Extract all metadata from a document.

        Args:
            document: NDI document object

        Returns:
            Dictionary of extracted metadata

        Examples:
            >>> metadata = extractor.extract_from_document(doc)
            >>> 'document_type' in metadata
            True
        """
        metadata = {}

        # Extract document type
        try:
            doc_type = document.document_properties.document_class.definition
            metadata['document_type'] = doc_type
        except AttributeError:
            metadata['document_type'] = 'unknown'

        # Extract based on document structure
        if hasattr(document, 'document_properties'):
            props = document.document_properties

            # Try each extractor
            for category, extractor_func in self.extractors.items():
                if hasattr(props, category):
                    category_data = getattr(props, category)
                    extracted = extractor_func(category_data)
                    if extracted:
                        metadata[category] = extracted

        return metadata

    def _extract_base_metadata(self, base_props: Any) -> Dict[str, Any]:
        """
        Extract base metadata fields.

        Args:
            base_props: Base properties object

        Returns:
            Dictionary of base metadata
        """
        metadata = {}

        # Common base fields
        fields = ['id', 'session_id', 'name', 'type', 'created']
        for field in fields:
            if hasattr(base_props, field):
                value = getattr(base_props, field)
                if value is not None:
                    metadata[field] = value

        return metadata

    def _extract_element_metadata(self, element_props: Any) -> Dict[str, Any]:
        """
        Extract element-specific metadata.

        Args:
            element_props: Element properties object

        Returns:
            Dictionary of element metadata
        """
        metadata = {}

        # Element fields
        fields = ['type', 'direct', 'subject_id', 'reference']
        for field in fields:
            if hasattr(element_props, field):
                value = getattr(element_props, field)
                if value is not None:
                    metadata[field] = value

        return metadata

    def _extract_probe_metadata(self, probe_props: Any) -> Dict[str, Any]:
        """
        Extract probe-specific metadata.

        Args:
            probe_props: Probe properties object

        Returns:
            Dictionary of probe metadata
        """
        metadata = {}

        # Probe fields
        fields = ['type', 'num_channels', 'material', 'impedance',
                  'wavelength', 'imaging_type']
        for field in fields:
            if hasattr(probe_props, field):
                value = getattr(probe_props, field)
                if value is not None:
                    metadata[field] = value

        return metadata

    def _extract_stimulus_metadata(self, stimulus_props: Any) -> Dict[str, Any]:
        """
        Extract stimulus-specific metadata.

        Args:
            stimulus_props: Stimulus properties object

        Returns:
            Dictionary of stimulus metadata
        """
        metadata = {}

        # Stimulus fields
        fields = ['presentation_time', 'parameters', 'device']
        for field in fields:
            if hasattr(stimulus_props, field):
                value = getattr(stimulus_props, field)
                if value is not None:
                    metadata[field] = value

        return metadata

    def _extract_app_metadata(self, app_props: Any) -> Dict[str, Any]:
        """
        Extract app-specific metadata.

        Args:
            app_props: App properties object

        Returns:
            Dictionary of app metadata
        """
        metadata = {}

        # App fields
        fields = ['name', 'version', 'url', 'os', 'interpreter', 'interpreter_version']
        for field in fields:
            if hasattr(app_props, field):
                value = getattr(app_props, field)
                if value is not None:
                    metadata[field] = value

        return metadata

    def extract_session_metadata(self, session: Any) -> Dict[str, Any]:
        """
        Extract metadata from a session.

        Args:
            session: NDI session object

        Returns:
            Dictionary of session metadata

        Examples:
            >>> metadata = extractor.extract_session_metadata(session)
            >>> 'session_id' in metadata
            True
        """
        metadata = {}

        # Session basic info
        if hasattr(session, 'id'):
            metadata['session_id'] = session.id()
        if hasattr(session, 'path'):
            metadata['path'] = session.path()

        # Count documents by type
        if hasattr(session, 'database'):
            db = session.database
            if hasattr(db, 'search'):
                # Count total documents
                all_docs = db.search({})
                metadata['total_documents'] = len(all_docs)

                # Count by type
                doc_types = {}
                for doc in all_docs:
                    try:
                        doc_type = doc.document_properties.document_class.definition
                        doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
                    except AttributeError:
                        doc_types['unknown'] = doc_types.get('unknown', 0) + 1

                metadata['document_types'] = doc_types

        # Get probes
        if hasattr(session, 'get_probes'):
            try:
                probes = session.get_probes()
                metadata['num_probes'] = len(probes)
                metadata['probe_names'] = [p.name for p in probes if hasattr(p, 'name')]
            except Exception:
                pass

        # Get epochs
        if hasattr(session, 'get_epochs'):
            try:
                epochs = session.get_epochs()
                metadata['num_epochs'] = len(epochs)
            except Exception:
                pass

        return metadata


class MetadataValidator:
    """
    Validate metadata for completeness and correctness.

    Provides validation rules for different metadata types to ensure
    data quality and consistency.

    Examples:
        >>> validator = MetadataValidator()
        >>> issues = validator.validate(metadata, 'probe')
        >>> len(issues)
        0
    """

    def __init__(self):
        """Initialize metadata validator."""
        self.rules = {
            'base': self._validate_base,
            'element': self._validate_element,
            'probe': self._validate_probe,
            'session': self._validate_session,
        }

    def validate(self, metadata: Dict[str, Any],
                 metadata_type: str = 'base') -> List[str]:
        """
        Validate metadata and return list of issues.

        Args:
            metadata: Metadata dictionary to validate
            metadata_type: Type of metadata ('base', 'element', 'probe', 'session')

        Returns:
            List of validation error messages (empty if valid)

        Examples:
            >>> validator = MetadataValidator()
            >>> issues = validator.validate({'id': 'abc123'}, 'base')
            >>> len(issues)
            0
        """
        validator = self.rules.get(metadata_type, self._validate_generic)
        return validator(metadata)

    def _validate_base(self, metadata: Dict[str, Any]) -> List[str]:
        """Validate base metadata."""
        issues = []

        # Required fields
        required = ['id', 'session_id']
        for field in required:
            if field not in metadata or not metadata[field]:
                issues.append(f"Missing required field: {field}")

        # ID format validation
        if 'id' in metadata:
            if not isinstance(metadata['id'], str):
                issues.append("Field 'id' must be a string")
            elif len(metadata['id']) < 1:
                issues.append("Field 'id' cannot be empty")

        return issues

    def _validate_element(self, metadata: Dict[str, Any]) -> List[str]:
        """Validate element metadata."""
        issues = []

        # Type validation
        if 'type' in metadata:
            valid_types = ['stimulus', 'probe', 'daq', 'acquisition']
            if metadata['type'] not in valid_types:
                issues.append(f"Element type '{metadata['type']}' not in valid types: {valid_types}")

        # Direct flag
        if 'direct' in metadata:
            if not isinstance(metadata['direct'], (bool, int)):
                issues.append("Field 'direct' must be boolean or int (0/1)")

        return issues

    def _validate_probe(self, metadata: Dict[str, Any]) -> List[str]:
        """Validate probe metadata."""
        issues = []

        # Numeric validations
        if 'num_channels' in metadata:
            if not isinstance(metadata['num_channels'], int) or metadata['num_channels'] < 1:
                issues.append("Field 'num_channels' must be positive integer")

        if 'impedance' in metadata:
            if not isinstance(metadata['impedance'], (int, float)) or metadata['impedance'] < 0:
                issues.append("Field 'impedance' must be non-negative number")

        if 'wavelength' in metadata:
            if not isinstance(metadata['wavelength'], (int, float)) or metadata['wavelength'] < 0:
                issues.append("Field 'wavelength' must be non-negative number")

        return issues

    def _validate_session(self, metadata: Dict[str, Any]) -> List[str]:
        """Validate session metadata."""
        issues = []

        # Required fields
        if 'session_id' not in metadata:
            issues.append("Missing required field: session_id")

        # Path validation
        if 'path' in metadata:
            import os
            if not os.path.exists(metadata['path']):
                issues.append(f"Session path does not exist: {metadata['path']}")

        return issues

    def _validate_generic(self, metadata: Dict[str, Any]) -> List[str]:
        """Generic validation for unknown metadata types."""
        issues = []

        # Just check it's not empty
        if not metadata:
            issues.append("Metadata is empty")

        return issues


class MetadataSearcher:
    """
    Search and filter documents based on metadata criteria.

    Provides high-level search capabilities using metadata patterns.

    Examples:
        >>> searcher = MetadataSearcher(session)
        >>> probes = searcher.find_by_type('probe')
        >>> recent = searcher.find_recent(days=7)
    """

    def __init__(self, session: Any):
        """
        Initialize metadata searcher.

        Args:
            session: NDI session object to search
        """
        self.session = session

    def find_by_type(self, element_type: str) -> List[Any]:
        """
        Find all documents of a specific element type.

        Args:
            element_type: Type of element ('probe', 'stimulus', etc.)

        Returns:
            List of matching documents

        Examples:
            >>> docs = searcher.find_by_type('probe')
        """
        query = {'element.type': element_type}
        return self.session.database.search(query)

    def find_by_app(self, app_name: str) -> List[Any]:
        """
        Find all documents created by a specific app.

        Args:
            app_name: Name of the app

        Returns:
            List of matching documents

        Examples:
            >>> docs = searcher.find_by_app('spike_extractor')
        """
        query = {'app.name': app_name}
        return self.session.database.search(query)

    def find_recent(self, days: int = 7) -> List[Any]:
        """
        Find documents created in the last N days.

        Args:
            days: Number of days to look back

        Returns:
            List of recent documents

        Examples:
            >>> recent_docs = searcher.find_recent(days=7)
        """
        from datetime import datetime, timedelta

        cutoff = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff.isoformat()

        # Search for documents with created date >= cutoff
        # Note: This is a simplified version; actual implementation
        # would depend on database support for date comparisons
        all_docs = self.session.database.search({})

        recent = []
        for doc in all_docs:
            try:
                created = doc.document_properties.base.created
                if isinstance(created, str):
                    created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                    if created_dt >= cutoff:
                        recent.append(doc)
            except (AttributeError, ValueError):
                pass

        return recent

    def find_by_subject(self, subject_id: str) -> List[Any]:
        """
        Find all documents for a specific subject.

        Args:
            subject_id: Subject identifier

        Returns:
            List of matching documents

        Examples:
            >>> docs = searcher.find_by_subject('mouse01')
        """
        query = {'element.subject_id': subject_id}
        return self.session.database.search(query)

    def find_missing_metadata(self, required_fields: List[str]) -> List[Tuple[Any, List[str]]]:
        """
        Find documents missing required metadata fields.

        Args:
            required_fields: List of required field names (dot notation)

        Returns:
            List of (document, missing_fields) tuples

        Examples:
            >>> missing = searcher.find_missing_metadata(['element.type', 'element.subject_id'])
        """
        all_docs = self.session.database.search({})
        docs_with_missing = []

        for doc in all_docs:
            missing_fields = []
            for field in required_fields:
                if not self._has_field(doc, field):
                    missing_fields.append(field)

            if missing_fields:
                docs_with_missing.append((doc, missing_fields))

        return docs_with_missing

    def _has_field(self, doc: Any, field_path: str) -> bool:
        """
        Check if document has a field (supports dot notation).

        Args:
            doc: Document to check
            field_path: Field path (e.g., 'element.type')

        Returns:
            True if field exists and is not None
        """
        parts = field_path.split('.')
        current = doc.document_properties

        for part in parts:
            if not hasattr(current, part):
                return False
            current = getattr(current, part)
            if current is None:
                return False

        return True
