import pymysql

mydb = pymysql.connect(
    host="localhost",
    user="root",
    passwd="Eyobed579@papa",
    database="organicdb"
)

# print(mydb)
cursor = mydb.cursor()

cursor.execute("delete from product_list where product_name = 'Silver' ")
# myresult = my_cursor.fetchall()
# #
# # for row in myresult:
# #     print(row)
mydb.commit()
'''my_cursor.execute("create database organicdb")


my_cursor.execute("show databases")
for db in my_cursor:
    print(db)
    
    
   
    



sqlFORMULA = "INSERT INTO students (name, age) VALUES (%s, %s)"
students = [("Papa", 21),
            ("Eyobed", 25),
            ("Rakeb", 16),
            ("Enu", 18),
            ("Nati", 29)]
my_cursor.executemany(sqlFORMULA, students)

mydb.commit()




my_cursor.execute("update students set age = 18 where name = 'Enu'")

mydb.commit()

my_cursor.execute("select * from students order by name desc")
myresult = my_cursor.fetchall()

for row in myresult:
    print(row)

my_cursor.execute("drop table if exists students")
mydb.commit()'''


# sqlFORMULA = "INSERT INTO students (name, age) VALUES (%s, %s)"
# students = [("Papa", 21),
#             ("Eyobed", 25),
#             ("Rakeb", 16),
#             ("Enu", 18),
#             ("Nati", 29)]

# students1 = [("Loza", 90),
#             ("Bibo", 31),
#             ("Yeamlak", 13),
#             ("Elo", 8),
#             ("Fikr", 14),
#             ("Natnael", 12)]


# #my_cursor.execute("delete from students where age <30")
# my_cursor.executemany(sqlFORMULA, students)
# mydb.commit()