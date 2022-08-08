# Index Class

The class `SampleDataIndex` handles the logic for actually performing CRUD operations only for indices. This class uses the [OpenSearch Client](https://opensearch-project.github.io/opensearch-py/api-ref.html) to make API calls for indices.

`SampleDataIndex` takes in three arguments for initialization:
- `index_name` (string): The name of the index in which CRUD operations will be performed on
- `index_body` (dict): The index configurations for [creating an index](https://opensearch.org/docs/latest/opensearch/rest-api/index-apis/create-index/)
- `client` ([OpenSearch Python client](https://opensearch-project.github.io/opensearch-py/api-ref.html)): The OpenSearch Python client object used to execute the CRUD operations

`SampleDataIndex` has four functions, mostly dealing with the CRUD operations; the functions will not take any arguments or return anything, but they will raise `ConnectionErrors` if `client` cannot perform the CRUD operations:
- `create_index()`: This function takes in the initialization arguments and creates the index
- `delete_index()`: This function takes in the initialization arguments and deletes the index
- `ingest_more()`: This function is a small wrapper around the ingestion tool. It takes in the same arguments as `ingest()` (from `sample_data_ingestor/sample_data_ingestor.py`)
    - **Arguments:**
        - `client` (OpenSearch object): The OpenSearch object used to make the API call to OS.
        - `data_template` (string or dict): The template used to generate documents. See the generation tool for reference.
        - `index_name` (string): The name of the target index in which documents will be ingested.
        - `mapping` (boolean): Whether the `data_template` is a JSON [mapping](https://opensearch.org/docs/latest/opensearch/mappings/).
        - `file_provided` (boolean): Whether the `data_template` is a file that contains the template to generate documents.
        - `number` (integer): How many documents to generate (if `minutes` was specified, `number` was automatically calculated as the number of minutes per day divided by `minutes`).
        - `minutes` (integer): The time interval between each successive data point (e.g. if minutes = 2, this tool will generate documents with timestamps that are 2 minutes apart from one another).
        - `chunk` (integer): The maximum amount of documents that can be ingested per `BULK` call.
        - `timestamp` (string): The *field name* which contains a timestamp. For the purposes of this tool, only `unix time` (in milliseconds) is supported.
        - `current_date` (datetime): The date at which documents are generated (e.g. if the date was today, then documents will be generated with timestamp fields containing today's date in `unix time` milliseconds).
        - `max_bulk_size` (integer): The maximum size in bytes of the request body to ingest documents for one `BULK` call (`chunk` also deals with limiting document ingestion)
        - `anomaly_detection_trend` (dict): The dictionary containing config variables to create trends in document data.