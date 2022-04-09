import psycopg2

connection = psycopg2.connect(
    user="postgres",
    password="1u2u3u4u5u6u7u8u9u",
    host="127.0.0.1",
    port="5432",
    dbname="online_store")

cursor = connection.cursor()


def help1():
    print('Допустимые команды:')
    print('enter - Войти')
    print('add - Зарегистрироваться')
    print('exit - выход\n')

def help2():
    print('Допустимые команды:')
    print('product - Вывести список всех товаров и их ценой')
    print('buy - Покупка товара')
    print('count - проверить баланс')
    print('upp - Пополнить баланс')
    print('look - Просмотреть свои покупки')
    print('end - Выйти из профиля\n')

# Вывести все продукты
def PRODUCT(word = 0):
    if word == 0:
        cursor.execute('SELECT * FROM Product')
    else:
        cursor.execute('SELECT * FROM Product WHERE name ILIKE %s', (word,))

    p_list = cursor.fetchall()
    print('Товар                     Описание                        Цена')
    for prod in p_list:
        print(f'{prod[1]:15}      {prod[2]:20}       {prod[3]:15}')
    print('\n')

# Покупка продуктов
def BUY(id, cart_id):
    name = input('Введите название товара, для добавления его в корзину: ')

    cursor.execute('SELECT COUNT(*) FROM Product '
                   'WHERE name = %s', (name,))
    success = cursor.fetchone()

    if success[0] == 0:
        print('Такого товара нет в каталоге')
        return

    cursor.execute('SELECT money FROM customer '
                   'WHERE id = %s', (id,))
    money = cursor.fetchone()[0]

    cursor.execute('SELECT price FROM product'
                   ' WHERE name = %s', (name,))

    price = cursor.fetchone()[0]

    if int(money) < int(price):
        print('У вас недостаточно средств для покупки')
        return

    money = int(money) - int(price)

    cursor.execute('UPDATE customer SET money = %s'
                   ' WHERE id = %s', (money, id,))
    connection.commit()


    cursor.execute('SELECT id FROM Product'
                   ' WHERE name = %s', (name,))
    id_product = cursor.fetchone()[0]

    cursor.execute('INSERT INTO cart_product VALUES(%s, %s)', (cart_id, id_product,))
    connection.commit()

    print('Покупка прошла успешно')

# Вывести кол-во стредств
def COUNT(id):
    cursor.execute('SELECT money FROM customer WHERE id = %s', (id,))
    money = cursor.fetchone()[0]
    print(f'Ваш баланс составляет {money}')

# Внести денги
def UPP(id):
    cursor.execute('SELECT money FROM customer WHERE id = %s', (id,))
    money = int(cursor.fetchone()[0])
    upper = int(input('Введите сумму для пополнения счета: '))
    money = money + upper

    cursor.execute('UPDATE customer SET money = %s WHERE id = %s', (money, id))
    connection.commit()
    COUNT(id)

# Просмотреть список покупок
def LOOK(id):
    cursor.execute('SELECT COUNT(product_id) FROM cart join cart_product ON cart.id = cart_product.cart_id WHERE customer_id = %s', (id,))
    success = cursor.fetchone()[0]
    if success == 0:
        print('Вы не совершали покупок')

    cursor.execute('SELECT product_id FROM cart join cart_product ON cart.id = cart_product.cart_id WHERE customer_id = %s', (id,))
    id_products = cursor.fetchall()

    for id_product in id_products:
        cursor.execute('SELECT name FROM product WHERE id = %s', (id_product[0],))
        print(cursor.fetchone()[0])
    print('\n')

# Вход
def ENTER(id, login):
    print("\nДобро пожаловать, ", login)
    print('Для вывода доступных команд введите help\n')
    cursor.execute('INSERT INTO cart VALUES (default, %s)', (id,))
    connection.commit()

    cursor.execute('SELECT cart.id FROM cart'
                   ' ORDER BY cart.id DESC'
                   ' LIMIT 1')
    cart_id = cursor.fetchone()[0]

    while(1):
        command = input('Введите каоманду: ')

        if command == 'product':
            PRODUCT()

        if command == 'find':
            name = input('Введите название товара: ')
            name = '%'+name+'%'
            PRODUCT(name)

        if command == 'buy':
            BUY(id, cart_id)

        if command == 'count':
            COUNT(id)

        if command == 'upp':
            UPP(id)

        if command == 'look':
            LOOK(id)

        if command == 'help':
            help2()

        if command == 'end':
            print('Вы вышли. Войдите или зарегистрируйтесь, чтобы продолжить')
            break
    cursor.execute('SELECT COUNT(*) FROM cart_product '
                   'WHERE cart_id = %s', (cart_id,))
    success = cursor.fetchone()[0]
    if success == 0:
        cursor.execute('DELETE FROM cart WHERE id = %s', (cart_id,))
        connection.commit()
    return


# Регистрация
def ADD():
    while(1):
        print('Для выхода введите в любом поле exit и завершите процесс регистрации')
        login = input('введите ваш логин: ')
        password = input('Введите ваш пароль: ')
        phone = input('Введите ваш телефон: ')
        email = input('Введите вашу почту: ')
        money = input('Введите вашу сумму денег (не обязательно): ')

        if login == 'exit' or password == 'exit' or phone == 'exit' or email == 'exit' or money == 'exit':
            return

        cursor.execute("SELECT COUNT(Customer.id) FROM Customer"
                       " WHERE Customer.login = %s", (login,))
        success = cursor.fetchone()
        if success[0] != 0:
            print('Пользователь с таким логином уже существует')
            continue

        cursor.execute('SELECT COUNT(Customer.phone) FROM Customer'
                       ' WHERE Customer.phone = %s', (phone,))
        success = cursor.fetchone()
        if success[0] != 0:
            print('Пользователь с таким телефоном уже существует')
            continue

        cursor.execute('SELECT COUNT(Customer.email) FROM Customer'
                       ' WHERE Customer.email = %s', (email,))
        success = cursor.fetchone()
        if success[0] != 0:
            print('Пользователь с такой почтой уже существует')
            continue
        cursor.execute("INSERT INTO Customer VALUES (default, (%s), (%s), (%s), (%s), (%s))", (login, password, phone, email, money,))
        connection.commit()
        print('Вы успешно зарегистрировались')

        cursor.execute('SELECT Customer.id FROM Customer '
                       'WHERE Customer.login = %s', (login,))
        id = cursor.fetchone()
        return ENTER(id[0], login)

print('Для вывода доступных команд введите help\n')


# Начальное меню входа\регистрации
while(1):
    command = input('Введите команду: ')

    if command == 'enter':
        login = input('Введите логин: ')
        password = input('Введите пароль: ')
        cursor.execute("SELECT COUNT(Customer.id) FROM Customer"
                       " WHERE Customer.login = %s and Customer.password = %s", (login, password))
        success = cursor.fetchone()
        if(success[0]):
            cursor.execute("SELECT Customer.id FROM Customer"
                           " WHERE Customer.login = %s and Customer.password = %s", (login, password))
            id = cursor.fetchone()[0]
            ENTER(id, login)
        else:
            print('Вы ввели неверный логин и/или пароль. Попробуйте снова или зарегистрируйтесь')

    if command == 'add':
        ADD()

    if command == 'help':
        help1()
        continue

    if command == 'exit':
        break

print('Всего доброго')
cursor.close()
connection.close()
