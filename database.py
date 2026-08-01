import psycopg2
import pandas as pd

class DatabaseManager:
    def __init__(self, db_url: str):
        self.db_url = db_url

    def get_schema(self) -> str:
        """
        # Comment: Connects to Neon PostgreSQL and fetches public table schemas,
        # Comment: column names, and data types to format context for LLM.
        """
        try:
            # Establish connection with Neon DB
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            
            # SQL query to query the PostgreSQL system information catalog
            cursor.execute("""
                SELECT table_name, column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position;
            """)
            rows = cursor.fetchall()
            conn.close()

            # Handle empty database schema case
            if not rows:
                return "No tables found in the public schema of this database."

            # Format schema rows into structured text grouping by table
            tables = {}
            for table, column, dtype in rows:
                if table not in tables:
                    tables[table] = []
                tables[table].append(f"{column} ({dtype})")

            schema_info = []
            for table_name, cols in tables.items():
                schema_info.append(f"Table '{table_name}': {', '.join(cols)}")

            return "\n".join(schema_info)

        except Exception as e:
            # Comment: Raise readable exception if connection fails
            raise ConnectionError(f"Failed to connect to Neon PostgreSQL: {str(e)}")

    def execute_query(self, query: str) -> pd.DataFrame:
        #========================================
        # Executes a SELECT query on Neon DB safely and returns Pandas DataFrame.
        # Includes security guardrails to reject data modification commands.
        #========================================
        clean_query = query.strip().upper()
        blocked_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "CREATE"]
        
        # Security check to block data altering operations
        for keyword in blocked_keywords:
            if keyword in clean_query:
                raise ValueError(f"Security Restriction: Execution of '{keyword}' queries is blocked.")

        conn = psycopg2.connect(self.db_url)
        try:
            # Load SQL result directly into a Pandas DataFrame
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        except Exception as e:
            conn.close()
            raise e