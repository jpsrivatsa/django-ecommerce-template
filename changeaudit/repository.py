from django.db import DatabaseError
from .middleware import RequestStore


class Repository:
    def __init__(self, connection):
        self.connection = connection
        self.request_header = RequestStore.get_request_headers()
        self.user = RequestStore.get_requested_user()
            
    def fetch(self, query, query_params):
        with self.connection.cursor() as cursor:
            cursor.execute(query, query_params)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    def exists(self, table, id):
        check_query = f"SELECT COUNT(*) FROM products_{table} WHERE {table}_id = %s"
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(check_query, [id])
                return cursor.fetchone()[0] > 0
        except DatabaseError as db_error:
            return {f"Database Error Occurred: {str(db_error)}"}
        except Exception as e:
            return {f"Unexpected Error Occured: {str(e)}"}

    def insert(self, table, columns, values):
        try:
            placeholders = self.get_placeholders(columns)
            insert_query = f"INSERT INTO products_{table} ({columns}, created_by_id,created_at) VALUES ({placeholders}, %s ,NOW())"
            with self.connection.cursor() as cursor:
                cursor.execute(insert_query, values + [self.user])
            self.__db__post(table,columns,values)
            return True
        except DatabaseError as db_error:
            return {'error': f"Database Error Occurred: {str(db_error)}"}
        except Exception as e:
            print(e)
            return {'error': f"Database Error Occurred: {str(db_error)}"}

    def update(self, table, columns, values, id):
        try:
            update_query = f"UPDATE products_{table} SET {columns}, changed_by_id = %s, changed_at = NOW() WHERE {table}_id = %s"
            values.append(self.user)
            values.append(id)
            with self.connection.cursor() as cursor:
                print(update_query, values)
                cursor.execute(update_query, values)
                return True  
            
        except DatabaseError as db_error:
            return {'error': f"Database Error Occurred: {str(db_error)}"}
        except Exception as e:
            print(e)
            return {'error': f"Database Error Occurred: {str(db_error)}"}    
    
    def get_placeholders(self,columns):
        return ', '.join(['%s'] * len(columns.split(',')))
    
    def __db__post(self,table,columns,values):
        return True
        