from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.routes import session
from app import login

import psycopg2


class DataBase(object):
    _connection: psycopg2 = None

    @classmethod
    def _to_connect(cls) -> psycopg2:
        try:
            # Подключение к существующей базе данных
            cls._connection = psycopg2.connect(user='admin',
                                               password="admin",
                                               host='localhost',
                                               database="onread")

        except psycopg2.OperationalError as ex:
            print(f'the operational error:\n{ex}')
        except BaseException as ex:
            print(f'other error:\n{ex}')
        else:
            print("connection to PostgreSQL DB successful")
        return cls._connection

    @classmethod
    def execute_query(cls, query: str, params: tuple = None, is_returning: bool = False):
        print(query)
        if cls._connection is None:
            cls._to_connect()
        cls._connection.autocommit = True
        cursor = cls._connection.cursor()
        try:
            if params is None:
                cursor.execute(query)
            else:
                cursor.execute(query, params)
            if is_returning:
                result = cursor.fetchall()
        except psycopg2.OperationalError as ex:
            print(f'{ex}')
        except Exception as ex:
            print(f'{ex}')
        else:
            print("the query is executed")
            if is_returning:
                return result
            else:
                return True
        finally:
            cursor.close()
        return None


class Reader(UserMixin):
    def __init__(self,
                 id: int,
                 login: str,
                 password_hash: str):
        self.id = id
        self.login = login
        self.password_hash = password_hash
        self.role = 'read'

    def __repr__(self):
        return f'U id={self.id} login={self.login}'

    def tuple(self):
        return (self.login,
                self.password_hash)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def add(cls, reader):
        query = '''
        INSERT INTO reader (login, password)
        VALUES {}
        '''.format(reader.tuple())
        return DataBase.execute_query(query)

    @classmethod
    def get_by_id(cls, id: int):
        query = '''
                    SELECT * 
                    FROM reader
                    WHERE id = {}
                    '''.format(id)
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        params = result[0]
        return Reader(*params)

    @classmethod
    def get_by_login(cls, login):
        query = '''
                   SELECT * 
                   FROM reader
                   WHERE login = '{}'
                   '''.format(login)
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        params = result[0]
        return Reader(*params)


class Author(UserMixin):
    def __init__(self,
                 id: int,
                 login: str,
                 password_hash: str):
        self.id = id
        self.login = login
        self.password_hash = password_hash
        self.role = 'auth'

    def __repr__(self):
        return f'U id={self.id} login={self.login}'

    def tuple(self):
        return (self.login,
                self.password_hash)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def add(cls, author):
        query = '''
        INSERT INTO author (login, password)
        VALUES {}
        '''.format(author.tuple())
        return DataBase.execute_query(query)

    @classmethod
    def get_by_id(cls, id: int):
        query = '''
                    SELECT * 
                    FROM author
                    WHERE id = {}
                    '''.format(id)
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        params = result[0]
        return Author(*params)

    @classmethod
    def get_by_login(cls, login):
        query = '''
                   SELECT * 
                   FROM author
                   WHERE login = '{}'
                   '''.format(login)
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        params = result[0]
        return Author(*params)


class Book(object):
    def __init__(self,
                 id: int,
                 name: str,
                 auth_id: int,
                 description: str):
        self.id = id
        self.name = name
        self.auth_id = auth_id
        self.description = description
        

    def tuple(self):
        return (self.name,
                self.auth_id,
                self.description)

    @classmethod
    def get_by_id(cls, id):
        query = '''
        SELECT * FROM book
        WHERE id = {}'''.format(id)
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        params = result[0]
        return Book(* params)

    @classmethod
    def get_id_by_name(cls, name):
        query = '''
        SELECT id FROM book
        WHERE name = '{}'
        '''.format(name)
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        params = result[0]
        print(params)
        return Book(* params)

    @classmethod
    def get_all_books(cls):
        query = '''
        SELECT * FROM book'''
        result = DataBase.execute_query(query, is_returning=True)
        print(result)
        if result is None or len(result) == 0:
            return None
        result = list(map(lambda x: Book(*x), result))
        return result

    @classmethod
    def get_books_by_auth(cls, id):
        query = '''
        SELECT * FROM book WHERE auth_id = {}'''.format(id)
        result = DataBase.execute_query(query, is_returning=True)
        print(result)
        if result is None or len(result) == 0:
            return None
        result = list(map(lambda x: Book(*x), result))
        return result

    @classmethod
    def get_auth_by_books(cls, id):
        query = '''
        SELECT auth_id 
        FROM book WHERE id = {}'''.format(id)
        result = DataBase.execute_query(query, is_returning=True)
        print(result)
        if result is None or len(result) == 0:
            return None
        params = result[0]
        print(params)
        return Book(* params)

    @classmethod
    def add(cls, book):
        query = '''
        INSERT INTO book (name, description, auth_id)
        VALUES {}'''.format(book.tuple())
        return DataBase.execute_query(query)


class Reader_book(object):
    '''описывает связь многие ко многим для таблиц
    reader и book - таблица bor'''

    # Добавление экземпляра отношения
    @classmethod
    def add_read_book(cls, reader_id, book_id):
        query = '''
        INSERT INTO bor (reader_id, book_id)
        VALUES ({}, {})'''.format(reader_id, book_id)
        return DataBase.execute_query(query)

    # Удаление экземпляра отношения
    @classmethod
    def delete(cls, reader_id, book_id):
        query = '''
        DELETE FROM bor
        WHERE reader_id = {} and book_id = {}
        '''.format(reader_id, book_id)
        return DataBase.execute_query(query)

    # Получение списка книг, которые пользователь читает
    @classmethod
    def get_books_by_reader_id(cls, reader_id):
        query = '''
        SELECT * FROM book INNER JOIN bor ON book.id = bor.book_id
        WHERE bor.reader_id = {}'''.format(reader_id)
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        books = []
        for item in result:
            params = item[:len(item)-2:]
            book = Book(*params)
            books.append(book)
        return books


class Chapter(object):
    def __init__(self,
                 id: int,
                 num_ch: int,
                 content: str, 
                 book_id: int):
        self.id = id
        self.num_ch = num_ch
        self.content = content
        self.book_id = book_id

    def tuple(self):
        return (self.num_ch,
                self.content,
                self.book_id)

    @classmethod
    def get_by_id(cls, id):
        query = '''
        SELECT * FROM chapter
        WHERE id = {}'''.format(id)
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        params = result[0]
        return Chapter(* params)

    @classmethod
    def get_con_by_id(cls, id):
        query = '''
        SELECT content FROM chapter
        WHERE id = {}'''.format(id)
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        return result[0][0]
       

    @classmethod
    def get_all_by_book_id(cls, book_id):
        query = '''
        SELECT * 
        FROM chapter
        WHERE book_id = {}
        '''.format(book_id)
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        result = list(map(lambda x: Chapter(*x), result))
        return result

    @classmethod
    def add(cls, chapter):
        query = '''
        INSERT INTO chapter (num_ch, content, book_id)
        VALUES {}
        RETURNING id
        '''.format(chapter.tuple())
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        return result[0][0]


class Bookmark(object):

    def __init__(self,
                 id: int,
                 read_id: int,
                 book_id: int,
                 ch_id: int):
        self.id = id
        self.read_id = read_id
        self.book_id = book_id
        self.ch_id = ch_id

    def tuple(self):
        return (self.read_id,
                self.book_id,
                self.ch_id)

    @classmethod
    def add_bookmark(cls, bookmark):
        query = '''
        INSERT INTO bookmark (reader_id, book_id, ch_id)
        VALUES {}
        RETURNING id
        '''.format(bookmark.tuple())
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        return result[0][0]

        
    @classmethod
    def get_by_id(cls, read_id):
        query = '''
        SELECT * FROM bookmark
        WHERE read_id = {}'''.format(read_id)
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        params = result[0]
        return Bookmark(* params)
    
    @classmethod
    def get_mark_by_readbook_id(cls, read_id, book_id):
        query = '''
        SELECT ch_id
        FROM bookmark
        WHERE id=(SELECT MAX(id) 
        FROM bookmark) AND reader_id = {} AND book_id = {}
        '''.format(read_id, book_id)
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        return result[0][0]      


    @classmethod
    def get_all():
        query = '''
        SELECT *
        FROM bookmark'''
        result = DataBase.execute_query(query, is_returning=True)
        print(result)
        if result is None or len(result) == 0:
            return None
        result = list(map(lambda x: Bookmark(*x), result))
        return result

    @classmethod
    def get_all_by_reader_id(cls, read_id):
        query = '''
        SELECT *
        FROM bookmark
        WHERE reader_id = {}
        '''.format(read_id)
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        result = list(map(lambda x: Bookmark(*x), result))
        return result

    @classmethod
    def get_by_chapter_id(cls, chapter_id, read_id):
        query = '''
        SELECT ch_id
        FROM bookmark
        WHERE ch_id <= {} AND reader_id = {}
        '''.format(chapter_id, read_id)
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        result = list(map(lambda x: Bookmark(*x), result))
        return result

    @classmethod
    def delete_by_chapter_id(cls, chapter_id, read_id):
        query = '''
        DELETE
        FROM bookmark
        WHERE ch_id <= {} AND reader_id = {}
        '''.format(chapter_id, read_id)
        return DataBase.execute_query(query)




# метод загрузки клиента
@login.user_loader
def load_user(id: str):
    if session['role'] == 'auth':
        user = Author.get_by_id(int(id))
    elif session['role'] == 'read':
        user = Reader.get_by_id(int(id))
    print(f'user loaded, user = {user}')
    return user