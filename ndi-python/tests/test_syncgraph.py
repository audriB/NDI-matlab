"""
Tests for NDI SyncGraph - time synchronization graph.

Tests graph building, pathfinding, and time conversion.
"""

import pytest
import numpy as np
from ndi.time.syncgraph import SyncGraph
from ndi.time.syncrules import FileMatch
from ndi.time.timemapping import TimeMapping


class TestSyncGraphBasic:
    """Test basic SyncGraph creation and configuration."""

    def test_syncgraph_creation(self):
        """Test creating a SyncGraph."""
        graph = SyncGraph()
        assert graph is not None
        assert len(graph.rules) == 0

    def test_syncgraph_add_rule(self):
        """Test adding a sync rule."""
        graph = SyncGraph()
        rule = FileMatch({'number_fullpath_matches': 2})

        graph.add_rule(rule)
        assert len(graph.rules) == 1
        assert graph.rules[0] == rule

    def test_syncgraph_add_duplicate_rule(self):
        """Test that duplicate rules are not added."""
        graph = SyncGraph()
        rule = FileMatch({'number_fullpath_matches': 2})

        graph.add_rule(rule)
        graph.add_rule(rule)  # Add same rule again

        assert len(graph.rules) == 1

    def test_syncgraph_remove_rule(self):
        """Test removing a sync rule."""
        graph = SyncGraph()
        rule1 = FileMatch({'number_fullpath_matches': 2})
        rule2 = FileMatch({'number_fullpath_matches': 3})

        graph.add_rule([rule1, rule2])
        assert len(graph.rules) == 2

        graph.remove_rule(0)
        assert len(graph.rules) == 1
        assert graph.rules[0] == rule2


class TestSyncGraphManualNodes:
    """Test SyncGraph with manually added nodes."""

    def test_manual_add_simple_nodes(self):
        """Test manually adding nodes to graph."""
        graph = SyncGraph()

        nodes = [
            {'epoch_id': 'e1', 'epoch_clock': 'utc', 'objectname': 'dev1'},
            {'epoch_id': 'e2', 'epoch_clock': 'utc', 'objectname': 'dev2'}
        ]

        # Simple bidirectional connection
        G = np.array([[0, 1], [1, 0]], dtype=float)
        mapping = [
            [None, TimeMapping('linear', [1.0, 0.0])],
            [TimeMapping('linear', [1.0, 0.0]), None]
        ]

        graph.manual_add_nodes(nodes, G, mapping)

        ginfo = graph.graphinfo()
        assert len(ginfo['nodes']) == 2
        assert ginfo['G'].shape == (2, 2)
        assert ginfo['G'][0, 1] == 1.0

    def test_manual_add_default_matrices(self):
        """Test manual add with default cost/mapping matrices."""
        graph = SyncGraph()

        nodes = [
            {'epoch_id': 'e1', 'epoch_clock': 'utc', 'objectname': 'dev1'},
            {'epoch_id': 'e2', 'epoch_clock': 'utc', 'objectname': 'dev2'}
        ]

        graph.manual_add_nodes(nodes)  # No G or mapping provided

        ginfo = graph.graphinfo()
        assert len(ginfo['nodes']) == 2
        # Default: Inf everywhere except diagonal
        assert ginfo['G'][0, 0] == 0.0
        assert np.isinf(ginfo['G'][0, 1])


class TestSyncGraphAutoMapping:
    """Test automatic clock type mappings."""

    def test_auto_mapping_same_utc(self):
        """Test automatic mapping for same UTC clocks."""
        graph = SyncGraph()

        # Add two nodes from DIFFERENT devices (add separately)
        nodes1 = [{'epoch_id': 'e1', 'epoch_clock': 'utc', 'objectname': 'dev1'}]
        nodes2 = [{'epoch_id': 'e2', 'epoch_clock': 'utc', 'objectname': 'dev2'}]

        graph.manual_add_nodes(nodes1)
        graph.manual_add_nodes(nodes2)

        ginfo = graph.graphinfo()
        # Should have automatic utc→utc mapping with cost 100
        assert ginfo['G'][0, 1] == 100.0
        assert ginfo['mapping'][0][1] is not None
        # Test identity mapping
        assert abs(ginfo['mapping'][0][1].map(10.0) - 10.0) < 1e-10

    def test_auto_mapping_utc_to_approx_utc(self):
        """Test automatic mapping between utc and approx_utc."""
        graph = SyncGraph()

        # Add two nodes from DIFFERENT devices
        nodes1 = [{'epoch_id': 'e1', 'epoch_clock': 'utc', 'objectname': 'dev1'}]
        nodes2 = [{'epoch_id': 'e2', 'epoch_clock': 'approx_utc', 'objectname': 'dev2'}]

        graph.manual_add_nodes(nodes1)
        graph.manual_add_nodes(nodes2)

        ginfo = graph.graphinfo()
        # Should have automatic utc↔approx_utc mapping
        assert ginfo['G'][0, 1] == 100.0
        assert ginfo['G'][1, 0] == 100.0

    def test_auto_mapping_dev_global_same_device(self):
        """Test automatic mapping for dev_global_time on same device."""
        graph = SyncGraph()

        # Add two epochs from the SAME device with internal connections
        G = np.array([[0, 100], [100, 0]], dtype=float)  # Manually set cost
        mapping = [
            [None, TimeMapping('linear', [1.0, 0.0])],
            [TimeMapping('linear', [1.0, 0.0]), None]
        ]
        nodes = [
            {'epoch_id': 'e1', 'epoch_clock': 'dev_global_time', 'objectname': 'dev1'},
            {'epoch_id': 'e2', 'epoch_clock': 'dev_global_time', 'objectname': 'dev1'}
        ]

        graph.manual_add_nodes(nodes, G, mapping)

        ginfo = graph.graphinfo()
        # Same device, same clock type - internal mapping cost 100
        assert ginfo['G'][0, 1] == 100.0

    def test_auto_mapping_dev_global_different_device(self):
        """Test no automatic mapping for dev_global_time on different devices."""
        graph = SyncGraph()

        nodes = [
            {'epoch_id': 'e1', 'epoch_clock': 'dev_global_time', 'objectname': 'dev1'},
            {'epoch_id': 'e2', 'epoch_clock': 'dev_global_time', 'objectname': 'dev2'}
        ]

        graph.manual_add_nodes(nodes)

        ginfo = graph.graphinfo()
        # Different devices, no automatic mapping
        assert np.isinf(ginfo['G'][0, 1])


class TestSyncGraphWithRules:
    """Test SyncGraph with sync rules applied."""

    def test_apply_filematch_rule(self):
        """Test applying FileMatch rule to graph."""
        graph = SyncGraph()
        rule = FileMatch({'number_fullpath_matches': 1})
        graph.add_rule(rule)

        # Create nodes with common files from DIFFERENT devices
        nodes1 = [{
            'epoch_id': 'e1',
            'epoch_clock': 'dev_global_time',
            'objectname': 'dev1',
            'objectclass': 'ndi.daq.system',
            'underlying_epochs': {'underlying': ['/path/file1.dat', '/path/file2.dat']}
        }]

        nodes2 = [{
            'epoch_id': 'e2',
            'epoch_clock': 'dev_global_time',
            'objectname': 'dev2',
            'objectclass': 'ndi.daq.system',
            'underlying_epochs': {'underlying': ['/path/file1.dat', '/path/file3.dat']}
        }]

        graph.manual_add_nodes(nodes1)
        graph.manual_add_nodes(nodes2)

        ginfo = graph.graphinfo()
        # FileMatch should create mapping (cost 1.0) because files match
        assert ginfo['G'][0, 1] == 1.0
        assert ginfo['mapping'][0][1] is not None
        # Should track that rule 1 created this edge
        assert ginfo['syncRuleG'][0, 1] == 1

    def test_rule_chooses_lowest_cost(self):
        """Test that graph chooses lowest cost mapping from multiple rules."""
        graph = SyncGraph()

        # Rule 1: cost 1.0
        rule1 = FileMatch({'number_fullpath_matches': 1})
        # Rule 2: cost 1.0 (but will be second, so not chosen if same cost)
        rule2 = FileMatch({'number_fullpath_matches': 2})

        graph.add_rule([rule1, rule2])

        # Add nodes from DIFFERENT devices
        nodes1 = [{
            'epoch_id': 'e1',
            'epoch_clock': 'dev_global_time',
            'objectname': 'dev1',
            'objectclass': 'ndi.daq.system',
            'underlying_epochs': {'underlying': ['/path/file1.dat', '/path/file2.dat']}
        }]

        nodes2 = [{
            'epoch_id': 'e2',
            'epoch_clock': 'dev_global_time',
            'objectname': 'dev2',
            'objectclass': 'ndi.daq.system',
            'underlying_epochs': {'underlying': ['/path/file1.dat', '/path/file2.dat']}
        }]

        graph.manual_add_nodes(nodes1)
        graph.manual_add_nodes(nodes2)

        ginfo = graph.graphinfo()
        # Both rules apply (both have matching files), both cost 1.0
        # First rule should be chosen
        assert ginfo['syncRuleG'][0, 1] == 1


class TestSyncGraphPathfinding:
    """Test shortest path finding and time conversion."""

    def test_direct_path_time_conversion(self):
        """Test time conversion with direct path."""
        graph = SyncGraph()

        nodes = [
            {'epoch_id': 'e1', 'epoch_clock': 'utc', 'objectname': 'dev1'},
            {'epoch_id': 'e2', 'epoch_clock': 'utc', 'objectname': 'dev2'}
        ]

        # Direct path with scale=2, shift=5: t_out = 2*t_in + 5
        G = np.array([[0, 1], [np.inf, 0]], dtype=float)
        mapping = [
            [None, TimeMapping('linear', [2.0, 5.0])],
            [None, None]
        ]

        graph.manual_add_nodes(nodes, G, mapping)

        # Convert time from node 0 to node 1
        t_out, msg = graph.time_convert(0, 1, 10.0)

        assert msg == ""
        # t_out = 2.0 * 10.0 + 5.0 = 25.0
        assert abs(t_out - 25.0) < 1e-10

    def test_multi_hop_time_conversion(self):
        """Test time conversion through multiple hops."""
        graph = SyncGraph()

        nodes = [
            {'epoch_id': 'e1', 'epoch_clock': 'utc', 'objectname': 'dev1'},
            {'epoch_id': 'e2', 'epoch_clock': 'utc', 'objectname': 'dev2'},
            {'epoch_id': 'e3', 'epoch_clock': 'utc', 'objectname': 'dev3'}
        ]

        # Path: 0 → 1 → 2
        # 0 → 1: t = 2*t + 0
        # 1 → 2: t = 1*t + 10
        # Combined: t = 2*t + 10
        G = np.array([
            [0, 1, np.inf],
            [np.inf, 0, 1],
            [np.inf, np.inf, 0]
        ], dtype=float)

        mapping = [
            [None, TimeMapping('linear', [2.0, 0.0]), None],
            [None, None, TimeMapping('linear', [1.0, 10.0])],
            [None, None, None]
        ]

        graph.manual_add_nodes(nodes, G, mapping)

        # Convert time from node 0 to node 2
        t_out, msg = graph.time_convert(0, 2, 5.0)

        assert msg == ""
        # Step 1: 5.0 → 2.0 * 5.0 + 0.0 = 10.0
        # Step 2: 10.0 → 1.0 * 10.0 + 10.0 = 20.0
        assert abs(t_out - 20.0) < 1e-10

    def test_shortest_path_selection(self):
        """Test that shortest path is chosen when multiple paths exist."""
        graph = SyncGraph()

        nodes = [
            {'epoch_id': 'e1', 'epoch_clock': 'utc', 'objectname': 'dev1'},
            {'epoch_id': 'e2', 'epoch_clock': 'utc', 'objectname': 'dev2'},
            {'epoch_id': 'e3', 'epoch_clock': 'utc', 'objectname': 'dev3'}
        ]

        # Two paths: 0 → 1 → 2 (cost 2+1=3) and 0 → 2 (cost 10)
        # Should choose direct path despite higher cost
        G = np.array([
            [0, 2, 10],
            [np.inf, 0, 1],
            [np.inf, np.inf, 0]
        ], dtype=float)

        mapping = [
            [None, TimeMapping('linear', [1.0, 0.0]), TimeMapping('linear', [3.0, 0.0])],
            [None, None, TimeMapping('linear', [1.0, 0.0])],
            [None, None, None]
        ]

        graph.manual_add_nodes(nodes, G, mapping)

        # Convert time - should use path 0 → 1 → 2 (cost 3)
        t_out, msg = graph.time_convert(0, 2, 10.0)

        assert msg == ""
        # Path 0 → 1 → 2: identity mappings = 10.0
        assert abs(t_out - 10.0) < 1e-10

    def test_no_path_error(self):
        """Test error when no path exists."""
        graph = SyncGraph()

        nodes = [
            {'epoch_id': 'e1', 'epoch_clock': 'utc', 'objectname': 'dev1'},
            {'epoch_id': 'e2', 'epoch_clock': 'utc', 'objectname': 'dev2'}
        ]

        # No path from 0 to 1
        G = np.array([[0, np.inf], [np.inf, 0]], dtype=float)

        graph.manual_add_nodes(nodes, G, None)

        t_out, msg = graph.time_convert(0, 1, 10.0)

        assert t_out is None
        assert "No path" in msg

    def test_same_node_conversion(self):
        """Test conversion from node to itself."""
        graph = SyncGraph()

        nodes = [{'epoch_id': 'e1', 'epoch_clock': 'utc', 'objectname': 'dev1'}]

        graph.manual_add_nodes(nodes)

        t_out, msg = graph.time_convert(0, 0, 10.0)

        assert msg == ""
        assert t_out == 10.0

    def test_invalid_node_index(self):
        """Test error with invalid node indices."""
        graph = SyncGraph()

        nodes = [{'epoch_id': 'e1', 'epoch_clock': 'utc', 'objectname': 'dev1'}]
        graph.manual_add_nodes(nodes)

        # Invalid source
        t_out, msg = graph.time_convert(5, 0, 10.0)
        assert t_out is None
        assert "Invalid source" in msg

        # Invalid destination
        t_out, msg = graph.time_convert(0, 5, 10.0)
        assert t_out is None
        assert "Invalid destination" in msg


class TestSyncGraphFindNode:
    """Test node finding functionality."""

    def test_find_by_objectname(self):
        """Test finding nodes by object name."""
        graph = SyncGraph()

        nodes = [
            {'epoch_id': 'e1', 'epoch_clock': 'utc', 'objectname': 'dev1'},
            {'epoch_id': 'e2', 'epoch_clock': 'utc', 'objectname': 'dev2'},
            {'epoch_id': 'e3', 'epoch_clock': 'utc', 'objectname': 'dev1'}
        ]

        graph.manual_add_nodes(nodes)

        indices = graph.find_node_index({'objectname': 'dev1'})

        assert len(indices) == 2
        assert 0 in indices
        assert 2 in indices

    def test_find_by_clock_type(self):
        """Test finding nodes by clock type."""
        graph = SyncGraph()

        nodes = [
            {'epoch_id': 'e1', 'epoch_clock': 'utc', 'objectname': 'dev1'},
            {'epoch_id': 'e2', 'epoch_clock': 'dev_global_time', 'objectname': 'dev1'},
            {'epoch_id': 'e3', 'epoch_clock': 'utc', 'objectname': 'dev2'}
        ]

        graph.manual_add_nodes(nodes)

        indices = graph.find_node_index({'epoch_clock': 'utc'})

        assert len(indices) == 2
        assert 0 in indices
        assert 2 in indices

    def test_find_by_multiple_properties(self):
        """Test finding nodes by multiple properties."""
        graph = SyncGraph()

        nodes = [
            {'epoch_id': 'e1', 'epoch_clock': 'utc', 'objectname': 'dev1'},
            {'epoch_id': 'e2', 'epoch_clock': 'utc', 'objectname': 'dev2'},
            {'epoch_id': 'e3', 'epoch_clock': 'dev_global_time', 'objectname': 'dev1'}
        ]

        graph.manual_add_nodes(nodes)

        indices = graph.find_node_index({
            'objectname': 'dev1',
            'epoch_clock': 'utc'
        })

        assert len(indices) == 1
        assert indices[0] == 0

    def test_find_no_matches(self):
        """Test finding with no matches."""
        graph = SyncGraph()

        nodes = [
            {'epoch_id': 'e1', 'epoch_clock': 'utc', 'objectname': 'dev1'}
        ]

        graph.manual_add_nodes(nodes)

        indices = graph.find_node_index({'objectname': 'nonexistent'})

        assert len(indices) == 0


class TestSyncGraphCaching:
    """Test graph info caching."""

    def test_graphinfo_caching(self):
        """Test that graphinfo is cached."""
        graph = SyncGraph()

        nodes = [{'epoch_id': 'e1', 'epoch_clock': 'utc', 'objectname': 'dev1'}]
        graph.manual_add_nodes(nodes)

        ginfo1 = graph.graphinfo()
        ginfo2 = graph.graphinfo()

        # Should return same cached object
        assert ginfo1 is ginfo2

    def test_cache_invalidation_on_rule_add(self):
        """Test that cache is invalidated when rules change."""
        graph = SyncGraph()

        nodes = [{'epoch_id': 'e1', 'epoch_clock': 'utc', 'objectname': 'dev1'}]
        graph.manual_add_nodes(nodes)

        ginfo1 = graph.graphinfo()

        # Add a rule
        rule = FileMatch({'number_fullpath_matches': 1})
        graph.add_rule(rule)

        ginfo2 = graph.graphinfo()

        # Cache should be invalidated, new graph built
        assert ginfo1 is not ginfo2
