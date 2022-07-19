from utils.sample_data_ingestor.sample_data_ingestor import ingest

"""
Index class: this class can create, delete, and ingest more data into a new or existing index
Arguments:
    - index_body: The body containing the configurations of the index (used for index creation)
    - index_name: The index name to create/ingest/delete
    - client: an OpenSearch Python client object
"""
class SampleDataIndex:
    def __init__(self, index_name, client, index_body):
        self.index_name = index_name
        self.index_body = index_body
        self.client = client

    # Checks if an index exists; if not, the index is created using the OpenSearch Python client (client is defined in the startup/refresh jobs)    
    def create_index(self):
        if not self.client.indices.exists(index = self.index_name):
            self.client.indices.create(index = self.index_name, body=self.index_body)
            print("The index %s was successfully created" % (self.index_name))
        else:
            print("The index %s exists already" % (self.index_name))

    # Checks if an index exists; if it does, the index is deleted using the OpenSearch Python client (client is defined in the startup/refresh jobs)          
    def delete_index(self):
        if self.client.indices.exists(index = self.index_name):
            self.client.indices.delete(index = self.index_name)
            print("The index %s was successfully deleted" % (self.index_name))
        else:
            print("The index %s does not exist" % (self.index_name))

    # Calls the ingest() function to ingest more data using provided key word arguments
    def ingest_more(self, **kwargs):
        ingest(client = self.client, **kwargs)