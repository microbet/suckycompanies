#! /usr/bin/python

import mysql.connector as mariadb

conn = mariadb.connect(user='dafuckapi', password='bgesaw#4', database='dafuckapi')
cursor = conn.cursor(buffered=True)

# go through the imagemetadata table and for each image check how many answers
# it has and then update its answer_count

sql = 'SELECT image_id FROM imagemetadata'
cursor.execute(sql)
for row in cursor:
    cursor2 = conn.cursor()
    sql = "SELECT count(*) AS count FROM answer WHERE image_id=%s"
    print("image is ", row[0])
    cursor2.execute(sql, (row[0],))
    row2 = cursor2.fetchone()
    print("count is ", row2[0])
    sql = "UPDATE imagemetadata SET answer_count=%s WHERE image_id=%s"
    cursor2.execute(sql, (row2[0], row[0]))

conn.commit()
conn.close()
