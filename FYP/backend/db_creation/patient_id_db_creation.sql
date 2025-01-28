# create db if a db has not been created yet
CREATE DATABASE patients;

# show all dbs to confirm creation
SHOW DATABASES;

# go into the db
USE patients;

# create patient login table
CREATE TABLE patient_id(
    id INT unsigned NOT NULL AUTO_INCREMENT, 
    name VARCHAR(100) NOT NULL UNIQUE, 
    pw_hash VARCHAR(64) NOT NULL, 
    PRIMARY KEY(id)
);

DESCRIBE patient_id;