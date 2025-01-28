# create db if a db has not been created yet
CREATE DATABASE patients;

# show all dbs to confirm creation
SHOW DATABASES;

# go into the db
USE patients;

# create patient login table
CREATE TABLE patient_id(
    id INT unsigned NOT NULL AUTO_INCREMENT, 
    name VARCHAR(100) NOT NULL, 
    pw_hash VARBINARY(256) NOT NULL, 
    PRIMARY KEY(id)
);

DESCRIBE patient_id;