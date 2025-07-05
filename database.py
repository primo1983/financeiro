import mysql.connector
from mysql.connector import errorcode

DB_CONFIG = {
    'user': 'financas',
    'password': 'Mudar1234@',
    'host': '127.0.0.1',
}

DB_NAME = 'financas'

def create_database():
    try:
        cnx = mysql.connector.connect(**DB_CONFIG)
        cursor = cnx.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} DEFAULT CHARACTER SET 'utf8mb4'")
        print(f"Banco de dados '{DB_NAME}' verificado/criado com sucesso.")
        cursor.close()
        cnx.close()
    except mysql.connector.Error as err:
        print(f"Erro ao criar o banco de dados: {err}")
        exit(1)

def init_db():
    try:
        cnx = mysql.connector.connect(**DB_CONFIG, database=DB_NAME)
        cursor = cnx.cursor()
        with open('schema.sql', 'r', encoding='utf-8') as f:
            sql_commands = f.read().split(';')
            for command in sql_commands:
                if command.strip():
                    cursor.execute(command)
        print("Tabelas criadas com sucesso a partir do schema.sql.")
        cursor.close()
        cnx.close()
    except mysql.connector.Error as err:
        print(f"Erro ao inicializar o banco de dados: {err}")
        exit(1)

if __name__ == '__main__':
    create_database()
    init_db()