import sqlite3

def apagar_itens(nome_do_banco):
    # Conectando ao banco de dados
    conn = sqlite3.connect(nome_do_banco)
    cursor = conn.cursor()

    # Obtendo a lista de tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tabelas = cursor.fetchall()

    # Iterando sobre as tabelas e apagando os dados
    for tabela in tabelas:
        if not tabela[0].startswith("sqlite_"):
            cursor.execute(f"DELETE FROM {tabela[0]}")

    # Commitando as alterações e fechando a conexão
    conn.commit()
    conn.close()

# Chame a função passando o nome do seu banco de dados
apagar_itens("hosprec.db")
