#!/bin/bash

echo "!!! mongorestore !!!"
cd /docker-entrypoint-initdb.d/
mongorestore --uri mongodb://127.0.0.1:27017 --archive < mongo.dump