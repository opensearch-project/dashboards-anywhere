# Authentication Headers for API Calls

To make requests to OpenSearch (OS), authentication headers are necessary to make CRUD operations on indices and plugins. The `Authentication` class handles the logic for creating this header. `Authentication` is an abstract class and by default, this tooling uses `BasicAuthentication` class (user credentials) to authenticate requests.

## `Authentication` (abstract class)

This class is designed to be overwritten for any user to design their own authentication. This class has no arguments for initialization but it does require one function to be implemented: `get_auth()`

- `get_auth()`: When this function is called, it should return the header necessary to make the API call
    - **Arguments:**
        - This function takes no arguments
    - **Returns:**
        - This function should return a header (typically as a dict)

## `BasicAuthentication` (implemented from `Authentication`)

This class is the only implementation of `Authentication` and is designed for basic user credential authentication.

This class has two arguments for initialization:
- **Arguments:**
    - `username` (string): The username of the user who has CRUD permissions for plugins and indices
    - `password` (string): The password of the user who has CRUD permissions for plugins and indices

`BasicAuthentication` has only one "get" function:

- `get_auth()`: When this function is called, it should return the header necessary to make the API call
    - **Arguments:**
            - This function takes no arguments
    - **Returns:**
        - This function returns a header (typically as a dict)
