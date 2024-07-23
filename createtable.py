import sqlite3

conn = sqlite3.connect('hosprec.db')

# Tabela Usuários
conn.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        nome VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        senha VARCHAR(255) NOT NULL,
        data_nascimento DATE,
        telefone VARCHAR(15),
        endereco VARCHAR(255)
    )
''')

# Tabela Anfitriões
conn.execute('''
    CREATE TABLE IF NOT EXISTS anfitrioes (
        id_anfitriao INTEGER PRIMARY KEY AUTOINCREMENT,
        nome VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        senha VARCHAR(255) NOT NULL,
        data_nascimento DATE,
        telefone VARCHAR(15),
        endereco VARCHAR(255)
    )
''')

# Tabela Localidade
conn.execute('''
    CREATE TABLE IF NOT EXISTS localidades (
        id_loc INTEGER PRIMARY KEY AUTOINCREMENT,
        localizacao TEXT,
        qty_hotel INTEGER
    )
''')

# Tabela Hotel
conn.execute('''
    CREATE TABLE IF NOT EXISTS hoteis (
        id_hotel INTEGER PRIMARY KEY AUTOINCREMENT,
        nome VARCHAR(255) NOT NULL,
        endereco VARCHAR(255),
        descricao TEXT,
        id_anfitriao INT,
	    id_loc INT,
        FOREIGN KEY (id_anfitriao) REFERENCES anfitrioes(id_anfitriao),
	    FOREIGN KEY (id_loc) REFERENCES localidades(id_loc)
    )
''')

# Tabela Quarto
conn.execute('''
    CREATE TABLE IF NOT EXISTS quartos (
        id_quarto INTEGER PRIMARY KEY AUTOINCREMENT,
        id_hotel INTEGER,
        nome_quarto TEXT,
        preco_por_noite NUMERIC(10, 2),
        FOREIGN KEY (id_hotel) REFERENCES hoteis(id_hotel)
    )
''')

# Tabela Reservas
conn.execute('''
    CREATE TABLE IF NOT EXISTS reservas (
        id_reserva INTEGER PRIMARY KEY AUTOINCREMENT,
        id_usuario INT,
        id_hotel INT,
        id_quarto INT,
        data_inicio DATE NOT NULL,
        data_fim DATE NOT NULL,
        numero_de_pessoas INT,
        status VARCHAR(20),
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
        FOREIGN KEY (id_hotel) REFERENCES hoteis(id_hotel),
        FOREIGN KEY (id_quarto) REFERENCES quartos(id_quarto)
    )
             ''')

# Tabela Contato
conn.execute('''
    CREATE TABLE IF NOT EXISTS contato (
        id_contato INTEGER PRIMARY KEY AUTOINCREMENT,
        id_usuario INT,
        nome VARCHAR(100),
        email VARCHAR(254),
        telefone VARCHAR(20),
        endereco VARCHAR(100),
        mensagem TEXT,
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
    )
''')

conn.commit()

conn.close()
