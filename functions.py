from telebot import types
import sqlite3
import telebot
import os
import settings
import random
import requests
import json
import datetime


class Catalog:
    def __init__(self, name):
        self.name = name


class Product:
    def __init__(self, user_id):
        self.user_id = user_id
        self.product = None
        self.section = None
        self.price = None
        self.amount = None
        self.amount_MAX = None
        self.code = None


class AddProduct:
    def __init__(self, section):
        self.section = section
        self.product = None
        self.price = None
        self.info = None


class DownloadProduct:
    def __init__(self, name_section):
        self.name_section = name_section
        self.name_product = None


class GiveBalance:
    def __init__(self, login):
        self.login = login
        self.balance = None
        self.code = None


class Admin_sending_messages:
    def __init__(self, user_id):
        self.user_id = user_id
        self.text = None


# Menu catalog
def menu_catalog():
    conn = sqlite3.connect("base_ts.sqlite")
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM catalog')
    row = cursor.fetchall()

    menu = types.InlineKeyboardMarkup(row_width=1)

    for i in row:
        menu.add(types.InlineKeyboardButton(text=f'{i[0]}', callback_data=f'{i[1]}'))

    menu.add(types.InlineKeyboardButton(text='Назад', callback_data='exit_to_menu'))

    cursor.close()
    conn.close()

    return menu


# Menu section
def menu_section(name_section):
    conn = sqlite3.connect("base_ts.sqlite")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM '{name_section}' ")
    row = cursor.fetchall()

    menu = types.InlineKeyboardMarkup(row_width=1)

    for i in row:
        menu.add(types.InlineKeyboardButton(text=f'{i[0]}', callback_data=f'{i[2]}'))

    menu.add(types.InlineKeyboardButton(text='Назад', callback_data='exit_to_menu'))

    cursor.close()
    conn.close()

    return menu


# Menu product
def menu_product(product, dict):
    conn = sqlite3.connect("base_ts.sqlite")
    cursor = conn.cursor()

    row = cursor.execute(f'SELECT * FROM section WHERE code = "{product}"').fetchone()
    section = row[1]
    info = row[3]

    amount = len(cursor.execute(f'SELECT * FROM "{product}"').fetchall())

    cursor.execute(f'SELECT * FROM "{section}" WHERE code = "{product}"')
    row = cursor.fetchone()

    dict.section = section
    dict.product = product
    dict.amount_MAX = amount
    dict.price = row[1]

    text = settings.text_purchase.format(
        name=row[0],
        info=info,
        price=row[1],
        amount=amount
    )

    return text, dict

#   Admin menu - add_to_section_to_catalog
def add_section_to_catalog(name_section):
    # Connection
    conn = sqlite3.connect("base_ts.sqlite")
    cursor = conn.cursor()
    code = random.randint(11111, 99999)
    # Add
    cursor.execute(f"INSERT INTO catalog VALUES ('{name_section}', '{code}')")
    conn.commit()

    # Create table section
    conn.execute(f"CREATE TABLE '{code}' (list text, price text, code text)")

    # Close connection
    cursor.close()
    conn.close()


# Admin menu - del_section_to_catalog
def del_section_to_catalog(name_section):
    # Connection
    conn = sqlite3.connect("base_ts.sqlite")
    cursor = conn.cursor()

    # Del
    cursor.execute(f"DELETE FROM catalog WHERE code = '{name_section}'")
    conn.commit()

    cursor.execute(f"DROP TABLE '{name_section}'")

    row = cursor.execute(f'SELECT * FROM section WHERE section = "{name_section}"').fetchall()

    for i in range(len(row)):
        cursor.execute(f'DROP TABLE "{row[i][2]}"')

        cursor.execute(f'DELETE FROM section WHERE code = "{row[i][2]}"')
        conn.commit()

    # Close connection
    cursor.close()
    conn.close()


# Admin menu - add_product_to_section
def add_product_to_section(name_product, price, name_section, info):
    # Connection
    conn = sqlite3.connect("base_ts.sqlite")
    cursor = conn.cursor()

    code = random.randint(11111, 99999)

    cursor.execute(f"INSERT INTO '{name_section}' VALUES ('{name_product}', '{price}', '{code}')")
    conn.commit()

    cursor.execute(f"INSERT INTO 'section' VALUES ('{name_product}', '{name_section}', '{code}', '{info}')")
    conn.commit()

    # Create table product
    cursor.execute(f"CREATE TABLE '{code}' (list text, code text)")

    # Close connection
    cursor.close()
    conn.close()


# Admin menu - del_product_to_section
def del_product_to_section(name_product, section):
    # Connection
    conn = sqlite3.connect("base_ts.sqlite")
    cursor = conn.cursor()

    # del
    product = cursor.execute(f'SELECT * FROM "{section}" WHERE list = "{name_product}"').fetchone()

    cursor.execute(f"DELETE FROM '{section}' WHERE list = '{name_product}'")
    conn.commit()

    cursor.execute(f"DROP TABLE '{product[2]}'")

    # Close connection
    cursor.close()
    conn.close()


def download_product(name_file, product):
    conn = sqlite3.connect("base_ts.sqlite")
    cursor = conn.cursor()

    file = open(name_file, 'r')

    for i in file:
        cursor.execute(f"INSERT INTO '{product}' VALUES ('{i}', '{random.randint(111111, 999999)}')")

    conn.commit()

    file.close()
    os.remove(name_file)

    cursor.close()
    conn.close()


def basket(user_id):
    conn = sqlite3.connect('base_ts.sqlite')
    cursor = conn.cursor()
    row = cursor.execute(f'SELECT * FROM purchase_information WHERE user_id = "{user_id}"').fetchall()

    text = ''

    for i in row:
        text = text + '💠 ' + i[2][:10:] + ' | ' + i[1] + '\n\n'

    return text


def profile(user_id):
    msg = f'📜 Профиль:\n\n' \
          f'ID - {user_id}'
    return msg


def first_join(user_id, name):
    conn = sqlite3.connect('base_ts.sqlite')
    cursor = conn.cursor()
    row = cursor.execute(f'SELECT * FROM users WHERE user_id = "{user_id}"').fetchall()

    if len(row) == 0:
        cursor.execute(f'INSERT INTO users VALUES ("{user_id}", "{name}", "{datetime.datetime.now()}", "0", "0", "0")')
        conn.commit()


def admin_info():
    conn = sqlite3.connect('base_ts.sqlite')
    cursor = conn.cursor()
    row = cursor.execute(f'SELECT * FROM users').fetchone()

    current_time = str(datetime.datetime.now())

    amount_user_all = 0
    amount_user_day = 0
    amount_user_hour = 0

    while row is not None:
        amount_user_all += 1
        if row[2][:-15:] == current_time[:-15:]:
            amount_user_day += 1
        if row[2][:-13:] == current_time[:-13:]:
            amount_user_hour += 1

        row = cursor.fetchone()

    msg = '❕ Информаци:\n\n' \
          f'❕ За все время - {amount_user_all}\n' \
          f'❕ За день - {amount_user_day}\n' \
          f'❕ За час - {amount_user_hour}'

    return msg

def check_payment(user_id):
    conn = sqlite3.connect('base_ts.sqlite')
    cursor = conn.cursor()
    try:
        session = requests.Session()
        session.headers['authorization'] = 'Bearer ' + settings.QIWI_TOKEN
        parameters = {'rows': '5'}
        h = session.get(
            'https://edge.qiwi.com/payment-history/v1/persons/{}/payments'.format(settings.QIWI_NUMBER),
            params=parameters)
        req = json.loads(h.text)
        result = cursor.execute(f'SELECT * FROM check_payment WHERE user_id = {user_id}').fetchone()
        comment = result[1]

        for i in range(len(req['data'])):
            if comment in str(req['data'][i]['comment']):
                balance = cursor.execute(f'SELECT * FROM users WHERE user_id = "{user_id}"').fetchone()

                balance = float(balance[5]) + float(req["data"][i]["sum"]["amount"])

                cursor.execute(f'UPDATE users SET balance = {balance} WHERE user_id = "{user_id}"')
                conn.commit()

                cursor.execute(f'DELETE FROM check_payment WHERE user_id = "{user_id}"')
                conn.commit()

                return 1, req["data"][i]["sum"]["amount"]
    except Exception as e:
        print(e)

    return 0, 0

def replenish_balance(user_id):
    conn = sqlite3.connect('base_ts.sqlite')
    cursor = conn.cursor()

    code = random.randint(111111, 999999)

    cursor.execute(f'INSERT INTO check_payment VALUES ("{user_id}", "{code}", "0")')
    conn.commit()

    msg = settings.replenish_balance.format(
        number=settings.QIWI_NUMBER,
        code=code,
    )

    return msg


def cancel_payment(user_id):
    conn = sqlite3.connect('base_ts.sqlite')
    cursor = conn.cursor()

    cursor.execute(f'DELETE FROM check_payment WHERE user_id = "{user_id}"')
    conn.commit()

def profile(user_id):
    conn = sqlite3.connect('base_ts.sqlite')
    cursor = conn.cursor()

    row = cursor.execute(f'SELECT * FROM users WHERE user_id = "{user_id}"').fetchone()

    return row


def buy(dict):
    conn = sqlite3.connect('base_ts.sqlite')
    cursor = conn.cursor()

    data = str(datetime.datetime.now())
    list = ''
    cursor.execute(f'SELECT * FROM "{dict.product}"')
    row = cursor.fetchmany(int(dict.amount))

    for i in range(int(dict.amount)):
        list = list + f'💠 {data[:19]} | {row[i][0]}\n'


        cursor.execute(f'INSERT INTO purchase_information VALUES ("{dict.user_id}", "{row[i][0]}", "{data}")')
        conn.commit()

        cursor.execute(f'DELETE FROM "{dict.product}" WHERE code = "{row[i][1]}"')
        conn.commit()


    balance = cursor.execute(f'SELECT * FROM users WHERE user_id = "{dict.user_id}"').fetchone()
    balance = float(balance[5]) - (float(dict.price) * float(dict.amount))
    cursor.execute(f'UPDATE users SET balance = "{balance}" WHERE user_id = "{dict.user_id}"')
    conn.commit()

    return list

def give_balance(dict):
    conn = sqlite3.connect('base_ts.sqlite')
    cursor = conn.cursor()

    cursor.execute(f'UPDATE users SET balance = "{dict.balance}" WHERE name = "{dict.login}"')
    conn.commit()

def check_balance(user_id, price):
    conn = sqlite3.connect('base_ts.sqlite')
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM users WHERE user_id = "{user_id}"')
    row = cursor.fetchone()

    if float(row[5]) >= float(price):
        return 1
    else:
        return 0


def list_sections():
    conn = sqlite3.connect("base_ts.sqlite")
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM catalog')
    row = cursor.fetchall()

    sections = []

    for i in row:
        sections.append(i[1])

    return sections


def list_product():
    conn = sqlite3.connect("base_ts.sqlite")
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM section')
    row = cursor.fetchall()

    list_product = []

    for i in row:
        list_product.append(i[2])

    return list_product