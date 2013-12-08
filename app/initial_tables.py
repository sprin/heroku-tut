from tables import engine

def create_tables():
    """
    Create tables the lazy way... with raw SQL.
    """
    conn = engine.raw_connection()
    cur = conn.cursor()
    cur.execute(
"""
CREATE TABLE file_upload(
    document_name TEXT
    , time_uploaded TEXT DEFAULT now()
    , filename TEXT NOT NULL
    , word_counts JSON NOT NULL
    , PRIMARY KEY(document_name, time_uploaded)
);
"""
    )
    conn.commit()

if __name__ == '__main__':
    create_tables()
