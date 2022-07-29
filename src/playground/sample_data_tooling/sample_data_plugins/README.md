# Plugin Class

This class handles the logic for performing CRUD operations for various plugins. `Plugins` is actually a generic class, which provides support for more plugin teams to build off of. In its current form, this tooling only implements the `AnomalyDetector` plugin.

## `Plugin` (generic class)

This generic class provides the groundwork for plugin teams to define their own `Plugin` objects to call. All `Plugin` classes/subclasses should follow the below arguments.

`Plugin` takes four arguments for initialization:
- **Arguments:**
    - `index_name` (string): The name of the source index
    - `payload` (dict, JSON string, or filename string): The configurations necessary for the API payload to create the plugin
    - `base_url`: The IP address/url where the OpenSearch backend lies (in the form `scheme://host`)
    - `auth` (Authentication object): The Authentication object needed to get headers; see `sample_data_authentication/README.md` for more information

`Plugin` also has two functions:
- `unzip()`: If `payload` is a zipped config filename, unzip it and return unzipped filename
    - **Arguments:**
            - This function takes no arguments
    - **Returns:**
        - This function returns a string filename of the unzipped file
- `convert_payload()`: This converts the `payload` to a dict
    - **Arguments:**
            - `payload`: A payload used for request calls; can be a dict, JSON string, or filename
            - `plugin_config_directory_name` (string):
    - **Returns:**
        - This function returns a header (typically as a dict) The directory within "config/" where the payload (if it was a filename) can be accessed

## `AnomalyDetection` (implemented from `Plugin`)

This class is the only implementation of `Plugin`. In addition to the arguments and functions from `Plugin`, this class handles the logic for making API requests to OpenSearch.

`AnomalyDetection`, in addition to the `Plugin` arguments, takes in two arguments for initialization:
- **Arguments:**
    - `target_index` (string): The name of the index to store the results of `AnomalyDetection`.
    - `days_ago` (int): This is for the historical analysis job. This variable specifies how many days ago the historical analysis job should look at data.

`AnomalyDetection`, in addition to the `Plugin` methods, has methods to create, start, stop, and delete detectors. All except the start and stop jobs have no arguments but all return the response json (as a dict).
- `create_detector()`: Using the arguments passed in, this function makes a `POST` request to create a new anomaly detector. After the function call, the detector's id is stored as `id`.
- `delete_detector()`: Using the arguments passed in as well as the `id` from calling `create_detector()`, this function makes a `DELETE` request to delete the anomaly detector. The detector object must call `create_object()` before deletion or else a `ValueError` is raised.
- `start_detector()`: Using the arguments passed in as well as the `id` from calling `create_detector()`, this function makes a `POST` request to start the anomaly detector job. The detector object must call `create_object()` before starting or else a `ValueError` is raised.
    - **Arguments:**
        - `historical_analysis` (bool): This boolean flag tells the detector whether to start a live detector job or a historical analysis job. If this is `True`, the function uses `days_ago` argument to start the job.
- `stop_detector()`: Using the arguments passed in as well as the `id` from calling `create_detector()`, this function makes a `POST` request to stop the anomaly detector job. The detector object must call `create_object()` before stopping or else a `ValueError` is raised.
    - **Arguments:**
        - `historical_analysis` (bool): This boolean flag tells the detector whether to stop a live detector job or a historical analysis job.