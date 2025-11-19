# Python Cloud Integration - Session Handoff Document

**Date**: November 19, 2025
**Purpose**: Complete integration of Python NDI client with operational Node.js backend
**Estimated Effort**: 42-82 hours (1-2 weeks)

---

## Executive Summary

### Key Discovery
The NDI Cloud backend **already exists and is operational** at `api.ndi-cloud.com`. The Python client has all low-level API classes but is missing ~10 high-level convenience functions. Integration requires **1-2 weeks of development**, not 6 months.

### Current Status
- ✅ **Backend**: Operational (Node.js/TypeScript on AWS Lambda)
- ✅ **Python low-level API**: Complete (GetDocument, CreateDataset, etc.)
- ❌ **Python high-level functions**: 60-70% complete (missing convenience wrappers)
- ❌ **Test failures**: 47 tests (36 missing functions, 8 cffi, 3 bugs)

### Success Criteria
- [ ] All 47 cloud tests passing (145/145 total tests)
- [ ] Can authenticate and get JWT token
- [ ] Can upload local dataset to cloud
- [ ] Can download cloud dataset locally
- [ ] Documentation complete

---

## Background Documents (Read These First!)

1. **PYTHON_CLOUD_INTEGRATION_ANALYSIS.md** - Detailed test failure analysis
2. **PYTHON_CLOUD_INTEGRATION_GUIDE.md** - Step-by-step integration guide with examples
3. **CLOUD_INFRASTRUCTURE_NEEDED.md** - Updated infrastructure status (v2.0)

---

## Task Breakdown

### Phase 1: Quick Fixes (1-2 hours) 🔴 DO THIS FIRST

#### Task 1.1: Fix Float Infinity Bug (30 min)

**File**: `ndi-python/ndi/cloud/upload/upload_collection.py`
**Line**: 201
**Issue**: Cannot convert float('inf') to integer

**Current Code**:
```python
end_index = min(i + int(max_document_chunk), doc_count)
```

**Fixed Code**:
```python
if max_document_chunk == float('inf'):
    end_index = doc_count
else:
    end_index = min(i + int(max_document_chunk), doc_count)
```

**Tests Fixed**: 2 tests in `test_cloud_upload.py`
- `test_upload_batch_mode_success`
- `test_upload_failure_handling`

---

#### Task 1.2: Install cffi Package (5 min)

**Command**:
```bash
cd ndi-python
pip install cffi

# If that doesn't work, try:
pip uninstall cryptography
pip install --no-binary :all: cryptography
```

**Tests Fixed**: 8 tests in `test_cloud_internal.py`
- All JWT decoding tests
- All token expiration tests

**Verification**:
```bash
python3 -c "import cffi; print('cffi installed successfully')"
python3 -m pytest tests/test_cloud_internal.py::TestDecodeJWT::test_decode_jwt_with_pyjwt -xvs
```

---

#### Task 1.3: Fix Test Recursion Issue (30 min)

**File**: `ndi-python/tests/test_cloud_upload.py`
**Line**: 320
**Issue**: Test mocks `os.path.join` then calls it, causing infinite recursion

**Current Code** (problematic):
```python
with patch('os.path.join', side_effect=lambda *args: os.path.join(*args) if args[0] != mock_database.path else os.path.join(tmpdir, args[-1])):
    # ... test code
```

**Fixed Code**:
```python
# Instead of mocking os.path.join globally, mock the database.path attribute
with patch.object(mock_database, 'path', tmpdir):
    success, msg = zip_for_upload(
        mock_database,
        doc_file_struct,
        total_size=22 / 1024,
        dataset_id='test_dataset',
        verbose=False,
        debug_log=False
    )
```

**Tests Fixed**: 1 test
- `test_zip_and_upload_success`

---

### Phase 2: Implement Missing Functions (16-24 hours) 🔴 CRITICAL

#### Task 2.1: Implement get_bulk_download_url() (2-3 hours)

**File**: `ndi-python/ndi/cloud/api/documents.py`
**Location**: Add after line 159 (after `document_count()` function)

**Code to Add**:
```python
class GetBulkDownloadUrl(CloudAPICall):
    """Request bulk download URL for multiple documents."""

    def __init__(self, token: str, dataset_id: str, document_ids: List[str]):
        super().__init__()
        self.token = token
        self.dataset_id = dataset_id
        self.document_ids = document_ids
        self.endpoint_name = 'bulk_download_documents'

    def execute(self) -> Tuple[bool, Any, requests.Response, str]:
        api_url = self.get_api_url(self.endpoint_name, dataset_id=self.dataset_id)
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        data = {'documentIds': self.document_ids}
        response = requests.post(api_url, json=data, headers=headers)

        if response.status_code == 200:
            return True, response.json(), response, api_url
        else:
            return False, response.json() if response.text else response.text, response, api_url


def get_bulk_download_url(token: str, dataset_id: str, document_ids: List[str]) -> Tuple[bool, Any, requests.Response, str]:
    """Convenience function for getting bulk download URL."""
    api_call = GetBulkDownloadUrl(token, dataset_id, document_ids)
    return api_call.execute()
```

**Also Update**: Add to `__all__` export list at top of file:
```python
__all__ = [
    # ... existing exports ...
    'GetBulkDownloadUrl',
    'get_bulk_download_url',
]
```

**Tests Fixed**: 5 tests in `test_cloud_download.py`

---

#### Task 2.2: Implement list_remote_document_ids() (3-4 hours)

**File**: `ndi-python/ndi/cloud/internal/list_remote_documents.py` (CREATE NEW)

**Full File Content**:
```python
"""
List remote document IDs from a cloud dataset.
"""

from typing import Dict, List, Optional
from ..api.documents import list_dataset_documents
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
        success, data, response, url = list_dataset_documents(
            token=token,
            dataset_id=dataset_id,
            page=page,
            page_size=page_size
        )

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
```

**Update**: `ndi-python/ndi/cloud/internal/__init__.py` (add export)
```python
from .list_remote_documents import list_remote_document_ids

__all__ = [
    # ... existing exports ...
    'list_remote_document_ids',
]
```

**Tests Fixed**: 2 tests in `test_cloud_download.py`

---

#### Task 2.3: Fix get_cloud_dataset_id_for_local_dataset() Import (30 min)

**File**: `ndi-python/ndi/cloud/internal/get_cloud_dataset_id_for_local_dataset.py`
**Line**: ~60
**Issue**: Tries to `import query` but should import `Query` class

**Find This Line**:
```python
from ndi.query import query
```

**Replace With**:
```python
from ndi.query import Query
```

**Find This Line** (in function body):
```python
q = query('', isa='dataset_remote')
```

**Replace With**:
```python
q = Query('', isa='dataset_remote')
```

**Tests Fixed**: 4 tests in `test_cloud_internal.py`
- All `TestGetCloudDatasetIdForLocalDataset` tests

---

#### Task 2.4: Implement list_datasets() (2-3 hours)

**File**: `ndi-python/ndi/cloud/internal/list_datasets.py` (CREATE NEW)

**Full File Content**:
```python
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
```

**Update**: `ndi-python/ndi/cloud/internal/__init__.py`
```python
from .list_datasets import list_datasets

__all__ = [
    # ... existing exports ...
    'list_datasets',
]
```

**Tests Fixed**: 6 tests in `test_cloud_internal.py`
- All `TestGetUploadedFileIds` tests

---

#### Task 2.5: Add Missing Sync Module Imports (2-3 hours)

**Problem**: Sync modules exist but don't import required internal functions

**Files to Update**:
1. `ndi-python/ndi/cloud/sync/two_way_sync.py`
2. `ndi-python/ndi/cloud/sync/mirror_to_remote.py`
3. `ndi-python/ndi/cloud/sync/mirror_from_remote.py`
4. `ndi-python/ndi/cloud/sync/upload_new.py`
5. `ndi-python/ndi/cloud/sync/download_new.py`
6. `ndi-python/ndi/cloud/sync/sync_mode.py`

**For Each File**, add these imports at the top:
```python
from ..internal.get_cloud_dataset_id_for_local_dataset import get_cloud_dataset_id_for_local_dataset
from ..internal.list_remote_documents import list_remote_document_ids
from ..upload.upload_collection import upload_document_collection
from ..download.download_collection import download_document_collection
```

**For sync_mode.py specifically**, also add:
```python
from .upload_new import upload_new
from .download_new import download_new
from .two_way_sync import two_way_sync
from .mirror_to_remote import mirror_to_remote
from .mirror_from_remote import mirror_from_remote
```

**Tests Fixed**: 15 tests in `test_cloud_sync.py`

---

#### Task 2.6: Create files_api Module (3-4 hours)

**File**: `ndi-python/ndi/cloud/api/files.py` - This file exists but may need helper functions

**Check if these functions exist**:
- `get_file_details()`
- `get_download_url()`

**If missing, add**:
```python
class GetFileDetails(CloudAPICall):
    """Get file details including download URL."""

    def __init__(self, token: str, dataset_id: str, file_id: str):
        super().__init__()
        self.token = token
        self.dataset_id = dataset_id
        self.file_id = file_id
        self.endpoint_name = 'get_file_details'

    def execute(self) -> Tuple[bool, Any, requests.Response, str]:
        api_url = self.get_api_url(
            self.endpoint_name,
            dataset_id=self.dataset_id,
            file_id=self.file_id
        )
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            return True, response.json(), response, api_url
        else:
            return False, response.json() if response.text else response.text, response, api_url


def get_file_details(token: str, dataset_id: str, file_id: str) -> Tuple[bool, Any, requests.Response, str]:
    """Get file details."""
    api_call = GetFileDetails(token, dataset_id, file_id)
    return api_call.execute()
```

**Tests Fixed**: 2 tests in `test_cloud_download.py`

---

#### Task 2.7: Create DatasetDir Class (3-4 hours)

**File**: `ndi-python/ndi/cloud/download/dataset_dir.py` (CREATE NEW)

**Purpose**: Manage local dataset directory structure

**Minimal Implementation**:
```python
"""
Dataset directory management for cloud downloads.
"""

import os
from pathlib import Path
from typing import Optional


class DatasetDir:
    """Manages local dataset directory structure."""

    def __init__(self, path: str, create: bool = True):
        """
        Initialize dataset directory.

        Args:
            path: Path to dataset directory
            create: If True, create directory structure if it doesn't exist
        """
        self.path = Path(path)

        if create:
            self.path.mkdir(parents=True, exist_ok=True)
            self.docs_path.mkdir(exist_ok=True)
            self.files_path.mkdir(exist_ok=True)

    @property
    def docs_path(self) -> Path:
        """Path to documents directory."""
        return self.path / 'documents'

    @property
    def files_path(self) -> Path:
        """Path to files directory."""
        return self.path / 'files'

    def get_doc_path(self, doc_id: str) -> Path:
        """Get path for a specific document JSON file."""
        return self.docs_path / f'{doc_id}.json'

    def get_file_path(self, file_name: str) -> Path:
        """Get path for a specific data file."""
        return self.files_path / file_name

    def exists(self) -> bool:
        """Check if dataset directory exists."""
        return self.path.exists()

    def is_empty(self) -> bool:
        """Check if dataset directory is empty."""
        if not self.exists():
            return True
        return not any(self.path.iterdir())
```

**Update**: `ndi-python/ndi/cloud/download/__init__.py`
```python
from .dataset_dir import DatasetDir

__all__ = [
    # ... existing exports ...
    'DatasetDir',
]
```

**Tests Fixed**: 1 test in `test_cloud_download.py`

---

### Phase 3: Integration Testing (16-24 hours) 🟡 IMPORTANT

#### Task 3.1: Get NDI Cloud Account (1-2 hours)

**Action Items**:
1. Contact NDI Cloud administrators (check repo README or website)
2. Request account on `dev-api.ndi-cloud.com`
3. Get added to an organization (required for dataset uploads)
4. Save credentials securely

**Deliverable**: Email and password for dev environment

---

#### Task 3.2: Configure Authentication (30 min)

**Test Authentication**:
```bash
cd ndi-python
python3 << 'EOF'
from ndi.cloud.api.auth import Login
import os

# Replace with your actual credentials
email = "your.email@example.com"
password = "your_password"

login_call = Login(email=email, password=password)
success, data, response, url = login_call.execute()

if success:
    token = data['idToken']
    print(f"✅ Login successful!")
    print(f"Token expires: {data.get('expiresAt', 'unknown')}")

    # Save token
    os.environ['NDI_CLOUD_TOKEN'] = token

    # Also save to file
    with open(os.path.expanduser('~/.ndi_cloud_token'), 'w') as f:
        f.write(token)
    print(f"Token saved to ~/.ndi_cloud_token")
else:
    print(f"❌ Login failed: {data}")
    print(f"Status code: {response.status_code}")
EOF
```

**Deliverable**: Working JWT token stored in `~/.ndi_cloud_token`

---

#### Task 3.3: Run Cloud Tests (4-6 hours)

**Test Sequence**:

```bash
# Set environment
export NDI_CLOUD_TOKEN=$(cat ~/.ndi_cloud_token)
export NDI_CLOUD_ENV="development"

# 1. Test admin functions (should already pass)
python3 -m pytest tests/test_cloud_admin.py -v
# Expected: 34/34 passing

# 2. Test utility functions (should already pass)
python3 -m pytest tests/test_cloud_utility.py -v
# Expected: 19/19 passing

# 3. Test internal functions (after implementing missing functions)
python3 -m pytest tests/test_cloud_internal.py -v
# Expected: 22/22 passing (after Phase 2 tasks)

# 4. Test download functions
python3 -m pytest tests/test_cloud_download.py -v
# Expected: 17/17 passing

# 5. Test sync functions
python3 -m pytest tests/test_cloud_sync.py -v
# Expected: 15/15 passing

# 6. Test upload functions
python3 -m pytest tests/test_cloud_upload.py -v
# Expected: 45/45 passing

# 7. Full cloud test suite
python3 -m pytest tests/test_cloud*.py -v
# Expected: 145/145 passing
```

**Troubleshooting**:
- If auth fails: Check token hasn't expired, regenerate if needed
- If 403 errors: Verify organization membership
- If 404 errors: Check API endpoint URLs in `ndi/cloud/api/base.py`

---

#### Task 3.4: End-to-End Test (4-6 hours)

**Create Integration Test Script**: `ndi-python/test_integration.py`

```python
"""
End-to-end integration test for NDI Cloud.
Tests: Create dataset → Upload docs → Download → Verify
"""

import os
import tempfile
import json
from pathlib import Path

from ndi.cloud.api.auth import Login
from ndi.cloud.api.datasets import CreateDataset, GetDataset, DeleteDataset
from ndi.cloud.api.documents import AddDocument, ListDatasetDocuments, GetDocument


def test_full_integration():
    """Complete round-trip test."""

    # 1. Authenticate
    print("1. Authenticating...")
    email = os.getenv('NDI_CLOUD_EMAIL')
    password = os.getenv('NDI_CLOUD_PASSWORD')

    login_call = Login(email=email, password=password)
    success, data, _, _ = login_call.execute()
    assert success, f"Login failed: {data}"

    token = data['idToken']
    print("   ✓ Authenticated")

    # 2. Create test dataset
    print("2. Creating dataset...")
    dataset_data = {
        'name': f'Integration Test Dataset',
        'abstract': 'Automated test dataset',
        'license': 'CC-BY-4.0'
    }

    create_call = CreateDataset(token=token, dataset_data=dataset_data)
    success, data, _, _ = create_call.execute()
    assert success, f"Create dataset failed: {data}"

    dataset_id = data['x_id']
    print(f"   ✓ Created dataset {dataset_id}")

    try:
        # 3. Add document
        print("3. Adding document...")
        doc_data = {
            'document_properties': {
                'base': {
                    'id': 'test_doc_001',
                    'type': 'ndi.test.document',
                    'session_id': 'test_session'
                },
                'definition': {
                    'name': 'Test Document',
                    'description': 'Integration test'
                }
            }
        }

        add_call = AddDocument(token=token, dataset_id=dataset_id, document_data=doc_data)
        success, data, _, _ = add_call.execute()
        assert success, f"Add document failed: {data}"

        doc_id = data['id']
        print(f"   ✓ Added document {doc_id}")

        # 4. List documents
        print("4. Listing documents...")
        list_call = ListDatasetDocuments(token=token, dataset_id=dataset_id)
        success, data, _, _ = list_call.execute()
        assert success, f"List documents failed: {data}"
        assert len(data['documents']) == 1, "Should have 1 document"
        print(f"   ✓ Found {len(data['documents'])} document(s)")

        # 5. Get specific document
        print("5. Retrieving document...")
        get_call = GetDocument(token=token, dataset_id=dataset_id, document_id=doc_id)
        success, data, _, _ = get_call.execute()
        assert success, f"Get document failed: {data}"
        assert data['base']['id'] == 'test_doc_001'
        print("   ✓ Retrieved document successfully")

        # 6. Verify dataset state
        print("6. Verifying dataset...")
        get_ds_call = GetDataset(token=token, dataset_id=dataset_id)
        success, data, _, _ = get_ds_call.execute()
        assert success, f"Get dataset failed: {data}"
        assert data['documentCount'] == 1
        print(f"   ✓ Dataset verified (documentCount={data['documentCount']})")

    finally:
        # 7. Cleanup
        print("7. Cleaning up...")
        delete_call = DeleteDataset(token=token, dataset_id=dataset_id)
        success, data, _, _ = delete_call.execute()
        assert success, f"Delete failed: {data}"
        print("   ✓ Test dataset deleted")

    print("\n✅ Integration test PASSED!")


if __name__ == '__main__':
    # Set credentials from environment
    if not os.getenv('NDI_CLOUD_EMAIL'):
        print("Set NDI_CLOUD_EMAIL and NDI_CLOUD_PASSWORD environment variables")
        exit(1)

    test_full_integration()
```

**Run Test**:
```bash
export NDI_CLOUD_EMAIL="your.email@example.com"
export NDI_CLOUD_PASSWORD="your_password"
python3 test_integration.py
```

**Expected Output**:
```
1. Authenticating...
   ✓ Authenticated
2. Creating dataset...
   ✓ Created dataset abc123
3. Adding document...
   ✓ Added document doc456
4. Listing documents...
   ✓ Found 1 document(s)
5. Retrieving document...
   ✓ Retrieved document successfully
6. Verifying dataset...
   ✓ Dataset verified (documentCount=1)
7. Cleaning up...
   ✓ Test dataset deleted

✅ Integration test PASSED!
```

---

### Phase 4: Documentation (8-16 hours) 🟢 OPTIONAL

#### Task 4.1: Update Integration Guide (4-6 hours)

Update `PYTHON_CLOUD_INTEGRATION_GUIDE.md` with:
- Real-world examples using live backend
- Troubleshooting section
- Performance tips
- Security best practices

#### Task 4.2: Create Example Scripts (4-6 hours)

Create `ndi-python/examples/cloud/`:
- `01_authenticate.py` - Login and save token
- `02_create_dataset.py` - Create and configure dataset
- `03_upload_documents.py` - Upload documents to cloud
- `04_download_dataset.py` - Download dataset locally
- `05_sync_datasets.py` - Two-way sync example

#### Task 4.3: Update README (2-4 hours)

Update `ndi-python/README.md` with:
- Cloud features section
- Quick start guide
- Link to integration guide

---

## Testing Checklist

### Before Starting
- [ ] Read all three background documents
- [ ] Have Python 3.11+ installed
- [ ] Have git access to NDI-matlab repo
- [ ] Understand NDI architecture basics

### Phase 1: Quick Fixes
- [ ] Float infinity bug fixed
- [ ] cffi installed successfully
- [ ] Test recursion issue resolved
- [ ] 11/47 tests now passing

### Phase 2: Missing Functions
- [ ] `get_bulk_download_url()` implemented
- [ ] `list_remote_document_ids()` implemented
- [ ] `get_cloud_dataset_id_for_local_dataset()` import fixed
- [ ] `list_datasets()` implemented
- [ ] Sync module imports added
- [ ] `files_api` helpers created
- [ ] `DatasetDir` class implemented
- [ ] 47/47 tests now passing

### Phase 3: Integration
- [ ] NDI Cloud account obtained
- [ ] Authentication working
- [ ] Can create dataset on cloud
- [ ] Can upload documents
- [ ] Can download documents
- [ ] End-to-end test passes

### Phase 4: Documentation
- [ ] Integration guide updated
- [ ] Example scripts created
- [ ] README updated
- [ ] User-facing docs complete

---

## Common Issues & Solutions

### Issue: Tests fail with "No module named '_cffi_backend'"
**Solution**: Install cffi: `pip install cffi`

### Issue: Tests fail with "NDI_CLOUD_TOKEN not set"
**Solution**:
```bash
export NDI_CLOUD_TOKEN=$(cat ~/.ndi_cloud_token)
# Or login and save token first
```

### Issue: 403 Forbidden errors
**Solution**:
- Check token hasn't expired (tokens expire after ~1 hour)
- Verify you're in an organization
- Contact admin to grant permissions

### Issue: 404 Not Found errors
**Solution**: Check API environment setting:
```python
# In ndi/cloud/api/base.py
# Verify get_api_base_url() returns correct URL
```

### Issue: Import errors after adding new files
**Solution**: Update `__init__.py` files to export new functions

---

## Success Metrics

### Minimum Success (Phase 1-2)
- ✅ All 145 cloud tests passing (47 previously failing now fixed)
- ✅ Can import all cloud modules without errors
- ✅ Low-level API calls work with mocks

### Full Success (Phase 1-3)
- ✅ All above +
- ✅ Can authenticate with live backend
- ✅ Can create/read/update/delete datasets on cloud
- ✅ Can upload/download documents
- ✅ End-to-end integration test passes

### Production Ready (Phase 1-4)
- ✅ All above +
- ✅ Complete documentation
- ✅ Example scripts working
- ✅ User guide published
- ✅ All 34 stub implementations complete (optional, for 100%)

---

## Time Estimates (Realistic)

| Phase | Optimistic | Realistic | Pessimistic |
|-------|------------|-----------|-------------|
| Phase 1 (fixes) | 1 hour | 2 hours | 4 hours |
| Phase 2 (functions) | 12 hours | 20 hours | 32 hours |
| Phase 3 (integration) | 8 hours | 16 hours | 24 hours |
| Phase 4 (docs) | 6 hours | 12 hours | 20 hours |
| **Total** | **27 hours** | **50 hours** | **80 hours** |

---

## Recommended Approach

### Week 1 (40 hours)
- **Day 1-2**: Phase 1 + start Phase 2 (quick fixes + first 3 functions)
- **Day 3-4**: Finish Phase 2 (remaining functions)
- **Day 5**: Phase 3 start (get account, test auth)

### Week 2 (40 hours)
- **Day 1-2**: Finish Phase 3 (integration testing)
- **Day 3-5**: Phase 4 (documentation and examples)

### Total: **80 hours = 2 weeks**

---

## Getting Help

If stuck, check these resources:
1. **Test files**: See how tests expect functions to behave
2. **Node.js backend**: Check `ndi-cloud-node` repo for API contracts
3. **MATLAB code**: Original implementation (though cloud client doesn't exist there)
4. **API docs**: https://api.ndi-cloud.com/docs (if available)

---

## Final Notes

- **Prioritize Phase 1-2**: These fix the test failures
- **Phase 3 requires credentials**: Get account early
- **Phase 4 is optional**: Can ship with minimal docs
- **Test incrementally**: Don't wait until end to run tests
- **Commit frequently**: One commit per task is fine

---

**Document Version**: 1.0
**Created**: November 19, 2025
**Next Session**: Start with Phase 1, Task 1.1
**Estimated Completion**: November 29, 2025 (2 weeks from now)

Good luck! 🚀
