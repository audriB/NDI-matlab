"""
List all datasets from cloud with pagination.
"""

from typing import List, Dict, Any, Optional
from ..api.datasets import ListDatasets
import os


def list_datasets(token: Optional[str] = None, is_published: bool = False) -> List[Dict[str, Any]]:
    """
    List all datasets from cloud (handles pagination automatically).

    Args:
        token: JWT authentication token (or get from environment)
        is_published: If True, list public datasets; if False, list user's private datasets

    Returns:
        List of dataset dictionaries
    """
    if token is None and not is_published:
        token = os.getenv('NDI_CLOUD_TOKEN')
        if not token:
            raise ValueError("No token provided and NDI_CLOUD_TOKEN not set")

    all_datasets = []
    page = 1
    page_size = 50

    while True:
        api_call = ListDatasets(
            token=token or "",
            page=page,
            page_size=page_size,
            is_published=is_published
        )
        success, data, response, url = api_call.execute()

        if not success:
            raise RuntimeError(f"Failed to list datasets: {data}")

        datasets = data.get('datasets', [])
        if not datasets:
            break

        all_datasets.extend(datasets)

        # Check if there are more pages
        has_more = data.get('hasMore', False)
        total = data.get('total', 0)

        if not has_more or len(all_datasets) >= total:
            break

        page += 1

    return all_datasets
