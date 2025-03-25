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

#create patient medication schedule
USE patients;
CREATE TABLE medication_schedule (
    id INT unsigned NOT NULL AUTO_INCREMENT,
    user_id INT unsigned NOT NULL,
    name VARCHAR(255) NOT NULL,
    dosage VARCHAR(100),
    schedule_type ENUM('interval', 'fixed') NOT NULL,
    interval_hours INT DEFAULT NULL,
    start_time TIME DEFAULT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES patient_id(id)
);
DESCRIBE medication_schedule;

#create patient vitals schedule 
USE patients;
CREATE TABLE vitals_schedule (
    id INT unsigned NOT NULL AUTO_INCREMENT,
    user_id INT unsigned NOT NULL,
    name VARCHAR(255) NOT NULL,
    schedule_type ENUM('interval', 'fixed') NOT NULL,
    interval_hours INT DEFAULT NULL,
    start_time TIME DEFAULT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES patient_id(id)
);
DESCRIBE vitals_schedule;

# create medication/ vitals tracking table
USE patients; 
CREATE TABLE tracker (
    tracking_id INT unsigned NOT NULL AUTO_INCREMENT,
    user_id INT unsigned NOT NULL,
    schedule_id INT NOT NULL,  -- Can reference either medication/vitals table
    schedule_type ENUM('medication', 'vitals') NOT NULL,  -- Determines source table
    scheduled_time DATETIME NOT NULL,
    actual_time DATETIME,
    status ENUM('taken', 'missed', 'pending') DEFAULT 'pending',
    notes TEXT,
    PRIMARY KEY (tracking_id),
    FOREIGN KEY (user_id) REFERENCES patient_id(id),
    INDEX (scheduled_time),
    INDEX (status)
);
DESCRIBE tracker;