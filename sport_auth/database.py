import psycopg2

def get_db_connection():
    return psycopg2.connect(database="sport_auth", user="postgres", password="pilot", host="localhost", port="5432")

def execute_query(query, args=None, fetchall=False, insert=False):
    conn = get_db_connection()
    cur = conn.cursor()
    if args:
        cur.execute(query, args)
    else:
        cur.execute(query)

    if insert:
        conn.commit()
        conn.close()
        return None
    else:
        result = cur.fetchall() if fetchall else cur.fetchone()
        conn.close()
        return result
