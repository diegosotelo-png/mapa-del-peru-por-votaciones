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