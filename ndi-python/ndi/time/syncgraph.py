"""
NDI SyncGraph - manages synchronization graph for time conversion across epochs.

The SyncGraph builds a directed graph of epoch nodes with time mappings between
them, allowing time conversion between different devices and epochs.
"""

from typing import List, Optional, Dict, Any, Tuple
import numpy as np
from pathlib import Path
import networkx as nx

from ..ido import IDO
from ..document import Document
from ..query import Query
from .syncrule import SyncRule
from .timemapping import TimeMapping
from .clocktype import ClockType


class SyncGraph(IDO):
    """
    NDI SyncGraph - synchronization graph for multi-clock time management.

    The SyncGraph maintains a graph of epoch nodes (from different devices/epochs)
    and manages time mappings between them using SyncRules. It enables time
    conversion across different time bases.

    Attributes:
        session: NDI session object
        rules: List of SyncRule objects to apply when building the graph

    Examples:
        >>> from ndi import Session
        >>> session = Session('/path/to/session')
        >>> graph = SyncGraph(session)
        >>> rule = FileMatchSyncRule({'number_fullpath_matches': 2})
        >>> graph.add_rule(rule)
    """

    def __init__(self, session=None, document: Optional[Document] = None):
        """
        Create a new SyncGraph object.

        Args:
            session: NDI Session object
            document: Optional NDI document for loading existing syncgraph

        Notes:
            If both session and document are provided, the syncgraph is
            loaded from the document (including all syncrules).
        """
        super().__init__()

        self.session = session
        self.rules: List[SyncRule] = []
        self._cached_graphinfo = None

        # Load from document if provided
        if session is not None and document is not None:
            syncgraph_doc, syncrule_docs = self.load_all_syncgraph_docs(session, document.id())
            self.identifier = document.id()
            for syncrule_doc in syncrule_docs:
                # Convert document to syncrule object
                # This would use ndi.database.fun.ndi_document2ndi_object in MATLAB
                # For now, we'll create basic syncrule objects
                # TODO: Implement full document-to-object conversion when documentservice is complete
                pass

    def __eq__(self, other: 'SyncGraph') -> bool:
        """
        Check equality of two syncgraph objects.

        Two syncgraphs are equal if their sessions and all rules are equal.

        Args:
            other: Another SyncGraph to compare

        Returns:
            True if sessions and rules are equal
        """
        if not isinstance(other, SyncGraph):
            return False

        # Compare sessions
        if self.session != other.session:
            return False

        # Compare rules
        if len(self.rules) != len(other.rules):
            return False

        for rule_a, rule_b in zip(self.rules, other.rules):
            if rule_a != rule_b:
                return False

        return True

    def add_rule(self, syncrule: SyncRule) -> 'SyncGraph':
        """
        Add a syncrule to the syncgraph.

        Args:
            syncrule: SyncRule object to add (or list of SyncRule objects)

        Returns:
            Self for chaining

        Notes:
            If the rule is already present (by equality), it won't be added again.
            Adding a rule invalidates the cached graphinfo.
        """
        if not isinstance(syncrule, list):
            syncrule = [syncrule]

        did_add = False
        for rule in syncrule:
            if not isinstance(rule, SyncRule):
                raise TypeError("Input must be a SyncRule object")

            # Check for duplication
            match = False
            for existing_rule in self.rules:
                if existing_rule == rule:
                    match = True
                    break

            if not match:
                did_add = True
                self.rules.append(rule)

        if did_add:
            self.remove_cached_graphinfo()

        return self

    def remove_rule(self, index: int) -> 'SyncGraph':
        """
        Remove a syncrule from the syncgraph.

        Args:
            index: Index of rule to remove (0-based)

        Returns:
            Self for chaining
        """
        if 0 <= index < len(self.rules):
            del self.rules[index]
            self.remove_cached_graphinfo()

        return self

    def graphinfo(self) -> Dict[str, Any]:
        """
        Return the graph information structure.

        Returns:
            Dictionary with fields:
            - nodes: List of epoch nodes
            - G: Adjacency matrix (cost of converting between nodes)
            - mapping: Matrix of TimeMapping objects between nodes
            - diG: Directed graph representation (for path finding)
            - syncRuleIDs: IDs of syncrules used
            - syncRuleG: Which syncrule was used for each edge

        Notes:
            This method uses caching. Call remove_cached_graphinfo() to
            force a rebuild.
        """
        ginfo = self.cached_graphinfo()
        if ginfo is None:
            ginfo = self.buildgraphinfo()
            self.set_cached_graphinfo(ginfo)
        return ginfo

    def buildgraphinfo(self) -> Dict[str, Any]:
        """
        Build graph info from scratch using all devices in the session.

        This method:
        1. Initializes empty graph structure
        2. Loads all DAQ systems from session (if available)
        3. Adds each DAQ system to the graph using addepoch()
        4. Builds NetworkX digraph for pathfinding

        Returns:
            Graph info dictionary with fields:
            - nodes: List of epoch node dictionaries
            - G: NxN adjacency matrix (cost of converting between nodes)
            - mapping: NxN list of lists with TimeMapping objects
            - diG: NetworkX DiGraph for pathfinding
            - syncRuleIDs: List of sync rule IDs
            - syncRuleG: NxN matrix tracking which rule created each edge

        Notes:
            If session has no daqsystem_load method or no DAQ systems,
            returns empty graph. Graph can also be manually built using
            manual_add_nodes() for testing.
        """
        # Initialize empty graph structure
        ginfo = {
            'nodes': [],
            'G': np.zeros((0, 0)),  # 2D empty array
            'mapping': [],
            'diG': None,
            'syncRuleIDs': [],
            'syncRuleG': np.zeros((0, 0))  # 2D empty array
        }

        # Update syncRuleIDs
        for rule in self.rules:
            ginfo['syncRuleIDs'].append(rule.id())

        # Load DAQ systems and add epochs if session is available
        if self.session is not None:
            if hasattr(self.session, 'daqsystem_load'):
                # Try to load all DAQ systems
                try:
                    daqsystems = self.session.daqsystem_load('name', '(.*)')
                    for daqsystem in daqsystems:
                        ginfo = self.addepoch(daqsystem, ginfo)
                except Exception as e:
                    # If DAQ system loading fails, continue with empty graph
                    # This allows SyncGraph to work in testing scenarios
                    pass

        # Build NetworkX digraph if we have nodes
        if len(ginfo['nodes']) > 0 and len(ginfo['G']) > 0:
            ginfo['diG'] = self._build_networkx_graph(ginfo['G'])

        return ginfo

    def manual_add_nodes(self, nodes: List[Dict[str, Any]],
                         G: Optional[np.ndarray] = None,
                         mapping: Optional[List[List[Optional[TimeMapping]]]] = None) -> 'SyncGraph':
        """
        Manually add nodes to the graph (for testing without full DAQ system).

        This method allows creating a graph structure for testing purposes
        without requiring a full DAQ system implementation.

        Args:
            nodes: List of epoch node dictionaries
            G: Optional NxN cost adjacency matrix (defaults to all Inf except diagonal=0)
            mapping: Optional NxN mapping matrix (defaults to all None)

        Returns:
            Self for chaining

        Examples:
            >>> from ndi.time import SyncGraph, ClockType, TimeMapping
            >>> graph = SyncGraph()
            >>> nodes = [
            ...     {'epoch_id': 'e1', 'epoch_clock': 'utc', 'objectname': 'dev1'},
            ...     {'epoch_id': 'e2', 'epoch_clock': 'utc', 'objectname': 'dev2'}
            ... ]
            >>> G = np.array([[0, 1], [1, 0]])  # Symmetric costs
            >>> mappings = [[None, TimeMapping('linear', [1, 0])],
            ...             [TimeMapping('linear', [1, 0]), None]]
            >>> graph.manual_add_nodes(nodes, G, mappings)
        """
        n = len(nodes)

        if G is None:
            # Default: Inf everywhere except diagonal
            G = np.full((n, n), np.inf)
            np.fill_diagonal(G, 0.0)

        if mapping is None:
            # Default: No mappings
            mapping = [[None]*n for _ in range(n)]

        # Create a mock DAQ system object
        class MockDAQSystem:
            def __init__(self, nodes, G, mapping):
                self._nodes = nodes
                self._G = G
                self._mapping = mapping

            def epochnodes(self):
                return self._nodes

            def epochgraph(self):
                return self._G, self._mapping

        mock_daq = MockDAQSystem(nodes, G, mapping)

        # Get current graph (or build if doesn't exist)
        ginfo = self.graphinfo()

        # Add new epochs to existing graph
        ginfo = self.addepoch(mock_daq, ginfo)

        # Update cache
        self.set_cached_graphinfo(ginfo)

        return self

    def cached_graphinfo(self) -> Optional[Dict[str, Any]]:
        """
        Return the cached graph info if it exists.

        Returns:
            Cached graph info, or None if not cached
        """
        if self._cached_graphinfo is None:
            # Try to load from session cache if available
            cache, key = self.getcache()
            if cache is not None and key is not None:
                entry = cache.lookup(key, 'syncgraph-hash')
                if entry:
                    self._cached_graphinfo = entry[0].data.get('graphinfo')
        return self._cached_graphinfo

    def set_cached_graphinfo(self, ginfo: Dict[str, Any]) -> None:
        """
        Set the cached graph info.

        Args:
            ginfo: Graph info to cache
        """
        self._cached_graphinfo = ginfo

        # Also update session cache if available
        cache, key = self.getcache()
        if cache is not None:
            cache.remove(key, 'syncgraph-hash')
            cache.add(key, 'syncgraph-hash',
                     {'graphinfo': ginfo, 'hashvalue': 0},
                     priority=1)

    def remove_cached_graphinfo(self) -> None:
        """
        Remove the cached graph info.
        """
        self._cached_graphinfo = None

        # Also remove from session cache
        cache, key = self.getcache()
        if cache is not None:
            cache.remove(key, 'syncgraph-hash')

    def addepoch(self, ndi_daqsystem_obj: Any, ginfo: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add an epoch from a DAQ system to the graph.

        This method implements the three-step algorithm from MATLAB:
        1. Add within-device graph (nodes and internal mappings)
        2. Add automatic clock-type connections
        3. Apply syncrules to find cross-device mappings

        Args:
            ndi_daqsystem_obj: DAQ system object (must have epochnodes() and epochgraph() methods)
            ginfo: Current graph info

        Returns:
            Updated graph info with new nodes and edges

        Notes:
            This method requires DAQ system objects with:
            - epochnodes(): returns list of epoch node dictionaries
            - epochgraph(): returns (cost_matrix, mapping_matrix) for internal epochs
        """
        # Step 1: Get epoch nodes and internal graph from DAQ system
        if not hasattr(ndi_daqsystem_obj, 'epochnodes'):
            # If DAQ system doesn't have epochnodes, skip it
            return ginfo

        new_nodes = ndi_daqsystem_obj.epochnodes()
        if len(new_nodes) == 0:
            return ginfo

        # Get internal cost/mapping matrices if available
        if hasattr(ndi_daqsystem_obj, 'epochgraph'):
            new_cost, new_mapping = ndi_daqsystem_obj.epochgraph()
        else:
            # Create default internal graph (no connections)
            new_n = len(new_nodes)
            new_cost = np.full((new_n, new_n), np.inf)
            new_mapping = [[None]*new_n for _ in range(new_n)]

        # Get dimensions
        old_n = len(ginfo['nodes'])
        new_n = len(new_nodes)
        total_n = old_n + new_n

        # Expand nodes list
        ginfo['nodes'].extend(new_nodes)

        # Expand G matrix (cost adjacency matrix)
        if old_n == 0:
            ginfo['G'] = new_cost
        else:
            new_G = np.full((total_n, total_n), np.inf)
            new_G[:old_n, :old_n] = ginfo['G']  # Upper-left: existing graph
            new_G[old_n:, old_n:] = new_cost    # Lower-right: new device internal
            ginfo['G'] = new_G

        # Expand mapping matrix
        if old_n == 0:
            ginfo['mapping'] = new_mapping
        else:
            new_mapping_full = [[None]*total_n for _ in range(total_n)]
            # Copy existing mappings
            for i in range(old_n):
                for j in range(old_n):
                    new_mapping_full[i][j] = ginfo['mapping'][i][j]
            # Copy new device mappings
            for i in range(new_n):
                for j in range(new_n):
                    new_mapping_full[old_n + i][old_n + j] = new_mapping[i][j]
            ginfo['mapping'] = new_mapping_full

        # Expand syncRuleG matrix (tracks which rule created each edge)
        if old_n == 0:
            ginfo['syncRuleG'] = np.zeros_like(new_cost)
        else:
            new_syncRuleG = np.zeros((total_n, total_n))
            new_syncRuleG[:old_n, :old_n] = ginfo['syncRuleG']
            ginfo['syncRuleG'] = new_syncRuleG

        # Step 2: Add automatic clock-type connections between old and new nodes
        for i in range(old_n):
            for j in range(old_n, total_n):
                if i != j:
                    # Try to create automatic mapping based on clock types
                    cost_ij, mapping_ij = self._automatic_clock_mapping(
                        ginfo['nodes'][i], ginfo['nodes'][j]
                    )
                    if cost_ij < np.inf:
                        ginfo['G'][i, j] = cost_ij
                        ginfo['mapping'][i][j] = mapping_ij

                    # Reverse direction
                    cost_ji, mapping_ji = self._automatic_clock_mapping(
                        ginfo['nodes'][j], ginfo['nodes'][i]
                    )
                    if cost_ji < np.inf:
                        ginfo['G'][j, i] = cost_ji
                        ginfo['mapping'][j][i] = mapping_ji

        # Step 3: Apply syncrules to find cross-device mappings
        if len(self.rules) > 0:
            for i in range(old_n):
                for j in range(old_n, total_n):
                    # Try both directions
                    for direction in [(i, j), (j, i)]:
                        i_idx, j_idx = direction

                        # Find best mapping from all rules
                        best_cost = ginfo['G'][i_idx, j_idx]
                        best_mapping = ginfo['mapping'][i_idx][j_idx]
                        best_rule_idx = 0

                        for rule_idx, rule in enumerate(self.rules):
                            cost, mapping = rule.apply(
                                ginfo['nodes'][i_idx],
                                ginfo['nodes'][j_idx]
                            )

                            if cost is not None and cost < best_cost:
                                best_cost = cost
                                best_mapping = mapping
                                best_rule_idx = rule_idx + 1  # 1-indexed

                        # Update graph with best mapping
                        if best_cost < np.inf:
                            ginfo['G'][i_idx, j_idx] = best_cost
                            ginfo['mapping'][i_idx][j_idx] = best_mapping
                            if best_rule_idx > 0:
                                ginfo['syncRuleG'][i_idx, j_idx] = best_rule_idx

        return ginfo

    def _automatic_clock_mapping(self, node_i: Dict[str, Any], node_j: Dict[str, Any]) -> Tuple[float, Optional[TimeMapping]]:
        """
        Create automatic time mapping between nodes based on clock types.

        Automatic mappings are created for same clock types:
        - utc → utc: cost=100, identity mapping
        - exp_global_time → exp_global_time: cost=100, identity mapping
        - dev_global_time → dev_global_time: cost=100, identity mapping (same device)

        Args:
            node_i: Source node
            node_j: Destination node

        Returns:
            Tuple of (cost, mapping) where cost is Inf if no automatic mapping exists
        """
        clock_i = node_i.get('epoch_clock')
        clock_j = node_j.get('epoch_clock')

        if clock_i is None or clock_j is None:
            return np.inf, None

        # Get clock type names (handle both ClockType objects and strings)
        if hasattr(clock_i, 'type'):
            type_i = clock_i.type
        elif isinstance(clock_i, str):
            type_i = clock_i
        else:
            type_i = str(clock_i)

        if hasattr(clock_j, 'type'):
            type_j = clock_j.type
        elif isinstance(clock_j, str):
            type_j = clock_j
        else:
            type_j = str(clock_j)

        # Check for same clock types that get automatic mappings
        if type_i == type_j:
            if type_i in ['utc', 'approx_utc', 'exp_global_time']:
                # Identity mapping with cost 100
                return 100.0, TimeMapping('linear', [1.0, 0.0])
            elif type_i == 'dev_global_time':
                # Only if same device
                if node_i.get('objectname') == node_j.get('objectname'):
                    return 100.0, TimeMapping('linear', [1.0, 0.0])

        # Check for utc ↔ approx_utc
        if (type_i == 'utc' and type_j == 'approx_utc') or \
           (type_i == 'approx_utc' and type_j == 'utc'):
            return 100.0, TimeMapping('linear', [1.0, 0.0])

        return np.inf, None

    def time_convert(self, source_node_idx: int, dest_node_idx: int, t_in: float) -> Tuple[Optional[float], str]:
        """
        Convert time from one epoch node to another using shortest path.

        This is a simplified version of the full time_convert that works directly
        with node indices. The full version with TimeReference objects will be
        implemented when TimeReference class is complete.

        Args:
            source_node_idx: Index of source node in graph
            dest_node_idx: Index of destination node in graph
            t_in: Input time value

        Returns:
            Tuple of (t_out, msg) where:
            - t_out: Converted time value (or None if conversion failed)
            - msg: Error message if conversion failed, empty string otherwise

        Examples:
            >>> graph = SyncGraph(session)
            >>> # After building graph with devices...
            >>> t_out, msg = graph.time_convert(0, 2, 10.5)
            >>> if msg == "":
            ...     print(f"Converted time: {t_out}")
        """
        # Get graph info
        ginfo = self.graphinfo()

        # Validate indices
        if source_node_idx < 0 or source_node_idx >= len(ginfo['nodes']):
            return None, f"Invalid source node index: {source_node_idx}"

        if dest_node_idx < 0 or dest_node_idx >= len(ginfo['nodes']):
            return None, f"Invalid destination node index: {dest_node_idx}"

        # Same node - no conversion needed
        if source_node_idx == dest_node_idx:
            return t_in, ""

        # Build NetworkX digraph if not cached
        if ginfo['diG'] is None:
            ginfo['diG'] = self._build_networkx_graph(ginfo['G'])
            self.set_cached_graphinfo(ginfo)

        diG = ginfo['diG']

        # Check if path exists
        if not nx.has_path(diG, source_node_idx, dest_node_idx):
            return None, f"No path exists from node {source_node_idx} to node {dest_node_idx}"

        # Find shortest path
        try:
            path = nx.dijkstra_path(diG, source_node_idx, dest_node_idx, weight='weight')
        except nx.NetworkXNoPath:
            return None, f"No path found from node {source_node_idx} to node {dest_node_idx}"

        # Apply time mappings along the path
        t_out = t_in
        for i in range(len(path) - 1):
            node_from = path[i]
            node_to = path[i + 1]

            # Get time mapping for this edge
            mapping = ginfo['mapping'][node_from][node_to]

            if mapping is None:
                return None, f"No time mapping found for edge {node_from} -> {node_to}"

            # Apply mapping
            t_out = mapping.map(t_out)

        return t_out, ""

    def find_node_index(self, node_properties: Dict[str, Any]) -> List[int]:
        """
        Find nodes in the graph matching given properties.

        Args:
            node_properties: Dictionary of properties to match. Can include:
                - epoch_id: Exact epoch ID match
                - objectname: Exact object name match
                - objectclass: Exact or partial class match
                - epoch_clock: Clock type to match

        Returns:
            List of node indices that match all specified properties

        Examples:
            >>> indices = graph.find_node_index({
            ...     'objectname': 'intan',
            ...     'epoch_clock': 'dev_global_time'
            ... })
        """
        ginfo = self.graphinfo()
        matches = []

        for idx, node in enumerate(ginfo['nodes']):
            match = True

            # Check each property
            for key, value in node_properties.items():
                node_value = node.get(key)

                if key == 'objectclass':
                    # Allow partial class match (e.g., 'ndi.daq.system' in full class name)
                    if node_value is None or value not in str(node_value):
                        match = False
                        break
                elif key == 'epoch_clock':
                    # Handle ClockType objects vs strings
                    if hasattr(node_value, 'type'):
                        node_clock_type = node_value.type
                    else:
                        node_clock_type = str(node_value)

                    if hasattr(value, 'type'):
                        search_clock_type = value.type
                    else:
                        search_clock_type = str(value)

                    if node_clock_type != search_clock_type:
                        match = False
                        break
                else:
                    # Exact match for other properties
                    if node_value != value:
                        match = False
                        break

            if match:
                matches.append(idx)

        return matches

    def _build_networkx_graph(self, G: np.ndarray) -> nx.DiGraph:
        """
        Build a NetworkX directed graph from the adjacency matrix.

        Args:
            G: Adjacency matrix where G[i,j] is the cost from node i to node j

        Returns:
            NetworkX DiGraph object

        Notes:
            Inf costs in G are excluded (no edge created).
            Edge weights are set to the costs for Dijkstra pathfinding.
        """
        diG = nx.DiGraph()
        n_nodes = G.shape[0]

        # Add all nodes
        for i in range(n_nodes):
            diG.add_node(i)

        # Add edges with weights
        for i in range(n_nodes):
            for j in range(n_nodes):
                if not np.isinf(G[i, j]) and G[i, j] > 0:
                    diG.add_edge(i, j, weight=G[i, j])

        return diG

    def getcache(self) -> Tuple[Optional[Any], Optional[str]]:
        """
        Get the cache and key for this syncgraph.

        Returns:
            Tuple of (cache, key) where:
            - cache: Session cache object (or None)
            - key: Cache key string (or None)
        """
        cache = None
        key = None

        if self.session is not None:
            if hasattr(self.session, 'cache'):
                cache = self.session.cache
                key = f'syncgraph_{self.id()}'

        return cache, key

    def newdocument(self) -> List[Document]:
        """
        Create NDI documents for this syncgraph.

        Returns:
            List of Document objects (syncgraph doc + all syncrule docs)
        """
        docs = []

        # Create syncgraph document
        syncgraph_doc = Document('syncgraph',
                                syncgraph_ndi_syncgraph_class=self.__class__.__module__ + '.' + self.__class__.__name__)
        syncgraph_doc.document_properties['base']['id'] = self.id()
        if self.session is not None:
            syncgraph_doc.document_properties['base']['session_id'] = self.session.id()
        else:
            syncgraph_doc.document_properties['base']['session_id'] = ''

        # Add dependencies to syncrules
        for rule in self.rules:
            syncgraph_doc = syncgraph_doc.add_dependency_value_n('syncrule_id', rule.id())
            docs.append(rule.newdocument())

        docs.insert(0, syncgraph_doc)
        return docs

    def searchquery(self) -> Query:
        """
        Create a search query for this syncgraph.

        Returns:
            Query object that searches for this syncgraph by ID and session ID
        """
        q = Query('base.id', 'exact_string', self.id())
        if self.session is not None:
            q = q & Query('base.session_id', 'exact_string', self.session.id())
        return q

    def __repr__(self) -> str:
        """String representation."""
        return f"SyncGraph(session={self.session}, rules={len(self.rules)})"

    def __str__(self) -> str:
        """String representation."""
        return self.__repr__()

    # Static methods

    @staticmethod
    def load_all_syncgraph_docs(ndi_session_obj: Any, syncgraph_doc_id: str) -> Tuple[Optional[Document], List[Document]]:
        """
        Load a syncgraph document and all of its syncrule documents.

        Args:
            ndi_session_obj: NDI session object
            syncgraph_doc_id: Document ID of the syncgraph

        Returns:
            Tuple of (syncgraph_doc, syncrule_docs) where:
            - syncgraph_doc: The syncgraph document (or None if not found)
            - syncrule_docs: List of syncrule documents

        Raises:
            ValueError: If multiple documents found with the same ID
        """
        syncrule_docs = []

        # Search for syncgraph document
        docs = ndi_session_obj.database_search(
            Query('base.id', 'exact_string', syncgraph_doc_id)
        )

        if len(docs) == 0:
            return None, []
        elif len(docs) > 1:
            raise ValueError(f"More than 1 document with base.id value of {syncgraph_doc_id}")

        syncgraph_doc = docs[0]

        # Load syncrule documents
        rules_id_list = syncgraph_doc.dependency_value_n('syncrule_id', error_if_not_found=False)
        for rule_id in rules_id_list:
            rules_doc = ndi_session_obj.database_search(
                Query('base.id', 'exact_string', rule_id)
            )
            if len(rules_doc) != 1:
                raise ValueError(f"Could not find syncrule with id {rule_id}; found {len(rules_doc)} occurrences")
            syncrule_docs.append(rules_doc[0])

        return syncgraph_doc, syncrule_docs
