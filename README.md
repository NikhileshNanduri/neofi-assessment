# NeoFi Assessment - Nikhil

## Description
Tech Stack Opted - Django <br>
DB - PostgreSQL

## Installation
The solution is dockerised, so simply run (Pre-req - Docker installation is mandatory) <br>
`docker compose build` <br>
`docker compose up`

2 containers will spin up, namely db and neofiapp

*No need to perform DB Migrations, the migration script is in the Docker ENTRYPOINT*

## API Documentation

Import `Neofi.postman_collection.json` in postman to get all the endpoints ready for testing/development. 
In the collection description, you will find the details for each endpoint

Note : To authenticate, provide Authorization with token in Headers.
