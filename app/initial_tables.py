from tables import engine

def create_tables():
    """
    Create tables the lazy way... with raw SQL.
    """
    conn = engine.raw_connection()
    cur = conn.cursor()
    cur.execute(
"""
DROP TABLE IF EXISTS file_upload_meta;
"""
    )
    conn.commit()
    cur.execute(
"""
CREATE TABLE file_upload_meta(
    document_name TEXT NOT NULL
    , document_slug TEXT NOT NULL
    , time_uploaded TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
    , s3_key TEXT NOT NULL
    , filename TEXT NOT NULL
    , word_counts JSON
    , PRIMARY KEY(document_slug, time_uploaded)
);
"""
    )
    conn.commit()
    print "Created tables"

if __name__ == '__main__':
    create_tables()
