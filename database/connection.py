"""
Database connection management
Handles connection pooling and basic operations
FIXED: Better connection persistence
"""

import pyodbc
from config import Config
from contextlib import contextmanager

class DatabaseConnection:
    """Database connection handler"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
        self._connection_string = self._build_connection_string()
        # Connect immediately
        self.connect()
    
    def _build_connection_string(self):
        """Build the database connection string"""
        if Config.DB_USE_WINDOWS_AUTH:
            return (
                f"DRIVER={{SQL Server}};"
                f"SERVER={Config.DB_SERVER};"
                f"DATABASE={Config.DB_NAME};"
                f"Trusted_Connection=yes;"
            )
        else:
            return (
                f"DRIVER={{SQL Server}};"
                f"SERVER={Config.DB_SERVER};"
                f"DATABASE={Config.DB_NAME};"
                f"UID={Config.DB_USERNAME};"
                f"PWD={Config.DB_PASSWORD};"
            )
    
    def connect(self):
        """Establish database connection"""
        try:
            # Only connect if not already connected
            if self.connection and self.cursor:
                try:
                    # Test if connection is still alive
                    self.cursor.execute("SELECT 1")
                    return True
                except:
                    # Connection is dead, close it properly
                    self.disconnect()
            
            self.connection = pyodbc.connect(self._connection_string)
            self.cursor = self.connection.cursor()
            return True
        except pyodbc.Error as e:
            # Try with ODBC Driver 17 if SQL Server driver fails
            if "SQL Server" in str(e):
                try:
                    alt_connection_string = self._connection_string.replace(
                        "SQL Server", "ODBC Driver 17 for SQL Server"
                    )
                    self.connection = pyodbc.connect(alt_connection_string)
                    self.cursor = self.connection.cursor()
                    # Update the connection string for future use
                    self._connection_string = alt_connection_string
                    return True
                except Exception as e2:
                    print(f"Database connection failed with alternate driver: {str(e2)}")
                    self.connection = None
                    self.cursor = None
                    return False
            print(f"Database connection failed: {str(e)}")
            self.connection = None
            self.cursor = None
            return False
    
    def disconnect(self):
        """Close database connection"""
        try:
            if self.cursor:
                self.cursor.close()
                self.cursor = None
            if self.connection:
                self.connection.close()
                self.connection = None
            return True
        except Exception as e:
            print(f"Error disconnecting: {str(e)}")
            return False
    
    def test_connection(self):
        """Test database connection"""
        try:
            if self.connect():
                self.cursor.execute("SELECT 1")
                result = self.cursor.fetchone()
                # Keep connection alive after test
                return result is not None
        except:
            return False
        return False
    
    def execute_query(self, query, params=None):
        """
        Execute a query and return results
        For SELECT queries, returns list of dictionaries
        For INSERT/UPDATE/DELETE, returns True/False
        """
        # Ensure we have a connection
        if not self.cursor or not self.connection:
            if not self.connect():
                print("Failed to establish database connection")
                if query.strip().upper().startswith('SELECT'):
                    return []
                return False
        
        try:
            # Test connection is alive
            self.cursor.execute("SELECT 1")
            self.cursor.fetchone()
        except:
            # Connection died, reconnect
            if not self.connect():
                print("Failed to reconnect to database")
                if query.strip().upper().startswith('SELECT'):
                    return []
                return False
        
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            # If it's a SELECT query, return results
            if query.strip().upper().startswith('SELECT'):
                columns = [column[0] for column in self.cursor.description] if self.cursor.description else []
                results = []
                for row in self.cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results
            else:
                # For INSERT, UPDATE, DELETE
                self.connection.commit()
                return True
                
        except pyodbc.Error as e:
            print(f"Query execution failed: {str(e)}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            if self.connection:
                try:
                    self.connection.rollback()
                except:
                    pass
            # Return empty list for SELECT queries, False for others
            if query.strip().upper().startswith('SELECT'):
                return []
            return False
        except Exception as e:
            print(f"Unexpected error in execute_query: {str(e)}")
            if query.strip().upper().startswith('SELECT'):
                return []
            return False
    
    def execute_scalar(self, query, params=None):
        """Execute a query and return a single value"""
        # Ensure we have a connection
        if not self.cursor or not self.connection:
            if not self.connect():
                print("Failed to establish database connection")
                return None
        
        try:
            # Test connection is alive
            self.cursor.execute("SELECT 1")
            self.cursor.fetchone()
        except:
            # Connection died, reconnect
            if not self.connect():
                return None
        
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            result = self.cursor.fetchone()
            return result[0] if result else None
            
        except Exception as e:
            print(f"Scalar query failed: {str(e)}")
            return None
    
    def check_table_exists(self, table_name):
        """Check if a table exists in the database"""
        try:
            query = """
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = ? AND TABLE_CATALOG = ?
            """
            result = self.execute_scalar(query, (table_name, Config.DB_NAME))
            return result > 0 if result is not None else False
        except Exception as e:
            print(f"Table check failed: {str(e)}")
            return False
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections - maintains persistent connection"""
        try:
            # Ensure connection is alive
            if not self.cursor or not self.connection:
                self.connect()
            else:
                # Test if connection is still alive
                try:
                    self.cursor.execute("SELECT 1")
                    self.cursor.fetchone()
                except:
                    # Connection died, reconnect
                    self.connect()
            
            yield self
        except Exception as e:
            print(f"Error in connection context manager: {str(e)}")
            yield self
        # Don't disconnect when leaving context to maintain persistence

# Global instance (singleton pattern)
_db_instance = None

def get_db():
    """Get the global database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseConnection()
    return _db_instance