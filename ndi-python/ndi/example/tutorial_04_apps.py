"""
Tutorial 04: Creating and Using NDI Apps

This tutorial demonstrates how to create applications that operate on
NDI sessions using the App and AppDoc framework.

MATLAB Equivalent: Various app examples in NDI-MATLAB
"""

import tempfile
import os
import numpy as np
from pathlib import Path


def example_01_basic_app():
    """
    Example 1: Create a simple app and document.

    Demonstrates:
    - Creating an App instance
    - Generating documents with app metadata
    - Version tracking
    """
    from ndi import App
    from ndi.session import SessionDir

    print("=== Example 1: Basic App ===\n")

    # Create a temporary session
    with tempfile.TemporaryDirectory() as tmpdir:
        session = SessionDir(tmpdir)

        # Create an app
        app = App(session, 'example_analyzer')

        print(f"App name: {app.name}")
        print(f"Variable name: {app.varappname()}")

        # Get version information
        version, url = app.version_url()
        print(f"App version: {version[:40]}...")  # Show first 40 chars
        print(f"Repository: {url}")

        # Create a document with app metadata
        doc = app.newdocument('analysis_results',
                             result='success',
                             accuracy=0.95,
                             num_samples=1000)

        # Add to session
        session.database.add(doc)

        # Search for app's documents
        query = app.searchquery()
        app_docs = session.database.search(query)

        print(f"\nFound {len(app_docs)} document(s) from this app")
        print(f"Document type: {app_docs[0].document_properties.document_class.definition}")

        print("\nExample 1 complete!\n")


def example_02_app_with_parameters():
    """
    Example 2: App with parameter documents using AppDoc mixin.

    Demonstrates:
    - Using AppDoc mixin for parameter management
    - Creating parameter and result documents
    - Linking results to parameters
    """
    from ndi import App
    from ndi.appdoc import AppDoc
    from ndi.session import SessionDir

    print("=== Example 2: App with Parameters ===\n")

    # Define a custom app with parameters
    class ThresholdAnalyzer(App, AppDoc):
        """Analyzer with threshold parameters."""

        def __init__(self, session):
            App.__init__(self, session, 'threshold_analyzer')
            AppDoc.__init__(
                self,
                doc_types=['parameters'],
                doc_document_types=['threshold_parameters'],
                doc_session=session
            )

        def run_analysis(self, data, threshold=0.5):
            """Run analysis with given threshold."""
            # Create parameter document
            params = {
                'threshold': threshold,
                'data_shape': data.shape,
                'algorithm': 'simple_threshold'
            }

            param_doc = self.newdocument('threshold_parameters', **params)
            self.session.database.add(param_doc)

            # Run analysis
            result = np.sum(data > threshold)

            # Create result document linked to parameters
            result_doc = self.newdocument('threshold_results',
                                         parameters_id=param_doc.id(),
                                         num_above_threshold=int(result),
                                         total_samples=int(data.size))

            self.session.database.add(result_doc)

            return result_doc

    # Use the app
    with tempfile.TemporaryDirectory() as tmpdir:
        session = SessionDir(tmpdir)
        analyzer = ThresholdAnalyzer(session)

        # Generate some test data
        test_data = np.random.rand(100, 100)

        # Run analysis
        result = analyzer.run_analysis(test_data, threshold=0.7)

        print(f"Analysis complete!")
        print(f"Samples above threshold: {result.document_properties.num_above_threshold}")
        print(f"Total samples: {result.document_properties.total_samples}")

        # Find all documents from this app
        app_docs = session.database.search(analyzer.searchquery())
        print(f"\nApp created {len(app_docs)} document(s)")

        print("\nExample 2 complete!\n")


def example_03_spike_extractor_app():
    """
    Example 3: Complete spike extraction app.

    Demonstrates:
    - Real-world neuroscience analysis app
    - Working with probes and epochs
    - Binary data handling
    - Full provenance tracking
    """
    from ndi import App, SessionDir
    from ndi.probe import ElectrodeProbe

    print("=== Example 3: Spike Extraction App ===\n")

    class SimpleSpikeExtractor(App):
        """Extract spikes from neural data."""

        def __init__(self, session):
            super().__init__(session, 'simple_spike_extractor')

        def extract_spikes(self, data, sampling_rate=30000, threshold_std=4.0):
            """
            Extract spikes from continuous data.

            Args:
                data: 1D array of neural data
                sampling_rate: Sampling rate in Hz
                threshold_std: Threshold in standard deviations

            Returns:
                Document with spike information
            """
            # Calculate threshold
            threshold = threshold_std * np.std(data)

            # Find threshold crossings
            crossings = np.where(np.abs(data) > threshold)[0]

            # Extract spike times
            spike_times = crossings / sampling_rate

            # Create parameter document
            param_doc = self.newdocument('spike_extraction_parameters',
                                        threshold_std=threshold_std,
                                        threshold_value=float(threshold),
                                        sampling_rate=sampling_rate)

            self.session.database.add(param_doc)

            # Create results document
            result_doc = self.newdocument('spike_extraction_results',
                                         parameters_id=param_doc.id(),
                                         num_spikes=len(spike_times),
                                         mean_rate=len(spike_times) / (len(data) / sampling_rate),
                                         spike_times=spike_times.tolist()[:100])  # First 100

            self.session.database.add(result_doc)

            return result_doc

    # Use the app
    with tempfile.TemporaryDirectory() as tmpdir:
        session = SessionDir(tmpdir)

        # Create a probe
        probe = ElectrodeProbe(session, 'electrode1', reference=1,
                              subject_id='mouse01', impedance=1e6)
        session.add_probe(probe)

        # Create app
        extractor = SimpleSpikeExtractor(session)

        # Simulate neural data with spikes
        np.random.seed(42)
        duration = 10.0  # seconds
        sampling_rate = 30000
        num_samples = int(duration * sampling_rate)

        # Background noise + some spikes
        data = 0.1 * np.random.randn(num_samples)

        # Add 50 artificial spikes
        spike_indices = np.random.randint(1000, num_samples-1000, 50)
        for idx in spike_indices:
            data[idx] += 1.0  # Add spike

        # Extract spikes
        result = extractor.extract_spikes(data, sampling_rate=sampling_rate)

        print(f"Extracted {result.document_properties.num_spikes} spikes")
        print(f"Mean firing rate: {result.document_properties.mean_rate:.2f} Hz")

        print("\nExample 3 complete!\n")


def example_04_app_with_database_utilities():
    """
    Example 4: App using enhanced database utilities.

    Demonstrates:
    - QueryBuilder for complex searches
    - MetadataExtractor for session analysis
    - Integration of apps with database utilities
    """
    from ndi import App, SessionDir
    from ndi.db.fun import QueryBuilder, MetadataExtractor

    print("=== Example 4: App with Database Utilities ===\n")

    class SmartAnalyzer(App):
        """App that uses database utilities."""

        def __init__(self, session):
            super().__init__(session, 'smart_analyzer')
            self.metadata_extractor = MetadataExtractor()

        def analyze_session(self):
            """Analyze session metadata."""
            metadata = self.metadata_extractor.extract_session_metadata(self.session)

            print("Session Analysis:")
            print(f"  Total documents: {metadata.get('total_documents', 0)}")
            print(f"  Document types: {metadata.get('document_types', {})}")
            print(f"  Number of probes: {metadata.get('num_probes', 0)}")

            # Create analysis document
            doc = self.newdocument('session_analysis',
                                  total_documents=metadata.get('total_documents', 0),
                                  document_types=metadata.get('document_types', {}))

            self.session.database.add(doc)

            return doc

        def find_recent_analyses(self, days=7):
            """Find recent analysis results using QueryBuilder."""
            qb = QueryBuilder()
            query = qb.where('app.name', '==', self.name) \
                      .order_by('base.created', 'desc') \
                      .limit(10) \
                      .build()

            return self.session.database.search(query)

    # Use the app
    with tempfile.TemporaryDirectory() as tmpdir:
        session = SessionDir(tmpdir)

        # Add some documents
        from ndi.document import Document
        for i in range(5):
            doc = Document('test_doc', value=i)
            session.database.add(doc)

        # Create and use analyzer
        analyzer = SmartAnalyzer(session)

        # Analyze session
        analysis = analyzer.analyze_session()

        # Find recent analyses
        recent = analyzer.find_recent_analyses()
        print(f"\nFound {len(recent)} recent analysis document(s)")

        print("\nExample 4 complete!\n")


def run_all_examples():
    """Run all app tutorial examples."""
    print("=" * 60)
    print("NDI App System Tutorial")
    print("=" * 60)
    print()

    example_01_basic_app()
    example_02_app_with_parameters()
    example_03_spike_extractor_app()
    example_04_app_with_database_utilities()

    print("=" * 60)
    print("All examples complete!")
    print("=" * 60)


if __name__ == '__main__':
    run_all_examples()
