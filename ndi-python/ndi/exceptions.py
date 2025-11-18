"""
NDI Exception Classes.

This module defines custom exception types for the NDI Python library.
Using specific exception types allows for more precise error handling and
better debugging.

Exception Hierarchy:
    NDIError
    ├── DatabaseError
    │   ├── DocumentNotFoundError
    │   ├── DuplicateDocumentError
    │   └── DatabaseConnectionError
    ├── SyncError
    │   ├── ClockSyncError
    │   └── TimeSyncError
    ├── CloudError
    │   ├── AuthenticationError
    │   ├── CloudSyncError
    │   ├── UploadError
    │   ├── DownloadError
    │   └── APIError
    ├── DAQError
    │   ├── HardwareError
    │   └── DataAcquisitionError
    ├── OntologyError
    │   ├── OntologyLookupError
    │   └── InvalidTermError
    ├── SessionError
    │   ├── SessionNotFoundError
    │   └── InvalidSessionError
    ├── EpochError
    │   ├── InvalidEpochError
    │   └── EpochNotFoundError
    ├── ProbeError
    │   ├── InvalidProbeError
    │   └── ProbeNotFoundError
    └── ValidationError
        ├── SchemaValidationError
        └── DataValidationError
"""


class NDIError(Exception):
    """
    Base exception class for all NDI-specific errors.

    All custom NDI exceptions inherit from this class, making it easy
    to catch all NDI-related errors with a single except clause.

    Example:
        try:
            # NDI operations
            pass
        except NDIError as e:
            print(f"NDI error occurred: {e}")
    """
    pass


# ============================================================================
# Database Errors
# ============================================================================

class DatabaseError(NDIError):
    """
    Base class for database-related errors.

    Raised when operations involving the NDI database fail.
    """
    pass


class DocumentNotFoundError(DatabaseError):
    """
    Raised when a requested document cannot be found in the database.

    Attributes:
        document_id: The ID of the document that was not found
        query: The query that failed to find the document
    """

    def __init__(self, message, document_id=None, query=None):
        super().__init__(message)
        self.document_id = document_id
        self.query = query


class DuplicateDocumentError(DatabaseError):
    """
    Raised when attempting to add a document that already exists.

    Attributes:
        document_id: The ID of the duplicate document
    """

    def __init__(self, message, document_id=None):
        super().__init__(message)
        self.document_id = document_id


class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails or is lost."""
    pass


# ============================================================================
# Time Synchronization Errors
# ============================================================================

class SyncError(NDIError):
    """
    Base class for time synchronization errors.

    Raised when time synchronization operations fail.
    """
    pass


class ClockSyncError(SyncError):
    """
    Raised when clock synchronization fails.

    Attributes:
        clock_a: Name of first clock
        clock_b: Name of second clock
    """

    def __init__(self, message, clock_a=None, clock_b=None):
        super().__init__(message)
        self.clock_a = clock_a
        self.clock_b = clock_b


class TimeSyncError(SyncError):
    """Raised when time conversion or mapping fails."""
    pass


# ============================================================================
# Cloud Service Errors
# ============================================================================

class CloudError(NDIError):
    """
    Base class for cloud service errors.

    Raised when cloud operations fail.
    """
    pass


class AuthenticationError(CloudError):
    """
    Raised when authentication to cloud services fails.

    Attributes:
        token_expired: Whether the error is due to an expired token
    """

    def __init__(self, message, token_expired=False):
        super().__init__(message)
        self.token_expired = token_expired


class CloudSyncError(CloudError):
    """
    Raised when cloud synchronization fails.

    Attributes:
        dataset_id: ID of the dataset being synced
        sync_mode: The synchronization mode that failed
    """

    def __init__(self, message, dataset_id=None, sync_mode=None):
        super().__init__(message)
        self.dataset_id = dataset_id
        self.sync_mode = sync_mode


class UploadError(CloudError):
    """
    Raised when uploading data to cloud fails.

    Attributes:
        file_path: Path to the file that failed to upload
        document_id: ID of the document that failed to upload
    """

    def __init__(self, message, file_path=None, document_id=None):
        super().__init__(message)
        self.file_path = file_path
        self.document_id = document_id


class DownloadError(CloudError):
    """
    Raised when downloading data from cloud fails.

    Attributes:
        url: URL that failed to download
        dataset_id: ID of the dataset being downloaded
    """

    def __init__(self, message, url=None, dataset_id=None):
        super().__init__(message)
        self.url = url
        self.dataset_id = dataset_id


class APIError(CloudError):
    """
    Raised when cloud API calls fail.

    Attributes:
        status_code: HTTP status code
        endpoint: API endpoint that failed
        response: Response from the API
    """

    def __init__(self, message, status_code=None, endpoint=None, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.endpoint = endpoint
        self.response = response


# ============================================================================
# Data Acquisition Errors
# ============================================================================

class DAQError(NDIError):
    """
    Base class for data acquisition errors.

    Raised when DAQ operations fail.
    """
    pass


class HardwareError(DAQError):
    """
    Raised when hardware interface fails.

    Attributes:
        device_name: Name of the device that failed
        hardware_type: Type of hardware (e.g., 'Intan', 'Blackrock')
    """

    def __init__(self, message, device_name=None, hardware_type=None):
        super().__init__(message)
        self.device_name = device_name
        self.hardware_type = hardware_type


class DataAcquisitionError(DAQError):
    """Raised when data acquisition fails."""
    pass


# ============================================================================
# Ontology Errors
# ============================================================================

class OntologyError(NDIError):
    """
    Base class for ontology-related errors.

    Raised when ontology operations fail.
    """
    pass


class OntologyLookupError(OntologyError):
    """
    Raised when ontology lookup fails.

    Attributes:
        term: The term that was being looked up
        ontology: The ontology being queried
    """

    def __init__(self, message, term=None, ontology=None):
        super().__init__(message)
        self.term = term
        self.ontology = ontology


class InvalidTermError(OntologyError):
    """
    Raised when an invalid ontology term is used.

    Attributes:
        term: The invalid term
    """

    def __init__(self, message, term=None):
        super().__init__(message)
        self.term = term


# ============================================================================
# Session Errors
# ============================================================================

class SessionError(NDIError):
    """
    Base class for session-related errors.

    Raised when session operations fail.
    """
    pass


class SessionNotFoundError(SessionError):
    """
    Raised when a session cannot be found.

    Attributes:
        session_path: Path to the session
        session_id: ID of the session
    """

    def __init__(self, message, session_path=None, session_id=None):
        super().__init__(message)
        self.session_path = session_path
        self.session_id = session_id


class InvalidSessionError(SessionError):
    """
    Raised when a session is invalid or corrupted.

    Attributes:
        session_path: Path to the invalid session
        reason: Reason the session is invalid
    """

    def __init__(self, message, session_path=None, reason=None):
        super().__init__(message)
        self.session_path = session_path
        self.reason = reason


# ============================================================================
# Epoch Errors
# ============================================================================

class EpochError(NDIError):
    """
    Base class for epoch-related errors.

    Raised when epoch operations fail.
    """
    pass


class InvalidEpochError(EpochError):
    """
    Raised when an epoch is invalid.

    Attributes:
        epoch_number: The invalid epoch number
        epoch_id: The invalid epoch ID
        reason: Reason the epoch is invalid
    """

    def __init__(self, message, epoch_number=None, epoch_id=None, reason=None):
        super().__init__(message)
        self.epoch_number = epoch_number
        self.epoch_id = epoch_id
        self.reason = reason


class EpochNotFoundError(EpochError):
    """
    Raised when an epoch cannot be found.

    Attributes:
        epoch_number: The epoch number that was not found
        epoch_id: The epoch ID that was not found
    """

    def __init__(self, message, epoch_number=None, epoch_id=None):
        super().__init__(message)
        self.epoch_number = epoch_number
        self.epoch_id = epoch_id


# ============================================================================
# Probe Errors
# ============================================================================

class ProbeError(NDIError):
    """
    Base class for probe-related errors.

    Raised when probe operations fail.
    """
    pass


class InvalidProbeError(ProbeError):
    """
    Raised when a probe is invalid.

    Attributes:
        probe_name: Name of the invalid probe
        reason: Reason the probe is invalid
    """

    def __init__(self, message, probe_name=None, reason=None):
        super().__init__(message)
        self.probe_name = probe_name
        self.reason = reason


class ProbeNotFoundError(ProbeError):
    """
    Raised when a probe cannot be found.

    Attributes:
        probe_name: Name of the probe that was not found
    """

    def __init__(self, message, probe_name=None):
        super().__init__(message)
        self.probe_name = probe_name


# ============================================================================
# Validation Errors
# ============================================================================

class ValidationError(NDIError):
    """
    Base class for validation errors.

    Raised when validation fails.
    """
    pass


class SchemaValidationError(ValidationError):
    """
    Raised when JSON schema validation fails.

    Attributes:
        schema_name: Name of the schema that failed validation
        validation_errors: List of validation errors
    """

    def __init__(self, message, schema_name=None, validation_errors=None):
        super().__init__(message)
        self.schema_name = schema_name
        self.validation_errors = validation_errors or []


class DataValidationError(ValidationError):
    """
    Raised when data validation fails.

    Attributes:
        field: The field that failed validation
        value: The invalid value
        expected: Description of expected value
    """

    def __init__(self, message, field=None, value=None, expected=None):
        super().__init__(message)
        self.field = field
        self.value = value
        self.expected = expected


# ============================================================================
# Utility Functions
# ============================================================================

def format_exception(exc: Exception, include_traceback: bool = False) -> str:
    """
    Format an exception for user-friendly display.

    Args:
        exc: The exception to format
        include_traceback: Whether to include full traceback

    Returns:
        Formatted exception string
    """
    import traceback

    if isinstance(exc, NDIError):
        # For NDI errors, format with attributes
        msg = f"{exc.__class__.__name__}: {str(exc)}"

        # Add attributes if they exist
        attrs = []
        for attr in dir(exc):
            if not attr.startswith('_') and attr not in ['args', 'with_traceback']:
                value = getattr(exc, attr, None)
                if value is not None and not callable(value):
                    attrs.append(f"{attr}={repr(value)}")

        if attrs:
            msg += f" ({', '.join(attrs)})"

        if include_traceback:
            msg += "\n\nTraceback:\n" + ''.join(traceback.format_tb(exc.__traceback__))

        return msg
    else:
        # For non-NDI errors, use default formatting
        if include_traceback:
            return ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        else:
            return f"{exc.__class__.__name__}: {str(exc)}"
