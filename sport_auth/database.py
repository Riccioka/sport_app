import psycopg2

def get_db_connection():
    return psycopg2.connect(database="sport_auth", user="postgres", password="pilot", host="localhost", port="5432")


def execute_query(query, args=None, fetchall=False, insert=False, update=False, delete=False):
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
    elif update:
        conn.commit()
        conn.close()
        return True
    elif delete:
        conn.commit()
        conn.close()
        return True
    elif fetchall:
        result = cur.fetchall()
    else:
        result = cur.fetchone()

    conn.close()
    return result
