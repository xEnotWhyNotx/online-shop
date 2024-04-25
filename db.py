import sqlite3
backupversion = 0
class BotDB:
    
    def __init__(self, db_file):
        #Инициализация соединения с бд
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        

    # def users_list(self):
    #     #Получение списка пользователей из БД
    #     csv_file = 'users.csv'
    #     # try :
    #     users_list = self.cursor.execute("SELECT * from users")
    #     rows = users_list.fetchall()
    #     print("Данные были получены, вот они", rows)
    
    #     try:
    #         users_list = self.cursor.execute("SELECT * from users")
    #         rows = users_list.fetchall()
        
    #         with open(csv_file, mode='w', newline='') as file:
    #             writer = csv.writer(file)
    #             writer.writerow([description[0] for description in self.cursor.description])
    #             writer.writerows(rows)
    #         backupversion+=1     
    #         return csv_file
        
    #     except Exception as e:
    #         print(f"Произошла ошибка при создании CSV файла: {e}")
    #         return None
    def users_list(self):
        # Получение списка пользователей из БД
        users_list = self.cursor.execute("SELECT * from users")
        rows = users_list.fetchall()

        user_list = []
        column_names = [description[0] for description in self.cursor.description]
        user_list.append(column_names)

        for row in rows:
            user_list.append(row)
        print(user_list)
        return user_list
        

