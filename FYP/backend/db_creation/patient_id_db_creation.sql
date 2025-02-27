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

# create chat history table 
CREATE TABLE chat_history (
    id INT unsigned NOT NULL AUTO_INCREMENT,
    user_id INT unsigned NOT NULL,
    message TEXT NOT NULL,
    sender ENUM('Human Message', 'AI Message') NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES patient_id(id),
    INDEX (timestamp)
);
DESCRIBE chat_history;

# create patient record info table
USE patients;
CREATE TABLE patient_records (
    record_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT unsigned NOT NULL,
    patient_name VARCHAR(255) NOT NULL,
    ailment TEXT,
    doctor_recommendations TEXT,
    medication VARCHAR(255),
    medication_timing VARCHAR(100),
    vitals TEXT,
    vitals_timing VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES patient_id(id)
);