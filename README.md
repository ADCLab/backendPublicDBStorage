# backendPublicDBStorage
This repository is a composition of flask, mongodb, and mysql webservices to manage temporary API keys and pushing data to a database.  This repo is generalized to allow for storage of data from any public websites.  This software package is best deployed using the docker-compose file provided.

## flask2mongo
flask2mongo is a python flask deployment that serves as the front-end for aquireing temporary keys, pushing data to a mongoDB database, and retriving simple fields from the mongoDB database.  flask2mongo has the following end-point:

/getkey
/validatekey
/pushdata
/getdata
