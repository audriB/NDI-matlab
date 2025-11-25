"""
NDI Cloud API Documents - Document management operations.

This module provides document-related API calls for the NDI Cloud.
"""

from typing import Dict, Any, Tuple, Optional, List
import requests
from .base import CloudAPICall


class GetDocument(CloudAPICall):
    """Get a document from a dataset."""

    def __init__(self, token: str, dataset_id: str, document_id: str):
        super().__init__()
        self.token = token
        self.dataset_id = dataset_id
        self.document_id = document_id
        self.endpoint_name = 'get_document'

    def execute(self) -> Tuple[bool, Any, requests.Response, str]:
        api_url = self.get_api_url(self.endpoint_name, dataset_id=self.dataset_id, document_id=self.document_id)
        headers = {'Accept': 'application/json', 'Authorization': f'Bearer {self.token}'}
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            return True, response.json(), response, api_url
        else:
            return False, response.json() if response.text else response.text, response, api_url


class ListDatasetDocuments(CloudAPICall):
    """List documents in a dataset (paginated)."""

    def __init__(self, token: str, dataset_id: str, page: int = 1, page_size: int = 20):
        super().__init__()
        self.token = token
        self.dataset_id = dataset_id
        self.page = page
        self.page_size = page_size
        self.endpoint_name = 'list_dataset_documents'

    def execute(self) -> Tuple[bool, Any, requests.Response, str]:
        api_url = self.get_api_url(self.endpoint_name, dataset_id=self.dataset_id, page=self.page, page_size=self.page_size)
        headers = {'Accept': 'application/json', 'Authorization': f'Bearer {self.token}'}
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            return True, response.json(), response, api_url
        else:
            return False, response.json() if response.text else response.text, response, api_url


class AddDocument(CloudAPICall):
    """Add a document to a dataset."""

    def __init__(self, token: str, dataset_id: str, document_data: Dict[str, Any]):
        super().__init__()
        self.token = token
        self.dataset_id = dataset_id
        self.document_data = document_data
        self.endpoint_name = 'add_document'

    def execute(self) -> Tuple[bool, Any, requests.Response, str]:
        api_url = self.get_api_url(self.endpoint_name, dataset_id=self.dataset_id)
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {self.token}'}
        response = requests.post(api_url, json=self.document_data, headers=headers)
        if response.status_code in [200, 201]:
            return True, response.json(), response, api_url
        else:
            return False, response.json() if response.text else response.text, response, api_url


class UpdateDocument(CloudAPICall):
    """Update a document in a dataset."""

    def __init__(self, token: str, dataset_id: str, document_id: str, document_data: Dict[str, Any]):
        super().__init__()
        self.token = token
        self.dataset_id = dataset_id
        self.document_id = document_id
        self.document_data = document_data
        self.endpoint_name = 'update_document'

    def execute(self) -> Tuple[bool, Any, requests.Response, str]:
        api_url = self.get_api_url(self.endpoint_name, dataset_id=self.dataset_id, document_id=self.document_id)
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {self.token}'}
        response = requests.put(api_url, json=self.document_data, headers=headers)
        if response.status_code == 200:
            return True, response.json(), response, api_url
        else:
            return False, response.json() if response.text else response.text, response, api_url


class DeleteDocument(CloudAPICall):
    """Delete a document from a dataset."""

    def __init__(self, token: str, dataset_id: str, document_id: str):
        super().__init__()
        self.token = token
        self.dataset_id = dataset_id
        self.document_id = document_id
        self.endpoint_name = 'delete_document'

    def execute(self) -> Tuple[bool, Any, requests.Response, str]:
        api_url = self.get_api_url(self.endpoint_name, dataset_id=self.dataset_id, document_id=self.document_id)
        headers = {'Accept': 'application/json', 'Authorization': f'Bearer {self.token}'}
        response = requests.delete(api_url, headers=headers)
        if response.status_code in [200, 204]:
            return True, response.json() if response.text else {}, response, api_url
        else:
            return False, response.json() if response.text else response.text, response, api_url


class DocumentCount(CloudAPICall):
    """Get document count for a dataset."""

    def __init__(self, token: str, dataset_id: str):
        super().__init__()
        self.token = token
        self.dataset_id = dataset_id
        self.endpoint_name = 'document_count'

    def execute(self) -> Tuple[bool, Any, requests.Response, str]:
        api_url = self.get_api_url(self.endpoint_name, dataset_id=self.dataset_id)
        headers = {'Accept': 'application/json', 'Authorization': f'Bearer {self.token}'}
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            return True, response.json(), response, api_url
        else:
            return False, response.json() if response.text else response.text, response, api_url


# Convenience functions
def get_document(token: str, dataset_id: str, document_id: str) -> Tuple[bool, Any, requests.Response, str]:
    """Get a document by ID."""
    return GetDocument(token, dataset_id, document_id).execute()


def list_dataset_documents(token: str, dataset_id: str, page: int = 1, page_size: int = 20) -> Tuple[bool, Any, requests.Response, str]:
    """List documents in a dataset."""
    return ListDatasetDocuments(token, dataset_id, page, page_size).execute()


def add_document(token: str, dataset_id: str, document_data: Dict[str, Any]) -> Tuple[bool, Any, requests.Response, str]:
    """Add a document to a dataset."""
    return AddDocument(token, dataset_id, document_data).execute()


def update_document(token: str, dataset_id: str, document_id: str, document_data: Dict[str, Any]) -> Tuple[bool, Any, requests.Response, str]:
    """Update a document."""
    return UpdateDocument(token, dataset_id, document_id, document_data).execute()


def delete_document(token: str, dataset_id: str, document_id: str) -> Tuple[bool, Any, requests.Response, str]:
    """Delete a document."""
    return DeleteDocument(token, dataset_id, document_id).execute()


def document_count(token: str, dataset_id: str) -> Tuple[bool, Any, requests.Response, str]:
    """Get document count for a dataset."""
    return DocumentCount(token, dataset_id).execute()


class GetBulkDownloadUrl(CloudAPICall):
    """Get a pre-signed URL for bulk document download.

    This initiates an async process that creates a ZIP file containing
    all requested documents. The returned URL can be used to download
    the ZIP once it's ready.
    """

    def __init__(self, token: str, dataset_id: str, document_ids: Optional[List[str]] = None):
        super().__init__()
        self.token = token
        self.dataset_id = dataset_id
        self.document_ids = document_ids  # None means all documents
        self.endpoint_name = 'bulk_download_documents'

    def execute(self) -> Tuple[bool, Any, requests.Response, str]:
        api_url = self.get_api_url(self.endpoint_name, dataset_id=self.dataset_id)
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        # POST with optional document IDs filter
        body = {}
        if self.document_ids:
            body['documentIds'] = self.document_ids
        response = requests.post(api_url, json=body, headers=headers)
        if response.status_code in [200, 201, 202]:
            return True, response.json(), response, api_url
        else:
            return False, response.json() if response.text else response.text, response, api_url


class BulkDeleteDocuments(CloudAPICall):
    """Delete multiple documents from a dataset in one call."""

    def __init__(self, token: str, dataset_id: str, document_ids: List[str]):
        super().__init__()
        self.token = token
        self.dataset_id = dataset_id
        self.document_ids = document_ids
        self.endpoint_name = 'bulk_delete_documents'

    def execute(self) -> Tuple[bool, Any, requests.Response, str]:
        api_url = self.get_api_url(self.endpoint_name, dataset_id=self.dataset_id)
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        body = {'documentIds': self.document_ids}
        response = requests.post(api_url, json=body, headers=headers)
        if response.status_code in [200, 204]:
            return True, response.json() if response.text else {}, response, api_url
        else:
            return False, response.json() if response.text else response.text, response, api_url


class GetBulkUploadUrl(CloudAPICall):
    """Get a pre-signed URL for bulk document upload.

    Returns a URL where a ZIP file containing JSON documents can be uploaded.
    The backend will process the ZIP and add documents to the dataset.
    """

    def __init__(self, token: str, dataset_id: str):
        super().__init__()
        self.token = token
        self.dataset_id = dataset_id
        self.endpoint_name = 'bulk_upload_documents'

    def execute(self) -> Tuple[bool, Any, requests.Response, str]:
        api_url = self.get_api_url(self.endpoint_name, dataset_id=self.dataset_id)
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            return True, response.json(), response, api_url
        else:
            return False, response.json() if response.text else response.text, response, api_url


# Additional convenience functions
def get_bulk_download_url(token: str, dataset_id: str, document_ids: Optional[List[str]] = None) -> Tuple[bool, Any, requests.Response, str]:
    """Get pre-signed URL for bulk document download.

    Args:
        token: Authentication token
        dataset_id: Dataset ID
        document_ids: Optional list of specific document IDs to download.
                     If None, downloads all documents.

    Returns:
        Tuple of (success, response_data, response, api_url)
        response_data contains the download URL when ready
    """
    return GetBulkDownloadUrl(token, dataset_id, document_ids).execute()


def bulk_delete_documents(token: str, dataset_id: str, document_ids: List[str]) -> Tuple[bool, Any, requests.Response, str]:
    """Delete multiple documents from a dataset.

    Args:
        token: Authentication token
        dataset_id: Dataset ID
        document_ids: List of document IDs to delete

    Returns:
        Tuple of (success, response_data, response, api_url)
    """
    return BulkDeleteDocuments(token, dataset_id, document_ids).execute()


def get_bulk_upload_url(token: str, dataset_id: str) -> Tuple[bool, Any, requests.Response, str]:
    """Get pre-signed URL for bulk document upload.

    Args:
        token: Authentication token
        dataset_id: Dataset ID

    Returns:
        Tuple of (success, response_data, response, api_url)
        response_data contains the upload URL
    """
    return GetBulkUploadUrl(token, dataset_id).execute()


def list_dataset_documents_all(token: str, dataset_id: str, page_size: int = 100) -> Tuple[bool, List[Dict[str, Any]], str]:
    """List ALL documents in a dataset by iterating through all pages.

    Args:
        token: Authentication token
        dataset_id: Dataset ID
        page_size: Number of documents per page (default 100)

    Returns:
        Tuple of (success, all_documents, error_message)
    """
    all_documents = []
    page = 1

    while True:
        success, data, response, api_url = list_dataset_documents(token, dataset_id, page, page_size)

        if not success:
            return False, all_documents, f"Failed to fetch page {page}: {data}"

        # Extract documents from response
        documents = data.get('documents', data.get('data', []))
        if not documents:
            break

        all_documents.extend(documents)

        # Check if there are more pages
        total = data.get('total', data.get('totalCount', len(all_documents)))
        if len(all_documents) >= total:
            break

        page += 1

        # Safety limit to prevent infinite loops
        if page > 10000:
            break

    return True, all_documents, ""
