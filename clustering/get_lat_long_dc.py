import os
import psycopg2

conn = psycopg2.connect(database='bikeshare',user='bikeshare',host='bikeshare.ctmvy2bluoic.us-west-2.rds.amazonaws.com',password="bikeshare")

cur = conn.cursor() 

# get all the DC metadata
cur.execute("SELECT * FROM metadata_washingtondc")
metadata = cur.fetchall()

# the following two commands get all the table names in the database
cur.execute("SELECT table_name FROM information_schema.tables")
tables = cur.fetchall()

for i in range(0,len(metadata)):
    print str(metadata[i])[1:-1]