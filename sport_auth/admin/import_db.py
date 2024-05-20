import csv
import psycopg2
from database import get_db_connection, execute_query

def import_csv_to_users_table(csv_file):
    db_connection = None
    try:
        db_connection = get_db_connection()
        with open(csv_file, 'r', newline='') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                execute_query(
                    'INSERT INTO users (id, surname, name, midname, email, password, age) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                    (row[0], row[1], row[2], row[3], row[4], row[5], row[6]),
                    insert=True
                )
        print("Data imported successfully.")
    except (Exception, psycopg2.Error) as error:
        print("Error while importing data:", error)
        if db_connection:
            db_connection.rollback()
    finally:
        if db_connection:
            db_connection.close()