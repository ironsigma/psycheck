# PsyCheck - Psychic Checkbook

A simple recurring transaction scheduler with balance forcasting


## Setup

Create a database using the schema located in `ironsigma/database` directory.

Create a `.env` file with the following properties:

``` properties
DB_HOST=localhost
DB_PORT=3306
DB_USER=user
DB_PASS=pass
DB_NAME=checkbook
```

## MariaDB Connector

Make sure the following packages are installed:

- python3-devel
- mariadb-connector-c-devel

then install as usual:

```bash
    pip install mariadb
```


## Running App

To run the app in development mode use the following:

``` shell
    sanic --debug --reload --access-logs --worker 1 --factory ironsigma.app:create
```
