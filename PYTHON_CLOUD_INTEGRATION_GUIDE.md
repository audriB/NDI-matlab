# Python Cloud Integration Guide

## How to Integrate the Python NDI Client with the Node.js Backend

This guide shows how to use the **existing Python cloud client code** (60-70% complete) to connect to the operational Node.js backend at `api.ndi-cloud.com`.

---

## Prerequisites

### 1. Account Setup

You need a user account on the NDI Cloud platform:

**Production**: https://api.ndi-cloud.com
**Development**: https://dev-api.ndi-cloud.com

Contact the NDI Cloud administrators to create an account with:
- Email address
- Password
- Organization access (required for dataset uploads)

### 2. Python Environment

```bash
# Install Python dependencies
pip install requests networkx matplotlib

# Optional: Fix JWT/crypto tests (if needed)
pip install cffi pyjwt
```

---

## Authentication

### Step 1: Login and Obtain JWT Token

```python
from ndi.cloud.api.auth import Login
import os

# Login to get JWT token
email = "your.email@example.com"
password = "your_password"

login_call = Login(email=email, password=password)
success, data, response, url = login_call.execute()

if success:
    token = data['idToken']  # JWT token from AWS Cognito
    print(f"Login successful! Token expires at: {data.get('expiresAt', 'unknown')}")

    # Store token in environment for later use
    os.environ['NDI_CLOUD_TOKEN'] = token
else:
    print(f"Login failed: {data}")
    raise Exception("Authentication failed")
```

### Step 2: Store Token for Future Sessions

**Option A: Environment Variable** (temporary, session-only)
```bash
export NDI_CLOUD_TOKEN="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Option B: Config File** (persistent)
```python
import json
from pathlib import Path

def save_token(token, email):
    """Save token to ~/.ndi/cloud_config.json"""
    config_dir = Path.home() / '.ndi'
    config_dir.mkdir(exist_ok=True)

    config_file = config_dir / 'cloud_config.json'
    config = {
        'email': email,
        'token': token,
        'last_updated': str(datetime.now())
    }

    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"Token saved to {config_file}")

def load_token():
    """Load token from ~/.ndi/cloud_config.json"""
    config_file = Path.home() / '.ndi' / 'cloud_config.json'
    if not config_file.exists():
        raise FileNotFoundError("No saved token. Call login() first.")

    with open(config_file) as f:
        config = json.load(f)

    return config['token']
```

---

## Working with Datasets

### Create a New Cloud Dataset

```python
from ndi.cloud.api.datasets import CreateDataset
import os

token = os.getenv('NDI_CLOUD_TOKEN')  # or use load_token()

# Dataset metadata
dataset_metadata = {
    'name': 'My Neuroscience Experiment',
    'abstract': 'Visual cortex recordings from mouse V1',
    'branchName': 'main',
    'license': 'CC-BY-4.0',
    'contributors': [
        {
            'firstName': 'Jane',
            'lastName': 'Doe',
            'orchid': '0000-0001-2345-6789',
            'role': 'Corresponding Author'
        }
    ],
    'species': 'Mus musculus',
    'brainRegions': ['Primary Visual Cortex (V1)'],
    'numberOfSubjects': 5
}

# Create dataset
create_call = CreateDataset(token=token, dataset_data=dataset_metadata)
success, data, response, url = create_call.execute()

if success:
    dataset_id = data['x_id']  # MongoDB ID for the dataset
    print(f"Dataset created! ID: {dataset_id}")
    print(f"View at: https://ndicloud.org/datasets/{dataset_id}")
else:
    print(f"Failed to create dataset: {data}")
```

### List Your Datasets

```python
from ndi.cloud.api.datasets import ListDatasets

list_call = ListDatasets(
    token=token,
    page=1,
    page_size=20,
    is_published=False  # False = your private datasets, True = public datasets
)

success, data, response, url = list_call.execute()

if success:
    datasets = data['datasets']
    print(f"Found {len(datasets)} datasets:")
    for ds in datasets:
        print(f"  - {ds['name']} (ID: {ds['x_id']}, Documents: {ds['documentCount']})")
else:
    print(f"Failed to list datasets: {data}")
```

### Get Dataset Details

```python
from ndi.cloud.api.datasets import GetDataset

get_call = GetDataset(token=token, dataset_id=dataset_id)
success, data, response, url = get_call.execute()

if success:
    print(f"Dataset: {data['name']}")
    print(f"Abstract: {data['abstract']}")
    print(f"Contributors: {len(data.get('contributors', []))} people")
    print(f"Documents: {data['documentCount']}")
    print(f"Files: {len(data.get('files', []))} files")
    print(f"Total size: {data.get('totalSize', 0) / 1e6:.2f} MB")
else:
    print(f"Failed to get dataset: {data}")
```

---

## Working with Documents

### Add a Document to a Dataset

```python
from ndi.cloud.api.documents import AddDocument

# NDI document (converted to cloud format)
document_data = {
    'base': {
        'id': 'unique_ndi_doc_id_12345',
        'session_id': 'session_001',
        'type': 'ndi.probe.timeseries'
    },
    'definition': {
        'name': 'Recording Probe 1',
        'reference': 'Probe in V1, depth 500um'
    },
    'files': {
        'file_list': ['recording_001.dat'],
        'file_info': [
            {
                'name': 'recording_001.dat',
                'size': 1048576,  # bytes
                'type': 'binary'
            }
        ]
    },
    'properties': {
        'sampling_rate': 30000,
        'num_channels': 64,
        'duration_seconds': 600
    }
}

add_doc_call = AddDocument(
    token=token,
    dataset_id=dataset_id,
    document_data={'document_properties': document_data}
)

success, data, response, url = add_doc_call.execute()

if success:
    doc_id = data['id']  # MongoDB ID for the document
    print(f"Document added! ID: {doc_id}")
else:
    print(f"Failed to add document: {data}")
```

### List Documents in a Dataset

```python
from ndi.cloud.api.documents import ListDatasetDocuments

list_docs_call = ListDatasetDocuments(
    token=token,
    dataset_id=dataset_id,
    page=1,
    page_size=50
)

success, data, response, url = list_docs_call.execute()

if success:
    documents = data['documents']
    print(f"Found {len(documents)} documents:")
    for doc in documents:
        print(f"  - {doc.get('base', {}).get('id', 'unknown')} (Type: {doc.get('base', {}).get('type', 'unknown')})")
else:
    print(f"Failed to list documents: {data}")
```

### Get a Specific Document

```python
from ndi.cloud.api.documents import GetDocument

get_doc_call = GetDocument(
    token=token,
    dataset_id=dataset_id,
    document_id=doc_id
)

success, data, response, url = get_doc_call.execute()

if success:
    print(f"Document ID: {data['id']}")
    print(f"NDI ID: {data.get('base', {}).get('id', 'unknown')}")
    print(f"Type: {data.get('base', {}).get('type', 'unknown')}")
    print(f"Files: {data.get('files', {}).get('file_list', [])}")
else:
    print(f"Failed to get document: {data}")
```

---

## File Upload/Download

### Upload a File (Single File)

```python
from ndi.cloud.api.files import GetUploadUrl
import requests

# Step 1: Get presigned upload URL from backend
file_struct = {
    'uid': 'file_unique_id_001',
    'name': 'recording_001.dat',
    'size': 1048576,  # bytes
    'contentType': 'application/octet-stream'
}

upload_url_call = GetUploadUrl(
    token=token,
    dataset_id=dataset_id,
    file_data=file_struct
)

success, data, response, url = upload_url_call.execute()

if success:
    upload_url = data['uploadUrl']

    # Step 2: Upload file directly to S3 using presigned URL
    with open('/path/to/recording_001.dat', 'rb') as f:
        file_data = f.read()

    upload_response = requests.put(
        upload_url,
        data=file_data,
        headers={'Content-Type': 'application/octet-stream'}
    )

    if upload_response.status_code == 200:
        print(f"File uploaded successfully!")
    else:
        print(f"Upload failed: {upload_response.status_code}")
else:
    print(f"Failed to get upload URL: {data}")
```

### Bulk Upload Files (Multiple Files as ZIP)

**Note**: This requires implementing the missing `bulk_upload_files()` function (see Analysis doc).

```python
# This functionality is partially implemented
# Full implementation coming soon

from ndi.cloud.upload.zip_for_upload import zip_for_upload

# Current status: Function exists but has "not yet implemented" markers
# After implementation is complete, usage would be:

# success, msg = zip_for_upload(
#     database=local_dataset.database,
#     doc_file_struct=file_list,
#     total_size=total_size_kb,
#     dataset_id=cloud_dataset_id,
#     verbose=True
# )
```

---

## Complete Workflow: Upload Local Dataset to Cloud

This is a **future capability** once missing functions are implemented:

```python
from ndi.session import Session
from ndi.cloud.upload.new_dataset import new_dataset
from ndi.cloud.upload.upload_collection import upload_document_collection
from ndi.cloud.upload.scan_for_upload import scan_for_upload

# Step 1: Load local NDI session
local_session = Session('/path/to/local/session')

# Step 2: Create cloud dataset (returns dataset_id)
cloud_dataset_id = new_dataset(local_session)  # Currently stub

# Step 3: Get all documents from local session
all_documents = local_session.database.alldocs()

# Step 4: Upload documents to cloud
success, report = upload_document_collection(
    dataset_id=cloud_dataset_id,
    document_list=all_documents,
    only_upload_missing=True,
    verbose=True
)

if success:
    print(f"Upload complete!")
    print(f"Uploaded {len(report['manifest'])} batches")
    print(f"View at: https://ndicloud.org/datasets/{cloud_dataset_id}")
else:
    print(f"Upload failed: {report}")
```

**Current Status**: Functions exist but have partial implementations. See `PYTHON_CLOUD_INTEGRATION_ANALYSIS.md` for list of missing functions.

---

## Complete Workflow: Download Cloud Dataset Locally

This is also a **future capability** once missing functions are implemented:

```python
from ndi.cloud.download.dataset import download_dataset

# Download entire dataset (documents + files)
success, msg, dataset = download_dataset(
    dataset_id=cloud_dataset_id,
    mode='local',  # 'local' downloads everything, 'hybrid' = docs only
    output_path='/path/to/download/location',
    verbose=True
)

if success:
    print(f"Download complete!")
    print(f"Dataset location: {dataset.path}")

    # Now you can use it as a normal NDI session
    session = Session(dataset.path)
    docs = session.database.alldocs()
    print(f"Loaded {len(docs)} documents")
else:
    print(f"Download failed: {msg}")
```

**Current Status**: Core download classes exist, but missing `DatasetDir`, file download logic, and bulk operations.

---

## Publishing a Dataset

```python
from ndi.cloud.api.datasets import PublishDataset

# Publish dataset (makes it publicly accessible)
publish_call = PublishDataset(token=token, dataset_id=dataset_id)
success, data, response, url = publish_call.execute()

if success:
    print(f"Dataset published!")
    print(f"Public URL: https://ndicloud.org/datasets/{dataset_id}")

    # Publishing may take time if dataset is large (>500 files)
    # Backend will copy files from private S3 to public S3
    if data.get('isPublishing'):
        print(f"Publishing in progress... Progress: {data.get('publishProgress', {})}")
else:
    print(f"Failed to publish: {data}")
```

---

## Error Handling

All API calls return a tuple: `(success, data, response, url)`

```python
success, data, response, url = api_call.execute()

if not success:
    # Handle error
    status_code = response.status_code
    error_message = data.get('message', 'Unknown error') if isinstance(data, dict) else data

    if status_code == 401:
        print("Authentication failed. Token may be expired.")
        # Re-login to get new token
    elif status_code == 403:
        print("Permission denied. Check organization access.")
    elif status_code == 404:
        print(f"Resource not found: {url}")
    elif status_code == 500:
        print(f"Server error: {error_message}")
    else:
        print(f"Error {status_code}: {error_message}")
```

---

## Token Expiration

JWT tokens expire after a certain time (typically 1 hour). Check expiration and refresh:

```python
from ndi.cloud.internal.get_token_expiration import get_token_expiration
from datetime import datetime, timezone

# Check if token is expired
token = os.getenv('NDI_CLOUD_TOKEN')
exp_time = get_token_expiration(token)

if exp_time < datetime.now(timezone.utc):
    print("Token expired! Re-authenticating...")
    # Re-login (see Step 1)
else:
    time_left = (exp_time - datetime.now(timezone.utc)).total_seconds() / 60
    print(f"Token valid for {time_left:.1f} more minutes")
```

---

## Configuration for Different Environments

```python
import os

# Set environment (production vs development)
os.environ['NDI_CLOUD_ENV'] = 'production'  # or 'development'

# The API base classes automatically use the correct URL:
# production: https://api.ndi-cloud.com/v1
# development: https://dev-api.ndi-cloud.com/v1
```

---

## Testing the Integration

### Quick Test: List Public Datasets

```python
from ndi.cloud.api.datasets import ListDatasets
import os

# No authentication required for public datasets
list_call = ListDatasets(
    token="",  # Empty token OK for public data
    page=1,
    page_size=10,
    is_published=True  # Public datasets
)

success, data, response, url = list_call.execute()

if success:
    print(f"Found {len(data['datasets'])} public datasets")
    for ds in data['datasets']:
        print(f"  - {ds['name']} (Documents: {ds['documentCount']})")
else:
    print(f"Error: {data}")
```

### Integration Test: Full Round Trip

```python
def test_integration():
    """Test: Create dataset → Add document → Retrieve → Delete"""
    from ndi.cloud.api.datasets import CreateDataset, GetDataset, DeleteDataset
    from ndi.cloud.api.documents import AddDocument, GetDocument
    import os

    token = os.getenv('NDI_CLOUD_TOKEN')

    # 1. Create dataset
    create_call = CreateDataset(token=token, dataset_data={'name': 'Test Dataset'})
    success, data, _, _ = create_call.execute()
    assert success, f"Create failed: {data}"
    dataset_id = data['x_id']
    print(f"✓ Created dataset {dataset_id}")

    # 2. Add document
    doc_data = {'document_properties': {'base': {'id': 'test_doc_001', 'type': 'test'}}}
    add_call = AddDocument(token=token, dataset_id=dataset_id, document_data=doc_data)
    success, data, _, _ = add_call.execute()
    assert success, f"Add document failed: {data}"
    doc_id = data['id']
    print(f"✓ Added document {doc_id}")

    # 3. Retrieve dataset
    get_call = GetDataset(token=token, dataset_id=dataset_id)
    success, data, _, _ = get_call.execute()
    assert success, f"Get dataset failed: {data}"
    assert data['documentCount'] == 1, "Document count mismatch"
    print(f"✓ Retrieved dataset (has {data['documentCount']} documents)")

    # 4. Cleanup
    delete_call = DeleteDataset(token=token, dataset_id=dataset_id)
    success, data, _, _ = delete_call.execute()
    assert success, f"Delete failed: {data}"
    print(f"✓ Deleted dataset")

    print("✅ Integration test passed!")

# Run test
test_integration()
```

---

## Limitations (Current Implementation)

### ✅ What Works Now

- ✅ Authentication (login, logout, password management)
- ✅ Dataset CRUD (create, read, update, delete, list)
- ✅ Document CRUD (add, get, update, delete, list)
- ✅ Single file upload (via presigned URLs)
- ✅ Get dataset/document count
- ✅ Organization management

### ❌ What's Not Yet Implemented

- ❌ Bulk document upload/download (functions exist but incomplete)
- ❌ Bulk file upload (ZIP processing)
- ❌ Sync operations (two-way sync, mirror, etc.)
- ❌ Dataset publishing workflows (partially works)
- ❌ DOI registration via Crossref
- ❌ Search functionality
- ❌ File download helpers

**See `PYTHON_CLOUD_INTEGRATION_ANALYSIS.md` for full list of missing functions and implementation status.**

---

## Next Steps

1. **Start using what works**: Authentication, dataset/document CRUD, single file uploads
2. **Contribute implementations**: Help implement missing functions (see Analysis doc for list)
3. **Report issues**: File bug reports for any integration problems
4. **Request features**: Let maintainers know which missing features are highest priority

---

## Support

- **Documentation**: https://docs.ndi-cloud.com
- **API Reference**: https://api.ndi-cloud.com/docs (OpenAPI spec)
- **Backend Source**: `ndi-cloud-node` repository
- **Python Client Source**: `ndi-python/ndi/cloud/` directory

For help, contact NDI Cloud administrators or file an issue on GitHub.
