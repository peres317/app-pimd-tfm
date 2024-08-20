CREATE DATABASE app_warehouse;
CREATE USER 'load'@'localhost' IDENTIFIED BY 'password';
GRANT INSERT ON app_warehouse.* TO 'load'@'localhost';
GRANT SELECT ON app_warehouse.* TO 'load'@'localhost';
GRANT USAGE ON app_warehouse.* TO 'load'@'localhost';
CREATE DATABASE app_warehouse_credentials;
CREATE USER 'credentials'@'localhost' IDENTIFIED BY 'password';
GRANT INSERT ON app_warehouse_credentials.* TO 'credentials'@'localhost';
GRANT SELECT ON app_warehouse_credentials.* TO 'credentials'@'localhost';
GRANT USAGE ON app_warehouse_credentials.* TO 'credentials'@'localhost';
GRANT UPDATE ON app_warehouse_credentials.* TO 'credentials'@'localhost';
GRANT DELETE ON app_warehouse_credentials.* TO 'credentials'@'localhost';
CREATE USER 'grafana'@'localhost' IDENTIFIED BY 'password';
GRANT SELECT ON app_warehouse.* TO 'grafana'@'localhost';
FLUSH PRIVILEGES;
EXIT
