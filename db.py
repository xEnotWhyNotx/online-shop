#Последняя версия BotDB на момент переноса функционала в отдельную папку


# import sqlite3
# import csv
# class BotDB:
    
#     def __init__(self, db_file):
#         #Инициализация соединения с бд
#         self.conn = sqlite3.connect(db_file)
#         self.cursor = self.conn.cursor()
       
#     def users_list(self):
#         #Получение списка пользователей из БД
#         csv_file = 'users_list.csv'
#         users_list = self.cursor.execute("SELECT * from users")
#         rows = users_list.fetchall()
#         print("Данные были получены, вот они", rows)
    
#         try:
#             users_list = self.cursor.execute("SELECT * from users")
#             rows = users_list.fetchall()
        
#             with open(csv_file, mode='w', newline='') as file:
#                 writer = csv.writer(file)
#                 writer.writerow([description[0] for description in self.cursor.description])
#                 writer.writerows(rows)
   
#             return csv_file
        
#         except Exception as e:
#             print(f"Произошла ошибка при создании CSV файла: {e}")
#             return None

    
#     def is_user_in_db(self, user_id):
#         query = self.cursor.execute("Select Telegram_id from Users where Telegram_id = ?", (user_id,)).fetchone()
#         if query == None:
#             return False
#         else:
#             return True
    
#     def create_new_user(self, user_id):
#         self.cursor.execute("INSERT INTO users (Telegram_id) values(?)", (user_id, ))
#         self.conn.commit()
    
#     def insert_seller(self, user_id):
#         self.cursor.execute("UPDATE users set role = ? where telegram_id = ?", ("Seller", user_id))
#         self.conn.commit()
    
#     def insert_customer(self, user_id):
#         self.cursor.execute("UPDATE users set role = ? where telegram_id = ?", ("Customer", user_id))
#         self.conn.commit()

#     def get_role(self, user_id):
#         role = self.cursor.execute("Select role from users where telegram_id = ?", (user_id, )).fetchone()
#         print(role)
#         return role
        