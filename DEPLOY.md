# Despliegue en la nube

La app ya está lista para Render o Railway.

## Render

1. Sube este proyecto a GitHub.
2. En Render crea un `New Web Service`.
3. Conecta el repositorio.
4. Render detectará `render.yaml`.
5. Si te pide datos manuales:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
6. Al terminar, Render te dará una URL pública.

## Railway

1. Sube este proyecto a GitHub.
2. En Railway crea un proyecto desde GitHub.
3. Railway usará `railway.json`.
4. Si te pide comando de inicio: `gunicorn app:app`

## Archivos que sí deben subirse

- `app.py`
- `database.py`
- `requirements.txt`
- `runtime.txt`
- `Procfile`
- `render.yaml`
- `railway.json`
- `d3.v7.min.js`
- `peru_departamental_simple.geojson`
- `peru_provincial_simple.geojson`
- `peru_distrital_simple.geojson`
- `ubigeo_departamentos.json`
- `ubigeo_provincias.json`
- `ubigeo_distritos.json`
- `election_results_ubigeo.json`

Los archivos `.parquet`, `.csv`, `.deps`, `.db` y logs no son necesarios para producción.
