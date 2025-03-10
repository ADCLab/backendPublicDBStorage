# backendPublicDBStorage
This is a simple API service built with **Flask** that integrates with **MariaDB** for managing API keys and **MongoDB** for storing and querying data. The service allows users to generate and validate API keys, insert data into MongoDB, and query specific fields from the database.

## Requirements
To run this project, you'll need:
- A docker environment

This package is best to deploy using a reverse proxy to enable HTTPS.  If exposed to the public web, seriously consider using Cloudflare and blocking based on country of origin, and deploying on an AWS lightsail.  With AWS lightsail you can take regular snapshots of the data (e.g. backup), and if the backend is attacked then the only loses will be to the lightsail instance (as oppose to getting into you lab or home server).  

## Deployment with Docker Compose
This container is designed to be deployed using Docker Compose. Below is an example configuration:

```yaml
version: '3.8'


services:
  mongodb:
    image: mongo:8.0.5
    container_name: dots_mongodb
    restart: unless-stopped
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: <mongo root password>
      MONGO_INITDB_DATABASE: <database name>
    volumes:
      - /bdata/docker/dots/mongodb:/data/db
      - /bdata/docker/dots/config:/data/configdb
    command: ["mongod", "--wiredTigerCacheSizeGB", "0.25", "--storageEngine", "wiredTiger", "--bind_ip_all"]
    mem_limit: 128m  # Limit MongoDB memory to 128MB
    # Uncomment the lines below to enable restart and expose port if necessary
    # ports:
    #   - "27017:27017"

  mariadb:
    image: adclab/keydb:v0.4.1
    container_name: dots_keydb
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: <root password to database>
      MYSQL_API_KEY_MANAGER_PASSWORD: <api_key_manager password to database>
    volumes:
      - /bdata/docker/dots/mysqldb:/data/db
    #ports:
    #  - "3307:3306"
    #entrypoint: ["/bin/bash", "/docker-entrypoint-initdb.d/init.sh"]

  flask2mongo:
    image: adclab/flask2mongo:v0.4.2
    container_name: online_experiments_flask2mongo
    restart: unless-stopped
    depends_on:
      - mongodb
      - mariadb
    ports:
      - "5000:5000"
    environment:
      NUM_WORKERS: 1 # Optional defaults to 1
      IP_ADDRESS: 0.0.0.0 # Optional defaults to 0.0.0.0
      PORT: 5000 # Optional defaults to 5000
      MYSQL_HOST: mariadb
      MYSQL_PORT: 3306
      MYSQL_DATABASE: api_tracking
      MYSQL_USER: api_key_manager
      MYSQL_PASSWORD: <api_key_manager password to database>
      MY_MONGO_HOST: mongodb
      MY_MONGO_PORT: 27017
      MY_MONGO_USER: admin
      MY_MONGO_PASS: <mongo root password>
      MY_MONGO_DB: <database name>
      MY_MONGO_COLLECTION: <collection name>
      MAX_FILE_SIZE: 1
      API_KEY_EXPIRATION: <time in seconds>
      CORS_ORIGINS: "*"
      SAMPLE_SIZE: 1000
      

```
The set-up above is memory optimized.  If there are issues you may have to change run-time settings in MongoDB (e.g. wiredTigerCacheSizeGB) and recompile the MariaDB docker image.

Ensure that environment variables such as database passwords are securely set and not hardcoded.

By default **MongoDB** and **MariaDB** are not publically accessible.  However, for testing purposes you can uncomment the port exposures for each service to access remotely.  **Make sure to hide ports when deploying to the public web!**   

Because MongoDB is used to maintain data it should be written to a persistant volume.  Meanwhile, MariaDB is used to manage temporary API keys that get deleted from the database as part of a regularly occuring process, there is no need for the data to persist.

CORS_ORIGINS is used to limit access to the API based on origin requests.  You can enter a list of urls or provide "*" (wildcard) to allow access from any source.  Usage of the wildcard option is dangerous and should only be used when testing or working within a restricted network.

## API Endpoints

### 1. **Generate API Key**

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

### 2. **Validate API Key**

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

### 3. **Insert Data into MongoDB**

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

### 4. **Query Values from MongoDB**

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

If you have any questions or need further assistance, feel free to open an issue or contact the maintainers.
