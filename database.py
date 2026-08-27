import sqlite3
import os

DB_PATH = "pozos.db"


def conectar():
    return sqlite3.connect(DB_PATH)


def crear_tabla():
    """Crea la tabla de pozos si no existe"""
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pozos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            departamento TEXT NOT NULL,
            nombre TEXT NOT NULL,
            profundidad REAL,
            produccion REAL,
            operador TEXT,
            anio INTEGER,
            estado TEXT
        )
    """)

    conn.commit()
    conn.close()


def insertar_datos_ejemplo():
    """Inserta datos de ejemplo si la tabla está vacía"""
    conn = conectar()
    cursor = conn.cursor()
    
    # Verificar si ya hay datos
    cursor.execute("SELECT COUNT(*) FROM pozos")
    count = cursor.fetchone()[0]
    
    if count == 0:
        datos_ejemplo = [
            ("Piura", "Pozo Talara 1", 2500.0, 1200.0, "Petroperú", 2015, "Activo"),
            ("Piura", "Pozo Talara 2", 2200.0, 950.0, "Sapet", 2018, "Activo"),
            ("Loreto", "Pozo Pastaza 1", 3100.0, 1800.0, "Petroperú", 2012, "Activo"),
            ("Loreto", "Pozo Pastaza 2", 2800.0, 1500.0, "Pluspetrol", 2019, "Inactivo"),
            ("Ucayali", "Pozo Ucayali 1", 2400.0, 800.0, "Frontera", 2017, "Activo"),
        ]
        
        cursor.executemany("""
            INSERT INTO pozos 
            (departamento, nombre, profundidad, produccion, operador, anio, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, datos_ejemplo)
        
        conn.commit()
    
    conn.close()


def insertar_pozo(departamento, nombre, profundidad, produccion, operador, anio, estado):
    """Inserta un nuevo pozo en la base de datos"""
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO pozos 
        (departamento, nombre, profundidad, produccion, operador, anio, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (departamento, nombre, profundidad, produccion, operador, anio, estado))

    conn.commit()
    conn.close()


def eliminar_pozo(id_pozo):
    """Elimina un pozo por ID"""
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM pozos WHERE id = ?", (id_pozo,))

    conn.commit()
    conn.close()


def listar_pozos_por_departamento(departamento):
    """Lista todos los pozos de un departamento específico"""
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nombre, profundidad, produccion, operador, anio, estado
        FROM pozos
        WHERE departamento = ?
        ORDER BY id DESC
    """, (departamento,))

    datos = cursor.fetchall()
    conn.close()
    return datos


def listar_conteo_por_departamento():
    """Retorna el conteo de pozos por departamento"""
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT departamento, COUNT(*) as total_pozos
        FROM pozos
        GROUP BY departamento
    """)

    datos = cursor.fetchall()
    conn.close()
    return {fila[0]: fila[1] for fila in datos}


def obtener_metricas_departamento(departamento):
    """Obtiene métricas del departamento: total, activos, BPD, profundidad promedio"""
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN estado = 'Activo' THEN 1 ELSE 0 END) as activos,
            SUM(produccion) as bpd_total,
            AVG(profundidad) as profundidad_media
        FROM pozos
        WHERE departamento = ?
    """, (departamento,))

    resultado = cursor.fetchone()
    conn.close()
    
    return {
        "total": resultado[0] or 0,
        "activos": resultado[1] or 0,
        "bpd_total": resultado[2] or 0.0,
        "profundidad_media": resultado[3] or 0.0
    }

    conn.close()

    return datos

# ---------------------------------------------------------------------------
# Conteo de pozos por zona (departamento / provincia / distrito)
# El usuario carga a mano cuántos pozos hay y si la zona tiene petar.
# Provincia y distrito vacíos ("") marcan el nivel al que pertenece la fila.
# ---------------------------------------------------------------------------


def crear_tabla_conteo():
    """Crea la tabla de conteo de pozos por zona si no existe"""
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conteo_pozos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            departamento TEXT NOT NULL,
            provincia TEXT NOT NULL DEFAULT '',
            distrito TEXT NOT NULL DEFAULT '',
            pozos INTEGER NOT NULL DEFAULT 0,
            petar INTEGER NOT NULL DEFAULT 0,
            UNIQUE (departamento, provincia, distrito)
        )
    """)

    conn.commit()
    conn.close()


def guardar_conteo(departamento, provincia, distrito, pozos, petar):
    """Inserta o actualiza el conteo de una zona"""
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO conteo_pozos (departamento, provincia, distrito, pozos, petar)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT (departamento, provincia, distrito)
        DO UPDATE SET pozos = excluded.pozos, petar = excluded.petar
    """, (departamento, provincia or "", distrito or "", int(pozos or 0), 1 if petar else 0))

    conn.commit()
    conn.close()


def listar_conteos():
    """Lista todos los conteos cargados"""
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, departamento, provincia, distrito, pozos, petar
        FROM conteo_pozos
        ORDER BY departamento, provincia, distrito
    """)

    filas = cursor.fetchall()
    conn.close()

    return [
        {
            "id": f[0],
            "departamento": f[1],
            "provincia": f[2],
            "distrito": f[3],
            "pozos": f[4],
            "petar": bool(f[5])
        }
        for f in filas
    ]


def eliminar_conteo(id_conteo):
    """Elimina el conteo de una zona por ID"""
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM conteo_pozos WHERE id = ?", (id_conteo,))

    conn.commit()
    conn.close()
