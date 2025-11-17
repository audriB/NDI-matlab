"""
NDI Document Validation Framework.

This module provides validation for NDI documents against their JSON schemas.
Python implementation of ndi.validate using jsonschema library instead of Java.

MATLAB equivalent: ndi.validate
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import warnings

try:
    import jsonschema
    from jsonschema import Draft7Validator, ValidationError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    warnings.warn(
        "jsonschema library not available. Install with: pip install jsonschema"
    )


class Validate:
    """
    Validate NDI documents against their JSON schemas.

    This class validates ndi.Document objects to ensure their properties match
    the expected types according to their schema. It implements JSON Schema
    DRAFT 7 validation.

    MATLAB equivalent: ndi.validate

    Attributes:
        validators (dict): Validator objects for document and superclasses
        reports (dict): Validation error reports
        is_valid (bool): Whether the document is valid
        errormsg (str): Complete error message
        errormsg_this (str): Errors for current class properties
        errormsg_super (str): Errors for superclass properties
        errormsg_depends_on (str): Errors for missing dependencies

    Example:
        >>> from ndi.validate import Validate
        >>> from ndi.document import Document
        >>> from ndi.session import SessionDir
        >>>
        >>> doc = Document('base', {...})
        >>> session = SessionDir('/path/to/session')
        >>> validator = Validate(doc, session)
        >>> if not validator.is_valid:
        ...     print(validator.errormsg)
    """

    def __init__(self, ndi_document_obj=None, ndi_session_obj=None):
        """
        Initialize and validate an NDI document.

        Args:
            ndi_document_obj (ndi.Document): The document to validate
            ndi_session_obj (ndi.Session, optional): Session for dependency checking

        Raises:
            ValueError: If ndi_document_obj is not an ndi.Document
            ValueError: If document has dependencies but no session provided
            ImportError: If jsonschema library is not available
        """
        if not JSONSCHEMA_AVAILABLE:
            raise ImportError(
                "jsonschema library required for validation. "
                "Install with: pip install jsonschema"
            )

        # Initialize properties
        self.validators = {}
        self.reports = {}
        self.errormsg_this = "no error found\n"
        self.errormsg_super = "no error found\n"
        self.errormsg_depends_on = "no error found\n"
        self.errormsg = ''
        self.is_valid = True

        # If no arguments, just initialize empty validator
        if ndi_document_obj is None:
            return

        # Import here to avoid circular dependency
        from ndi.document import Document
        from ndi.session import Session

        # Check if valid document
        if not isinstance(ndi_document_obj, Document):
            raise ValueError(
                'You must pass in an instance of ndi.Document as your first argument'
            )

        # Check for dependencies
        has_dependencies = (
            'depends_on' in ndi_document_obj.document_properties
        )

        if has_dependencies:
            if ndi_session_obj is None or not isinstance(ndi_session_obj, Session):
                raise ValueError(
                    'You must pass in an instance of ndi.Session as your second '
                    'argument to check for dependency'
                )

        # Extract schema
        try:
            schema = self._extract_schema(ndi_document_obj)
        except Exception as e:
            raise ValueError(f"Failed to extract schema: {e}")

        # Get document properties
        doc_class = ndi_document_obj.document_properties['document_class']
        property_list_name = doc_class['property_list_name']
        property_list = ndi_document_obj.document_properties[property_list_name].copy()

        # Add depends_on if present
        if has_dependencies:
            property_list['depends_on'] = (
                ndi_document_obj.document_properties['depends_on']
            )

        # Validate main properties
        self._validate_properties(
            property_list,
            schema,
            property_list_name
        )

        # Validate superclasses
        if 'superclasses' in doc_class and doc_class['superclasses']:
            self._validate_superclasses(
                ndi_document_obj,
                doc_class['superclasses'],
                has_dependencies
            )

        # Check dependencies
        if has_dependencies:
            self._check_dependencies(
                ndi_document_obj.document_properties['depends_on'],
                ndi_session_obj
            )

        # Prepare final report
        if not self.is_valid:
            self.errormsg = (
                "Validation has failed. Here is a detailed report:\n"
                "=" * 78 + "\n"
                "Errors for this instance of ndi.document class:\n"
                "-" * 78 + "\n"
                f"{self.errormsg_this}\n"
                "-" * 78 + "\n"
                "Errors for super class(es):\n"
                "-" * 78 + "\n"
                f"{self.errormsg_super}\n"
                "-" * 78 + "\n"
                "Errors relating to dependencies:\n"
                "-" * 78 + "\n"
                f"{self.errormsg_depends_on}\n"
                "-" * 78 + "\n"
                "To get detailed report as dict, access the 'reports' attribute"
            )
        else:
            self.errormsg = 'This ndi_document contains no type error'

    def _validate_properties(
        self,
        properties: Dict[str, Any],
        schema: Dict[str, Any],
        context_name: str
    ) -> None:
        """
        Validate properties against a schema.

        Args:
            properties: Properties to validate
            schema: JSON schema to validate against
            context_name: Name for error reporting
        """
        try:
            validator = Draft7Validator(schema)
            errors = list(validator.iter_errors(properties))

            if errors:
                self.is_valid = False
                self.reports['this'] = errors
                error_msgs = []
                for error in errors:
                    path = '.'.join(str(p) for p in error.path) if error.path else 'root'
                    error_msgs.append(f"  {path}: {error.message}")

                self.errormsg_this = (
                    f"{context_name}:\n" + "\n".join(error_msgs) + "\n"
                )
        except Exception as e:
            self.is_valid = False
            self.errormsg_this = f"Validation error: {str(e)}\n"

    def _validate_superclasses(
        self,
        ndi_document_obj,
        superclasses: List[Dict],
        has_dependencies: bool
    ) -> None:
        """
        Validate superclass properties.

        Args:
            ndi_document_obj: The document being validated
            superclasses: List of superclass definitions
            has_dependencies: Whether document has dependencies
        """
        self.validators['super'] = []
        self.reports['super'] = []

        for superclass_def in superclasses:
            definition = superclass_def['definition']

            try:
                schema = self._extract_schema(definition)
                superclass_name = self._extract_name_from_definition(definition)

                if superclass_name in ndi_document_obj.document_properties:
                    properties = dict(
                        ndi_document_obj.document_properties[superclass_name]
                    )

                    if has_dependencies:
                        properties['depends_on'] = (
                            ndi_document_obj.document_properties['depends_on']
                        )

                    validator = Draft7Validator(schema)
                    errors = list(validator.iter_errors(properties))

                    if errors:
                        self.is_valid = False
                        self.reports['super'].append({
                            'name': superclass_name,
                            'errors': errors
                        })

                        error_msgs = []
                        for error in errors:
                            path = '.'.join(str(p) for p in error.path) if error.path else 'root'
                            error_msgs.append(f"  {path}: {error.message}")

                        self.errormsg_super = (
                            f"{superclass_name}:\n" + "\n".join(error_msgs) + "\n"
                        )
            except Exception as e:
                self.is_valid = False
                self.errormsg_super += f"Error validating {definition}: {str(e)}\n"

    def _check_dependencies(
        self,
        depends_on: List[Dict],
        ndi_session_obj
    ) -> None:
        """
        Check that all dependencies exist in the database.

        Args:
            depends_on: List of dependency specifications
            ndi_session_obj: Session to search for dependencies
        """
        from ndi.query import Query

        self.reports['dependencies'] = {}
        missing_deps = []

        for dep in depends_on:
            dep_name = dep['name']
            dep_value = dep['value']

            # Search for dependency in database
            query = Query('base.id', 'exact_string', dep_value)
            results = ndi_session_obj.database_search(query)

            if len(results) < 1:
                self.reports['dependencies'][dep_name] = 'fail'
                missing_deps.append(dep_name)
                self.is_valid = False
            else:
                self.reports['dependencies'][dep_name] = 'success'

        if missing_deps:
            self.errormsg_depends_on = (
                "Cannot find the following dependencies in database:\n" +
                "\n".join(f"  - {dep}" for dep in missing_deps) + "\n"
            )

    def throw_error(self) -> None:
        """
        Raise an error if validation failed.

        Raises:
            ValueError: If document is not valid
        """
        if not self.is_valid:
            raise ValueError(self.errormsg)

    @staticmethod
    def _extract_schema(ndi_document_or_path: Union[object, str, Path]) -> Dict:
        """
        Extract schema from document or path.

        Args:
            ndi_document_or_path: Document object or path to schema

        Returns:
            dict: Parsed JSON schema

        Raises:
            FileNotFoundError: If schema file not found
            ValueError: If schema cannot be parsed
        """
        from ndi.document import Document

        schema_path = None

        if isinstance(ndi_document_or_path, Document):
            # Extract from document
            validation_path = (
                ndi_document_or_path.document_properties
                ['document_class']['validation']
            )
            # Replace placeholders - in Python we need to find the schema path
            # For now, assume schemas are in common/database_documents
            schema_path = validation_path.replace(
                '$NDISCHEMAPATH',
                str(Path(__file__).parent.parent / 'common' / 'database_documents')
            )
        elif isinstance(ndi_document_or_path, (str, Path)):
            # It's a path
            schema_path = str(ndi_document_or_path)
            if schema_path.endswith('.json') and not schema_path.endswith('_schema.json'):
                schema_path = schema_path.replace('.json', '_schema.json')

            # Replace placeholders
            schema_path = schema_path.replace(
                '$NDIDOCUMENTPATH',
                str(Path(__file__).parent.parent / 'common' / 'database_documents')
            ).replace(
                '$NDISCHEMAPATH',
                str(Path(__file__).parent.parent / 'common' / 'database_documents')
            )

        if schema_path is None:
            raise ValueError("Could not determine schema path")

        # Read and parse schema
        try:
            with open(schema_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Schema file not found: {schema_path}\n"
                "Verify schema file exists in the database_documents folder."
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in schema file: {e}")

    @staticmethod
    def _extract_name_from_definition(definition: str) -> str:
        """
        Extract name from definition path.

        Args:
            definition: Path to definition file

        Returns:
            str: Name without extension
        """
        path = Path(definition)
        return path.stem  # Returns filename without extension


def validate_document(
    ndi_document_obj,
    ndi_session_obj=None,
    raise_on_error: bool = False
) -> Validate:
    """
    Convenience function to validate an NDI document.

    Args:
        ndi_document_obj (ndi.Document): Document to validate
        ndi_session_obj (ndi.Session, optional): Session for dependency checking
        raise_on_error (bool): If True, raise error on validation failure

    Returns:
        Validate: Validation object with results

    Raises:
        ValueError: If raise_on_error=True and validation fails

    Example:
        >>> from ndi.validate import validate_document
        >>> validator = validate_document(doc, session)
        >>> if validator.is_valid:
        ...     print("Document is valid!")
    """
    validator = Validate(ndi_document_obj, ndi_session_obj)

    if raise_on_error:
        validator.throw_error()

    return validator
