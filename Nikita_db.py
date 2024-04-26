import sqlite3
import csv
actual_id = 0
class BotDB:
    
    def __init__(self, db_file):
        #Инициализация соединения с бд
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        
    def users_list(self):
        #Получение списка пользователей из БД
        csv_file = 'users_list.csv'
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
 
    def check_orders(self):
        #Формируем csv файл со списком заказов#
        csv_file = "current_orders.csv"
        try:
            order_list = self.cursor.execute("SELECT * from orders")
            order_list = order_list.fetchall()
        
            with open(csv_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([description[0] for description in self.cursor.description])
                writer.writerows(order_list)
   
            return csv_file
        
        except Exception as e:
            print(f"Произошла ошибка при создании CSV файла: {e}")
            return None
    
    def create_new_item(self):
        name = "default"
        description = "default"
        price = 0
        amount = 0
        self.cursor.execute('''INSERT INTO items (name, description, price, amount) VALUES (?, ?, ? ,?)''', (name, description, price, amount))
        self.conn.commit()
        global actual_id
        actual_id = self.cursor.lastrowid
    
    def insert_name(self, name):
        global actual_id
        self.cursor.execute('''UPDATE items set name = ? where item_id = (?)''', (name, actual_id) )
        self.conn.commit()

    def insert_description(self, description):
        global actual_id
        self.cursor.execute('''UPDATE items set description = ? where item_id = (?)''', (description, actual_id) )
        self.conn.commit()

    def insert_price(self, price):
        global actual_id
        self.cursor.execute('''UPDATE items set price = ? where item_id = (?)''', (price, actual_id) )
        self.conn.commit()  
    
    def insert_amount(self, amount):
        global actual_id
        self.cursor.execute('''UPDATE items set amount = ? where item_id = (?)''', (amount, actual_id) )
        self.conn.commit()  