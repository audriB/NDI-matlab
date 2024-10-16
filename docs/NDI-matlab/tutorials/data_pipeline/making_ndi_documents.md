# Making your own NDI documents

To make an NDI document, there are two parts. First, there is the **document definition** and second, there is the **document schema** which tells NDI what formats and data entries are acceptable.

## 7.2.2 Designing the database document

Let's look at the design of the database document definition for [ndi.calc.example.simple](https://vh-lab.github.io/NDI-matlab/reference/%2Bndi/%2Bcalc/%2Bexample/simple.m/), which we placed in `ndi_common/database_documents/apps/calculations/simple_calc.json`:

### Code block 7.2.2.1: Database documentation definition for `simple_calc` (Do not type into Matlab command line)

```json
{
        "document_class": {
                "definition":                                           "$NDIDOCUMENTPATH\/apps\/calculations\/simple_calc.json",
                "validation":                                           "$NDISCHEMAPATH\/apps\/calculations\/simple_calc_schema.json",
                "class_name":                                           "ndi_calculation_simple_simple_calc",
                "property_list_name":                                   "simple",
                "class_version":                                        1,
                "superclasses": [
                        { "definition":                                 "$NDIDOCUMENTPATH\/ndi_document.json" },
                        { "definition":                                 "$NDIDOCUMENTPATH\/ndi_document_app.json" }
                ]
        },
        "depends_on": [
                {       "name": "probe_id",
                        "value": 0
                }
        ],
        "simple": {
                "input_parameters": {
                        "answer":                                       5
                },
                "answer":                                               0
        }
}
```

The first block, `document_class`, is necessary for any document defined in NDI. It includes the location of the definition file, the location
of a file for validation (we will cover later), the class name, the `property_list_name` which tells NDI what the structure that has the main
results (later on in the file), the class version (which is 1), and the superclasses of the document. The line that includes the definition for `ndi_document` indicates that simple calc documents have all the fields of an ndi.document, which must be true for any NDI document. In this case, this document also is a subclass of ndi_document_app, which allows information about the application that created the calculation to be recorded.

In the next block, there is a set of "depends_on" fields, which indicate which dependencies are required for this document type. Here, we make the
document that describes each probe as a dependency, so that the "answer" can be attributed to the probe by any program or user that examines the
document.


Finally, we have the data that is associated with our calculation in the structure `simple`. Because it is a document for an NDI calculation, it
must contain a structure "input_parameters" that describe how the calculator should search for its inputs, if there are such parameters (or the
structure can be empty if there are none). Last, we have the entries of the structure that contain the output of our calculation, which in this
case is a simple field "answer".


## Designing an NDI document schema


The schema notes are here: https://github.com/VH-Lab/DID-matlab/blob/main/docs/development/did-schema4.md

Examples are here:

https://github.com/VH-Lab/NDI-matlab/tree/main/ndi_common/schema_documents





