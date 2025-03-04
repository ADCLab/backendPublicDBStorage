# backendPublicDBStorage
This repository is a composition of flask, mongodb, and mysql webservices to manage temporary API keys and pushing data to a database.  This repo is generalized to allow for storage of data from any public websites.  This software package is best deployed using the docker-compose file provided.

## flask2mongo
flask2mongo is a python flask deployment that serves as the front-end for aquireing temporary keys, pushing data to a mongoDB database, and retriving simple fields from the mongoDB database.  flask2mongo has the following end-point:

### /getkey [get]
Description: gets a new API key to be used for uploading data and downloading a single field from the dataset
Output: {"api_key": <api key>, "expires_in": <time until expiration>}

### /validatekey/{api_key} [get]
Description: validates API key
Output: 
  {'valid':True, "expires_in": <time until expiration>}
  {'valid':False, "message": "API key expired or invalid"}

### /insert [post]
Description: Use to upload json data
Input:
  headers = {"X-API-KEY": api_key,"Content-Type": "application/json"}
  data = {"name": "Test User","email": "test@example.com","age": 30}
Output:
  {"success": True, "message": "Data stored successfully"}
  {"success": False, "message": "Invalid API key"}
  {"success": False, "message": "API key expired"}
  {"success": False, "message": "No content found in the request"}
  {"success": False, "message": f"File is too large. Maximum size is {MAX_FILE_SIZE} MB."}
  {"success": False, "message": "Invalid JSON payload"}
  

### /getvalues [get]
