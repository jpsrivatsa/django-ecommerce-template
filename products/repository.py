from django.db import DatabaseError
from .middleware import RequestStore
import logging
from .messages import MessageTemplates
logger = logging.getLogger(__name__)

class Repository:
    def __init__(self, connection):
        self.connection = connection
        self.user = RequestStore.get_requested_user()

    def fetch(self, query, params=None):
        """
        Fetch rows from the database and return a list of dictionaries.
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
        except DatabaseError as db_error:
            logger.error(MessageTemplates.get_message("DATABASE_ERROR",error=str(db_error)))
            raise
        except Exception as e:
            logger.error(MessageTemplates.get_message("Unexpected_ERROR",error=str(e)))
            raise

    def exists(self, table, id):
        """
        Check if a record exists in the table by its ID.
        """
        query = f"SELECT 1 FROM products_{table} WHERE {table}_id = %s LIMIT 1"
        try:
            return self.fetch(query, [id]) != []
        except Exception as e:
            logger.error(f"Error checking existence in {table}: {str(e)}")
            raise

    def insert(self, table, data):
        """
        Insert a new record into the table.
        """
        try:
            placeholders = self._generate_placeholders(data.keys())
            columns = ', '.join(data.keys())
            query = (
                f"INSERT INTO products_{table} ({columns}, created_by_id, created_at) "
                f"VALUES ({placeholders}, %s, NOW())"
            )
            params = list(data.values()) + [self.user]
            self._execute_query(query, params)
            AuditService.log_change(self.connection, table, data, "INSERT", self.user)
            return True
        except Exception as e:
            logger.error(f"Error inserting into {table}: {str(e)}")
            raise

    def update(self, table, data):
        """
        Update an existing record in the table.
        """
        try:
            if f"{table}_id" not in data:
                raise ValueError(f"Missing id in update data.")

            set_clause = self._generate_set_clause(data.keys())
            query = (
                f"UPDATE products_{table} SET {set_clause}, "
                f"changed_by_id = %s, changed_at = NOW() WHERE {table}_id = %s"
            )
            params = [v for k, v in data.items() if k != f"{table}_id"] + [self.user, data[f"{table}_id"]]            
            db_post = AuditService.log_change(self.connection, table, data, "UPDATE", self.user)
            if db_post == True:
                self._execute_query(query, params)
                return True
            elif db_post != False:
                return db_post
        except Exception as e:
            logger.error(f"Error updating {table}: {str(e)}")
            raise

    def _execute_query(self, query, params):
        """
        Execute a query with parameters.
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
        except DatabaseError as db_error:
            logger.error(f"Database error during query execution: {str(db_error)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during query execution: {str(e)}")
            raise

    def _generate_placeholders(self, columns):
        """
        Generate placeholders for SQL query based on the number of columns.
        """
        return ', '.join(['%s'] * len(columns))

    def _generate_set_clause(self, columns):
        """
        Generate SET clause for SQL update query.
        """
        return ', '.join([f"{col} = %s" for col in columns if col != f"{col.split('_')[0]}_id"])


class AuditService:
    @staticmethod
    def log_change(connection, table, data, change_type, user):
        """
        Log changes to the database for auditing purposes.
        """
        try:
            entity_id = data.get(f"{table}_id")
            if not entity_id:
                raise ValueError(f"Entity ID missing for audit logging in table {table}")

            change_id_query = "SELECT COALESCE(MAX(id), 0) + 1 FROM changeaudit_changehistory"
            with connection.cursor() as cursor:
                cursor.execute(change_id_query)
                change_id = cursor.fetchone()[0]

            change_dir_id = f"{table.upper()}{entity_id}{str(change_id).zfill(9)}"
            changed_items = []

            if change_type == "INSERT":
                changed_items = [(change_dir_id, key, '', value) for key, value in data.items()]
            elif change_type == "UPDATE":
                select_query = f"SELECT {', '.join(data.keys())} FROM products_{table} WHERE {table}_id = %s"
                old_values = Repository(connection).fetch(select_query, [entity_id])
                for key, old_value in old_values[0].items():
                    new_value = data.get(key)
                    if old_value != new_value:
                        changed_items.append((change_dir_id, key, old_value, new_value))

            if changed_items:
                insert_changehistory = """
                    INSERT INTO changeaudit_changehistory 
                    (CHDIR_ID, entity_type, entity_id, change_type, created_by_id, created_at) 
                    VALUES (%s, %s, %s, %s, %s, NOW())
                """
                insert_changeditem = """
                    INSERT INTO changeaudit_changeditem 
                    (CHDIR_ID, field_name, old_value, new_value) VALUES (%s, %s, %s, %s)
                """
                with connection.cursor() as cursor:
                    cursor.execute(insert_changehistory, [change_dir_id, table, entity_id, change_type, user])
                    cursor.executemany(insert_changeditem, changed_items)
                
                return True
            
            else:
                return 'no change'

        except Exception as e:
            logger.error(f"Error in audit logging for {table}: {str(e)}")
            raise
