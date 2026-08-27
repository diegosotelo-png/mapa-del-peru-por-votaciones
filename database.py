"""Almacenamiento de los pozos.

Funciona con dos motores sin cambiar nada del resto de la app:

  * SQLite  -> por defecto, en el archivo DB_PATH (uso local).
  * Postgres -> si existe la variable de entorno DATABASE_URL.

En Render el disco es efímero: sin DATABASE_URL los datos se pierden en
cada despliegue. Con DATABASE_URL apuntando a un Postgres, persisten.
"""

import os
import sqlite3

DATABASE_URL = (os.environ.get("DATABASE_URL") or "").strip()
USA_POSTGRES = DATABASE_URL.startswith(("postgres://", "postgresql://"))
DB_PATH = os.environ.get("DB_PATH", "pozos.db")


def motor():
    return "postgres" if USA_POSTGRES else "sqlite"


def conectar():
    if USA_POSTGRES:
        import psycopg2
        url = DATABASE_URL
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://"):]
        return psycopg2.connect(url)
    return sqlite3.connect(DB_PATH)


def q(sql):
    """SQLite usa ? y Postgres %s para los parámetros."""
    return sql.replace("?", "%s") if USA_POSTGRES else sql


def ejecutar(sql, params=(), fetch=None):
    conn = conectar()
    try:
        cursor = conn.cursor()
        cursor.execute(q(sql), params)
        datos = None
        if fetch == "one":
            datos = cursor.fetchone()
        elif fetch == "all":
            datos = cursor.fetchall()
        conn.commit()
        return datos
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Conteo de pozos por zona (departamento / provincia / distrito)
# El usuario carga a mano cuántos pozos hay y si la zona tiene petar.
# Provincia y distrito vacíos ("") marcan el nivel al que pertenece la fila.
# ---------------------------------------------------------------------------


def crear_tabla_conteo():
    """Crea la tabla de conteo de pozos por zona si no existe"""
    clave = "SERIAL PRIMARY KEY" if USA_POSTGRES else "INTEGER PRIMARY KEY AUTOINCREMENT"
    ejecutar(f"""
        CREATE TABLE IF NOT EXISTS conteo_pozos (
            id {clave},
            departamento TEXT NOT NULL,
            provincia TEXT NOT NULL DEFAULT '',
            distrito TEXT NOT NULL DEFAULT '',
            pozos INTEGER NOT NULL DEFAULT 0,
            petar INTEGER NOT NULL DEFAULT 0,
            UNIQUE (departamento, provincia, distrito)
        )
    """)


def guardar_conteo(departamento, provincia, distrito, pozos, petar):
    """Inserta o actualiza el conteo de una zona"""
    ejecutar("""
        INSERT INTO conteo_pozos (departamento, provincia, distrito, pozos, petar)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT (departamento, provincia, distrito)
        DO UPDATE SET pozos = excluded.pozos, petar = excluded.petar
    """, (departamento, provincia or "", distrito or "", int(pozos or 0), 1 if petar else 0))


def listar_conteos():
    """Lista todos los conteos cargados"""
    filas = ejecutar("""
        SELECT id, departamento, provincia, distrito, pozos, petar
        FROM conteo_pozos
        ORDER BY departamento, provincia, distrito
    """, fetch="all") or []

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
    ejecutar("DELETE FROM conteo_pozos WHERE id = ?", (id_conteo,))


# ---------------------------------------------------------------------------
# Tabla original de pozos individuales (la usan los endpoints /api/wells)
# ---------------------------------------------------------------------------


def crear_tabla():
    """Crea la tabla de pozos si no existe"""
    clave = "SERIAL PRIMARY KEY" if USA_POSTGRES else "INTEGER PRIMARY KEY AUTOINCREMENT"
    ejecutar(f"""
        CREATE TABLE IF NOT EXISTS pozos (
            id {clave},
            departamento TEXT NOT NULL,
            nombre TEXT NOT NULL,
            profundidad REAL,
            produccion REAL,
            operador TEXT,
            anio INTEGER,
            estado TEXT
        )
    """)


def insertar_pozo(departamento, nombre, profundidad, produccion, operador, anio, estado):
    """Inserta un nuevo pozo en la base de datos"""
    ejecutar("""
        INSERT INTO pozos
        (departamento, nombre, profundidad, produccion, operador, anio, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (departamento, nombre, profundidad, produccion, operador, anio, estado))


def eliminar_pozo(id_pozo):
    """Elimina un pozo por ID"""
    ejecutar("DELETE FROM pozos WHERE id = ?", (id_pozo,))


def listar_pozos_por_departamento(departamento):
    """Lista todos los pozos de un departamento específico"""
    return ejecutar("""
        SELECT id, nombre, profundidad, produccion, operador, anio, estado
        FROM pozos
        WHERE departamento = ?
        ORDER BY id DESC
    """, (departamento,), fetch="all") or []


def listar_conteo_por_departamento():
    """Retorna el conteo de pozos por departamento"""
    filas = ejecutar("""
        SELECT departamento, COUNT(*) as total_pozos
        FROM pozos
        GROUP BY departamento
    """, fetch="all") or []
    return {fila[0]: fila[1] for fila in filas}
