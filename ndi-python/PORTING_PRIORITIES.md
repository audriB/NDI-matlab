# NDI-Python Porting Priorities

## Quick Stats
- **Overall Completion**: ~50-60%
- **MATLAB Files**: ~400
- **Python Files**: ~200
- **Fully Complete Subsystems**: Ontology, Cloud Sync, Cloud Admin
- **Critical Missing**: GUI (85%), Database Metadata App (100%), App Implementations (100%)

---

## TIER 1: CRITICAL - BLOCKING BASIC FUNCTIONALITY

### 1. Element Specialization Classes
**Priority**: CRITICAL
**Impact**: Blocks neuroscience data analysis

**Missing Classes**:
- `/home/user/NDI-matlab/src/ndi/+ndi/+element/timeseries.m` → `ndi/element/timeseries.py`
- `/home/user/NDI-matlab/src/ndi/+ndi/neuron.m` → `ndi/neuron.py`
- `/home/user/NDI-matlab/src/ndi/+ndi/+element/oneepoch.m` → `ndi/element/oneepoch.py`
- `/home/user/NDI-matlab/src/ndi/+ndi/+element/downsample.m` → `ndi/element/downsample.py`
- `/home/user/NDI-matlab/src/ndi/+ndi/+element/missingepochs.m` → `ndi/element/missingepochs.py`
- `/home/user/NDI-matlab/src/ndi/+ndi/+element/spikesForProbe.m` → `ndi/element/spikes_for_probe.py`

**Dependencies**: Base element class (already exists)
**Estimated Effort**: 2-3 weeks

---

### 2. Epoch Management System
**Priority**: CRITICAL
**Impact**: Required for multi-epoch experiments

**Missing Classes**:
- `/home/user/NDI-matlab/src/ndi/+ndi/+epoch/epochset.m` → `ndi/epoch/epochset.py`
- `/home/user/NDI-matlab/src/ndi/+ndi/+epoch/+epochset/param.m` → `ndi/epoch/epochset_param.py`
- `/home/user/NDI-matlab/src/ndi/+ndi/+epoch/epochprobemap.m` → `ndi/epoch/epochprobemap.py`
- `/home/user/NDI-matlab/src/ndi/+ndi/+epoch/epochprobemap_daqsystem.m` → `ndi/epoch/epochprobemap_daqsystem.py`
- `/home/user/NDI-matlab/src/ndi/+ndi/+epoch/epochrange.m` → `ndi/epoch/epochrange.py`
- `/home/user/NDI-matlab/src/ndi/+ndi/+epoch/findepochnode.m` → `ndi/epoch/findepochnode.py`

**Dependencies**: Time classes (already complete)
**Estimated Effort**: 2-3 weeks

---

### 3. File Navigator Implementations
**Priority**: HIGH
**Impact**: Required for different file organization patterns

**Missing Classes**:
- `/home/user/NDI-matlab/src/ndi/+ndi/+file/+navigator/epochdir.m` → `ndi/file/navigator/epochdir.py`
- `/home/user/NDI-matlab/src/ndi/+ndi/+file/+type/mfdaq_epoch_channel.m` → `ndi/file/type/mfdaq_epoch_channel.py`
- `/home/user/NDI-matlab/src/ndi/+ndi/+file/pfilemirror.m` → `ndi/file/pfilemirror.py`
- `/home/user/NDI-matlab/src/ndi/+ndi/+file/temp_fid.m` → `ndi/file/temp_fid.py`
- `/home/user/NDI-matlab/src/ndi/+ndi/+file/temp_name.m` → `ndi/file/temp_name.py`

**Dependencies**: Base navigator (already exists)
**Estimated Effort**: 1-2 weeks

---

### 4. Validation Framework
**Priority**: HIGH
**Impact**: Required for data integrity

**Missing Classes**:
- `/home/user/NDI-matlab/src/ndi/+ndi/validate.m` → `ndi/validate.py`

**Missing Validators**:
- `/home/user/NDI-matlab/src/ndi/+ndi/+validators/mustHaveRequiredColumns.m`
- `/home/user/NDI-matlab/src/ndi/+ndi/+validators/mustBeEpochInput.m`
- `/home/user/NDI-matlab/src/ndi/+ndi/+validators/mustBeCellArrayOfNonEmptyCharacterArrays.m`
- `/home/user/NDI-matlab/src/ndi/+ndi/+validators/mustBeCellArrayOfNdiSessions.m`
- `/home/user/NDI-matlab/src/ndi/+ndi/+validators/mustBeCellArrayOfClass.m`
- `/home/user/NDI-matlab/src/ndi/+ndi/+validators/mustBeID.m`

**Estimated Effort**: 1 week

---

## TIER 2: HIGH PRIORITY - IMPORTANT FOR FULL FUNCTIONALITY

### 5. Database Metadata App (LARGE)
**Priority**: HIGH
**Impact**: Required for dataset publishing and metadata management

**Status**: 0% complete (53 MATLAB files, 0 Python files)

**Location**: `/home/user/NDI-matlab/src/ndi/+ndi/+database/+metadata_app/`

**Key Components to Port**:
1. **Class Definitions** (18 files):
   - Affiliation, AuthorData, DatasetData, DeviceType, Electrode
   - ElectrodeArray, License, Organization, Pipette, Probe
   - ProbeData, Species, SpeciesData, Strain, Subject, SubjectData

2. **Utility Functions** (35 files):
   - checkValidRORID, expandDropDownItems, generateShortName
   - getCCByLicences, getOpenMindsInstances, getOrcId
   - getRorId, getSpeciesInfo, loadProbes, loadSubjects
   - And many more...

**Dependencies**: 
- OpenMINDS compatibility
- GUI framework (for full functionality)
- Database core (already exists)

**Estimated Effort**: 6-8 weeks (MAJOR EFFORT)

---

### 6. Probe Specializations
**Priority**: MEDIUM-HIGH
**Impact**: Required for specific probe types

**Missing Classes**:
- `/home/user/NDI-matlab/src/ndi/+ndi/+probe/timeseries.m` → `ndi/probe/timeseries.py`
- `/home/user/NDI-matlab/src/ndi/+ndi/+probe/+timeseries/mfdaq.m` → `ndi/probe/timeseries/mfdaq.py`
- `/home/user/NDI-matlab/src/ndi/+ndi/+probe/+timeseries/stimulator.m` → `ndi/probe/timeseries/stimulator.py`
- `/home/user/NDI-matlab/src/ndi/+ndi/+probe/+fun/probestruct2probe.m` → `ndi/probe/fun/probestruct2probe.py`
- `/home/user/NDI-matlab/src/ndi/+ndi/+probe/+fun/getProbeTypeMap.m` → `ndi/probe/fun/get_probe_type_map.py`

**Estimated Effort**: 2 weeks

---

### 7. App Implementations
**Priority**: MEDIUM-HIGH
**Impact**: Required for spike sorting and analysis

**Missing Apps**:
- `/home/user/NDI-matlab/src/ndi/+ndi/+app/spikeextractor.m` → `ndi/app/spikeextractor.py`
- `/home/user/NDI-matlab/src/ndi/+ndi/+app/spikesorter.m` → `ndi/app/spikesorter.py`
- `/home/user/NDI-matlab/src/ndi/+ndi/+app/oridirtuning.m` → `ndi/app/oridirtuning.py`
- `/home/user/NDI-matlab/src/ndi/+ndi/+app/markgarbage.m` → `ndi/app/markgarbage.py`
- `/home/user/NDI-matlab/src/ndi/+ndi/+app/+stimulus/decoder.m` → `ndi/app/stimulus/decoder.py`
- `/home/user/NDI-matlab/src/ndi/+ndi/+app/+stimulus/tuning_response.m` → `ndi/app/stimulus/tuning_response.py`

**Dependencies**: Calculator framework (partial), Element classes
**Estimated Effort**: 4-6 weeks

---

### 8. Calculator Implementations
**Priority**: MEDIUM-HIGH
**Impact**: Required for analysis pipelines

**Missing Calculators**:
- `/home/user/NDI-matlab/src/ndi/+ndi/+calc/+stimulus/tuningcurve.m` → `ndi/calc/stimulus/tuningcurve.py`

**Missing Calculator Methods** (in base calculator.py):
- `graphical_edit_calculator()`
- `plot_parameters()`
- `docfiletext()`
- `parameter_examples()`
- `parameter_default()`

**Estimated Effort**: 2-3 weeks

---

### 9. DAQ System Classes
**Priority**: MEDIUM
**Impact**: Required for multi-file DAQ systems

**Missing Classes**:
- `/home/user/NDI-matlab/src/ndi/+ndi/+daq/+system/mfdaq.m` → `ndi/daq/system/mfdaq.py`
- `/home/user/NDI-matlab/src/ndi/+ndi/+daq/+metadatareader/NewStimStims.m` → `ndi/daq/metadatareader/new_stim_stims.py`
- `/home/user/NDI-matlab/src/ndi/+ndi/+daq/+metadatareader/NielsenLabStims.m` → `ndi/daq/metadatareader/nielsen_lab_stims.py`

**Estimated Effort**: 2 weeks

---

## TIER 3: MEDIUM PRIORITY - ENHANCED FUNCTIONALITY

### 10. Database Utility Functions
**Priority**: MEDIUM
**Impact**: Enhanced database operations

**Missing Functions** (in `/home/user/NDI-matlab/src/ndi/+ndi/+database/+fun/`):
- `createGenBankControlledVocabulary.m`
- `createNIFbrainareas.m`
- `dataset_metadata.m`
- `lookup_uberon_term.m`
- `queryNCIm.m`
- `readGenBankNames.m`, `readGenBankNodes.m`
- `read_presentation_time_structure.m`, `write_presentation_time_structure.m`
- `readtablechar.m`, `writetablechar.m`

**Estimated Effort**: 2 weeks

---

### 11. Session Utility Classes
**Priority**: MEDIUM
**Impact**: Session management features

**Missing Classes**:
- `/home/user/NDI-matlab/src/ndi/+ndi/+session/sessiontable.m` → `ndi/session/sessiontable.py`
- `/home/user/NDI-matlab/src/ndi/+ndi/+session/mock.m` → `ndi/session/mock.py`

**Estimated Effort**: 1 week

---

### 12. Time Sync Rules
**Priority**: MEDIUM
**Impact**: Advanced time synchronization

**Missing Classes**:
- `/home/user/NDI-matlab/src/ndi/+ndi/+time/+syncrule/commontriggers.m` → `ndi/time/syncrule/commontriggers.py`
- `/home/user/NDI-matlab/src/ndi/+ndi/+time/+syncrule/filefind.m` → `ndi/time/syncrule/filefind.py`
- `/home/user/NDI-matlab/src/ndi/+ndi/+time/+syncrule/filematch.m` → `ndi/time/syncrule/filematch.py`

**Estimated Effort**: 1-2 weeks

---

### 13. Utility Functions (+fun/)
**Priority**: MEDIUM
**Impact**: Various utility operations

**Missing Function Categories** (60+ functions):

**High Priority Functions**:
- File utilities: `fun.file.MD5`, `fun.file.dateCreated`, `fun.file.dateUpdated`
- Document utilities: `fun.doc.*` subdirectories
- Data manipulation: `fun.data.readImageStack`, `fun.data.mat2ngrid`, `fun.data.readngrid`, `fun.data.writengrid`

**Medium Priority Functions**:
- Plot utilities: `fun.plot.multichan`
- Table utilities: `fun.table.*`
- Epoch utilities: `fun.epoch.*`
- Probe utilities: `fun.probe.location`
- Stimulus utilities: `fun.stimulus.*`

**Estimated Effort**: 4-6 weeks (spread out)

---

## TIER 4: LOWER PRIORITY - NICE TO HAVE

### 14. Pipeline Management
**Priority**: LOW-MEDIUM
**Impact**: Advanced workflow management

**Missing Class**:
- `/home/user/NDI-matlab/src/ndi/+ndi/pipeline.m` → `ndi/pipeline.py`

**Dependencies**: Calculator system, GUI (for full functionality)
**Estimated Effort**: 3-4 weeks

---

### 15. GUI Components
**Priority**: LOW (can use web/CLI instead)
**Impact**: User interface (85% missing)

**Missing Components** (15 files):
- Main GUIs: `gui.m`, `gui_v2.m`, `docViewer.m`
- Components: `Icon.m`, `Lab.m`, `Data.m`
- Progress: Various progress monitoring components
- Utilities: `centerFigure.m`

**Note**: May not be priority if web-based interface is planned
**Estimated Effort**: 8-12 weeks (if needed)

---

### 16. Setup/Conversion Scripts
**Priority**: LOW
**Impact**: Lab-specific data conversion (0% ported)

**Missing** (80+ files in `/home/user/NDI-matlab/src/ndi/+ndi/+setup/+conv/`):
- Birren lab (6 files)
- Dabrowska lab (6 files)
- Gluckman lab (3 files)
- Haley lab (3 files)
- Marder lab (20 files)
- VHLab (6 files)
- DAQ system configurations (11 files)
- Stimulus extractors (3 files)

**Note**: These are lab-specific; port on-demand
**Estimated Effort**: 6-10 weeks (if all needed)

---

### 17. Documentation Generation
**Priority**: LOW
**Impact**: Auto-documentation features

**Missing** (7 files in `/home/user/NDI-matlab/src/ndi/+ndi/+docs/`):
- `all_documents2markdown.m`
- `build.m`, `calcbuild.m`
- `concatenateFiles.m`, `docfun.m`
- `document2markdown.m`
- `schemastructure2docstructure.m`

**Estimated Effort**: 2-3 weeks

---

## RECOMMENDED PORTING ORDER

### Phase 1: Core Functionality (8-10 weeks)
1. Element specializations (element.timeseries, neuron, etc.) - 3 weeks
2. Epoch management (epochset, epochprobemap) - 3 weeks
3. File navigator implementations (epochdir, etc.) - 2 weeks
4. Validation framework - 1 week

### Phase 2: Analysis Capabilities (10-14 weeks)
5. Database metadata app - 8 weeks
6. App implementations (spike sorting, etc.) - 6 weeks
7. Calculator implementations - 3 weeks
8. Probe specializations - 2 weeks

### Phase 3: Enhanced Features (6-10 weeks)
9. DAQ system classes - 2 weeks
10. Database utility functions - 2 weeks
11. Time sync rules - 2 weeks
12. Utility functions (prioritized subset) - 4 weeks

### Phase 4: Advanced Features (as needed)
13. Pipeline management
14. GUI components (if needed)
15. Lab-specific setup (on-demand)
16. Documentation generation

---

## QUICK WINS (Easy ports with high value)

1. **Session utilities** (~1 week)
   - session.sessiontable
   - session.mock

2. **Validators** (~1 week)
   - 6 missing validator functions

3. **File utilities** (~1 week)
   - temp_fid, temp_name, pfilemirror

4. **Time sync rules** (~2 weeks)
   - 3 syncrule implementations

5. **Basic utility functions** (~2 weeks)
   - File MD5, date functions
   - Table utilities
   - Some doc utilities

**Total Quick Wins**: ~7 weeks of work, adds significant functionality

---

## FILES TO READ FOR PORTING

### For Element Timeseries:
- `/home/user/NDI-matlab/src/ndi/+ndi/+element/timeseries.m`
- `/home/user/NDI-matlab/src/ndi/+ndi/neuron.m`
- `/home/user/NDI-matlab/ndi-python/ndi/element.py` (base class)

### For Epoch Management:
- `/home/user/NDI-matlab/src/ndi/+ndi/+epoch/epochset.m`
- `/home/user/NDI-matlab/src/ndi/+ndi/+epoch/epochprobemap.m`
- `/home/user/NDI-matlab/ndi-python/ndi/epoch.py` (base class)

### For File Navigator:
- `/home/user/NDI-matlab/src/ndi/+ndi/+file/+navigator/epochdir.m`
- `/home/user/NDI-matlab/ndi-python/ndi/file/navigator.py` (base class)

### For Database Metadata:
- `/home/user/NDI-matlab/src/ndi/+ndi/+database/+metadata_app/` (entire directory)
- `/home/user/NDI-matlab/ndi-python/ndi/database/` (existing implementations)

---

## CONCLUSION

**Most Critical Path**: 
Element specializations → Epoch management → Database metadata app → App implementations

**Estimated Time to Feature Parity**: 30-40 weeks of focused development

**Current State**: System is functional for basic NDI operations but lacks advanced analysis features.
