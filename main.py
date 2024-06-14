import psycopg2
import time
import random 
from datetime import date
import re
import time

pattern = r"^\S+@\S+\.\S+$"

class Database_manager:
    def __init__(self, dbname, host, port, user, password):
        self.dbname=dbname
        self.host=host
        self.port=port
        self.user=user
        self.password=password
        self.connection=None
        self.cursor=None

    def connect(self):
        try:
            self.connection=psycopg2.connect(dbname=self.dbname,host= self.host, port=self.port, user=self.user, password=self.password)
            print('Connected successfully')
        except Exception as e:
            print(f'Connection refused: {e}')
        else:
            self.cursor = self.connection.cursor()
    def insert(self, table_name, **kwargs):
        columns=', '.join([column for column in kwargs.get('columns', [])])
        values=', '.join([f"'{column}'" if type(column) == str else f"{column}" for column in kwargs.get('values', [])])

        query =f'''INSERT INTO {table_name}({columns}) values({values})'''
        try:
            self.cursor.execute(query=query)
            self.connection.commit()
        except Exception as error:
            print(f'Error: {error}')
    def select(self, table, **kwargs):
        if kwargs.get('column', False):
            query= f'Select * from {table} where {kwargs["column"]} = {kwargs["value"]}'
        else:
            query= f'Select * from {table}'
        try:
            self.cursor.execute(query=query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f'Error: {e}')
            
    def delete(self, table, id):
        query= f'delete from {table} where id={id}'
        try:
            self.cursor.execute(query=query)
            self.connection.commit()
        except Exception as e:
            print(f'Error: {e}')
    def update(self, table, column, value, id):
        query= f"update {table} set {column} = '{value}' where id = {id}"
        try:
            self.cursor.execute(query=query)
            self.connection.commit()
        except Exception as e:
            print(f'Error: {e}')



database=Database_manager('store', 'localhost', 5432, 'postgres','postgres')
database.connect()


while True:
    while True:
        try:
            task = int(input('Зайти как админ(1) или как пользователь(2): '))
            break
        except ValueError:
            print('Некорректные данные')
            time.sleep(1)
    
    if task == 1:
        login = input('Введи логин: ')
        password = input('Введи пароль: ')
        if login == 'admin' and password == 'admin':
            while True:
                while True:
                    try:
                        actions=int(input('Что вы хотите сделать\n1) создать нового пользователя\n2) создать новый журнал\n3) Посмотреть все\n4)Выйти\n:'))
                        break                        
                    except ValueError:
                        print('Некорректные данные')
                        time.sleep(1)
                if actions == 1:
                    name=input('Имя: ')
                    surname=input('Фамилия: ')
                    email=input('Email: ')
                    if not re.match(pattern,email):
                        print('Некорректные данные')
                        time.sleep(1)
                        break
                    age=int(input('Age: '))
                    database.insert('users', columns=['name', 'surname', 'email', 'age'], values=[f'{name}', f'{surname}', f'{email}', f'{age}'])
                elif actions == 2:
                    title=input('Название: ')
                    description=input('Описание: ')
                    database.insert('magazines', columns=['title', 'description', 'date_created'], values=[f'{title}', f'{description}', f'{date.today()}'])
                elif actions == 3:
                    users = (database.select('users'))
                    magazines = (database.select('magazines'))
                    subscriptions = (database.select('subscriptions'))
                    print('Пользователи')
                    for user in users:
                        print(f'{user[0]}) {user[1]} {user[2]}')
                    print('Пользователи')
                    for magazine in magazines:
                        print(f'''{magazine[0]}) {magazine[1]}\n{magazine[2]}''')
                    for subscription in subscriptions:
                        print(f'{subscription[0]}) {subscription[1]} - {subscription[2]}')
                elif actions == 4:
                    break
        else:
            print('Не правильный логин или пароль')
            time.sleep(1)
    elif task == 2:
        break

all_id_users=[]
all_id_magazines=[]

while True:
    users = (database.select('users'))
    for user in users:
        print(f'{user[0]}) {user[1]} {user[2]}')
        all_id_users.append(user[0])
    while True:
        try:
            id_user = int(input('Кто ты?(НАПИШИ ЦИФРУ СЛЕВА ОТ ИМЕНИ!!!): '))
            if id_user not in all_id_users:
                raise ValueError
            break
        except ValueError:
            print('ТЫ ДУРАК?')
    task= int(input('Хочешь подписаться(1) или же отвязаться от рассылки(2): '))

    if task == 1:
        print('Вот все журналы')
        magazines = (database.select('magazines'))
        for magazine in magazines:
            print(f'''{magazine[0]}) {magazine[1]}
{magazine[2]}\n''')
            all_id_magazines.append(magazine[0])
        try:
            id_magazine=int(input('Какой журнал?(НАПИШИ ЦИФРУ СЛЕВА ОТ ЖУРНАЛА!!!): '))
            if id_magazine not in all_id_magazines:
                raise ValueError
        except ValueError:
            print('ТЫ ДУРАК?')
            time.sleep(1)
            break
        database.insert('subscriptions', columns=['id_user', 'id_magazine'], values=[f'{id_user}', f'{id_magazine}'])
    
    elif task == 2:
        all_subscriptions_id=[]
        subscriptions = (database.select('subscriptions', column='id_user', value=id_user))
        for subscription in subscriptions:
            all_subscriptions_id.append(subscription[2])
        magazines = (database.select('magazines'))
        if subscriptions == []:
            print('У вас нету подписок')
            time.sleep(2)
            continue
        print('Вот все журналы')
        for magazine in magazines:
            if magazine[0] in all_subscriptions_id:
                print(f'''{magazine[0]}) {magazine[1]}           
{magazine[2]}\n''')
        id_magazine_del=int(input('Какой журнал?(НАПИШИ ЦИФРУ СЛЕВА ОТ ЖУРНАЛА!!!): '))
        database.delete('subscriptions', id_magazine_del)



