# Phase 3 Implementation Plan - DAQ System & Time Synchronization

**Date Created**: November 17, 2025
**Status**: PLANNING COMPLETE ✅
**Estimated Timeline**: 6 weeks
**Actual Start**: November 17, 2025

---

## 🎯 Phase 3 Goals

Complete the DAQ (Data Acquisition) System and Time Synchronization infrastructure to enable:
- Reading data from multiple hardware platforms (Intan, Blackrock, CED, SpikeGadgets)
- Synchronizing timestamps across multiple devices
- Converting times between different clock domains
- Managing epochs and file navigation

---

## 📊 Current Status Assessment

### ✅ What's Already Complete (60% of Phase 3)

**Time System** (~80% done):
- `ClockType` - Complete with enum and validation
- `TimeReference` - Complete structure
- `TimeMapping` - Complete polynomial mapping
- `TimeSeries` - Complete abstract interface
- `SyncRule` - Complete base class
- Time utilities: `samples2times()`, `times2samples()` - fully tested

**DAQ System** (~50% done):
- `DAQSystemString` - Complete with parsing/generation
- `System` - Basic structure (needs file navigator and ingest)
- `Reader` - Abstract base defined
- `MFDAQReader` - Base structure
- Hardware readers: Intan, Blackrock, CED, SpikeGadgets, NDR (partial implementations)

### ❌ What Needs To Be Completed (40% remaining)

**Priority 1 - Critical (Weeks 1-3)**:
1. **SyncRule implementations** - FileFind, FileMatch, CommonTriggers
2. **SyncGraph completion** - Graph building and time conversion
3. **FileNavigator abstraction** - Blocking file I/O

**Priority 2 - Important (Weeks 3-5)**:
4. Hardware reader enhancements (Intan, Blackrock details)
5. System.ingest() and document integration
6. EpochProbeMap integration

**Priority 3 - Polish (Week 6)**:
7. Comprehensive testing
8. Documentation and examples

---

## 🗺️ Implementation Roadmap

### Week 1: SyncRule Implementations

**Goals**:
- Implement `FileFind` sync rule (load mappings from files)
- Implement `FileMatch` sync rule (match by file characteristics)
- Implement `CommonTriggers` sync rule (match by triggers)

**Deliverables**:
- `ndi/time/syncrule/filefind.py` (~150 lines)
- `ndi/time/syncrule/filematch.py` (~130 lines)
- `ndi/time/syncrule/commontriggers.py` (~130 lines)
- Tests for each rule (~100 lines each)

**Dependencies**: None (SyncRule base already exists)

---

### Week 2: SyncGraph Completion

**Goals**:
- Complete `SyncGraph.build_graph()` - enumerate DAQ systems and apply sync rules
- Complete `SyncGraph.timeconvert()` - convert times between epochs
- Complete `SyncGraph.find_path()` - Dijkstra pathfinding

**Deliverables**:
- Enhanced `ndi/time/syncgraph.py` (+300 lines)
- Integration tests (~150 lines)
- Time conversion examples

**Dependencies**: SyncRule implementations (Week 1)

---

### Week 3: FileNavigator Abstraction

**Goals**:
- Create abstract `FileNavigator` base class
- Implement `EpochDirNavigator` (file-based)
- Implement `MemoryNavigator` (for testing)
- Integrate with System class

**Deliverables**:
- `ndi/file/navigator/_navigator_base.py` (~200 lines)
- Enhanced navigator implementations
- System integration tests

**Dependencies**: None (can run in parallel with Weeks 1-2)

---

### Week 4: Hardware Reader Enhancements

**Goals**:
- Complete Intan reader (header parsing, channel mapping)
- Complete Blackrock reader (NSx/NEV parsing)
- Complete CED Spike2 reader (config reading)
- Complete SpikeGadgets reader (config/metadata)

**Deliverables**:
- Enhanced hardware readers (+600 lines across 4 files)
- Tests with real data formats
- Channel mapping validation

**Dependencies**: FileNavigator (Week 3)

---

### Week 5: System Integration

**Goals**:
- Implement `System.ingest()` with document generation
- Implement `System.getprobes()` - probe extraction
- Implement `System.getepochprobemap()`
- Implement `System.getmetadata()` - metadata chain

**Deliverables**:
- Enhanced `ndi/daq/system.py` (+200 lines)
- Document generation and persistence
- Integration with Phase 2 (probes, metadata)

**Dependencies**: FileNavigator (Week 3), Hardware readers (Week 4)

---

### Week 6: Testing & Documentation

**Goals**:
- Comprehensive test suite for all Phase 3 components
- Integration tests combining DAQ + time sync
- Documentation and examples
- Performance optimization

**Deliverables**:
- Test coverage >95% for new code
- `tutorial_05_daq_time.py` - Complete DAQ/time tutorial
- Updated PHASE3_PROGRESS.md
- SESSION_HANDOFF.md update

**Dependencies**: All previous weeks

---

## 📁 File Structure

```
ndi-python/
├── ndi/
│   ├── daq/
│   │   ├── system.py                    # ENHANCE: Add ingest(), getprobes()
│   │   ├── reader.py                    # ENHANCE: Document integration
│   │   ├── daqsystemstring.py           # ✅ COMPLETE
│   │   ├── metadatareader.py            # ENHANCE: Compression support
│   │   └── reader/
│   │       └── mfdaq/
│   │           ├── intan.py             # ENHANCE: Channel mapping
│   │           ├── blackrock.py         # ENHANCE: NSx parsing
│   │           ├── cedspike2.py         # ENHANCE: Config reading
│   │           └── spikegadgets.py      # ENHANCE: Config/metadata
│   ├── time/
│   │   ├── clocktype.py                 # ✅ COMPLETE
│   │   ├── timereference.py             # ✅ COMPLETE
│   │   ├── timemapping.py               # ✅ COMPLETE
│   │   ├── timeseries.py                # ✅ COMPLETE
│   │   ├── syncrule.py                  # ✅ COMPLETE (base)
│   │   ├── syncgraph.py                 # ENHANCE: Graph building, timeconvert
│   │   ├── syncrule/
│   │   │   ├── __init__.py              # NEW
│   │   │   ├── filefind.py              # NEW: Load from sync files
│   │   │   ├── filematch.py             # NEW: Match by file characteristics
│   │   │   └── commontriggers.py        # NEW: Match by triggers
│   │   └── fun/
│   │       ├── samples2times.py         # ✅ COMPLETE
│   │       └── times2samples.py         # ✅ COMPLETE
│   └── file/
│       └── navigator/
│           └── _navigator_base.py       # NEW: Abstract file navigation
├── tests/
│   ├── test_syncrule_filefind.py        # NEW
│   ├── test_syncrule_filematch.py       # NEW
│   ├── test_syncrule_commontriggers.py  # NEW
│   ├── test_syncgraph_complete.py       # NEW
│   ├── test_file_navigator.py           # NEW
│   ├── test_hardware_readers.py         # NEW
│   └── test_daq_time_integration.py     # ENHANCE
└── ndi/example/
    └── tutorial_05_daq_time.py          # NEW
```

---

## 🎯 Success Criteria

### Code Completeness
- [ ] All 3 SyncRule subclasses implemented and tested
- [ ] SyncGraph.build_graph() builds correct graph structure
- [ ] SyncGraph.timeconvert() converts times accurately
- [ ] FileNavigator abstraction complete
- [ ] All 4 hardware readers can list channels
- [ ] System.ingest() generates proper documents
- [ ] Full integration between DAQ and time systems

### Testing
- [ ] >95% test coverage on new code
- [ ] Integration tests pass for DAQ + time workflows
- [ ] Real data format tests (if available)
- [ ] SyncGraph pathfinding validated
- [ ] Edge cases handled (missing files, invalid times, etc.)

### Documentation
- [ ] All classes have comprehensive docstrings
- [ ] Tutorial demonstrating DAQ + time usage
- [ ] Architecture documentation updated
- [ ] PHASE3_PROGRESS.md tracks completion
- [ ] SESSION_HANDOFF.md prepared for next session

---

## 📊 Estimated Effort

| Component | Lines of Code | Effort | Dependencies |
|-----------|---------------|--------|--------------|
| SyncRule impls (3 classes) | ~410 | 1 week | SyncRule base |
| SyncGraph completion | ~300 | 1 week | SyncRule impls |
| FileNavigator | ~200 | 1 week | None |
| Hardware readers | ~600 | 1 week | FileNavigator |
| System integration | ~200 | 1 week | All above |
| Testing & docs | ~600 | 1 week | All above |
| **TOTAL** | **~2,310** | **6 weeks** | - |

---

## 🔧 Key Design Decisions

### 1. FileNavigator Abstraction
**Decision**: Create abstract base class with file and memory implementations
**Rationale**: Enables testing without filesystem, cleaner separation of concerns
**Impact**: Unblocks System/Reader file I/O

### 2. SyncRule Plugin Architecture
**Decision**: Keep sync rules as separate classes in syncrule/ package
**Rationale**: Extensible, users can add custom sync rules
**Impact**: Clean API, easy to add new synchronization methods

### 3. SyncGraph Path Finding
**Decision**: Use Dijkstra's algorithm for shortest path in epoch graph
**Rationale**: Standard graph algorithm, handles weighted edges (costs)
**Impact**: Efficient time conversion, well-understood algorithm

### 4. Hardware Reader Strategy
**Decision**: Complete basic functionality (channel listing) before advanced features
**Rationale**: Enables testing and integration; advanced features can be added incrementally
**Impact**: Phase 3 can complete without full hardware support

---

## 🚨 Risks & Mitigation

### Risk 1: FileNavigator complexity
**Impact**: HIGH - Blocks System and Reader functionality
**Mitigation**: Start with minimal viable abstraction, expand as needed
**Contingency**: Use existing EpochDir navigator if abstraction takes too long

### Risk 2: Hardware data format complexity
**Impact**: MEDIUM - May delay reader completion
**Mitigation**: Focus on channel enumeration first, data reading second
**Contingency**: Mark advanced readers as "partial" and document limitations

### Risk 3: SyncGraph pathfinding edge cases
**Impact**: MEDIUM - Time conversion errors
**Mitigation**: Comprehensive test suite with various graph structures
**Contingency**: Fall back to simpler direct mappings if graph is too complex

### Risk 4: Integration with Phases 1 & 2
**Impact**: LOW - Already well-integrated
**Mitigation**: Use existing Document, Probe, Session APIs
**Contingency**: Mock dependencies during development

---

## 📚 References

- **MATLAB DAQ System**: `/home/user/NDI-matlab/src/ndi/+ndi/+daq/`
- **MATLAB Time System**: `/home/user/NDI-matlab/src/ndi/+ndi/+time/`
- **Python Implementation**: `/home/user/NDI-matlab/ndi-python/ndi/`
- **Existing Tests**: `/home/user/NDI-matlab/ndi-python/tests/test_phase4_daq_time.py`

---

## 📈 Progress Tracking

This plan will be updated weekly with:
- Completed components
- Test results
- Blockers and resolutions
- Timeline adjustments

See `PHASE3_PROGRESS.md` for detailed progress tracking (to be created).

---

**Plan Status**: ✅ READY TO EXECUTE
**Next Step**: Begin Week 1 - Implement SyncRule subclasses
**Owner**: Claude Code (NDI Python Port Project)
**Created**: November 17, 2025
