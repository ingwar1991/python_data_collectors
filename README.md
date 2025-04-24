# data_collectors

Python library for collecting data from 3rd-party vendors. 

It leverages **Redis** and **Celery** to register jobs, which are then processed by worker nodes. 
Each job represents a single API call, ensuring that pagination is handled between jobs rather than within a single job. 

This approach optimizes the data collection process by parallelizing the API calls. 
By splitting the process into independent jobs and eliminating the need to wait for API responses within each job, 
the system is able to significantly reduce the overall processing time, addressing the common bottleneck of waiting for 3rd-party API responses.

## Adding a New Vendor

To add a new vendor, you need to create a folder with the vendor's name under the `project/app/collectors/vendors` directory.

### Folder Structure

Inside the vendor folder, you need to have two files:

- `config.yaml`
- `collector.py` with the `Collector` class inherited from `project/app/collectors/BaseCollector`

### `config.yaml` Contents

The `config.yaml` file should look like this:

```yaml
vendor_name: THE SAME AS DIR NAME 
base_url: <BASE_URL> 
endpoint: <ENDPOINT> 
http_method: <HTTP_METHOD> 
response_type: json|xml|text 
limit: <LIMIT> 
auth_type: no_auth|basic|token|token_bearer|oauth|custom
```

#### Authentication Configuration

Depending on the `auth_type`, the `config.yaml` may require additional fields:

##### basic
```yaml
username: <USERNAME>
password: <PASSWORD>
```


##### token or token_bearer
```yaml
token: <TOKEN>
```

##### oauth
```yaml
token_url: <TOKEN_URL>
client_id: <CLIENT_ID>
client_secret: <CLIENT_SECRET>
```

### Custom Authentication Configuration

For a custom `auth_type`, you need to create a custom **Requester** at `project/app/vendors/YOUR_VENDOR/`.

This **Requester** should inherit from `project/app/requester/BaseRequester` and implement the following abstract method:

```python
@abstractmethod
def authenticate(self):
    pass
```

### Implementing the Vendor Collector

The `Collector` class inside the vendor's `collector.py` should inherit from `project/app/collectors/BaseCollector`. 
It must implement the following abstract methods from `BaseCollector`:

1. `_hydrate_request_params(self, data: Dict) -> Dict`

```python
@abstractmethod
def _hydrate_request_params(self, data: Dict) -> Dict:
  """
  Returns hydrated dict of params for request
  """
  pass
```

2. `_hydrate(self, raw_data: Dict) -> BaseHydratedCollection`
```python
@abstractmethod
def _hydrate(self, raw_data: Dict) -> BaseHydratedCollection:
    """
    Returns collection of hydrated entities
    """
    pass
```

3. `_paginate(self, request_params: Dict, raw_data: Dict) -> Dict`
```python
@abstractmethod
def _paginate(self, request_params: Dict, raw_data: Dict) -> Dict:
    """
    Returns Dictionary containing next_page_request_params.
    """
    pass
```

## Hydration
For hydration, we have two base classes located at `project/app/hydrated`:
* BaseHydratedEntity
* BaseHydratedCollection

To hydrate raw_data, you will need to create two classes:
* HydratedEntity
* HydratedCollection

These classes can be placed either in `project/app/vendor/YOUR_VENDOR/hydrated/` (if used only by this vendor) 
or in `project/app/hydrated/ENTITY_NAME/` (if shared by multiple vendors).

### HydratedEntity
HydratedEntity must inherit from BaseHydratedEntity and implement the following method:

1. `_generate_unique_id(self) -> str`
```python
@abstractmethod
def _generate_unique_id(self) -> str:
    pass
```

### HydratedCollection
HydratedCollection must inherit from BaseHydratedCollection and implement the following three methods:

1. `_get_db_conn(self)`
```python
@abstractmethod
def _get_db_conn(self):
    pass
```

2. `get_existing_unique_ids_from_db(self) -> List[str]`
```python
@abstractmethod
def _get_existing_unique_ids_from_db(self) -> List[str]:
    pass
```

3. `_insert_new_in_db(self)`
```python
@abstractmethod
def _insert_new_in_db(self):
    pass
```

## Database
Database connections should be created in `project/app/db/` and then used by HydratedCollection class.

## Frontend
There is a small front-end web project with just one page. It includes a form for filtering, ordering, and applying grouping for data, as well as displaying the found data.

You can access it at:
`http://localhost:${FRONT_PORT}`

where ${FRONT_PORT} is env var from docker/.env

### Config

We have `config.yaml.template` files located at the following directories:

- `project/app/collectors`
- `project/app/collectors/vendors/crowdstrike`
- `project/app/collectors/vendors/qualys`

These files should be copied and renamed as `config.yaml`, and then filled with the required data.

---

# Running the Project

To run the project, you will need to have **Docker Compose** & **Docker Engine** installed.

## Environment

There is a `.env.template` file located in the `docker/` directory. You must copy this file as `.env` and fill it with the required data.

### Learn about `start.sh`

`start.sh` is a bash script that allows you to:

- Start and shut down containers
- Run tests
- Access specific container bash environments

##### Usage: 
```bash
./start {param}
```

###### Parameters:
- `-d`: Run containers and detach
- `-b {DESTINATION}`: Go to a specific container bash. Available destinations:
  - `c`: Go to collectors container bash
  - `f`: Go to front container bash
  - `d`: Go to db container bash
  - `r`: Go to redis container bash
  - `w1`: Go to worker1 container bash
  - `w2`: Go to worker2 container bash
- `-t`: Run containers, then run tests and stop on success. If tests fail, it will automatically send you to the collectors container bash.
- `-s`: Stop containers and remove volumes

### Learn about `getLogs.sh`

`getLogs.sh` allows you to read logs from a specific container.

#### Usage: 
```bash
./getLogs {param}
```

##### Parameters:
- `c`: Get logs from the collectors container
- `f`: Get logs from the front container
- `d`: Get logs from the db container
- `r`: Get logs from the redis container
- `w1`: Get logs from worker1 container
- `w2`: Get logs from worker2 container

## Tests

It is a good idea to start by running tests.

To do this, navigate to the root directory and run:

```bash
./start -t
```

This will start the containers, run the tests, and stop the containers if the tests pass. If the tests fail, it will automatically send you to the `data_collectors_collectors` container.

## Run

After the tests pass, you can start the project with:

```bash
./start -d
```

This will start everything and detach.

Then, you can access the front project at:

`http://localhost:${FRONT_PORT}`

where `${FRONT_PORT}` is an environment variable defined in the `docker/.env` file.
