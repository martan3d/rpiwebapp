# create database

import MySQLdb as db
import sys

con = db.connect( passwd="raspberry")
cur = con.cursor()

try:
   cur.execute('CREATE DATABASE webapp;')
except:
   print "Webapp database already exists, manually drop it before running this script"
   sys.exit(1)

cur.execute('USE webapp;')

try:
   cur.execute("CREATE USER 'www-data'@'localhost' IDENTIFIED BY 'raspberry';")
except:
   pass

cur.execute("GRANT ALL ON webapp.* TO 'www-data'@'localhost';")

db.connect(host="localhost", passwd="raspberry", db="webapp")

TABLES = {}
TABLES['nodes'] = (
    "CREATE TABLE `nodes` ("
    "  `boxnum`      int(16) NOT NULL AUTO_INCREMENT,"
    "  `name`        varchar(64) NOT NULL,"
    "  `address`     varchar(64) NOT NULL,"
    "  `type`        varchar(64) NOT NULL,"
    "  `status`      varchar(64) NOT NULL,"
    "  PRIMARY KEY (`boxnum`)"
    ") ENGINE=InnoDB")

cur.execute(TABLES['nodes'])

