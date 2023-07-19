FROM mongo

# create a user and database
ENV MONGO_INITDB_ROOT_USERNAME ricardo
ENV MONGO_INITDB_ROOT_PASSWORD ricardo
ENV MONGO_INITDB_DATABASE my-mongo-db
COPY init.js /docker-entrypoint-initdb.d/

VOLUME /data/db

EXPOSE 27017