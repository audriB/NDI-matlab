# NDI-matlab vs ndi-python: Comprehensive Feature Comparison

## Executive Summary

**Total MATLAB Files**: ~400+ .m files
**Total Python Files**: ~200+ .py files
**Completion Estimate**: ~50-60% of core functionality ported

---

## 1. CORE CLASSES COMPARISON

### 1.1 Main Classes

| Class | MATLAB | Python | Status | Notes |
|-------|--------|--------|--------|-------|
| session | ✓ (41533 bytes) | ✓ (29380 bytes) | PARTIAL | Missing: syncgraph updates, some helpers |
| session.dir | ✓ | ✓ (SessionDir) | COMPLETE | |
| session.mock | ✓ | ✗ | MISSING | |
| session.sessiontable | ✓ | ✗ | MISSING | |
| document | ✓ (44196 bytes) | ✓ (32271 bytes) | GOOD | Core methods present |
| documentservice | ✓ | ✓ | COMPLETE | |
| element | ✓ (28581 bytes) | ✓ (27222 bytes) | GOOD | Core methods present |
| element.timeseries | ✓ | ✗ | MISSING | Inheritance not implemented |
| element.oneepoch | ✓ | ✗ | MISSING | |
| element.downsample | ✓ | ✗ | MISSING | |
| element.missingepochs | ✓ | ✗ | MISSING | |
| element.spikesForProbe | ✓ | ✗ | MISSING | |
| probe | ✓ (18692 bytes) | ✓ (20095 bytes) | GOOD | Core functionality present |
| probe.timeseries | ✓ | ✗ | MISSING | |
| probe.timeseries.mfdaq | ✓ | ✗ | MISSING | |
| probe.timeseries.stimulator | ✓ | ✗ | MISSING | |
| neuron | ✓ | ✗ | MISSING | Entire class missing |
| calculator | ✓ (54775 bytes) | ✓ (16307 bytes) | PARTIAL | Missing many helper methods |
| app | ✓ | ✓ | GOOD | |
| appdoc | ✓ | ✓ | GOOD | |
| cache | ✓ | ✓ | GOOD | |
| database | ✓ | ✓ | GOOD | |
| dataset | ✓ | ✓ | GOOD | |
| dataset.dir | ✓ | ✓ | GOOD | |
| epoch | ✓ | ✓ | GOOD | |
| ido | ✓ | ✓ | COMPLETE | |
| ontology | ✓ (36798 bytes) | ✓ (23172 bytes) | GOOD | |
| pipeline | ✓ | ✗ | MISSING | Entire class missing |
| query | ✓ | ✓ | GOOD | |
| subject | ✓ | ✓ | GOOD | |
| validate | ✓ | ✗ | MISSING | |

---

## 2. FILE NAVIGATOR SUBSYSTEM (+file/)

### 2.1 Navigator Classes

| Component | MATLAB | Python | Status |
|-----------|--------|--------|--------|
| file.navigator (base) | ✓ (41454 bytes, ~30 methods) | ✓ (31361 bytes, ~25 methods) | GOOD |
| file.navigator.epochdir | ✓ | ✗ | MISSING |
| file.type.mfdaq_epoch_channel | ✓ | ✗ | MISSING |
| file.pfilemirror | ✓ | ✗ | MISSING |
| file.temp_fid | ✓ | ✗ | MISSING |
| file.temp_name | ✓ | ✗ | MISSING |

**Missing Methods in Python Navigator**:
- `find_ingested_documents()`
- Various caching methods
- Some epoch file handling methods

---

## 3. CALCULATOR SUBSYSTEM (+calc/)

### 3.1 Calculator Implementations

| Component | MATLAB | Python | Status |
|-----------|--------|--------|--------|
| calc.example.simple | ✓ | ✓ | COMPLETE |
| calc.stimulus.tuningcurve | ✓ | ✗ | MISSING |

**Missing Calculator Features**:
- `graphical_edit_calculator()` - GUI for editing calculators
- `parameter_examples()` - Example parameter generation
- `parameter_default()` - Default parameter generation
- `docfiletext()` - Documentation text generation
- Stimulus-based calculators entirely missing

---

## 4. DAQ SUBSYSTEM (+daq/)

### 4.1 DAQ Readers

| Reader | MATLAB | Python | Status | Notes |
|--------|--------|--------|--------|-------|
| daq.reader.mfdaq (base) | ✓ (51498 bytes) | ✓ (in __init__.py) | GOOD | |
| daq.reader.mfdaq.blackrock | ✓ (10680 bytes) | ✓ (12771 bytes) | GOOD | All methods present |
| daq.reader.mfdaq.cedspike2 | ✓ (15599 bytes) | ✓ (16527 bytes) | GOOD | All methods present |
| daq.reader.mfdaq.intan | ✓ (19660 bytes) | ✓ (21151 bytes) | GOOD | All methods present |
| daq.reader.mfdaq.ndr | ✓ (9575 bytes) | ✓ (9191 bytes) | GOOD | All methods present |
| daq.reader.mfdaq.spikegadgets | ✓ (16066 bytes) | ✓ (18426 bytes) | GOOD | All methods present |

### 4.2 DAQ Systems

| Component | MATLAB | Python | Status |
|-----------|--------|--------|--------|
| daq.system.mfdaq | ✓ | ✗ | MISSING |
| daq.metadatareader | ✓ | ✓ | PARTIAL |
| daq.metadatareader.NewStimStims | ✓ | ✗ | MISSING |
| daq.metadatareader.NielsenLabStims | ✓ | ✗ | MISSING |
| daq.daqsystemstring | ✓ | ✓ | COMPLETE |

### 4.3 Premature/Image DAQ

| Component | MATLAB | Python | Status |
|-----------|--------|--------|--------|
| daq.premature.ndi_daqsystem_image | ✓ | ✗ | MISSING |
| daq.premature.ndi_daqsystem_image_tiffstack | ✓ | ✗ | MISSING |
| daq.premature.ndi_image | ✓ | ✗ | MISSING |
| daq.premature.ndi_image_tiffstack | ✓ | ✗ | MISSING |

**Status**: DAQ readers are well-ported (90%+), but DAQ system classes and metadata readers are incomplete.

---

## 5. DATABASE SUBSYSTEM (+database/)

### 5.1 Database Implementations

| Implementation | MATLAB | Python | Status |
|----------------|--------|--------|--------|
| database.implementations.database.matlabdumbjsondb | ✓ | ✓ | COMPLETE |
| database.implementations.database.matlabdumbjsondb2 | ✓ | ✓ | COMPLETE |
| database.implementations.database.didsqlite | ✓ | ✓ (sqlite.py) | COMPLETE |
| database.implementations.binarydoc.matfid | ✓ | ✗ | MISSING |

### 5.2 Database Functions (+database/+fun/)

**MATLAB**: 32 function files
**Python**: 23 function files in db/fun/

**Missing in Python**:
- `createGenBankControlledVocabulary.m`
- `createNIFbrainareas.m`
- `dataset_metadata.m`
- `lookup_uberon_term.m`
- `queryNCIm.m`
- `readGenBankNames.m`
- `readGenBankNodes.m`
- `read_presentation_time_structure.m`
- `write_presentation_time_structure.m`
- `readtablechar.m`
- `writetablechar.m`

### 5.3 Database Metadata App (+database/+metadata_app/)

**MATLAB**: 53 files (comprehensive metadata management)
**Python**: ✗ COMPLETELY MISSING

**Missing Components**:
- All metadata app class files (Affiliation, Author, Dataset, Electrode, License, Organization, Probe, Species, Strain, Subject, etc.)
- All metadata app checker files
- All metadata app utility functions
- GUI components for metadata editing

### 5.4 Database Utility Functions

| Component | MATLAB | Python | Status |
|-----------|--------|--------|--------|
| database.ingestion_help | ✓ | ✗ | MISSING |
| database.binarydoc | ✓ | ✗ | MISSING |
| database.internal.list_binary_files | ✓ | ✗ | MISSING |
| database.metadata.table2treatment | ✓ | ✗ | MISSING |
| database.metadata_ds_core (7 files) | ✓ | ✗ | MISSING |

**Status**: Core database (60%), utility functions (40%), metadata app (0%)

---

## 6. GUI SUBSYSTEM (+gui/)

### 6.1 GUI Components

| Component | MATLAB | Python | Status |
|-----------|--------|--------|--------|
| gui.gui | ✓ | ✗ | MISSING |
| gui.gui_v2 | ✓ | ✗ | MISSING |
| gui.docViewer | ✓ | ✗ | MISSING |
| gui.Icon | ✓ | ✗ | MISSING |
| gui.Lab | ✓ | ✗ | MISSING |
| gui.Data | ✓ | ✗ | MISSING |
| gui.component.ProgressMonitor (abstract) | ✓ | ✗ | MISSING |
| gui.component.CommandWindowProgressMonitor | ✓ | ✓ (progress_monitor.py) | PARTIAL |
| gui.component.NDIProgressBar | ✓ | ✗ | MISSING |
| gui.component.ProgressBarWindow | ✓ | ✗ | MISSING |
| gui.component.internal.ProgressTracker | ✓ | ✓ (progress_tracker.py) | PARTIAL |
| gui.component.internal.AsynchProgressTracker | ✓ | ✗ | MISSING |
| gui.component.internal.event.* | ✓ (2 event classes) | ✗ | MISSING |
| gui.utility.centerFigure | ✓ | ✗ | MISSING |

**Status**: GUI subsystem ~15% ported. Most GUI components missing.

---

## 7. APP SUBSYSTEM (+app/)

### 7.1 App Implementations

| Component | MATLAB | Python | Status |
|-----------|--------|--------|--------|
| app (base class) | ✓ | ✓ | GOOD |
| app.appdoc (base class) | ✓ | ✓ | GOOD |
| app.markgarbage | ✓ | ✗ | MISSING |
| app.oridirtuning | ✓ | ✗ | MISSING |
| app.spikeextractor | ✓ | ✗ | MISSING |
| app.spikesorter | ✓ | ✗ | MISSING |
| app.stimulus.decoder | ✓ | ✗ | MISSING |
| app.stimulus.tuning_response | ✓ | ✗ | MISSING |

**Status**: Base app classes ported (100%), specific app implementations (0%)

---

## 8. EPOCH SUBSYSTEM (+epoch/)

### 8.1 Epoch Classes

| Component | MATLAB | Python | Status |
|-----------|--------|--------|--------|
| epoch (base) | ✓ | ✓ | COMPLETE |
| epoch.epochset | ✓ | ✗ | MISSING |
| epoch.epochset.param | ✓ | ✗ | MISSING |
| epoch.epochprobemap | ✓ | ✗ | MISSING |
| epoch.epochprobemap_daqsystem | ✓ | ✗ | MISSING |
| epoch.epochrange | ✓ | ✗ | MISSING |
| epoch.findepochnode | ✓ | ✗ | MISSING |

**Status**: Basic epoch class ported, advanced epoch management missing.

---

## 9. TIME SUBSYSTEM (+time/)

### 9.1 Time Classes

| Component | MATLAB | Python | Status |
|-----------|--------|--------|--------|
| time.clocktype | ✓ | ✓ | COMPLETE |
| time.syncgraph | ✓ | ✓ | GOOD |
| time.syncrule | ✓ | ✓ | GOOD |
| time.syncrule.commontriggers | ✓ | ✗ | MISSING |
| time.syncrule.filefind | ✓ | ✗ | MISSING |
| time.syncrule.filematch | ✓ | ✗ | MISSING |
| time.timemapping | ✓ | ✓ | COMPLETE |
| time.timereference | ✓ | ✓ | COMPLETE |
| time.timeseries | ✓ | ✓ | COMPLETE |
| time.fun.samples2times | ✓ | ✓ | COMPLETE |
| time.fun.times2samples | ✓ | ✓ | COMPLETE |

**Status**: Core time classes (100%), advanced sync rules (0%)

---

## 10. ONTOLOGY SUBSYSTEM (+ontology/)

### 10.1 Ontology Classes

| Ontology | MATLAB | Python | Status |
|----------|--------|--------|--------|
| CHEBI | ✓ | ✓ | COMPLETE |
| CL | ✓ | ✓ | COMPLETE |
| EMPTY | ✓ | ✓ | COMPLETE |
| NCBITaxon | ✓ | ✓ | COMPLETE |
| NCIT | ✓ | ✓ | COMPLETE |
| NCIm | ✓ | ✓ | COMPLETE |
| NDIC | ✓ | ✓ | COMPLETE |
| OM | ✓ | ✓ | COMPLETE |
| PATO | ✓ | ✓ | COMPLETE |
| PubChem | ✓ | ✓ | COMPLETE |
| RRID | ✓ | ✓ | COMPLETE |
| Uberon | ✓ | ✓ | COMPLETE |
| WBStrain | ✓ | ✓ | COMPLETE |
| obo_parser | ✗ | ✓ | PYTHON ADDITION |

**Status**: Ontology subsystem 100% ported (13/13 + parser)

---

## 11. CLOUD SUBSYSTEM (+cloud/)

### 11.1 Cloud API

| Component | MATLAB | Python | Status |
|-----------|--------|--------|--------|
| cloud.api.auth.* | ✓ (6 functions) | ✓ (auth.py) | GOOD |
| cloud.api.datasets.* | ✓ (12 functions) | ✓ (datasets.py) | GOOD |
| cloud.api.documents.* | ✓ (12 functions) | ✓ (documents.py) | GOOD |
| cloud.api.files.* | ✓ (6 functions) | ✓ (files.py) | GOOD |
| cloud.api.users.* | ✓ (2 functions) | ✓ (users.py) | GOOD |
| cloud.api.implementation.* | ✓ (30 classes) | ✗ | MISSING |
| cloud.api.call | ✓ | ✓ (client.py) | GOOD |
| cloud.api.url | ✓ | ✓ (base.py) | GOOD |

### 11.2 Cloud Sync

| Component | MATLAB | Python | Status |
|-----------|--------|--------|--------|
| cloud.sync.downloadNew | ✓ | ✓ | COMPLETE |
| cloud.sync.uploadNew | ✓ | ✓ | COMPLETE |
| cloud.sync.mirrorFromRemote | ✓ | ✓ | COMPLETE |
| cloud.sync.mirrorToRemote | ✓ | ✓ | COMPLETE |
| cloud.sync.twoWaySync | ✓ | ✓ | COMPLETE |
| cloud.sync.validate | ✓ | ✓ | COMPLETE |
| cloud.sync.SyncOptions | ✓ | ✓ | COMPLETE |
| cloud.sync.enum.SyncMode | ✓ | ✓ (sync_mode.py) | COMPLETE |
| cloud.sync.internal.* | ✓ (13 functions) | ✓ (13 functions) | COMPLETE |
| cloud.sync.internal.index.* | ✓ (5 functions) | ✓ (5 functions) | COMPLETE |

### 11.3 Cloud Download/Upload

| Component | MATLAB | Python | Status |
|-----------|--------|--------|--------|
| cloud.download.dataset | ✓ | ✓ | COMPLETE |
| cloud.download.datasetDocuments | ✓ | ✓ | COMPLETE |
| cloud.download.downloadDatasetFiles | ✓ | ✓ | COMPLETE |
| cloud.download.downloadDocumentCollection | ✓ | ✓ | COMPLETE |
| cloud.download.jsons2documents | ✓ | ✓ | COMPLETE |
| cloud.download.internal.* | ✓ (2 functions) | ✓ (2 functions) | COMPLETE |
| cloud.upload.newDataset | ✓ | ✓ | COMPLETE |
| cloud.upload.scanForUpload | ✓ | ✓ | COMPLETE |
| cloud.upload.uploadDocumentCollection | ✓ | ✓ | COMPLETE |
| cloud.upload.uploadToNDICloud | ✓ | ✓ | COMPLETE |
| cloud.upload.zipForUpload | ✓ | ✓ | COMPLETE |
| cloud.upload.internal.* | ✓ | ✓ | COMPLETE |

### 11.4 Cloud Admin

| Component | MATLAB | Python | Status |
|-----------|--------|--------|--------|
| cloud.admin.checkSubmission | ✓ | ✓ | COMPLETE |
| cloud.admin.createNewDOI | ✓ | ✓ | COMPLETE |
| cloud.admin.registerDatasetDOI | ✓ | ✓ | COMPLETE |
| cloud.admin.crossref.* | ✓ (8 functions) | ✓ (8 functions) | COMPLETE |
| cloud.admin.crossref.conversion.* | ✓ (5 functions) | ✓ (5 functions) | COMPLETE |
| cloud.admin.crossref.Constants | ✓ | ✓ | COMPLETE |

### 11.5 Cloud Utilities

| Component | MATLAB | Python | Status |
|-----------|--------|--------|--------|
| cloud.internal.* | ✓ (9 functions) | ✓ (9 functions) | COMPLETE |
| cloud.utility.* | ✓ (2 functions) | ✓ (2 functions) | COMPLETE |
| cloud.authenticate | ✓ | ✗ | MISSING |
| cloud.authenticateOriginal | ✓ | ✗ | MISSING |
| cloud.downloadDataset | ✓ | ✗ | MISSING |
| cloud.syncDataset | ✓ | ✗ | MISSING |
| cloud.uilogin | ✓ | ✗ | MISSING |
| cloud.uploadDataset | ✓ | ✗ | MISSING |
| cloud.uploadSingleFile | ✓ | ✗ | MISSING |
| cloud.ui.dialog.selectCloudDataset | ✓ | ✗ | MISSING |

**MATLAB Cloud Files**: 151
**Python Cloud Files**: 82

**Status**: Cloud API and sync (95%), Cloud UI helpers (0%)

---

## 12. SETUP SUBSYSTEM (+setup/)

### 12.1 Setup Makers

| Component | MATLAB | Python | Status |
|-----------|--------|--------|--------|
| setup.NDIMaker.sessionMaker | ✓ | ✓ (session_maker.py) | GOOD |
| setup.NDIMaker.subjectMaker | ✓ | ✓ (subject_maker.py) | GOOD |
| setup.NDIMaker.epochProbeMapMaker | ✓ | ✓ (epoch_probe_map_maker.py) | GOOD |
| setup.NDIMaker.SubjectInformationCreator | ✓ | ✓ (subject_information_creator.py) | GOOD |
| setup.NDIMaker.TreatmentCreator | ✓ | ✗ | MISSING |
| setup.NDIMaker.imageDocMaker | ✓ | ✗ | MISSING |
| setup.NDIMaker.stimulusDocMaker | ✓ | ✗ | MISSING |
| setup.NDIMaker.tableDocMaker | ✓ | ✗ | MISSING |
| setup.NDIMaker.treatmentMaker | ✓ | ✗ | MISSING |

### 12.2 Lab-Specific Setup

| Component | MATLAB Files | Python Files | Status |
|-----------|--------------|--------------|--------|
| setup.conv.birren.* | 6 | 0 | MISSING |
| setup.conv.dabrowska.* | 6 | 0 | MISSING |
| setup.conv.gluckman.* | 3 | 0 | MISSING |
| setup.conv.haley.* | 3 | 0 | MISSING |
| setup.conv.marder.* | 20 | 0 | MISSING |
| setup.conv.vhlab.* | 6 | 0 | MISSING |
| setup.daq.system.* | 11 | 0 | MISSING |
| setup.daq.metadatareader.* | 2 | 0 | MISSING |
| setup.daq.reader.mfdaq.stimulus.* | 3 | 0 | MISSING |
| setup.epoch.* | 1 | 0 | MISSING |
| setup.stimulus.* | 2 | 0 | MISSING |
| setup.DaqSystemConfiguration | ✓ | ✗ | MISSING |
| setup lab classes (5 labs) | ✓ | ✗ | MISSING |

**MATLAB Setup Files**: 88
**Python Setup Files**: 7

**Status**: Core makers (50%), lab-specific setup (0%)

---

## 13. UTILITY SUBSYSTEMS

### 13.1 Common Utilities (+common/)

| Component | MATLAB | Python | Status |
|-----------|--------|--------|--------|
| common.PathConstants | ✓ | ✓ (path_constants.py) | COMPLETE |
| common.assertDIDInstalled | ✓ | ✓ (did_integration.py) | GOOD |
| common.getCache | ✓ | ✗ | MISSING |
| common.getDatabaseHierarchy | ✓ | ✗ | MISSING |
| common.getLogger | ✓ | ✓ (logger.py) | COMPLETE |

### 13.2 Utility Functions (+util/)

| Component | MATLAB | Python | Status |
|-----------|--------|--------|--------|
| util.unwrapTableCellContent | ✓ | ✗ | MISSING |
| util.rehydrateJSONNanNull | ✓ | ✓ (json_utils.py) | GOOD |
| util.hexDump | ✓ | ✓ (hex.py) | GOOD |
| util.hexDiff | ✓ | ✓ (hex.py) | GOOD |
| util.hexDiffBytes | ✓ | ✓ (hex.py) | GOOD |
| util.getHexDiffFromFileObj | ✓ | ✗ | MISSING |
| util.downsampleTimeseries | ✓ | ✗ | MISSING |
| util.choosefileordir | ✓ | ✗ | MISSING |
| util.choosefile | ✓ | ✗ | MISSING |
| util.datestamp2datetime | ✓ | ✓ (datetime_utils.py) | GOOD |
| - | ✗ | ✓ (cache_utils.py) | PYTHON ADDITION |
| - | ✗ | ✓ (document_utils.py) | PYTHON ADDITION |
| - | ✗ | ✓ (file_utils.py) | PYTHON ADDITION |
| - | ✗ | ✓ (math_utils.py) | PYTHON ADDITION |
| - | ✗ | ✓ (plot_utils.py) | PYTHON ADDITION |
| - | ✗ | ✓ (string_utils.py) | PYTHON ADDITION |
| - | ✗ | ✓ (table_utils.py) | PYTHON ADDITION |

### 13.3 Function Utilities (+fun/)

**MATLAB**: ~80 function files in various subdirectories
**Python**: ~20 function files

**Missing Python Function Categories**:
- `fun.calc.*` - Calculation utilities
- `fun.data.*` - Data manipulation (readImageStack, mat2ngrid, etc.)
- `fun.dataset.*` - Dataset utilities
- `fun.doc.*` - Document utilities (many subdirectories)
- `fun.docTable.*` - Document table utilities
- `fun.epoch.*` - Epoch utilities
- `fun.file.*` - File utilities (MD5, dateCreated, dateUpdated)
- `fun.plot.*` - Plotting utilities
- `fun.probe.*` - Probe utilities
- `fun.stimulus.*` - Stimulus utilities
- `fun.table.*` - Table utilities

### 13.4 Validators (+validators/)

| Component | MATLAB | Python | Status |
|-----------|--------|--------|--------|
| validators.mustMatchRegex | ✓ | ✓ | GOOD |
| validators.mustBeNumericClass | ✓ | ✓ | GOOD |
| validators.mustBeTextLike | ✓ | ✓ | GOOD |
| validators.mustHaveRequiredColumns | ✓ | ✗ | MISSING |
| validators.mustBeEpochInput | ✓ | ✗ | MISSING |
| validators.mustBeCellArrayOfNonEmptyCharacterArrays | ✓ | ✗ | MISSING |
| validators.mustBeCellArrayOfNdiSessions | ✓ | ✗ | MISSING |
| validators.mustBeCellArrayOfClass | ✓ | ✗ | MISSING |
| validators.mustBeID | ✓ | ✗ | MISSING |

---

## 14. EXAMPLE/TUTORIAL SUBSYSTEM

### 14.1 Examples

| Component | MATLAB | Python | Status |
|-----------|--------|--------|--------|
| example.fun.* | ✓ (7 functions) | ✗ | MISSING |
| example.tutorial.* | ✓ (6 tutorials) | ✗ | MISSING |
| example.tutorial.plottreeshrewdata | ✓ | ✗ | MISSING |
| - | ✗ | ✓ (tutorial_01_basics.py) | PYTHON ADDITION |
| - | ✗ | ✓ (tutorial_02_daq.py) | PYTHON ADDITION |
| - | ✗ | ✓ (tutorial_03_dataset.py) | PYTHON ADDITION |

---

## 15. MOCK/TEST SUBSYSTEM

### 15.1 Mock Objects

| Component | MATLAB | Python | Status |
|-----------|--------|--------|--------|
| mock.ctest | ✓ | ✗ | MISSING |
| mock.fun.clear | ✓ | ✗ | MISSING |
| mock.fun.stimulus_presentation | ✓ | ✗ | MISSING |
| mock.fun.stimulus_response | ✓ | ✓ | PARTIAL |
| mock.fun.subject_stimulator_neuron | ✓ | ✗ | MISSING |
| - | ✗ | ✓ (daqsystem.py) | PYTHON ADDITION |
| - | ✗ | ✓ (database.py) | PYTHON ADDITION |
| - | ✗ | ✓ (probe.py) | PYTHON ADDITION |
| - | ✗ | ✓ (session.py) | PYTHON ADDITION |

---

## 16. DOCUMENTATION SUBSYSTEM (+docs/)

| Component | MATLAB | Python | Status |
|-----------|--------|--------|--------|
| docs.all_documents2markdown | ✓ | ✗ | MISSING |
| docs.build | ✓ | ✗ | MISSING |
| docs.calcbuild | ✓ | ✗ | MISSING |
| docs.concatenateFiles | ✓ | ✗ | MISSING |
| docs.docfun | ✓ | ✗ | MISSING |
| docs.document2markdown | ✓ | ✗ | MISSING |
| docs.schemastructure2docstructure | ✓ | ✗ | MISSING |

---

## 17. CRITICAL MISSING FEATURES

### 17.1 High Priority Missing Classes

1. **pipeline** - Entire pipeline management system
2. **neuron** - Neuron element type
3. **element.timeseries** - Timeseries element specialization
4. **epoch.epochset** - Epoch set management
5. **epoch.epochprobemap** - Epoch-probe mapping
6. **validate** - Validation framework
7. **session.sessiontable** - Session table management

### 17.2 High Priority Missing Subsystems

1. **GUI Components** (~85% missing)
   - All main GUI windows (gui, gui_v2, docViewer, Icon, Lab, Data)
   - Most progress monitoring components
   - All GUI utilities

2. **Database Metadata App** (100% missing)
   - All 53 metadata app files
   - Critical for dataset publishing

3. **App Implementations** (100% missing)
   - spikeextractor
   - spikesorter
   - oridirtuning
   - markgarbage
   - stimulus apps

4. **Lab-Specific Setup** (100% missing)
   - All lab conversion scripts
   - DAQ system configurations
   - Lab-specific utilities

5. **Calculator Implementations**
   - stimulus.tuningcurve
   - Helper methods for parameter generation

6. **File Navigator Implementations**
   - epochdir navigator
   - pfilemirror
   - File type handlers

7. **Function Utilities** (~60% missing)
   - Document utilities
   - Data manipulation
   - Plotting utilities
   - Stimulus utilities

### 17.3 Missing Method-Level Features

#### Session Methods Missing:
- `update_syncgraph_in_db()`
- `autoclose_listener_callback()`
- Some hidden helper methods

#### Calculator Methods Missing:
- `graphical_edit_calculator()`
- `plot_parameters()`
- `docfiletext()`
- `parameter_examples()`
- `parameter_default()`

#### Navigator Methods Missing:
- `find_ingested_documents()`
- Advanced caching methods

---

## 18. FEATURE COMPLETENESS BY SUBSYSTEM

| Subsystem | Completeness | Notes |
|-----------|--------------|-------|
| Core Classes | 70% | Main classes ported, specializations missing |
| File Navigator | 60% | Base class good, implementations missing |
| Calculator | 40% | Base class partial, implementations missing |
| DAQ Readers | 95% | All readers ported well |
| DAQ System | 30% | System classes incomplete |
| Database Core | 60% | Implementations good, utilities partial |
| Database Metadata | 0% | Completely missing |
| Database Functions | 72% | 23/32 functions |
| GUI | 15% | Most GUI missing |
| Apps | 30% | Base classes only |
| Epoch | 30% | Basic class only |
| Time | 80% | Core classes complete, rules missing |
| Ontology | 100% | Fully ported |
| Cloud API | 95% | API complete, UI helpers missing |
| Cloud Sync | 100% | Fully ported |
| Cloud Admin | 100% | Fully ported |
| Setup Makers | 50% | Core makers, lab setup missing |
| Utilities | 50% | Many utility functions missing |
| Validators | 40% | Basic validators only |
| Examples | 40% | Different tutorials |
| Mock | 50% | Different mock objects |
| Documentation | 0% | All doc generation missing |

---

## 19. OVERALL PORT STATUS

### Statistics

- **Total MATLAB .m files**: ~400
- **Total Python .py files**: ~200
- **Estimated lines of code ported**: ~50%
- **Functional subsystems fully ported**: 3 (Ontology, Cloud Sync, Cloud Admin)
- **Functional subsystems partially ported**: 15
- **Functional subsystems not started**: 2 (GUI, Database Metadata)

### Priority Recommendations for Completion

#### Tier 1 (Critical for Basic Functionality)
1. element.timeseries - Required for many element types
2. epoch.epochset and epoch.epochprobemap - Core epoch management
3. Database metadata app - Critical for publishing
4. File navigator implementations (epochdir)
5. Validation framework

#### Tier 2 (Important for Full Functionality)
1. GUI components (at least basic ones)
2. App implementations (spikeextractor, spikesorter)
3. Calculator implementations (tuningcurve)
4. DAQ system classes
5. Utility functions (data, doc, file, plot)

#### Tier 3 (Nice to Have)
1. Pipeline management
2. Lab-specific setup scripts
3. Documentation generation
4. Advanced sync rules
5. Additional validators

---

## 20. PYTHON-SPECIFIC IMPROVEMENTS

The Python port has added some improvements:
1. Better utility organization (separate utils for cache, document, file, math, plot, string, table)
2. OBO parser for ontologies
3. More Pythonic mock objects
4. Different tutorial approach

---

## CONCLUSION

The ndi-python port has successfully implemented:
- **Core architecture**: ~70% complete
- **Cloud functionality**: ~95% complete  
- **DAQ readers**: ~95% complete
- **Ontology system**: 100% complete
- **Time management**: ~80% complete

Major gaps remain in:
- **GUI components**: ~85% missing
- **Database metadata app**: 100% missing
- **Lab-specific setup**: 100% missing
- **App implementations**: 100% missing
- **Advanced features**: Pipeline, specialized elements, validators

The port is functional for basic NDI operations (sessions, documents, DAQ reading, cloud sync, ontology) but lacks the advanced features needed for full MATLAB feature parity, particularly in GUI, metadata management, and specialized analysis apps.
