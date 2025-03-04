# backendPublicDBStorage
This is a simple API service built with **Flask** that integrates with **MYSQL** for managing API keys and **MongoDB** for storing and querying data. The service allows users to generate and validate API keys, insert data into MongoDB, and query specific fields from the database.

## Requirements
To run this project, you'll need:
- A docker environment
- Best used with a reverse proxy to enable HTTPS 
- If exposed to the public web, consider using Cloudflare and blocking based on country of origin

## Deployment with Docker Compose
This container is designed to be deployed using Docker Compose. Below is an example configuration:

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:8.0.5
    container_name: dots_mongodb
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: <mongodb root password>
    volumes:
      - /bdata/docker/dots/mongodb:/data/db
      - /bdata/docker/dots/config:/data/configdb
    restart: unless-stopped
    # ports:
    #  - "27017:27017"

  mysqldb:
    image: adclab/keydb:v0.3.0
    container_name: dots_keydb
    environment:
      MYSQL_ROOT_PASSWORD: <mysql root password>
      MYSQL_API_KEY_MANAGER_PASSWORD: <mysql key manager password>
    restart: unless-stopped
    # volumes:
    #  - /bdata/docker/dots/mysqldb:/data/db
    # ports:
    #  - "3306:3306"

  flask2mongo:
    image: adclab/flask2mongo:v0.4.0
    container_name: dots_flask2mongo
    depends_on:
      - mongodb
      - mysqldb
    ports:
      - "5000:5000"
    restart: unless-stopped
    environment:
      MYSQL_HOST: mysqldb
      MYSQL_PORT: 3306
      MYSQL_DATABASE: api_tracking
      MYSQL_USER: api_key_manager
      MYSQL_PASSWORD: <mysql key manager password>
      MY_MONGO_HOST: mongodb
      MY_MONGO_PORT: 27017
      MY_MONGO_USER: admin
      MY_MONGO_PASS: <mongodb root password>
      MY_MONGO_DB:  <database name>
      MY_MONGO_COLLECTION: <collection name>
      MAX_FILE_SIZE: <INT in MB>
      API_KEY_EXPIRATION: <time in seconds>
      CORS_ORIGINS: www.example.com, www.mywebpage.com
      SAMPLE_SIZE: 1000
```

Ensure that environment variables such as database passwords are securely set and not hardcoded.

By default **MongoDB** and **MYSQL** are not publically accessible.  However, for testing purposes you can uncomment the port exposures for each service to access remotely.  **Make sure to hide ports when deploying to the public web!**   

Because MongoDB is used to maintain data it should be written to a persistant volume.  Meanwhile, MYSQL is used to manage temporary API keys that get deleted from the database as part of a regularly occuring process, there is no need for the data to persist.

CORS_ORIGINS is used to limit access to the API based on origin requests.  You can enter a list of urls or provide "*" (wildcard) to allow access from any source.  Usage of the wildcard option is dangerous and should only be used when testing or working within a restricted network.

## flask2mongo
flask2mongo is a python flask deployment that serves as the front-end for aquireing temporary keys, pushing data to a mongoDB database, and retriving simple fields from the mongoDB database.  By default, the application will run on `http://localhost:5000`.  

### Environment Variables

This application requires several environment variables to be set for configuration. These include:

- `MYSQL_HOST`: The host address for the MySQL server (default is `localhost`).
- `MYSQL_USER`: The username for the MySQL server (default is `root`).
- `MYSQL_PASSWORD`: The password for the MySQL server.
- `MYSQL_DB`: The name of the database to connect to (default is `api_tracking`).
- `API_KEY_EXPIRATION`: The expiration time (in seconds) for API keys (default is 600 seconds).
- `MY_MONGO_HOST`: The host address for the MongoDB server.
- `MY_MONGO_PORT`: The port for the MongoDB server (default is `27017`).
- `MY_MONGO_USER`: The username for the MongoDB server.
- `MY_MONGO_PASS`: The password for the MongoDB server.
- `MY_MONGO_DB`: The MongoDB database name.
- `MY_MONGO_COLLECTION`: The MongoDB collection name.
- `MAX_FILE_SIZE`: The maximum file size (in MB) allowed for uploads (default is 1 MB).
- `CORS_ORIGINS`: A comma-separated list of allowed origins for CORS (default is `*`).
- `SAMPLE_SIZE`: The number of random records to fetch when querying MongoDB (default is 1000).

### API Endpoints

#### 1. **Generate API Key**

- **Endpoint**: `/getkey`
- **Method**: `GET`
- **Description**: Generates a new API key and inserts it into the MySQL database with an expiration time.
- **Response**: A JSON object containing the API key and expiration time.

```json
{
  "api_key": "some-generated-api-key",
  "expires_in": 600
}
```

#### 2. **Validate API Key**

- **Endpoint**: `/validatekey/<api_key>`
- **Method**: `GET`
- **Description**: Validates the provided API key by checking if it exists in the MySQL database and whether it has expired.
- **Response**: A JSON object indicating whether the key is valid or not.

```json
{
  "valid": true,
  "expires_in": 500
}
```

If invalid or expired:

```json
{
  "valid": false,
  "message": "API key expired or invalid"
}
```

#### 3. **Insert Data into MongoDB**

- **Endpoint**: `/insert`
- **Method**: `POST`
- **Description**: Inserts JSON data into the MongoDB collection after validating the API key and ensuring the content size is within the allowed limit.
- **Headers**: `X-API-KEY` (API key for authentication)
- **Response**: A JSON object indicating success or failure.

```json
{
  "success": true,
  "message": "Data stored successfully"
}
```

If the file is too large:

```json
{
  "success": false,
  "message": "File is too large. Maximum size is 1 MB."
}
```

#### 4. **Query Values from MongoDB**

- **Endpoint**: `/getvalues`
- **Method**: `GET`
- **Description**: Queries a specific field in the MongoDB collection and returns a random sample of values for that field.
- **Query Parameters**:
  - `field`: The field name to query.
- **Response**: A JSON object with the queried values or an error message if no data is found.

```json
{
  "success": true,
  "field": "field_name",
  "values": ["value1", "value2", "value3"]
}
```

If the field is not found:

```json
{
  "success": false,
  "message": "No records found for the field 'field_name'"
}
```


---

# Docker Container

## Overview
This repository provides a Docker container setup, including a `Dockerfile` and initialization scripts, to streamline deployment. The container is configured to run custom startup scripts to ensure a smooth execution of necessary processes. It uses MySQL to manage API keys.

## Files
- **Dockerfile**: Defines the container environment and dependencies.
- **run_at_start.sh**: Script executed at container startup.

## Deployment with Docker Compose
This container is designed to be deployed using Docker Compose. Below is an example configuration:

```yaml
version: '3.8'
services:
  mysqldb:
    image: adclab/keydb:v0.3.0
    container_name: dots_keydb
    environment:
      MYSQL_ROOT_PASSWORD: <root_password>
      MYSQL_API_KEY_MANAGER_PASSWORD: <password>
    volumes:
      - /bdata/docker/dots/mysqldb:/data/db
    #ports:
    #  - "3307:3306"
```

Ensure that environment variables such as `MYSQL_ROOT_PASSWORD` and `MYSQL_API_KEY_MANAGER_PASSWORD` are securely set.

## MySQL Configuration
This container includes MySQL for managing API keys. Ensure that your MySQL environment variables are properly set up in the `Dockerfile` or provided via environment variables at runtime.

To connect to the MySQL database inside the container:
```sh
docker exec -it my-container mysql -u root -p
```

Modify the database schema or insert API keys as needed using SQL queries.

### MySQL Table Structure
The `run_at_start.sh` script creates a MySQL database named `api_tracking` and a table called `api_keys`.

#### **Table: `api_keys`**
| Column      | Type         | Attributes                                   |
|------------|-------------|----------------------------------------------|
| `id`       | `INT`       | AUTO_INCREMENT, PRIMARY KEY                 |
| `api_key`  | `VARCHAR(255)` | NOT NULL, UNIQUE                        |
| `created_at` | `TIMESTAMP`  | DEFAULT CURRENT_TIMESTAMP                 |
| `expires_at` | `TIMESTAMP`  | DEFAULT CURRENT_TIMESTAMP                 |

Additionally, the script:
- Creates a MySQL user (`api_key_manager`) with privileges to manage the `api_tracking` database.
- Sets up an event that runs every minute to delete expired API keys (`expires_at < NOW()`).
- Enables the MySQL event scheduler to ensure automated cleanup.

## Customizing the Container
Modify the scripts (`init.sh` and `run_at_start.sh`) to customize startup behavior as needed.

## Stopping and Removing the Container
To stop the container:
```sh
docker stop my-container
```

To remove the container:
```sh
docker rm my-container
```

## Logs
To view container logs:
```sh
docker logs my-container
```

If you have any questions or need further assistance, feel free to open an issue or contact the maintainers.
