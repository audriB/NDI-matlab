# NDI Test Coverage Comparison: MATLAB vs Python

**Date**: November 25, 2025
**Python Test Pass Rate**: 95.0% (796/838 tests)

---

## Executive Summary

This document provides a comprehensive comparison of MATLAB and Python test coverage for the NDI (Neuroscience Data Interface) project, identifying gaps that must be addressed for 100% feature parity.

### Test Suite Statistics

| Metric | MATLAB | Python |
|--------|--------|--------|
| Test Files | 44 | 42 |
| Test Categories | 19 | 15 |
| Estimated Test Functions | ~100 | 838 |
| DAQ System Tests | 8 | 1 |
| FileNavigator Tests | 2 | 0 |
| Element Tests | 1 | 0 |

---

## Coverage Comparison by Category

### ✅ WELL-COVERED IN PYTHON

#### 1. Cloud Integration (Python-Only)
| Python Test File | Coverage |
|-----------------|----------|
| test_cloud_upload.py | Upload operations, batching, ZIP |
| test_cloud_download.py | Download modes, JSON conversion |
| test_cloud_sync.py | Two-way sync, mirror modes |
| test_cloud_admin.py | DOI generation, Crossref |
| test_cloud_internal.py | JWT, token management |
| test_cloud_utility.py | Metadata validation |

**Note**: Cloud functionality is primarily Python-focused, no equivalent in MATLAB.

#### 2. Database Operations (Good Parity)
| MATLAB | Python |
|--------|--------|
| test_ndi_document.m | test_document.py |
| Database operations | test_database_backends.py |
| - | test_db_query_builder.py |
| - | test_db_metadata_manager.py |
| - | test_db_utilities.py |
| - | test_db_maintenance.py |

**Status**: Python has more comprehensive database testing than MATLAB.

#### 3. Core Functionality (Good Parity)
| MATLAB | Python |
|--------|--------|
| Session usage | test_session.py |
| Document usage | test_document.py |
| Query operations | test_query.py |
| Cache | test_cache.py |

#### 4. Time Synchronization (Good Parity)
| MATLAB | Python |
|--------|--------|
| test_ndi_syncgraph_documents.m | test_syncgraph.py |
| test_ndi_syncrule_documents.m | test_syncrules.py |

#### 5. Calculator Tests (Python-Only)
- test_cross_correlation_calculator.py
- test_spike_rate_calculator.py
- test_tuning_curve_calculator.py

**Note**: These are Python-specific implementations for neural analysis.

---

### ❌ MAJOR GAPS - Missing in Python

#### 1. DAQ System Tests (CRITICAL)

**MATLAB Tests (8 files)**:
| File | Functionality |
|------|---------------|
| intan_flat.m | Intan RHD file reader, channel info, data reading |
| intan_flat_metadata.m | Metadata support with TSV files |
| intan_flat_saved.m | Reading saved Intan sessions |
| build_intan_flat_exp.m | Complete Intan setup with session |
| sg_flat.m | SpikeGadgets .rec file reader |
| blackrock.m | Blackrock NSx format (incomplete in MATLAB) |
| test_ndi_device_image_tiffstack.m | TIFF stack image acquisition |
| test_ndi_image_tiffstack_multipleepoch.m | Multi-epoch TIFF stacks |

**Python Coverage**: Only `test_phase4_daq_time.py` (basic time/sample conversion)

**Required Python Tests**:
```
tests/test_daq_intan.py           # Intan RHD reader tests
tests/test_daq_spikegadgets.py    # SpikeGadgets .rec reader tests
tests/test_daq_tiffstack.py       # TIFF image stack tests
tests/test_daq_reader.py          # Generic DAQ reader tests
```

**Key Functions to Test**:
- `samplerate()` - Get channel sample rates
- `readchannels_epochsamples()` - Read continuous data
- `getchannels()` - Get channel information
- `getepochprobemap()` - Epoch-probe mapping

---

#### 2. FileNavigator Tests (CRITICAL)

**MATLAB Tests (2 files)**:
| File | Functionality |
|------|---------------|
| test_ndi_filenavigator.m | Epoch detection, file pattern matching |
| test_ndi_filenavigator_fileIDfunction.m | File ID retrieval |

**Python Coverage**: None

**Required Python Tests**:
```
tests/test_filenavigator.py
```

**Key Functions to Test**:
- `numepochs()` - Count detected epochs
- `getepochfiles()` - Get files for epoch
- `epochtable()` - Generate epoch table
- File pattern matching (*.rhd, *.rec, etc.)

---

#### 3. Element Tests (CRITICAL)

**MATLAB Tests (1 file)**:
| File | Functionality |
|------|---------------|
| test_ndi_element.m | Element creation, dependencies, epoch data |

**Python Coverage**: None

**Required Python Tests**:
```
tests/test_element.py
```

**Key Functions to Test**:
- Element creation with probe dependencies
- `add_epoch_data()` - Add data to element
- `read_timeseries()` - Read element data
- Filtered element dependencies (e.g., LFP from raw)
- Independent element creation

---

#### 4. Probe Tests (PARTIAL)

**MATLAB Tests (1 file)**:
| File | Functionality |
|------|---------------|
| test_ndi_probe.m | Probe interface, data reading |

**Python Coverage**: `test_probe_specializations.py` covers specialized probes but NOT:
- `samplerate()` method
- `read_epochsamples()` method
- Integration with DAQ systems

---

#### 5. Document JSON Schema Validation (GAP)

**MATLAB Test**: `test_ndi_document_jsons.m`
- Loads ALL JSON document definitions
- Creates blank document from each
- Validates schema compliance

**Python Coverage**: None

**Required Python Test**:
```
tests/test_document_json_schemas.py
```

---

#### 6. App Tests (GAP)

**MATLAB Tests (2 files)**:
| File | Functionality |
|------|---------------|
| markgarbage.m | Validity interval marking |
| spikeextractor.m | Spike extraction/sorting |

**Python Coverage**: None

**Required Python Tests**:
```
tests/test_app_markgarbage.py
tests/test_app_spikeextractor.py
```

---

#### 7. Ingest Tests (GAP)

**MATLAB Tests (3 files)**:
| File | Functionality |
|------|---------------|
| mfdaq_compare.m | Compare ingested vs non-ingested data |
| syncgraph.m | Syncgraph ingest testing |
| compare.m | Session comparison |

**Python Coverage**: None

**Required Python Tests**:
```
tests/test_ingest.py
```

---

#### 8. Setup/Configuration Tests (GAP)

**MATLAB Tests (3 files)**: Lab-specific setup tests
- marderlab_hamood.m
- dbkatzlab_narendra.m
- angeluccilab.m

**Python Coverage**: None - low priority as these are lab-specific

---

## Remaining Failing Tests (42)

| Category | Count | Root Cause | Priority |
|----------|-------|------------|----------|
| Ontology API | 18 | External API unavailable | Low |
| JWT/Crypto | 5 | cffi dependency missing | Low |
| Integration | 2 | File path issues | Medium |
| Validate | 2 | jsonschema missing | Low |
| Cloud tests | ~15 | Various issues | Medium |

---

## Recommended Action Plan

### Priority 1: DAQ System Tests (HIGH - 8-16 hours)
Create comprehensive DAQ tests covering:
1. **test_daq_reader.py** - Base reader functionality
2. **test_daq_intan.py** - Intan RHD file reading
3. **test_daq_spikegadgets.py** - SpikeGadgets .rec reading
4. **test_daq_tiffstack.py** - TIFF image stacks

### Priority 2: FileNavigator Tests (HIGH - 4-8 hours)
Create **test_filenavigator.py** covering:
- Epoch detection from file patterns
- File grouping logic
- Epoch table generation

### Priority 3: Element Tests (HIGH - 4-8 hours)
Create **test_element.py** covering:
- Element creation with dependencies
- Epoch data management
- Timeseries reading

### Priority 4: Document Schema Tests (MEDIUM - 2-4 hours)
Create **test_document_schemas.py** to validate all JSON definitions

### Priority 5: Probe Integration Tests (MEDIUM - 2-4 hours)
Extend **test_probe_specializations.py** with:
- `samplerate()` tests
- `read_epochsamples()` tests
- DAQ system integration

### Priority 6: App Tests (LOW - 4-8 hours)
Create app tests when core functionality is complete

---

## Test Data Requirements

The MATLAB tests rely on specific test data directories:
- `exp1_eg/` - Intan RHD example data
- `exp_sg/` - SpikeGadgets example data
- `exp_image_tiffstack/` - TIFF image data

Python tests need access to similar test fixtures or mock data.

---

## Summary

| Category | MATLAB | Python | Gap |
|----------|--------|--------|-----|
| DAQ Systems | ✅ 8 tests | ❌ 1 test | **CRITICAL** |
| FileNavigator | ✅ 2 tests | ❌ 0 tests | **CRITICAL** |
| Elements | ✅ 1 test | ❌ 0 tests | **CRITICAL** |
| Probes | ✅ 1 test | ⚠️ Partial | Medium |
| Database | ✅ 8 tests | ✅ 6 tests | Good |
| Session | ✅ 1 test | ✅ 1 test | Good |
| Cache | ✅ 1 test | ✅ 1 test | Good |
| SyncGraph | ✅ 2 tests | ✅ 2 tests | Good |
| Cloud | ❌ None | ✅ 6 tests | Python-only |
| Apps | ✅ 2 tests | ❌ 0 tests | Gap |
| Ingest | ✅ 3 tests | ❌ 0 tests | Gap |

**Estimated effort to reach 100% parity**: 30-50 hours

---

**Document Created**: November 25, 2025
**Author**: Claude Code Session
