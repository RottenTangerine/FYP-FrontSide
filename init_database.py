import sqlite3

conn = sqlite3.connect('test.db')
cursor = conn.cursor()

# cursor.execute('DROP TABLE alltest')
cursor.execute('CREATE TABLE alltest ('
               'id integer primary key autoincrement,'
               'test_name varchar(255),'
               'author varchar(255),'
               f'ans_img varchar({2 ** 22}),'  # max_img_size = 4mb 
               f'ans_txt varchar({2 ** 12})'  # 2000 chinese character
               ');')


# cursor.execute('DROP TABLE allpaper')
cursor.execute('CREATE TABLE allpaper ('
               'id integer primary key autoincrement,'
               'student_id varchar(255),'
               'test_id integer(255),'
               'mark varchar(255),'
               f'ans_img varchar({2 ** 22}),'  # max_img_size = 4mb 
               f'ans_txt varchar({2 ** 12})'  # 2000 chinese character
               ');')

conn.commit()
cursor.close()
conn.close()
