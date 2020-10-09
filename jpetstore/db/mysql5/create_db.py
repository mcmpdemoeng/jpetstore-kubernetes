import mysql.connector
from mysql.connector import errorcode
import os
url = os.environ.get('mysqlUrl')
user = os.environ.get('mysqlUser')
pswd = os.environ.get('mysqlPass')
# Obtain connection string information from the portal
config = {
  'host': url,
  'user': user,
  'password': pswd,
  'database':'mysql'
}
# Construct connection string
try:
   conn = mysql.connector.connect(**config)
   print("Connection established")
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with the user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)
else:
    cursor = conn.cursor()
import codecs
fd = codecs.open('/src/jpetstore-mysql-1-schema.sql', mode='r', encoding='utf-8-sig', errors='ignore')
operation = fd.read()
fd.close()
try:
  for result in cursor.execute(operation, multi=True):
    if result.with_rows:
      print("Rows produced by statement '{}':".format(
        result.statement))
      print(result.fetchall())
    else:
      print("Number of rows affected by statement '{}': {}".format(
        result.statement, result.rowcount))
except:
  print("###")

fd = codecs.open('/src/jpetstore-mysql-2-dataload.sql', mode='r', encoding='utf-8-sig', errors='ignore')
operation = fd.read()
fd.close()
try:
  for result in cursor.execute(operation, multi=True):
    if result.with_rows:
      print("Rows produced by statement '{}':".format(
        result.statement))
      print(result.fetchall())
    else:
      print("Number of rows affected by statement '{}': {}".format(
        result.statement, result.rowcount))
except:
  print("---")
conn.commit()
conn.close()
