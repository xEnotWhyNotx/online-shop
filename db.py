import sqlite3
import csv
class BotDB:
    
    def __init__(self, db_file):
        #Инициализация соединения с бд
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        

    def create_user(self, user_id):
        checking_user = self.cursor.execute("select * from users where telegram_id = ?", user_id).fetchone()
        if not checking_user:
            self.cursor.execute("INSERT INTO users (telegram_id) values (?)", user_id)
            self.conn.commit()
            return 1
        else:
            pass
            


    
    def users_list(self):
        #Получение списка пользователей из БД
        csv_file = 'users_list.csv'
        users_list = self.cursor.execute("SELECT * from users")
        rows = users_list.fetchall()
        print("Данные были получены, вот они", rows)
    
        try:
            users_list = self.cursor.execute("SELECT * from users")
            rows = users_list.fetchall()
        
            with open(csv_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([description[0] for description in self.cursor.description])
                writer.writerows(rows)
   
            return csv_file
        
        except Exception as e:
            print(f"Произошла ошибка при создании CSV файла: {e}")
            return None
 
    def check_password(self, user_id):
        users_list = self.cursor.execute("SELECT password from users where telegram_id = ?", user_id)
        password = users_list.fetchone()
        return password
    
    
