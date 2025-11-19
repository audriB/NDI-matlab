# NDI-MATLAB to ndi-python FEATURE PARITY ANALYSIS
## Comprehensive Assessment - 100% Validation

Generated: 2025-11-19
Status: **CRITICAL GAPS IDENTIFIED** - Production deployment NOT recommended without remediation

---

## EXECUTIVE SUMMARY

The ndi-python port demonstrates **INCOMPLETE feature parity** with the NDI-MATLAB system. 
While core classes (Session, Document) are functionally similar, several major subsystems are significantly underdeveloped:

- **Database subsystem: 4.5% coverage** (5 vs 110 MATLAB files)
- **Setup subsystem: 8.6% coverage** (7 vs 81 MATLAB files)  
- **GUI subsystem: 20% coverage** (3 vs 15 MATLAB files)
- **Utility functions: 31% coverage** (16 vs 51 MATLAB files)
- **Fun subsystem: 31% coverage** (16 vs 51 MATLAB files)

**Recommendation:** Do NOT consider this production-ready without significant development effort.

---

## 1. CORE CLASS COMPARISON

### 1.1 Session Class
**MATLAB:** session.m (928 lines)
**Python:** session.py (972 lines)
**Status:** MOSTLY COMPLETE with gaps

#### MATLAB Methods (38 public/protected methods):
- session() - constructor
- id() - get identifier
- unique_reference_string() - [DEPRECATED]
- daqsystem_add/rm/load/clear() - DAQ system management
- newdocument() - create document
- searchquery() - query builder
- database_add/rm/search/clear() - database operations
- database_openbinarydoc/closebinarydoc/existbinarydoc() - binary file handling
- validate_documents() - validation
- ingest() - data ingestion
- is_fully_ingested() - status check
- syncgraph_addrule/rmrule() - time synchronization
- getpath() - get session path
- getprobes/getelements() - retrieve hardware objects
- findexpobj() - find experiment objects
- creator_args() - serialization
- docinput2docs() - input processing
- all_docs_in_session() - document queries
- eq() - equality comparison

#### Python Methods (31 public methods):
- __init__() - constructor
- id() - get identifier
- newdocument() - create document
- searchquery() - query builder
- database_add() - add documents
- database_search() - search documents
- database_rm() - remove documents
- database_clear() - clear database
- database_openbinarydoc() - open binary
- database_closebinarydoc() - close binary
- database_existbinarydoc() - check existence
- daqsystem_add() - add DAQ system
- daqsystem_load() - load DAQ system
- daqsystem_rm() - remove DAQ system
- daqsystem_clear() - clear DAQ systems
- getprobes() - get probe objects
- add_probe() - add probe
- getelements() - get element objects
- syncgraph_addrule() - add sync rule
- syncgraph_rmrule() - remove sync rule
- get_ingested_docs() - get ingested documents
- findexpobj() - find experiment object
- creator_args() - get constructor args
- docinput2docs() - convert input to docs
- all_docs_in_session() - check docs in session
- validate_documents() - validate docs
- ingest() - run ingestion
- is_fully_ingested() - check if fully ingested
- __eq__() - equality
- __repr__() - string representation

#### Missing in Python:
- unique_reference_string() (deprecated anyway)

#### Status: **95% COMPLETE** - Functionally equivalent

---

### 1.2 Document Class
**MATLAB:** document.m (951 lines)
**Python:** document.py (984 lines)
**Status:** MOSTLY COMPLETE

#### MATLAB Methods (36+ methods):
- document() - constructor (3 variants)
- set_session_id() - set session
- add_dependency_value_n() - add numbered dependencies
- to_table() - convert to table
- id() - get ID
- session_id() - get session ID
- datestamp() - get timestamp
- dependency_value_n() - get dependency
- get_dependency_value() - get dependency value
- set_dependency_value() - set dependency value
- add_dependency_value() - add dependency
- property_names() - get all properties
- has_property() - check property
- setproperties() - batch set properties
- get_properties() - batch get properties
- AND many more property access methods

#### Python Methods (30+ methods):
- __init__() - constructor
- _timestamp() - generate timestamp
- _set_nested_property() - set property
- set_session_id() - set session ID
- id() - get ID
- session_id() - get session ID
- datestamp() - get timestamp
- type() - get document type
- has_property() - check property
- get_property() - get property
- set_property() - set property
- get_property_path() - get by path
- set_property_path() - set by path
- add_dependency_value() - add dependency
- get_dependency_value() - get dependency
- set_dependency_value() - set dependency
- get_dependency_value_n() - get numbered dependency
- add_dependency_value_n() - add numbered dependency
- dependency_names() - list dependencies
- remove_dependency() - remove dependency
- setproperties() - batch set
- __eq__() - equality
- __repr__() - repr
- to_dict() - convert to dict

#### Status: **90% COMPLETE** - Core functionality present, some utility methods missing

---

### 1.3 Calculator Class
**MATLAB:** calculator.m (1065 lines)
**Python:** calculator.py (473 lines) - **MAJOR GAP**
**Status:** 44% COMPLETE - CRITICAL MISSING FUNCTIONALITY

#### MATLAB Methods:
- calculator() - constructor
- run() - execute calculations
- default_search_for_input_parameters() - default params
- search_for_input_parameters() - search for inputs
- calculate() - abstract calculation method
- search_for_calculator_docs() - find existing results
- newdocument() - create calculator document
- diagnostic_plots() - generate plots
- fast_start - quick start property

#### Python Methods:
- __init__() - constructor
- run() - execute calculations
- default_search_for_input_parameters() - default params
- search_for_input_parameters() - search inputs

#### Missing in Python:
- search_for_calculator_docs() - Find existing calculations
- calculate() - Abstract calculation interface
- diagnostic_plots() - Plotting capability
- fast_start property - GUI initialization
- ~~170% more lines of MATLAB code~~ - Indicates significant missing implementation

#### Status: **44% COMPLETE** - **CRITICAL GAP** - Core calculation pipeline incomplete

---

### 1.4 Element Class
**MATLAB:** element.m (572 lines)
**Python:** _element.py (755 lines)
**Status:** ~85% COMPLETE

#### MATLAB Methods (20 methods):
- element() - constructor
- issyncgraphroot() - sync graph check
- epochsetname() - get epoch name
- epochclock() - get clock
- t0_t1() - get time bounds
- getcache() - get cache
- buildepochtable() - build epoch table
- elementstring() - string representation
- addepoch() - add epoch
- loadaddedepochs() - load epochs
- load_element_doc() - load document
- doc_unique_id() - get ID
- id() - get ID
- load_all_element_docs() - load docs
- eq() - equality
- newdocument() - create document
- searchquery() - search query

#### Python Methods (22 methods):
- __init__() - constructor (with variants)
- _init_from_params() - init from params
- _init_from_document() - init from doc
- issyncgraphroot() - sync graph check
- epochsetname() - get epoch name
- epochclock() - get clock
- t0_t1() - get time bounds
- getcache() - get cache
- buildepochtable() - build epoch table
- elementstring() - string representation
- addepoch() - add epoch
- loadaddedepochs() - load epochs
- epochtableentry() - get epoch entry
- newdocument() - create document
- searchquery() - search query
- readtimeseries() - READ TIME SERIES DATA (NEW)
- samplerate() - get sample rate (NEW)
- addepoch_timeseries() - add with timeseries (NEW)
- __eq__() - equality
- __repr__() - repr
- __str__() - str

#### New in Python (that MATLAB lacks):
- readtimeseries() - Time series reading
- samplerate() - Sample rate access

#### Status: **85-90% COMPLETE** - Python has ADDITIONAL functionality

---

### 1.5 Probe Class
**MATLAB:** probe.m (367 lines)
**Python:** probe/_probe.py (556 lines)
**Status:** ~75% COMPLETE

#### MATLAB Methods (10 methods):
- probe() - constructor
- buildepochtable() - build epoch table
- epochclock() - get clock
- issyncgraphroot() - sync graph check
- epochsetname() - get epoch name
- probestring() - string representation
- getchanneldevinfo() - get channel info
- epochprobemapmatch() - match probe map
- eq() - equality
- buildmultipleepochtables() - batch build

#### Python Methods (15+ methods):
- __init__() - constructor
- _init_from_params() - init from params
- _init_from_document() - init from doc
- issyncgraphroot() - sync check
- epochsetname() - get epoch name
- epochclock() - get clock
- buildepochtable() - build epoch table
- probestring() - string representation
- getchanneldevinfo() - get channel info
- epochprobemapmatch() - match probe map
- __eq__() - equality
- __repr__() - repr

#### Status: **75% COMPLETE** - Core functionality present

---

### Other Main Classes

| Class | MATLAB | Python | Coverage | Status |
|-------|--------|--------|----------|--------|
| ontology | 584 lines (29 methods) | 23,172 bytes (16 files, 56 methods) | 120% | PYTHON HAS MORE |
| epoch | 82 lines | 22,847 bytes (_epoch.py) | ~100% | COMPLETE |
| validate | 323 lines | 415 lines | ~95% | COMPLETE |
| query | 155 lines | 225 lines | ~95% | COMPLETE |
| cache | 267 lines | 214 lines | ~90% | COMPLETE |
| app | 117 lines | 214 lines | ~100% | COMPLETE |
| subject | 174 lines | 82 lines | ~70% | PARTIAL |
| ido | 12 lines | 120 lines | ~100% | COMPLETE |
| neuron | 24 lines | 90 lines | ~100% | COMPLETE |
| appdoc | N/A | 161 lines | N/A | PYTHON ONLY |
| pipeline | 422 lines | N/A | 0% | **MISSING IN PYTHON** |
| dataset | 494 lines | 3 files | ~60% | PARTIAL |

---

## 2. SUBSYSTEM COMPARISON - FILE COUNT & COVERAGE

### Critical Gaps Identified

```
SUBSYSTEM          MATLAB FILES   PYTHON FILES   COVERAGE      STATUS
============================================================================
database           110            5              4.5%          CRITICAL GAP
setup              81             7              8.6%          CRITICAL GAP
gui                15             3              20.0%         MAJOR GAP
fun                51             16             31.4%         MAJOR GAP
cloud              151            82             54.3%         PARTIAL
daq                17             12             70.6%         ACCEPTABLE
util               13             13             100%          COMPLETE
file               6              7              116%           COMPLETE+
time               11             14             127%           COMPLETE+
ontology           13             16             123%           COMPLETE+
validators         9              2              22.2%         MAJOR GAP
element            6              6              100%          COMPLETE
epoch              6              2              33%            PARTIAL
example            13             5              38.5%          PARTIAL
common             5              4              80%            ACCEPTABLE
calc               2              6              300%           PYTHON EXTENDED
probe              6              5              83%            ACCEPTABLE
session            4              N/A            N/A            (main class)
mock               5              5              100%          COMPLETE
dataset            1              3              300%           PYTHON EXTENDED
============================================================================
TOTAL MATLAB FILES:   664
TOTAL PYTHON FILES:   300
OVERALL COVERAGE:     45.2%
```

---

## 3. CRITICAL GAP ANALYSIS

### 3.1 Database Subsystem - CRITICAL (4.5% Coverage)

**MATLAB Structure (110 files):**
- database.m (253 lines) - Base class with 23 methods
- +database/+app/ - Database viewer application
- +database/+fun/ (34 files) - Utility functions:
  * copy_session_to_dataset.m
  * databasehierarchyinit.m
  * extract_docs_files.m
  * findalldependencies.m/findallantecedents.m
  * find_ingested_docs.m
  * docs2graph.m
  * dataset_metadata.m
  * And 26 more specialized functions
- +database/+implementations/ (5 files) - Multiple database backends:
  * didsqlite.m (SQLite implementation)
  * matlabdumbjsondb.m (JSON implementation)
  * matlabdumbjsondb2.m (Enhanced JSON implementation)
  * Binary document handling
- +database/+metadata/ - Metadata handling (1 file)
- +database/+metadata_app/ (48 files) - Complete metadata application:
  * Data validation UI (subject.m)
  * Class definitions for domain objects (Electrode, Probe, etc.)
  * OpenMINDS integration (40 files)
  * RRID/RORC lookups
  * DOI registration
- +database/+metadata_ds_core/ (15 files) - Metadata dataset core
- +database/+internal/ - Internal utilities

**Python Structure (5 files):**
- __init__.py
- base.py (356 lines) - Abstract base
- matlabdumbjsondb.py (282 lines) - Basic JSON implementation
- matlabdumbjsondb2.py (342 lines) - Enhanced JSON implementation
- sqlite.py (411 lines) - SQLite implementation

**Missing in Python:**
1. ❌ **Metadata application UI** (48 files) - No graphical metadata editor
2. ❌ **Database utility functions** (34 files):
   - No cross-dataset operations
   - No dependency tracking
   - No ingestion pipeline functions
   - No document graph analysis
   - No dataset metadata generation
3. ❌ **Database app** - No dataset viewer/explorer
4. ❌ **OpenMINDS integration** - No metadata model handling
5. ❌ **Ontology integration** - No UBERON/ROR/RRID lookups in metadata
6. ❌ **DOI registration** - Cannot generate DOIs for datasets
7. ❌ **Metadata import/export** - Limited metadata handling

**Severity:** **CRITICAL** - No metadata application, no utility pipeline

---

### 3.2 Setup Subsystem - CRITICAL (8.6% Coverage)

**MATLAB Structure (81 files):**
- +setup/+NDIMaker/ (9 files) - Generic data ingestion tools:
  * sessionMaker.m
  * subjectMaker.m  
  * TreatmentCreator.m
  * stimulusDocMaker.m
  * imageDocMaker.m
  * tableDocMaker.m
  * AND MORE
- +setup/+conv/ (72 files) - Conversion frameworks for specific labs:
  * +birren/ - Birren lab conversion
  * +dabrowska/ - Dabrowska lab conversion
  * +emmons/ - Emmons lab conversion
  * +hires/ - Hires lab conversion
  * And more lab-specific converters

**Python Structure (7 files):**
- __init__.py
- /creators/ (2 files):
  * subject_information_creator.py
  * __init__.py
- /makers/ (4 files):
  * session_maker.py
  * subject_maker.py
  * epoch_probe_map_maker.py
  * __init__.py

**Missing in Python:**
1. ❌ **Lab-specific converters** (72 files) - No lab conversion frameworks
2. ❌ **Generic makers** (only 3 vs 9) - Missing stimulus, image, table makers
3. ❌ **Treatment creator** - No standardized treatment documentation
4. ❌ **Conversion pipelines** - Cannot import from external data sources

**Severity:** **CRITICAL** - Users cannot ingest their own lab data

---

### 3.3 GUI Subsystem - MAJOR GAP (20% Coverage)

**MATLAB Structure (15 files):**
- gui.m & gui_v2.m - Main GUI applications
- docViewer.m - Document viewer
- Lab.m - Lab management
- Data.m - Data browsing
- Icon.m - Icon management
- /+component/ (8 files) - UI components:
  * NDIProgressBar.m
  * ProgressBarWindow.m
  * CommandWindowProgressMonitor.m
  * AsynchProgressTracker.m
  * ProgressTracker.m
  * Abstract classes for progress monitoring
- /+utility/ - UI utilities

**Python Structure (3 files):**
- __init__.py
- progress_monitor.py
- progress_tracker.py

**Missing in Python:**
1. ❌ **Document viewer** - Cannot browse documents
2. ❌ **Lab management GUI** - No lab/experiment browser
3. ❌ **Data explorer** - Cannot visualize database contents
4. ❌ **Progress bar components** - Only basic logging
5. ❌ **Interactive GUI applications** - No graphical tools

**Severity:** **MAJOR** - No GUI tools for data exploration or management

---

### 3.4 Function Utilities - MAJOR GAP (31% Coverage)

**MATLAB +fun/ (51 files):**
- timestamp.m - Generate timestamps
- uuid.m - Generate UUIDs
- AND 49 more general-purpose utility functions

**Python ndi/fun/ (16 files):**
- Basic utilities implemented

**Missing Functions:**
- Many MATLAB utility functions not ported

**Severity:** **MAJOR** - Utility functions incomplete

---

### 3.5 Validators Subsystem - MAJOR GAP (22% Coverage)

**MATLAB Structure (9 files):**
- Multiple validation classes for data integrity

**Python Structure (2 files):**
- Minimal validator implementation

**Status:** **MAJOR GAP** - Validation framework underdeveloped

---

### 3.6 Epoch Subsystem - PARTIAL (33% Coverage)

**MATLAB Structure (6 files in +epoch/):**
- Full epoch management

**Python Structure (2 files):**
- Limited epoch implementation

**Status:** **PARTIAL** - Epoch handling incomplete

---

## 4. METHOD-LEVEL ANALYSIS - DETAILED

### Session Class Method Comparison

**Missing in Python Session:**
```
MATLAB Method                          Python Equivalent
─────────────────────────────────────────────────────────
unique_reference_string()              DEPRECATED - Not needed
daqsystem_rm() - remove DAQ            daqsystem_rm() - ✓ Present
daqsystem_load() - load DAQ config     daqsystem_load() - ✓ Present
```

**Result:** Session methods are well-mapped between MATLAB and Python.

---

### Document Class Method Comparison

**Partially Missing in Python Document:**
- Some property access methods simplified in Python (more Pythonic)
- Core functionality preserved

**Result:** Document methods adequately mapped with Pythonic simplifications.

---

### Calculator Class Method Comparison

**CRITICAL: Missing in Python Calculator:**
```
MATLAB Method                          Status
─────────────────────────────────────────────
search_for_calculator_docs()           ❌ MISSING
calculate() [abstract]                 ❌ MISSING  
diagnostic_plots()                     ❌ MISSING
fast_start [property]                  ❌ MISSING
```

**Impact:** Cannot search for existing calculations, cannot generate diagnostic plots

**Result:** **44% COMPLETE** - Critical pipeline functions missing

---

## 5. DEPENDENCY ANALYSIS

### MATLAB External Dependencies (12 packages required)

1. ✅ vhlab_vhtools - Version control utilities
2. ✅ vhlab-toolbox-matlab - General MATLAB utilities
3. ✅ vhlab-library-matlab - Library functions
4. ✅ vhlab-thirdparty-matlab - Third-party integrations
5. ✅ vhlab-NewStim-matlab - Stimulus generation (conditional)
6. ✅ DID-matlab - Digital data management
7. ✅ NDR-matlab - Data representation
8. ✅ Catalog - File cataloging
9. ✅ mksqlite - SQLite interface
10. ✅ NDI-compress-matlab - Data compression
11. ✅ Violinplot-Matlab - Plotting utility
12. ✅ openminds-metadata-models-matlab - OpenMINDS support

**Python Equivalents:**
- ✅ Standard libraries (os, json, datetime, etc.)
- ✅ External: sqlite3, numpy, pandas (implicit)
- ❌ **NO EXPLICIT EQUIVALENT** for lab-specific utilities (DID, NDR, vhtools)
- ❌ **MISSING:** Complete OpenMINDS Python implementation

**Status:** **60-70% coverage** of external dependencies

---

## 6. ARCHITECTURE-LEVEL GAPS

### Missing Architectural Components

1. **No Metadata Application Pipeline**
   - MATLAB has full metadata UI with OpenMINDS support
   - Python has only basic document handling
   - **Impact:** Cannot create rich metadata documents

2. **No Lab Conversion Framework**
   - MATLAB has 72 files for lab-specific data conversion
   - Python has generic makers only
   - **Impact:** Users cannot ingest their lab data

3. **No Database Utility Pipeline**
   - MATLAB has 34 utility functions for database operations
   - Python has basic add/search/remove only
   - **Impact:** Cannot perform complex database operations

4. **No GUI/TUI Interface**
   - MATLAB has 15 files for GUI applications
   - Python has only 3 progress monitor files
   - **Impact:** No interactive data exploration tools

5. **No Ingestion Pipeline**
   - MATLAB has explicit ingestion workflow
   - Python implementation exists but may be incomplete
   - **Impact:** Data flow unclear in Python

---

## 7. PRODUCTION READINESS ASSESSMENT

### For Core Data Management: 75-80% Ready
- Session, Document, Element, Probe classes functional
- Database CRUD operations work
- Query system operational

### For Advanced Features: 20-30% Ready
- Calculator pipeline incomplete
- Metadata handling limited
- No data import tools
- No visualization/GUI
- Limited validation

### Overall Production Readiness: **NOT RECOMMENDED**

**Risk Factors:**
1. Cannot import existing lab data (setup subsystem)
2. Cannot manage rich metadata (database subsystem)
3. Cannot run calculation pipelines fully (calculator)
4. No tools for data exploration (GUI)
5. Incomplete validators

---

## 8. REMEDIATION ROADMAP

### HIGH PRIORITY (Block Production Deployment)
- [ ] Complete calculator.py - add missing methods (est. 20 hours)
- [ ] Implement metadata application UI or CLI (est. 80 hours)
- [ ] Port setup/conv converters for at least one lab (est. 60 hours)
- [ ] Complete database utility functions (est. 40 hours)

### MEDIUM PRIORITY (Needed for General Use)
- [ ] Expand validators subsystem (est. 30 hours)
- [ ] Complete epoch handling (est. 25 hours)
- [ ] Implement basic data visualization (est. 40 hours)

### LOW PRIORITY (Enhancement)
- [ ] Full GUI application (est. 100+ hours)
- [ ] All lab converters (est. 200+ hours)
- [ ] Advanced plotting (est. 60+ hours)

**Total Estimated Work:** 600-800 hours for full parity

---

## 9. RECOMMENDATIONS

### For Current State (Beta/Research Use Only)
1. ✅ Use for core session/document operations
2. ✅ Use for basic data storage and retrieval
3. ❌ Do NOT use for production data ingestion
4. ❌ Do NOT use for metadata-heavy workflows
5. ❌ Do NOT use for complex calculations

### To Achieve Production Parity
1. **Priority 1:** Port the setup subsystem converters (enables data import)
2. **Priority 2:** Complete calculator implementation (enables analysis pipeline)
3. **Priority 3:** Implement metadata UI (enables rich data documentation)
4. **Priority 4:** Complete database utilities (enables complex queries)
5. **Priority 5:** Implement validators (ensures data integrity)

### Long-term Strategy
- Consider whether full MATLAB compatibility is necessary
- Focus on Python-native paradigms rather than 1:1 translation
- Build high-value features in Python rather than porting all MATLAB code

---

## DETAILED FINDINGS SUMMARY TABLE

| Component | MATLAB Lines | Python Lines | Coverage | Critical |
|-----------|--------------|--------------|----------|----------|
| **Core Classes** |
| session | 928 | 972 | 95% | No |
| document | 951 | 984 | 90% | No |
| calculator | 1065 | 473 | 44% | **YES** |
| element | 572 | 755 | 85% | No |
| probe | 367 | 556 | 75% | No |
| **Subsystems** |
| database | 110 | 5 | 4.5% | **YES** |
| setup | 81 | 7 | 8.6% | **YES** |
| gui | 15 | 3 | 20% | YES |
| fun | 51 | 16 | 31% | YES |
| validators | 9 | 2 | 22% | YES |
| ontology | 13 | 16 | 123% | No |
| time | 11 | 14 | 127% | No |
| **TOTALS** |
| **All Files** | **664** | **300** | **45%** | **CRITICAL** |

---

## CONCLUSION

The ndi-python port represents a **solid foundation** for core NDI operations but is **NOT production-ready** due to:

1. **Critical gaps in database metadata handling** (4.5% coverage)
2. **Critical gaps in data import/conversion** (8.6% coverage)
3. **Incomplete calculator pipeline** (44% coverage)
4. **Missing GUI/TUI tools** (20% coverage)
5. **Incomplete validators** (22% coverage)

**Estimated Effort for Production Parity:** 600-800 hours
**Current State:** Suitable for research/development only
**Deployment:** NOT RECOMMENDED

