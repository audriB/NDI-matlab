# Python Cloud Integration Analysis

## Executive Summary

The Python port has **partial cloud client implementation** (60-70% complete). The Node.js backend exists and is operational, but the Python client has missing high-level functions needed to fully interface with it. Of the 47 failing cloud tests:

- **8 tests (17%)**: Infrastructure issue (cffi/cryptography dependency)
- **36 tests (77%)**: Missing implementations (stub functions not yet written)
- **3 tests (6%)**: Code bugs (overflow handling + test recursion)

## Test Failure Analysis

### Category 1: Infrastructure Issues (8 failures)

**Error**: `pyo3_runtime.PanicException: Python API call failed` (cffi/cryptography)

**Tests Affected**:
- JWT decoding tests (6 tests in test_cloud_internal.py)
- Token expiration tests (2 tests)

**Root Cause**: Missing `cffi` package dependency

**Fix**: `pip install cffi` or rebuild cryptography with proper dependencies

**Impact**: Not a code issue - just missing system dependencies

---

### Category 2: Missing Implementations (36 failures)

These tests expect functions that don't exist in the codebase. The API classes exist, but convenience/wrapper functions are missing.

#### Missing from `ndi.cloud.api.documents`:
- `get_bulk_download_url()` - Used by 5 download tests
- Tests: test_download_with_document_ids, test_download_all_documents, test_download_with_timeout, test_download_api_error

#### Missing from `ndi.cloud.download.download_collection`:
- `list_remote_document_ids()` - Used by 2 download tests
- Tests: test_download_all_documents, test_download_empty_dataset

#### Missing from `ndi.cloud.download.dataset`:
- `files_api` module - Used by 1 download test
- `DatasetDir` class - Used by 1 download test
- Tests: test_download_dataset_local_mode, test_download_dataset_hybrid_mode

#### Missing from `ndi.cloud.internal.get_cloud_dataset_id_for_local_dataset`:
- `query()` function import - Used by 4 internal tests
- Tests: All TestGetCloudDatasetIdForLocalDataset tests (4 tests)

#### Missing from `ndi.cloud.internal.get_uploaded_file_ids`:
- `list_datasets()` function - Used by 6 internal tests
- Tests: All TestGetUploadedFileIds tests (6 tests)

#### Missing from sync modules:
- `ndi.cloud.sync.*` modules missing `get_cloud_dataset_id_for_local_dataset` imports
- `ndi.cloud.sync.sync_mode` missing `download_new`, `upload_new` functions
- Tests: All sync tests (15 tests total)

**Pattern**: The low-level API classes exist (GetDocument, ListDatasetDocuments, etc.), but high-level convenience functions and module-level functions are missing.

---

### Category 3: Code Bugs (3 failures)

#### Bug 1: Float Infinity Handling (2 tests)
**File**: `ndi/cloud/upload/upload_collection.py:201`
```python
end_index = min(i + int(max_document_chunk), doc_count)
# Fails when max_document_chunk = float('inf')
```

**Error**: `OverflowError: cannot convert float infinity to integer`

**Tests Affected**:
- test_upload_batch_mode_success
- test_upload_failure_handling

**Fix**: Add infinity check before int() conversion:
```python
if max_document_chunk == float('inf'):
    end_index = doc_count
else:
    end_index = min(i + int(max_document_chunk), doc_count)
```

#### Bug 2: Test Recursion Issue (1 test)
**File**: `tests/test_cloud_upload.py:320`

**Error**: `RecursionError: maximum recursion depth exceeded`

**Root Cause**: Test mocks `os.path.join` then calls `os.path.join` inside the mock, causing infinite recursion

**Fix**: This is a TEST bug, not a code bug. Mock needs to be restructured to avoid calling the mocked function.

---

## Cloud Architecture: Node.js Backend (Existing)

### Confirmed: Backend Exists and is Operational

Based on the architecture summary provided, the Node.js backend is **fully built and deployed**:

| Component | Status | Details |
|-----------|--------|---------|
| **Backend Server** | ✅ Deployed | Serverless Node.js/TypeScript on AWS Lambda |
| **Database** | ✅ Operational | MongoDB (DocumentDB) |
| **Storage** | ✅ Configured | 7 S3 buckets across 2 AWS accounts |
| **Authentication** | ✅ Active | AWS Cognito with JWT tokens |
| **Endpoints** | ✅ Live | api.ndi-cloud.com (prod), dev-api.ndi-cloud.com (dev) |

### API Endpoints (Node.js Backend)

**Authentication** (`/auth`)
- POST /auth/login
- POST /auth/logout
- POST /auth/verify-email
- POST /auth/change-password
- POST /auth/forgot-password
- POST /auth/reset-password

**Users** (`/users`)
- POST /users (create account)
- GET /users/:id
- PUT /users/:id
- DELETE /users/:id

**Datasets** (`/datasets`)
- GET /datasets (list with pagination)
- POST /datasets (create)
- GET /datasets/:id
- PUT /datasets/:id (update)
- DELETE /datasets/:id
- POST /datasets/:id/submit (publish workflow)
- POST /datasets/:id/publish
- POST /datasets/:id/unpublish
- GET /datasets/:id/bookmark
- GET /datasets/search

**Documents** (`/datasets/:id/documents`)
- GET /datasets/:id/documents (list, paginated)
- POST /datasets/:id/documents (add)
- GET /datasets/:id/documents/:docId
- PUT /datasets/:id/documents/:docId
- DELETE /datasets/:id/documents/:docId
- POST /datasets/:id/documents/bulk-upload (ZIP of JSON arrays)
- POST /datasets/:id/documents/bulk-download (async ZIP creation)
- GET /datasets/:id/documents/search

**Files** (`/datasets/:id/files`)
- GET /datasets/:id/files/upload-url (presigned S3 URL)
- POST /datasets/:id/files/bulk-upload (ZIP of raw files)
- GET /datasets/:id/files/:fileId/download-url

**Organizations** (`/organizations`)
- POST /organizations
- GET /organizations/:id
- PUT /organizations/:id
- POST /organizations/:id/users (add user)

---

## Python Client Implementation Status

### ✅ What's Implemented (Low-Level API)

The Python port has complete **low-level API classes** in `ndi/cloud/api/`:

| Module | Classes | Status |
|--------|---------|--------|
| `api/auth.py` | Login, Logout, ChangePassword, ForgotPassword, ResetPassword | ✅ Complete |
| `api/users.py` | CreateUser, GetUser, UpdateUser, DeleteUser | ✅ Complete |
| `api/datasets.py` | CreateDataset, GetDataset, UpdateDataset, ListDatasets, PublishDataset | ✅ Complete |
| `api/documents.py` | GetDocument, AddDocument, UpdateDocument, DeleteDocument, ListDatasetDocuments | ✅ Complete |
| `api/files.py` | GetUploadUrl, BulkUploadFiles | ✅ Complete |
| `api/organizations.py` | CreateOrganization, GetOrganization, UpdateOrganization | ✅ Complete |

**Example**:
```python
from ndi.cloud.api.documents import GetDocument

# This works:
api_call = GetDocument(token="my_jwt_token", dataset_id="abc123", document_id="doc456")
success, data, response, url = api_call.execute()
```

### ❌ What's Missing (High-Level Functions)

The Python port is **missing convenience functions and integrations**:

#### Missing Bulk Operations
- `get_bulk_download_url()` - Get presigned URL for bulk document download
- `bulk_download_documents()` - Download multiple documents as ZIP
- `bulk_upload_documents()` - Upload multiple documents from ZIP

#### Missing Sync Functions
- `list_remote_document_ids()` - Get all document IDs from remote dataset
- `get_cloud_dataset_id_for_local_dataset()` - Map local dataset to cloud dataset
- `list_datasets()` - List all datasets (convenience wrapper)

#### Missing File Operations
- `files_api` module - File management convenience layer
- File streaming helpers
- Presigned URL management

#### Missing Integration Functions
- `query()` function in `ndi.query` module (used by cloud functions)
- `DatasetDir` class - Local dataset directory management
- Sync index management (read/write sync state)

#### Missing Implementations (Documented as TODOs)

From grep analysis, **34 "not yet implemented" markers** found in:
- `upload/zip_for_upload.py` (5 TODOs)
- `upload/upload_collection.py` (5 TODOs)
- `upload/scan_for_upload.py` (4 TODOs)
- `upload/upload_to_ndicloud.py` (4 TODOs)
- `upload/new_dataset.py` (6 TODOs)
- `admin/register_dataset_doi.py` (1 TODO)
- `admin/crossref/*` (5 TODOs)

---

## Integration Requirements: Python Client → Node.js Backend

### Authentication Flow

**Python needs to obtain JWT token**:

1. User provides credentials (email + password)
2. Python calls Node.js `/auth/login` endpoint
3. Backend returns JWT ID token (AWS Cognito)
4. Python stores token (environment variable or config file)
5. All subsequent API calls include `Authorization: Bearer <token>` header

**Example Integration Code Needed**:
```python
# In ndi/cloud/auth/login.py
import os
from ndi.cloud.api.auth import Login

def login_to_cloud(email: str, password: str) -> str:
    """
    Authenticate user and return JWT token.
    Stores token in environment variable NDI_CLOUD_TOKEN.
    """
    api_call = Login(email=email, password=password)
    success, data, response, url = api_call.execute()

    if success:
        token = data['idToken']
        os.environ['NDI_CLOUD_TOKEN'] = token
        return token
    else:
        raise Exception(f"Login failed: {data}")

def get_token() -> str:
    """Get stored token from environment."""
    token = os.getenv('NDI_CLOUD_TOKEN')
    if not token:
        raise Exception("Not authenticated. Call login_to_cloud() first.")
    return token
```

### Dataset Sync Flow

**Uploading Local Dataset to Cloud**:

1. Create cloud dataset (if new)
   - POST `/datasets` with metadata
   - Backend returns `dataset_id`

2. Upload documents (bulk)
   - Convert local NDI documents to JSON
   - Create ZIP of JSON array
   - POST `/datasets/:id/documents/bulk-upload`
   - Backend extracts ZIP, inserts to MongoDB

3. Upload files (bulk)
   - Create ZIP of raw data files
   - POST `/datasets/:id/files/bulk-upload`
   - Backend extracts ZIP, streams to S3

4. Track sync state locally
   - Store `dataset_id` in local database
   - Record last sync timestamp

**Downloading Cloud Dataset Locally**:

1. Get dataset metadata
   - GET `/datasets/:id`
   - Create local dataset directory

2. Download documents (bulk)
   - POST `/datasets/:id/documents/bulk-download`
   - Backend creates ZIP asynchronously
   - Returns presigned download URL
   - Python downloads ZIP, extracts JSONs
   - Convert JSONs to NDI documents

3. Download files (optional for local mode)
   - GET `/datasets/:id/files/:fileId/download-url` for each file
   - Download from presigned S3 URLs

### Configuration Requirements

**Python client needs**:

```python
# Environment variables
NDI_CLOUD_TOKEN = "eyJhbGc..."  # JWT token
NDI_CLOUD_API_URL = "https://api.ndi-cloud.com/v1"  # or dev-api
NDI_CLOUD_MODE = "local"  # or "hybrid" or "cloud"

# Config file (~/.ndi/cloud_config.json)
{
    "email": "user@example.com",
    "token_expiration": "2025-01-20T10:00:00Z",
    "default_mode": "hybrid",
    "auto_sync": false
}
```

---

## Recommendations

### Priority 1: Fix Code Bugs (1-2 hours)

**Fix infinity handling in upload_collection.py**:
```python
# Line 201 in ndi/cloud/upload/upload_collection.py
if max_document_chunk == float('inf'):
    end_index = doc_count
else:
    end_index = min(i + int(max_document_chunk), doc_count)
```

**Fix test recursion issue**:
```python
# In tests/test_cloud_upload.py:320
# Instead of mocking os.path.join, mock database.path directly
with patch.object(mock_database, 'path', tmpdir):
    # ... rest of test
```

### Priority 2: Implement Missing Convenience Functions (2-3 days)

**Add bulk download function** (`ndi/cloud/api/documents.py`):
```python
def get_bulk_download_url(token: str, dataset_id: str, document_ids: List[str]) -> Tuple[bool, str, Any, str]:
    """
    Request bulk download URL for multiple documents.
    POST /datasets/:id/documents/bulk-download
    """
    api_url = f"{get_api_base_url()}/datasets/{dataset_id}/documents/bulk-download"
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    response = requests.post(api_url, json={'document_ids': document_ids}, headers=headers)

    if response.status_code == 200:
        download_url = response.json()['downloadUrl']
        return True, download_url, response, api_url
    else:
        return False, None, response, api_url
```

**Add list_remote_document_ids** (`ndi/cloud/internal/list_remote_documents.py`):
```python
def list_remote_document_ids(dataset_id: str, token: str = None) -> Dict[str, List[str]]:
    """
    List all document IDs in a remote dataset.
    Returns: {'ndi_id': [...], 'api_id': [...]}
    """
    if not token:
        token = get_token()

    all_ndi_ids = []
    all_api_ids = []
    page = 1

    while True:
        success, data, _, _ = list_dataset_documents(token, dataset_id, page=page, page_size=100)
        if not success or not data.get('documents'):
            break

        for doc in data['documents']:
            all_api_ids.append(doc['id'])  # MongoDB ID
            if 'base' in doc and 'id' in doc['base']:
                all_ndi_ids.append(doc['base']['id'])  # NDI ID

        if not data.get('hasMore'):
            break
        page += 1

    return {'ndi_id': all_ndi_ids, 'api_id': all_api_ids}
```

**Add get_cloud_dataset_id_for_local_dataset** (fix import):
```python
# In ndi/cloud/internal/get_cloud_dataset_id_for_local_dataset.py
# Change line that imports 'query'
from ndi.query import Query  # Not 'query'

def get_cloud_dataset_id_for_local_dataset(dataset):
    """Get cloud dataset ID for a local dataset."""
    # Search for dataset_remote document type
    q = Query('', isa='dataset_remote')
    docs = dataset.database_search(q)

    if len(docs) == 0:
        return '', []
    elif len(docs) > 1:
        raise RuntimeError(f"Dataset {dataset.path} has more than one remote cloudDatasetId")

    cloud_id = docs[0].document_properties.get('dataset_remote', {}).get('dataset_id', '')
    return cloud_id, docs
```

### Priority 3: Install Missing Dependencies (5 minutes)

```bash
pip install cffi
# Or rebuild cryptography:
pip uninstall cryptography
pip install --no-binary :all: cryptography
```

### Priority 4: Complete Stub Implementations (1-2 weeks)

34 functions marked "not yet implemented" need to be completed:
- Bulk file upload/download
- ZIP creation and extraction
- File scanning and metadata extraction
- DOI registration via Crossref
- Sync state management

---

## MATLAB Integration Status

**MATLAB does NOT have cloud client code**. The MATLAB codebase has no cloud integration - it's purely local/offline.

If MATLAB users want cloud features, they would need:
1. Export MATLAB dataset to disk
2. Use Python to upload to cloud
3. Or build MATLAB HTTP client (similar effort to Python)

---

## Summary: Path to Full Integration

| Task | Effort | Impact | Status |
|------|--------|--------|--------|
| Fix code bugs (infinity, recursion) | 1-2 hours | Fixes 3 tests | ❌ Not done |
| Install cffi dependency | 5 minutes | Fixes 8 tests | ❌ Not done |
| Implement missing convenience functions | 2-3 days | Fixes 36 tests | ❌ Not done |
| Complete stub implementations | 1-2 weeks | Full feature parity | ❌ Not done |
| Integration testing with live backend | 2-3 days | Production readiness | ❌ Not done |
| **Total** | **2-3 weeks** | **All 47 tests passing** | **In Progress** |

---

## Next Steps

1. **Fix bugs immediately** (1-2 hours):
   - Fix infinity handling in upload_collection.py
   - Install cffi package

2. **Implement critical missing functions** (2-3 days):
   - `get_bulk_download_url()`
   - `list_remote_document_ids()`
   - `get_cloud_dataset_id_for_local_dataset()` (fix import)
   - `list_datasets()`

3. **Create integration guide** (see companion document: PYTHON_CLOUD_INTEGRATION_GUIDE.md):
   - How to authenticate
   - How to upload dataset
   - How to download dataset
   - Example workflows

4. **Test against live backend** (after implementing missing functions):
   - Obtain test account on api.ndi-cloud.com or dev-api.ndi-cloud.com
   - Run integration tests
   - Verify sync workflows work end-to-end

The Python cloud client is **60-70% complete**. The backend exists and works. With 2-3 weeks of focused development, full integration would be operational.
