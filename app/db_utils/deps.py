from app.db_utils.db_connection import DBConn

def get_db():
    conn = DBConn()
    db = conn.connect()
    try:
        yield db
    finally:
        conn.disconnect()
