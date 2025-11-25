"""
NDI Cloud API Files - File management operations.

This module provides file-related API calls for the NDI Cloud.
"""

from typing import Dict, Any, Tuple, Optional, List
import requests
from .base import CloudAPICall


class GetFile(CloudAPICall):
    """Get a file from a dataset."""

    def __init__(self, token: str, dataset_id: str, file_uid: str):
        super().__init__()
        self.token = token
        self.dataset_id = dataset_id
        self.file_uid = file_uid
        self.endpoint_name = 'get_file'

    def execute(self) -> Tuple[bool, Any, requests.Response, str]:
        api_url = self.get_api_url(self.endpoint_name, dataset_id=self.dataset_id, file_uid=self.file_uid)
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            return True, response.content, response, api_url
        else:
            return False, response.json() if response.text else response.text, response, api_url


class GetFileDetails(CloudAPICall):
    """Get file details/metadata."""

    def __init__(self, token: str, dataset_id: str, file_uid: str):
        super().__init__()
        self.token = token
        self.dataset_id = dataset_id
        self.file_uid = file_uid
        self.endpoint_name = 'get_file_details'

    def execute(self) -> Tuple[bool, Any, requests.Response, str]:
        api_url = self.get_api_url(self.endpoint_name, dataset_id=self.dataset_id, file_uid=self.file_uid)
        headers = {'Accept': 'application/json', 'Authorization': f'Bearer {self.token}'}
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            return True, response.json(), response, api_url
        else:
            return False, response.json() if response.text else response.text, response, api_url


class GetFileUploadURL(CloudAPICall):
    """Get a pre-signed URL for file upload."""

    def __init__(self, token: str, organization_id: str, dataset_id: str, file_uid: str):
        super().__init__()
        self.token = token
        self.organization_id = organization_id
        self.dataset_id = dataset_id
        self.file_uid = file_uid
        self.endpoint_name = 'get_file_upload_url'

    def execute(self) -> Tuple[bool, Any, requests.Response, str]:
        api_url = self.get_api_url(self.endpoint_name, organization_id=self.organization_id,
                                   dataset_id=self.dataset_id, file_uid=self.file_uid)
        headers = {'Accept': 'application/json', 'Authorization': f'Bearer {self.token}'}
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            return True, response.json(), response, api_url
        else:
            return False, response.json() if response.text else response.text, response, api_url


class ListFiles(CloudAPICall):
    """List files in a dataset."""

    def __init__(self, token: str, dataset_id: str):
        super().__init__()
        self.token = token
        self.dataset_id = dataset_id
        self.endpoint_name = 'list_files'

    def execute(self) -> Tuple[bool, Any, requests.Response, str]:
        api_url = self.get_api_url(self.endpoint_name, dataset_id=self.dataset_id)
        headers = {'Accept': 'application/json', 'Authorization': f'Bearer {self.token}'}
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            return True, response.json(), response, api_url
        else:
            return False, response.json() if response.text else response.text, response, api_url


# Convenience functions
def get_file(token: str, dataset_id: str, file_uid: str) -> Tuple[bool, Any, requests.Response, str]:
    """Get a file by UID."""
    return GetFile(token, dataset_id, file_uid).execute()


def get_file_details(token: str, dataset_id: str, file_uid: str) -> Tuple[bool, Any, requests.Response, str]:
    """Get file details."""
    return GetFileDetails(token, dataset_id, file_uid).execute()


def get_file_upload_url(token: str, organization_id: str, dataset_id: str, file_uid: str) -> Tuple[bool, Any, requests.Response, str]:
    """Get pre-signed upload URL."""
    return GetFileUploadURL(token, organization_id, dataset_id, file_uid).execute()


def list_files(token: str, dataset_id: str) -> Tuple[bool, Any, requests.Response, str]:
    """List files in a dataset."""
    return ListFiles(token, dataset_id).execute()


class GetFileCollectionUploadUrl(CloudAPICall):
    """Get a pre-signed URL for bulk file upload (ZIP of files).

    Returns a URL where a ZIP file containing raw data files can be uploaded.
    The backend will extract and process the files.
    """

    def __init__(self, token: str, organization_id: str, dataset_id: str):
        super().__init__()
        self.token = token
        self.organization_id = organization_id
        self.dataset_id = dataset_id
        self.endpoint_name = 'get_file_collection_upload_url'

    def execute(self) -> Tuple[bool, Any, requests.Response, str]:
        api_url = self.get_api_url(
            self.endpoint_name,
            organization_id=self.organization_id,
            dataset_id=self.dataset_id
        )
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            return True, response.json(), response, api_url
        else:
            return False, response.json() if response.text else response.text, response, api_url


class PutFiles(CloudAPICall):
    """Upload a file (typically a ZIP) to a pre-signed URL.

    This is used after getting a URL from GetFileCollectionUploadUrl
    to actually upload the file data.
    """

    def __init__(self, upload_url: str, file_data: bytes, content_type: str = 'application/zip'):
        super().__init__()
        self.upload_url = upload_url
        self.file_data = file_data
        self.content_type = content_type
        self.endpoint_name = 'put_files'

    def execute(self) -> Tuple[bool, Any, requests.Response, str]:
        # Upload directly to the pre-signed URL (typically S3)
        headers = {
            'Content-Type': self.content_type
        }
        response = requests.put(self.upload_url, data=self.file_data, headers=headers)
        if response.status_code in [200, 201, 204]:
            return True, {}, response, self.upload_url
        else:
            return False, response.text, response, self.upload_url


class UploadFileToPresignedUrl(CloudAPICall):
    """Upload a single file to a pre-signed URL.

    Args:
        upload_url: The pre-signed URL to upload to
        file_path: Path to the file to upload
    """

    def __init__(self, upload_url: str, file_path: str):
        super().__init__()
        self.upload_url = upload_url
        self.file_path = file_path
        self.endpoint_name = 'upload_file_presigned'

    def execute(self) -> Tuple[bool, Any, requests.Response, str]:
        import os
        import mimetypes

        # Determine content type
        content_type, _ = mimetypes.guess_type(self.file_path)
        if content_type is None:
            content_type = 'application/octet-stream'

        headers = {
            'Content-Type': content_type
        }

        with open(self.file_path, 'rb') as f:
            file_data = f.read()

        response = requests.put(self.upload_url, data=file_data, headers=headers)
        if response.status_code in [200, 201, 204]:
            return True, {}, response, self.upload_url
        else:
            return False, response.text, response, self.upload_url


# Additional convenience functions
def get_file_collection_upload_url(token: str, organization_id: str, dataset_id: str) -> Tuple[bool, Any, requests.Response, str]:
    """Get pre-signed URL for bulk file upload.

    Args:
        token: Authentication token
        organization_id: Organization ID
        dataset_id: Dataset ID

    Returns:
        Tuple of (success, response_data, response, api_url)
        response_data contains the upload URL
    """
    return GetFileCollectionUploadUrl(token, organization_id, dataset_id).execute()


def put_files(upload_url: str, file_data: bytes, content_type: str = 'application/zip') -> Tuple[bool, Any, requests.Response, str]:
    """Upload file data to a pre-signed URL.

    Args:
        upload_url: The pre-signed URL from get_file_collection_upload_url
        file_data: The raw bytes of the file to upload
        content_type: MIME type of the file (default: application/zip)

    Returns:
        Tuple of (success, response_data, response, api_url)
    """
    return PutFiles(upload_url, file_data, content_type).execute()


def upload_file_to_presigned_url(upload_url: str, file_path: str) -> Tuple[bool, Any, requests.Response, str]:
    """Upload a file from disk to a pre-signed URL.

    Args:
        upload_url: The pre-signed URL to upload to
        file_path: Local path to the file to upload

    Returns:
        Tuple of (success, response_data, response, api_url)
    """
    return UploadFileToPresignedUrl(upload_url, file_path).execute()
