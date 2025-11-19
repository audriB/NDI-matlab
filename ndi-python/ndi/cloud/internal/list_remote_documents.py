"""
List remote document IDs from a cloud dataset.
"""

from typing import Dict, List, Optional
from ..api.documents import ListDatasetDocuments
import os


def list_remote_document_ids(dataset_id: str, token: Optional[str] = None) -> Dict[str, List[str]]:
    """
    List all document IDs in a remote dataset.

    Args:
        dataset_id: The cloud dataset ID
        token: JWT authentication token (or get from environment)

    Returns:
        Dictionary with:
            - 'ndi_id': List of NDI document IDs (from document.base.id)
            - 'api_id': List of MongoDB document IDs
    """
    if token is None:
        token = os.getenv('NDI_CLOUD_TOKEN')
        if not token:
            raise ValueError("No token provided and NDI_CLOUD_TOKEN not set")

    all_ndi_ids = []
    all_api_ids = []
    page = 1
    page_size = 100

    while True:
        api_call = ListDatasetDocuments(
            token=token,
            dataset_id=dataset_id,
            page=page,
            page_size=page_size
        )
        success, data, response, url = api_call.execute()

        if not success:
            raise RuntimeError(f"Failed to list documents: {data}")

        documents = data.get('documents', [])
        if not documents:
            break

        for doc in documents:
            # MongoDB ID
            if 'id' in doc:
                all_api_ids.append(doc['id'])
            elif '_id' in doc:
                all_api_ids.append(doc['_id'])

            # NDI ID
            if 'base' in doc and 'id' in doc['base']:
                all_ndi_ids.append(doc['base']['id'])

        # Check if there are more pages
        has_more = data.get('hasMore', False)
        if not has_more or len(documents) < page_size:
            break

        page += 1

    return {
        'ndi_id': all_ndi_ids,
        'api_id': all_api_ids
    }
