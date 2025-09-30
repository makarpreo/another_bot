import mysql.connector
from mysql.connector import Error
from config import *


class Table:
    """Родительский класс для работы с таблицами БД"""

    def __init__(self, table_name):
        self.table_name = table_name

    @staticmethod
    def get_db_connection():
        """Создает и возвращает соединение с MySQL"""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            return conn
        except Error as e:
            print(f"Ошибка подключения к MySQL: {e}")
            return None

    @staticmethod
    def print_row(row):
        """Форматированный вывод строки"""
        print('| ' + ' | '.join(list(map(str, row))) + ' |')

    def print_rows(self):
        """Выводит все строки таблицы"""
        try:
            conn = self.get_db_connection()
            if conn and conn.is_connected():
                cursor = conn.cursor()
                query = f'SELECT * FROM {self.table_name};'
                cursor.execute(query)
                results = cursor.fetchall()

                if results:
                    for row in results:
                        self.print_row(row)
                else:
                    print(f"Таблица {self.table_name} пуста")
        except Exception as ex:
            print(f'Ошибка при выводе данных: {ex}')
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()


class Car(Table):
    """Класс для работы с таблицей cars"""

    def __init__(self):
        super().__init__('cars')

    def add_car(self, car_name):
        """Добавляет новую машину"""
        conn = self.get_db_connection()
        try:
            if conn and conn.is_connected():
                cursor = conn.cursor()
                # query = "SELECT COUNT(*) FROM cars WHERE car_name = %s"
                # cursor.execute(query, (car_name,))
                # result = cursor.fetchone()
                # if result[0] > 0:
                #     return f'Ошибка при добавлении машины: машина с таким названием уже существует'
                query = 'INSERT INTO cars (car_name, car_status) VALUES (%s, "active");'
                cursor.execute(query, (car_name,))
                conn.commit()
                return f"Машина '{car_name}' успешно добавлена"
        except Exception as ex:
            return f'Ошибка при добавлении машины: {ex}'
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    def edit_last_note(self, username, car_id, text):
        # select * from notes where car_id=15 AND user_id='makarpreo' order by 1 desc LIMIT 1;
        try:
            conn = self.get_db_connection()
            if conn and conn.is_connected():
                cursor = conn.cursor()
                print(car_id, username)
                query = f'select note_id from notes where car_id={car_id} AND user_id="{username}" order by 1 desc LIMIT 1;'
                print(query)
                cursor.execute(query)
                note_id = cursor.fetchone()
                query = f'UPDATE notes SET note="{text}" WHERE note_id={note_id[0]};'
                print(query)
                cursor.execute(query)
                conn.commit()
                # print(results)
                # if results:
                #     if conn and conn.is_connected():
                #         cursor.close()
                #         conn.close()
                #     return results
        except Exception as ex:
            return f'Ошибка при удалении машины: {ex}'
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    def show_active_list(self):
        try:
            conn = self.get_db_connection()
            if conn and conn.is_connected():
                cursor = conn.cursor()
                query = 'SELECT * FROM cars WHERE car_status="active";'
                cursor.execute(query)
                results = cursor.fetchall()
                print(results)
                if results:
                    if conn and conn.is_connected():
                        cursor.close()
                        conn.close()
                    return results
        except Exception as ex:
            return f'Ошибка при удалении машины: {ex}'
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    def show_archive(self):
        try:
            conn = self.get_db_connection()
            if conn and conn.is_connected():
                cursor = conn.cursor()
                query = 'SELECT car_name, car_id, archive_date FROM archive;'
                cursor.execute(query)
                results = cursor.fetchall()
                print(results)
                if results:
                    if conn and conn.is_connected():
                        cursor.close()
                        conn.close()
                    return results
        except Exception as ex:
            return f'Ошибка: {ex}'
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    def delete_car_by_id(self, car_id):
        """Удаляет машину по ID"""
        try:
            conn = self.get_db_connection()
            if conn and conn.is_connected():
                cursor = conn.cursor()
                query = 'DELETE FROM cars WHERE car_id = %s;'
                cursor.execute(query, (car_id,))
                conn.commit()
                return f"Машина с ID {car_id} удалена"
        except Exception as ex:
            return f'Ошибка при удалении машины: {ex}'
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    def delete_car_by_name(self, car_name):
        """Удаляет машину по ID"""
        try:
            conn = self.get_db_connection()
            if conn and conn.is_connected():
                cursor = conn.cursor()
                query = 'DELETE FROM cars WHERE car_name = %s;'
                cursor.execute(query, (car_name,))
                conn.commit()
                return f"Машина с ID {car_name} удалена"
        except Exception as ex:
            return f'Ошибка при удалении машины: {ex}'
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    def get_car_name(self, car_id):
        try:
            conn = self.get_db_connection()
            if conn and conn.is_connected():
                cursor = conn.cursor()
                query = f'SELECT car_name FROM cars WHERE car_id={car_id};'
                cursor.execute(query)
                name = cursor.fetchone()
                if name:
                    return name[0]
                print(123123123)
                return ''
        except Exception as ex:
            return f'Ошибка: {ex}'
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    # def return_id(self, car_name):
    #     try:
    #         conn = self.get_db_connection()
    #         if conn.is_connected():
    #             cursor = conn.cursor()
    #             query = select car_id from cars where car_name="{car_name}" AND car_status="active";'
    #             cursor.execute(query)
    #             result = cursor.fetchall()
    #             if result:
    #                 return result[0][0]
    #             else:
    #                 return 'Нет активных машин с таким названием'
    #     except Exception as ex:
    #         print(f'была ошибка: {ex}')
    #     finally:
    #         conn.close()

    def print_note(self, car_id):
        """Добавляет новую заметку"""
        try:
            conn = self.get_db_connection()
            if conn and conn.is_connected():
                cursor = conn.cursor()
                query = f'select note, user_id from notes join cars using(car_id) where car_id={car_id};'
                cursor.execute(query)
                results = cursor.fetchall()
                print(results)
                if results:
                    if conn and conn.is_connected():
                        cursor.close()
                        conn.close()
                    return results
        except Exception as ex:
            print(f'Ошибка при добавлении заметки: {ex}')
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    def change_car_status(self, car_status, car_id):
        try:
            conn = self.get_db_connection()
            if conn and conn.is_connected():
                cursor = conn.cursor()
                query = f'UPDATE cars SET car_status = "{car_status}" WHERE car_id = {car_id};'
                cursor.execute(query)
                conn.commit()
                return f'статус car_id:{car_id} изменен на: {car_status}'
        except Exception as ex:
            print(f'Ошибка при изменении статуса: {ex}')
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    def move_car_to_archive(self, car_id):
        try:
            conn = self.get_db_connection()
            if conn and conn.is_connected():
                cursor = conn.cursor()
                query = f'UPDATE cars SET car_status="not active" WHERE car_id = {car_id};'
                cursor.execute(query)
                conn.commit()
                query = f'select car_name from cars where car_id={car_id};'
                cursor.execute(query)
                car_name = cursor.fetchone()
                query = f'INSERT INTO archive (car_id, archive_date, car_name) VALUES ({car_id}, NOW(), "{car_name[0]}")'
                cursor.execute(query)
                conn.commit()
                return f'машина ID:{car_id} перемещена в архив'
        except Exception as ex:
            print(f'Ошибка при изменении статуса: {ex}')
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()


    def do_car_active_again(self, car_id):
        try:
            conn = self.get_db_connection()
            if conn and conn.is_connected():
                cursor = conn.cursor()
                query = f'UPDATE cars SET car_status = "active" WHERE car_id = {car_id};'
                cursor.execute(query)
                conn.commit()
                return f'статус car_id:{car_id} изменен на: active'
        except Exception as ex:
            print(f'Ошибка при изменении статуса: {ex}')
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()


class Note(Table):
    """Класс для работы с таблицей notes"""

    def __init__(self):
        super().__init__('notes')

    def get_notes_with_ids(self, car_id):
        """Возвращает список записей с ID: [(id, note_text, username), ...]"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT note_id, note, user_id FROM notes WHERE car_id = %s ORDER BY note_id",
                (car_id,)
            )
            result = cursor.fetchall()
            return result
        except Error as e:
            return f"Ошибка при получении записей: {e}"
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def update_note_text(self, note_id, new_text):
        """Обновляет текст записи по ID"""
        try:
            conn = self.get_db_connection()

            cursor = conn.cursor()
            cursor.execute(
                "UPDATE notes SET note = %s WHERE note_id = %s",
                (new_text, note_id)
            )
            conn.commit()
            return f"Запись #{note_id} успешно обновлена"
        except Error as e:
            return f"Ошибка при обновлении записи: {e}"
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def delete_note_by_id(self, note_id):
        """Удаляет запись по ID"""
        try:
            conn = self.get_db_connection()

            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes WHERE note_id = %s", (note_id,))
            conn.commit()
            return f"Запись #{note_id} успешно удалена"
        except Error as e:
            return f"Ошибка при удалении записи: {e}"
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def add_note(self, note_text, car_id, user_id):
        """Добавляет новую заметку"""
        try:
            conn = self.get_db_connection()
            if conn and conn.is_connected():
                cursor = conn.cursor()
                query = 'INSERT INTO notes (note, car_id, user_id) VALUES (%s, %s, %s);'
                cursor.execute(query, (note_text, car_id, user_id))
                conn.commit()
                if conn and conn.is_connected():
                    cursor.close()
                    conn.close()
                return f"Заметка для машины с ID {car_id} добавлена"
        except Exception as ex:
            print(f'Ошибка при добавлении заметки: {ex}')
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    def print_notes_with_cars(self):
        """Выводит заметки с именами машин"""
        try:
            conn = self.get_db_connection()
            if conn and conn.is_connected():
                cursor = conn.cursor()
                query = '''
                SELECT notes.note_id, notes.note, cars.car_name 
                FROM notes 
                JOIN cars ON notes.car_id = cars.car_id;
                '''
                cursor.execute(query)
                results = cursor.fetchall()
                if results:
                    if conn and conn.is_connected():
                        cursor.close()
                        conn.close()
                    return results
                    # print("\nЗаметки с именами машин:")
                    # for row in results:
                    #     self.print_row(row)
                else:
                    print("Нет заметок для отображения")
        except Exception as ex:
            print(f'Ошибка при выводе заметок: {ex}')
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()


# Пример использования
if __name__ == '__main__':
    car = Car()
    note = Note()
    # print(car.edit_last_note(car_id=15, username='makarpreo', text='new text'))
    # cars.print_note(7)
    # cars.show_active_list()
    print('success')
