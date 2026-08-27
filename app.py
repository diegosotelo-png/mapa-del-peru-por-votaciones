from flask import Flask, jsonify, request, send_from_directory, Response
import gzip
import os
import database

# Inicializar BD
database.crear_tabla()
database.insertar_datos_ejemplo()
database.crear_tabla_conteo()

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index():
    return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mapa de Estadísticas de Votos — Perú</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        html, body {
            min-height: 100%;
            overflow-y: auto;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
            background: #e9f0f7;
        }
        .wrap { min-height: 100vh; height: auto; background: #f5f5f5; overflow: visible; }
        .map-side {
            flex: 1;
            background: #122033;
            position: relative;
            overflow: visible;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }
        .db-bar {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px 14px;
            background: #ffffff;
            border-bottom: 1px solid #ddd;
            font-size: 12px;
            color: #666;
        }
        .db-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #1D9E75;
            flex-shrink: 0;
        }
        .db-dot.error { background: #f44336; }
        
        .header {
            background: linear-gradient(135deg, #122033 0%, #1d334d 100%);
            color: white;
            padding: 18px 20px;
            text-align: center;
            border-bottom: 3px solid #e8752a;
        }
        .header h1 {
            font-size: 32px;
            color: #ffffff;
            margin: 0 0 5px 0;
            font-weight: bold;
        }
        .header p {
            margin: 0;
            font-size: 13px;
            color: #cbd7e4;
        }
        
        #svgmap {
            flex: 1;
            width: 100%;
            background: #f0f4f8;
        }
        
        .legend {
            position: sticky;
            top: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 18px;
            background: white;
            border-bottom: 1px solid #d8e3ef;
            padding: 9px 12px;
            font-size: 14px;
            font-weight: 800;
            z-index: 20;
            box-shadow: 0 2px 10px rgba(18,32,51,0.07);
        }
        .lr { display: flex; align-items: center; gap: 8px; margin-bottom: 0; color: #314154; }
        .lr:last-child { margin: 0; }
        .ld { width: 14px; height: 14px; border-radius: 3px; flex-shrink: 0; }
        
        .level-bar {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            padding: 10px 14px;
            background: #ffffff;
            border-bottom: 1px solid #d7e2ed;
        }
        .level-chip {
            border: 1px solid #d7e2ed;
            background: #f8fbff;
            color: #526579;
            border-radius: 4px;
            padding: 7px 12px;
            font-size: 12px;
            font-weight: 800;
        }
        .level-chip.active {
            background: #1565c0;
            border-color: #1565c0;
            color: #ffffff;
        }
        .map-info {
            position: absolute;
            top: 188px;
            right: 15px;
            z-index: 10;
            background: rgba(255,255,255,0.94);
            border: 1px solid #d7e2ed;
            border-radius: 6px;
            padding: 10px 12px;
            min-width: 220px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .map-info h2 {
            color: #0d2137;
            font-size: 16px;
            margin: 0 0 4px;
        }
        .map-info p {
            color: #6f7d8a;
            font-size: 12px;
            margin: 0;
        }
        .metrics {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 16px;
        }
        .metric {
            background: #f0f4f8;
            border-radius: 6px;
            padding: 10px;
            text-align: center;
            border-left: 4px solid #4fc3f7;
        }
        .metric-n { font-size: 22px; font-weight: bold; color: #0d2137; }
        .metric-l { font-size: 11px; color: #999; margin-top: 4px; }
        
        .well-card {
            background: #f0f4f8;
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 10px;
            margin-bottom: 10px;
            font-size: 12px;
        }
        .wh {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        .wn { font-weight: bold; color: #0d2137; }
        .badge {
            font-size: 10px;
            padding: 2px 8px;
            border-radius: 3px;
            color: white;
        }
        .badge.activo { background: #1D9E75; }
        .badge.inactivo { background: #f44336; }
        .badge.perforacion { background: #ff9800; }
        .wr {
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            padding: 3px 0;
            border-bottom: 1px solid #ddd;
        }
        .wr:last-child { border: none; }
        .wr span:first-child { color: #999; }
        .btn-del {
            background: none;
            border: none;
            cursor: pointer;
            color: #f44336;
            font-size: 16px;
            padding: 0;
        }
        .btn-del:hover { opacity: 0.7; }
        
        .btn-add {
            width: 100%;
            padding: 10px;
            margin-top: 10px;
            background: #1D9E75;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            font-weight: bold;
        }
        .btn-add:hover { background: #158f6a; }
        
        .placeholder {
            text-align: center;
            padding: 40px 20px;
            color: #999;
            font-size: 12px;
        }
        
        .modal-bg {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 30;
            align-items: center;
            justify-content: center;
        }
        .modal-bg.open { display: flex; }
        .modal {
            background: white;
            border-radius: 6px;
            border: 1px solid #ddd;
            padding: 20px;
            width: 320px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        .modal h3 { font-size: 14px; font-weight: bold; margin-bottom: 14px; color: #0d2137; }
        .fr { margin-bottom: 10px; }
        .fr label { display: block; font-size: 11px; color: #666; margin-bottom: 4px; font-weight: bold; }
        .fr input, .fr select {
            width: 100%;
            padding: 7px 8px;
            font-size: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background: white;
            color: #333;
        }
        .mbtns { display: flex; gap: 8px; margin-top: 14px; }
        .mbtns button {
            flex: 1;
            padding: 8px;
            font-size: 12px;
            border: 1px solid #ddd;
            background: white;
            color: #333;
            border-radius: 4px;
            cursor: pointer;
        }
        .mbtns button.ok { background: #1D9E75; color: white; border-color: #1D9E75; }
        .map-toolbar {
            position: absolute;
            top: 188px;
            left: 15px;
            display: flex;
            gap: 8px;
            z-index: 10;
        }
        .map-btn {
            display: none;
            border: 1px solid #cfe0f2;
            background: #ffffff;
            color: #0d2137;
            border-radius: 4px;
            padding: 7px 10px;
            font-size: 12px;
            font-weight: 700;
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(0,0,0,0.12);
        }
        .map-btn.show { display: inline-flex; }
        .breadcrumb {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-bottom: 12px;
            font-size: 11px;
            color: #789;
        }
        .area-card {
            border: 1px solid #d8e2ed;
            background: #f8fbff;
            border-radius: 6px;
            padding: 10px;
            margin-bottom: 10px;
        }
        .area-head {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 10px;
            margin-bottom: 8px;
        }
        .area-title {
            color: #0d2137;
            font-size: 13px;
            font-weight: 800;
        }
        .area-sub {
            color: #7d8b99;
            font-size: 11px;
            margin-top: 2px;
        }
        .area-action {
            border: 1px solid #1D9E75;
            background: #ffffff;
            color: #15795c;
            border-radius: 4px;
            padding: 5px 8px;
            font-size: 11px;
            font-weight: 700;
            cursor: pointer;
            white-space: nowrap;
        }
        .area-action:hover { background: #eaf8f3; }
        .district-list {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            padding-top: 4px;
        }
        .district-chip {
            border: 1px solid #d7e2ec;
            background: #ffffff;
            border-radius: 3px;
            padding: 4px 6px;
            color: #334;
            font-size: 10px;
        }
        details summary {
            color: #1565c0;
            cursor: pointer;
            font-size: 11px;
            font-weight: 700;
            list-style-position: inside;
        }
        .section-title {
            color: #0d2137;
            font-size: 14px;
            margin: 16px 0 10px;
            border-bottom: 1px solid #e5edf5;
            padding-bottom: 6px;
        }
        .source-note {
            margin-top: 12px;
            color: #8b98a5;
            font-size: 10px;
            line-height: 1.4;
        }
        .header { padding: 14px 20px; }
        .header h1 { font-size: 32px; }
        .header p { font-size: 15px; font-weight: 700; }
        .db-bar { font-size: 14px; font-weight: 700; }
        #svgmap, .level-bar, .map-toolbar, .map-info { display: none; }
        .map-grid {
            flex: none;
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            align-items: stretch;
            gap: 12px;
            padding: 12px;
            background: #e9f0f7;
            overflow: visible;
        }
        .map-pane {
            min-width: 0;
            min-height: 620px;
            height: clamp(620px, calc(100vh - 205px), 860px);
            display: flex;
            flex-direction: column;
            background: #f4f8fc;
            border: 1px solid #cfddea;
            border-radius: 6px;
            overflow: hidden;
            position: relative;
        }
        .pane-hdr {
            padding: 11px 13px;
            background: #ffffff;
            border-bottom: 1px solid #dbe6f0;
        }
        .pane-hdr h2 {
            color: #0d2137;
            font-size: 20px;
            margin: 0 0 3px;
            line-height: 1.12;
        }
        .pane-hdr p {
            color: #718091;
            font-size: 15px;
            font-weight: 700;
            margin: 0;
        }
        .map-svg {
            flex: 1;
            min-height: 0;
            width: 100%;
            background: #edf3f8;
            cursor: grab;
            touch-action: none;
        }
        .map-svg:active { cursor: grabbing; }
        .vote-card {
            position: absolute;
            left: 10px;
            bottom: 10px;
            width: min(230px, calc(100% - 20px));
            background: rgba(255,255,255,0.94);
            border: 1px solid #cdd8e5;
            border-radius: 6px;
            padding: 9px 10px;
            box-shadow: 0 8px 22px rgba(18,32,51,0.12);
            color: #152438;
        }
        .vote-title {
            font-size: 12px;
            font-weight: 900;
            line-height: 1.15;
            margin-bottom: 7px;
        }
        .vote-row {
            display: grid;
            grid-template-columns: 64px 1fr 42px;
            align-items: center;
            gap: 7px;
            font-size: 11px;
            font-weight: 800;
            margin-top: 5px;
        }
        .vote-bar {
            height: 8px;
            overflow: hidden;
            background: #e4ebf2;
            border-radius: 999px;
        }
        .vote-fill {
            height: 100%;
            border-radius: 999px;
        }
        .vote-fill.keiko { background: #E8752A; }
        .vote-fill.sanchez { background: #1FA64A; }
        .pozo-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
            font-size: 12px;
            font-weight: 800;
            color: #314154;
            margin-top: 6px;
        }
        .pozo-val { font-size: 15px; color: #0d2137; }
        .pozo-input {
            width: 96px;
            padding: 3px 7px;
            border: 1px solid #cbd6e2;
            border-radius: 5px;
            font-family: inherit;
            font-size: 12px;
            font-weight: 800;
            color: #0d2137;
            background: #fff;
        }
        input.pozo-input { text-align: right; }
        .card-btns { display: flex; gap: 6px; justify-content: flex-end; margin-top: 9px; }
        .card-btn {
            padding: 4px 10px;
            border: 1px solid #cbd6e2;
            border-radius: 5px;
            background: #fff;
            color: #2b3a4a;
            font-family: inherit;
            font-size: 11px;
            font-weight: 800;
            cursor: pointer;
        }
        .card-btn.ok { background: #1D9E75; border-color: #1D9E75; color: #fff; }
        .card-btn:disabled { opacity: 0.45; cursor: default; }
        .pozo-val.si { color: #1FA64A; }
        .pozo-val.no { color: #97a4b2; }
        .nomap {
            position: absolute;
            right: 10px;
            top: 10px;
            max-width: 46%;
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
            justify-content: flex-end;
        }
        .nomap-chip {
            padding: 3px 7px;
            border: 1px dashed #9aa8b6;
            border-radius: 999px;
            background: rgba(255,255,255,0.94);
            color: #46586b;
            font-family: inherit;
            font-size: 10px;
            font-weight: 800;
            cursor: pointer;
        }
        .nomap-chip:hover { border-color: #1D9E75; color: #14324a; }
        .add-btn {
            margin-left: auto;
            padding: 6px 12px;
            border: 1px solid #1D9E75;
            border-radius: 6px;
            background: #1D9E75;
            color: #fff;
            font-size: 12px;
            font-weight: 800;
            cursor: pointer;
        }
        .vote-foot {
            margin-top: 7px;
            font-size: 10px;
            color: #6c7b8a;
            font-weight: 800;
        }
        .empty-map {
            fill: #7b8998;
            font-size: 16px;
            font-weight: 800;
        }
        @media (max-width: 980px) {
            .header { padding: 12px 14px; }
            .header h1 { font-size: 24px; }
            .header p { font-size: 12px; }
            .db-bar { font-size: 12px; padding: 8px 10px; }
            .map-grid {
                grid-template-columns: 1fr;
                overflow: visible;
                gap: 10px;
                padding: 10px;
            }
            .map-pane {
                min-height: min(620px, 88vh);
                height: min(620px, 88vh);
            }
            .vote-card {
                left: 8px;
                bottom: 8px;
                width: min(210px, calc(100% - 16px));
                padding: 8px;
            }
            .vote-row {
                grid-template-columns: 58px 1fr 38px;
                gap: 5px;
                font-size: 10px;
            }
            .vote-title { font-size: 11px; }
            .pane-hdr { padding: 10px 12px; }
            .pane-hdr h2 { font-size: 18px; }
            .pane-hdr p { font-size: 13px; }
            .legend {
                flex-wrap: wrap;
                gap: 8px 14px;
                justify-content: flex-start;
                padding: 8px 10px;
                font-size: 12px;
            }
        }
    </style>
</head>
<body>
    <div class="wrap">
        <div class="map-side">
            <div class="header">
                <h1>Mapa de Pozos — Perú</h1>
                <p>Pozos y petar por departamento, provincia y distrito</p>
            </div>
            <div class="db-bar">
                <div class="db-dot" id="dbdot"></div>
                <span id="dbmsg">Cargando datos...</span>
                <button class="add-btn" onclick="openModal()">+ Agregar pozos</button>
            </div>
            <div class="legend">
                <div class="lr"><div class="ld" style="background: #1FA64A;"></div>Territorio</div>
                <div class="lr"><div class="ld" style="background: #2D8BC9;"></div>Seleccionado</div>
            </div>
            <div class="map-grid">
                <section class="map-pane">
                    <div class="pane-hdr">
                        <h2>Mapa del Perú</h2>
                        <p id="deptMeta">Selecciona un departamento</p>
                    </div>
                    <svg class="map-svg" id="deptMap" viewBox="0 0 360 560"></svg>
                    <div class="vote-card" id="deptStats"></div>
                </section>
                <section class="map-pane">
                    <div class="pane-hdr">
                        <h2 id="provinceTitle">Provincias</h2>
                        <p id="provinceMeta">Aparecen al elegir un departamento</p>
                    </div>
                    <svg class="map-svg" id="provinceMap" viewBox="0 0 360 560"></svg>
                    <div class="vote-card" id="provinceStats"></div>
                </section>
                <section class="map-pane">
                    <div class="pane-hdr">
                        <h2 id="districtTitle">Distritos</h2>
                        <p id="districtMeta">Aparecen al elegir una provincia</p>
                    </div>
                    <svg class="map-svg" id="districtMap" viewBox="0 0 360 560"></svg>
                    <div class="nomap" id="districtNoMap"></div>
                    <div class="vote-card" id="districtStats"></div>
                </section>
            </div>
        </div>
    </div>
    
    <div class="modal-bg" id="mbg">
        <div class="modal">
            <h3 id="mtitle">Agregar pozos</h3>
            <div class="fr"><label>Departamento</label><select id="zDept" onchange="refreshProvOptions(); loadZoneIntoForm();"></select></div>
            <div class="fr"><label>Provincia (dejar vacío = todo el departamento)</label><select id="zProv" onchange="refreshDistOptions(); loadZoneIntoForm();"></select></div>
            <div class="fr"><label>Distrito (dejar vacío = toda la provincia)</label><select id="zDist" onchange="loadZoneIntoForm();"></select></div>
            <div class="fr"><label>Cantidad de pozos</label><input id="zPozos" type="number" min="0" placeholder="0"/></div>
            <div class="fr">
                <label>¿Hay petar?</label>
                <select id="zPetar">
                    <option value="0">No hay</option>
                    <option value="1">Sí hay</option>
                </select>
            </div>
            <div class="mbtns">
                <button onclick="closeModal()">Cancelar</button>
                <button class="ok" onclick="savePozos()">Guardar</button>
            </div>
        </div>
    </div>

    <script src="/data/d3.v7.min.js"></script>
    <script>
        const DATA_URLS = {
            departments: "/data/peru_departamental_simple.geojson",
            provinces: "/data/peru_provincial_simple.geojson",
            districts: "/data/peru_distrital_simple.geojson",
            ubigeoDepartments: "/data/ubigeo_departamentos.json",
            ubigeoProvinces: "/data/ubigeo_provincias.json",
            ubigeoDistricts: "/data/ubigeo_distritos.json"
        };
        let pozosData = [];
        let geo = { departments: null, provinces: null, districts: null };
        let ubigeo = { departments: [], provinces: [], districts: [] };
        let currentLevel = "departments";
        let selectedDept = null;
        let selectedProvince = null;
        let selectedDistrict = null;
        const panelZones = {};
        const editingPanels = new Set();
        const W = 360, H = 560;
        const MAP_GREEN = "#1FA64A";
        function setDbStatus(msg, isError = false) {
            document.getElementById("dbdot").style.background = isError ? "#f44336" : "#1D9E75";
            document.getElementById("dbmsg").textContent = msg;
        }

        async function loadPozos() {
            try {
                const res = await fetch("/api/pozos");
                pozosData = await res.json();
                const zonas = pozosData.length;
                const total = pozosData.reduce((s, r) => s + (r.pozos || 0), 0);
                setDbStatus(`Base local conectada — ${total} pozo${total !== 1 ? "s" : ""} en ${zonas} zona${zonas !== 1 ? "s" : ""}`);
            } catch (e) {
                setDbStatus("Error cargando base de datos", true);
            }
        }

        function norm(value) {
            return String(value || "")
                .normalize("NFD")
                .replace(/[\u0300-\u036f]/g, "")
                .toUpperCase()
                .trim();
        }

        const PROVINCE_ALIASES = {
            "PUIRA": "PIURA",
            "VICTOR FAFARDO": "VICTOR FAJARDO",
            "NAZCA": "NASCA"
        };

        function normProvince(value) {
            const key = norm(value);
            return PROVINCE_ALIASES[key] || key;
        }

        // Nombre de provincia tal como lo escribe el ubigeo, para guardar
        // siempre el mismo texto venga del mapa o del formulario.
        function canonicalProvince(dept, province) {
            if (!province) return "";
            const deptRow = ubigeoDeptFor(dept);
            const row = ubigeo.provinces.find(p =>
                (!deptRow || p.departamento_id === deptRow.id) &&
                normProvince(p.provincia) === normProvince(province));
            return row ? row.provincia : province;
        }

        function titleCase(value) {
            return String(value || "")
                .toLowerCase()
                .split(" ")
                .map(part => part ? part[0].toUpperCase() + part.slice(1) : part)
                .join(" ");
        }

        function jsArg(value) {
            return JSON.stringify(value || "");
        }

        function esc(value) {
            return String(value ?? "")
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#39;");
        }

        function getDeptName(f) {
            const p = f.properties || {};
            return p.NOMBDEP || p.NOMBDEPTO || p.FIRST_NOMB || p.name || p.NAME || p.NAME_1 || Object.values(p)[0];
        }

        function getProvinceName(f) {
            const p = f.properties || {};
            return p.NOMBPROV || p.PROVINCIA || p.name || p.NAME || Object.values(p)[0];
        }

        function getDistrictName(f) {
            const p = f.properties || {};
            return p.NOMBDIST || p.DISTRITO || p.name || p.NAME || Object.values(p)[0];
        }

        function getAreaName(f, level) {
            if (level === "departments") return titleCase(getDeptName(f));
            if (level === "provinces") return titleCase(getProvinceName(f));
            return titleCase(getDistrictName(f));
        }

        function featureUbigeo(feature, level) {
            const p = feature.properties || {};
            if (level === "departments") return String(p.FIRST_IDDP || p.IDDPTO || p.IDDP || "").padStart(2, "0");
            if (level === "provinces") return String(p.FIRST_IDPR || p.IDPROV || p.IDPRO || "").padStart(4, "0");
            return String(p.IDDIST || p.UBIGEO || p.CODIGO || p.FIRST_IDDI || p.IDDISTRITO || "").padStart(6, "0");
        }

        function formatNumber(value) {
            return Math.round(Number(value || 0)).toLocaleString("es-PE");
        }

        function pozoRowsIn(dept, prov, dist) {
            return pozosData.filter(r => {
                if (norm(r.departamento) !== norm(dept)) return false;
                if (prov && normProvince(r.provincia) !== normProvince(prov)) return false;
                if (dist && norm(r.distrito) !== norm(dist)) return false;
                return true;
            });
        }

        // Si la zona tiene un valor cargado a mano, ese manda.
        // Si no, se suman los valores de las zonas de adentro.
        function pozoSummary(dept, prov, dist) {
            const rows = pozoRowsIn(dept, prov, dist);
            if (!rows.length) return null;
            const own = rows.find(r =>
                normProvince(r.provincia) === normProvince(prov || "") &&
                norm(r.distrito) === norm(dist || ""));
            if (own) return { pozos: own.pozos || 0, petar: !!own.petar, propio: true, zonas: 1 };
            return {
                pozos: rows.reduce((sum, r) => sum + (r.pozos || 0), 0),
                petar: rows.some(r => r.petar),
                propio: false,
                zonas: rows.length
            };
        }

        function pozoSummaryPeru() {
            const depts = [...new Set(pozosData.map(r => norm(r.departamento)))];
            if (!depts.length) return null;
            let pozos = 0, petar = false;
            depts.forEach(d => {
                const item = pozoSummary(d, null, null);
                if (!item) return;
                pozos += item.pozos;
                petar = petar || item.petar;
            });
            return { pozos, petar, propio: false, zonas: depts.length };
        }

        function zoneForFeature(feature, level) {
            if (level === "departments") return { dept: getDeptName(feature) };
            if (level === "provinces") return { dept: getDeptName(feature), prov: getProvinceName(feature) };
            return { dept: getDeptName(feature), prov: getProvinceName(feature), dist: getDistrictName(feature) };
        }

        function renderPozoStats(elementId, title, zone, detail = "") {
            const el = document.getElementById(elementId);
            if (!el) return;
            // Con el formulario abierto el hover del mapa no debe pisarlo
            if (editingPanels.has(elementId)) return;
            panelZones[elementId] = { title, zone, detail };
            const data = zone && zone.dept
                ? pozoSummary(zone.dept, zone.prov, zone.dist)
                : pozoSummaryPeru();
            const editable = !!(zone && zone.dept);
            const btnLabel = data && data.propio ? "Editar" : "Agregar";
            const btn = editable
                ? `<button class="card-btn ok" onclick="startEdit('${elementId}')">${btnLabel}</button>`
                : `<button class="card-btn" disabled title="Elige una zona en el mapa">Editar</button>`;
            if (!data) {
                el.innerHTML = `
                    <div class="vote-title">${esc(title)}</div>
                    <div class="pozo-row"><span>Pozos</span><span class="pozo-val">—</span></div>
                    <div class="pozo-row"><span>Petar</span><span class="pozo-val no">Sin cargar</span></div>
                    <div class="vote-foot">${editable ? "Sin datos para esta zona" : "Elige una zona en el mapa"}</div>
                    <div class="card-btns">${btn}</div>
                `;
                return;
            }
            const foot = data.propio
                ? `Cargado para esta zona${detail ? ` · ${esc(detail)}` : ""}`
                : `Suma de ${data.zonas} zona${data.zonas !== 1 ? "s" : ""} cargada${data.zonas !== 1 ? "s" : ""}${detail ? ` · ${esc(detail)}` : ""}`;
            el.innerHTML = `
                <div class="vote-title">${esc(title)}</div>
                <div class="pozo-row"><span>Pozos</span><span class="pozo-val">${formatNumber(data.pozos)}</span></div>
                <div class="pozo-row"><span>Petar</span><span class="pozo-val ${data.petar ? "si" : "no"}">${data.petar ? "Sí hay" : "No hay"}</span></div>
                <div class="vote-foot">${foot}</div>
                <div class="card-btns">${btn}</div>
            `;
        }

        function startEdit(elementId) {
            const panel = panelZones[elementId];
            const el = document.getElementById(elementId);
            if (!panel || !el || !panel.zone || !panel.zone.dept) return;
            const { title, zone } = panel;
            const own = pozosData.find(r =>
                norm(r.departamento) === norm(zone.dept) &&
                normProvince(r.provincia) === normProvince(zone.prov || "") &&
                norm(r.distrito) === norm(zone.dist || ""));
            editingPanels.add(elementId);
            el.innerHTML = `
                <div class="vote-title">${esc(title)}</div>
                <div class="pozo-row">
                    <span>Pozos</span>
                    <input class="pozo-input" id="${elementId}-pozos" type="number" min="0" step="1" value="${own ? own.pozos : ""}" placeholder="0"/>
                </div>
                <div class="pozo-row">
                    <span>Petar</span>
                    <select class="pozo-input" id="${elementId}-petar">
                        <option value="0"${own && own.petar ? "" : " selected"}>No hay</option>
                        <option value="1"${own && own.petar ? " selected" : ""}>Sí hay</option>
                    </select>
                </div>
                <div class="vote-foot">${esc(zoneLabel(zone))}</div>
                <div class="card-btns">
                    <button class="card-btn" onclick="cancelEdit('${elementId}')">Cancelar</button>
                    <button class="card-btn ok" onclick="saveEdit('${elementId}')">Guardar</button>
                </div>
            `;
            document.getElementById(`${elementId}-pozos`).focus();
        }

        function zoneLabel(zone) {
            if (zone.dist) return "Se guarda en el distrito";
            if (zone.prov) return "Se guarda en la provincia";
            return "Se guarda en el departamento";
        }

        function cancelEdit(elementId) {
            editingPanels.delete(elementId);
            const panel = panelZones[elementId];
            if (panel) renderPozoStats(elementId, panel.title, panel.zone, panel.detail);
        }

        async function saveEdit(elementId) {
            const panel = panelZones[elementId];
            if (!panel) return;
            const { zone } = panel;
            const cantidad = Number(document.getElementById(`${elementId}-pozos`).value);
            if (!Number.isFinite(cantidad) || cantidad < 0) {
                alert("Ingresa una cantidad de pozos válida (0 o más)");
                return;
            }
            const petar = document.getElementById(`${elementId}-petar`).value === "1";
            try {
                const res = await fetch("/api/pozos", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        departamento: zone.dept,
                        provincia: canonicalProvince(zone.dept, zone.prov),
                        distrito: zone.dist || "",
                        pozos: cantidad,
                        petar: petar
                    })
                });
                if (!res.ok) throw new Error("Error al guardar");
                editingPanels.delete(elementId);
                await loadPozos();
                refreshCurrentView();
            } catch (e) {
                alert("Error: " + e.message);
            }
        }

        function hasGeometry(feature) {
            return !!(feature && feature.geometry);
        }

        function provincesForDept(dept) {
            return geo.provinces.features
                .filter(hasGeometry)
                .filter(f => norm(getDeptName(f)) === norm(dept))
                .sort((a, b) => getProvinceName(a).localeCompare(getProvinceName(b), "es"));
        }

        function districtsFor(dept, province = null) {
            return geo.districts.features
                .filter(hasGeometry)
                .filter(f => norm(getDeptName(f)) === norm(dept))
                .filter(f => !province || normProvince(getProvinceName(f)) === normProvince(province))
                .sort((a, b) => {
                    const prov = getProvinceName(a).localeCompare(getProvinceName(b), "es");
                    return prov || getDistrictName(a).localeCompare(getDistrictName(b), "es");
                });
        }

        function ubigeoDeptFor(dept) {
            return ubigeo.departments.find(d => norm(d.departamento) === norm(dept));
        }

        function provinceRowsForDept(dept) {
            const row = ubigeoDeptFor(dept);
            if (!row) return provincesForDept(dept).map(f => ({ provincia: getProvinceName(f), id: null }));
            return ubigeo.provinces
                .filter(p => p.departamento_id === row.id)
                .sort((a, b) => a.provincia.localeCompare(b.provincia, "es"));
        }

        function districtRowsFor(dept, province = null) {
            const deptRow = ubigeoDeptFor(dept);
            if (!deptRow) return districtsFor(dept, province).map(f => ({ distrito: getDistrictName(f), provincia_id: null }));
            let rows = ubigeo.districts.filter(d => d.departamento_id === deptRow.id);
            if (province) {
                const provRow = ubigeo.provinces.find(p => p.departamento_id === deptRow.id && normProvince(p.provincia) === normProvince(province));
                rows = provRow ? rows.filter(d => d.provincia_id === provRow.id) : [];
            }
            return rows.sort((a, b) => a.distrito.localeCompare(b.distrito, "es"));
        }

        function districtsWithoutMap(dept, province = null) {
            const conMapa = new Set(districtsFor(dept, province).map(f => norm(getDistrictName(f))));
            return districtRowsFor(dept, province)
                .map(row => row.distrito)
                .filter(name => !conMapa.has(norm(name)));
        }

        function getFill() {
            return MAP_GREEN;
        }

        function redrawMap() {
            renderDepartments();
            if (selectedDept) renderProvinces(selectedDept);
            if (selectedDept && selectedProvince) renderDistricts(selectedDept, selectedProvince);
        }

        function renderEmpty(svgId, message) {
            const svg = d3.select("#" + svgId);
            svg.selectAll("*").remove();
            svg.on(".zoom", null);
            svg.append("text")
                .attr("class", "empty-map")
                .attr("x", W / 2)
                .attr("y", H / 2)
                .attr("text-anchor", "middle")
                .text(message);
        }

        function renderEmptyStats(elementId, message) {
            const el = document.getElementById(elementId);
            if (!el) return;
            el.innerHTML = `<div class="vote-title">${esc(message)}</div><div class="vote-foot">Selecciona un área del mapa</div>`;
        }

        function labelFontSize(level, count) {
            if (level === "districts") {
                if (count > 40) return 6.4;
                if (count > 24) return 7.2;
                if (count > 14) return 8.2;
                return 10.5;
            }
            if (level === "provinces") return count > 12 ? 8.4 : 9.6;
            return 6.9;
        }

        function splitLabel(text, level) {
            const words = String(text).split(/\\s+/).filter(Boolean);
            const maxChars = level === "departments" ? 10 : level === "districts" ? 11 : 12;
            const lines = [];
            let line = "";
            words.forEach(word => {
                const next = line ? `${line} ${word}` : word;
                if (next.length > maxChars && line) {
                    lines.push(line);
                    line = word;
                } else {
                    line = next;
                }
            });
            if (line) lines.push(line);
            if (lines.length <= 2) return lines;
            return [lines[0], lines.slice(1).join(" ")];
        }

        function labelCenterNudge(feature, level) {
            const name = norm(getAreaName(feature, level));
            const nudges = {
                departments: {
                    "LAMBAYEQUE": [3, -10],
                    "CALLAO": [-4, -6],
                    "LA LIBERTAD": [-2, -4],
                    "MADRE DE DIOS": [-2, 3]
                }
            };
            return (nudges[level] && nudges[level][name]) || [0, 0];
        }

        function labelMetrics(level) {
            return level === "departments"
                ? { factor: 0.64, padX: 8, padY: 6 }
                : { factor: 0.70, padX: 13, padY: 9 };
        }

        function boxesOverlap(a, b) {
            return !(a.x2 < b.x1 || a.x1 > b.x2 || a.y2 < b.y1 || a.y1 > b.y2);
        }

        // Zona que tapa la tarjeta de pozos (abajo a la izquierda del mapa)
        const CARD_BOX = { x1: -2, x2: 208, y1: H - 138, y2: H + 2 };

        function overlapsCard(box) {
            return boxesOverlap(box, CARD_BOX);
        }

        function buildLabels(features, level, pathFn) {
            const fontSize = labelFontSize(level, features.length);
            const metrics = labelMetrics(level);
            const items = features.map((feature, index) => {
                const [baseX, baseY] = pathFn.centroid(feature);
                const [nudgeX, nudgeY] = labelCenterNudge(feature, level);
                const x = baseX + nudgeX;
                const y = baseY + nudgeY;
                const bounds = pathFn.bounds(feature);
                const area = Math.abs((bounds[1][0] - bounds[0][0]) * (bounds[1][1] - bounds[0][1]));
                const lines = splitLabel(getAreaName(feature, level), level);
                const maxLine = Math.max(...lines.map(line => line.length));
                const width = maxLine * fontSize * metrics.factor + metrics.padX;
                const height = lines.length * fontSize * 1.18 + metrics.padY;
                return {
                    feature,
                    index,
                    x,
                    y,
                    area,
                    lines,
                    fontSize,
                    metrics,
                    width,
                    height,
                    box: {
                        x1: x - width / 2,
                        x2: x + width / 2,
                        y1: y - height / 2,
                        y2: y + height / 2
                    }
                };
            }).sort((a, b) => b.area - a.area);

            const placed = [];
            const skipped = [];
            items.forEach(item => {
                const insideCanvas = item.box.x1 >= 0 && item.box.y1 >= 0 && item.box.x2 <= W && item.box.y2 <= H
                    && !overlapsCard(item.box);
                const collides = placed.some(other => boxesOverlap(item.box, other.box));
                if (insideCanvas && !collides) placed.push(item);
                else skipped.push(item);
            });
            return { placed, skipped, items };
        }

        function movedLabel(item, dx, dy, scale = 1) {
            const fontSize = item.fontSize * scale;
            const metrics = item.metrics || labelMetrics("districts");
            const maxLine = Math.max(...item.lines.map(line => line.length));
            const width = maxLine * fontSize * metrics.factor + metrics.padX;
            const height = item.lines.length * fontSize * 1.18 + metrics.padY;
            const x = item.x + dx;
            const y = item.y + dy;
            return {
                ...item,
                x,
                y,
                fontSize,
                width,
                height,
                box: {
                    x1: x - width / 2,
                    x2: x + width / 2,
                    y1: y - height / 2,
                    y2: y + height / 2
                }
            };
        }

        function labelPointInsideFeature(item, projection) {
            const point = projection.invert([item.x, item.y]);
            return !point || d3.geoContains(item.feature, point);
        }

        function labelOffsetCandidates(level) {
            const maxRadius = level === "departments" ? 10 : level === "provinces" ? 12 : 14;
            const steps = level === "departments" ? [0, 4, 7, 10] : [0, 5, 8, 12, maxRadius];
            const directions = [[0,0], [0,-1], [0,1], [-1,0], [1,0], [-1,-1], [1,-1], [-1,1], [1,1]];
            const offsets = [];
            steps.forEach(step => {
                directions.forEach(([dx, dy]) => {
                    const item = [dx * step, dy * step];
                    if (!offsets.some(([x, y]) => x === item[0] && y === item[1])) offsets.push(item);
                });
            });
            return offsets;
        }

        function placeLabelsWithNudge(items, level, projection) {
            const offsets = labelOffsetCandidates(level);
            const scales = level === "districts" ? [1, 0.92, 0.82, 0.72] : [1, 0.92, 0.84, 0.76];
            const placed = [];
            const skipped = [];

            items
                .slice()
                .sort((a, b) => b.area - a.area)
                .forEach(item => {
                    let chosen = null;
                    for (const scale of scales) {
                        for (const [dx, dy] of offsets) {
                            const candidate = movedLabel(item, dx, dy, scale);
                            const insideCanvas = candidate.box.x1 >= 2 && candidate.box.y1 >= 2 && candidate.box.x2 <= W - 2 && candidate.box.y2 <= H - 2
                                && !overlapsCard(candidate.box);
                            const insideFeature = labelPointInsideFeature(candidate, projection);
                            const collides = placed.some(other => boxesOverlap(candidate.box, other.box));
                            if (insideCanvas && insideFeature && !collides) {
                                chosen = candidate;
                                break;
                            }
                        }
                        if (chosen) break;
                    }
                    if (!chosen) {
                        for (const scale of scales) {
                            for (const [dx, dy] of offsets) {
                                const candidate = movedLabel(item, dx, dy, scale);
                                const insideCanvas = candidate.box.x1 >= 2 && candidate.box.y1 >= 2 && candidate.box.x2 <= W - 2 && candidate.box.y2 <= H - 2
                                && !overlapsCard(candidate.box);
                                const collides = placed.some(other => boxesOverlap(candidate.box, other.box));
                                if (insideCanvas && !collides) {
                                    chosen = candidate;
                                    break;
                                }
                            }
                            if (chosen) break;
                        }
                    }
                    if (chosen) placed.push(chosen);
                    else skipped.push(item);
                });

            return { placed, skipped };
        }

        function renderGrid(svg) {
            const grid = svg.append("g").attr("pointer-events", "none");
            for (let x = 0; x <= W; x += 56) {
                grid.append("line")
                    .attr("x1", x).attr("x2", x)
                    .attr("y1", 0).attr("y2", H)
                    .attr("stroke", "#d8e0e8")
                    .attr("stroke-width", 1);
            }
            for (let y = 0; y <= H; y += 56) {
                grid.append("line")
                    .attr("x1", 0).attr("x2", W)
                    .attr("y1", y).attr("y2", y)
                    .attr("stroke", "#d8e0e8")
                    .attr("stroke-width", 1);
            }
        }

        // El lado izquierdo se corta antes de la tarjeta de pozos
        function calloutRange(side) {
            return side === "left" ? [28, CARD_BOX.y1 - 12] : [28, H - 28];
        }

        // Cuántas etiquetas caben en un lado con separación legible
        function calloutCapacity(items, side) {
            const [top, bottom] = calloutRange(side);
            const slot = Math.max(...items.map(item =>
                item.lines.length * item.fontSize * 1.12 + 4));
            return Math.max(1, Math.floor((bottom - top) / slot));
        }

        // Si un lado se llena y al otro le sobra sitio, las etiquetas
        // sobrantes se pasan allí en vez de quedarse sin mostrar.
        function balanceCalloutSides(items) {
            ["left", "right"].forEach(side => {
                const other = side === "left" ? "right" : "left";
                const capacity = calloutCapacity(items, side);
                const otherCapacity = calloutCapacity(items, other);
                items
                    .filter(item => item.side === side)
                    .sort((a, b) => b.area - a.area)
                    .slice(capacity)
                    .forEach(item => {
                        if (items.filter(i => i.side === other).length < otherCapacity) item.side = other;
                    });
            });
        }

        // Reparte los callouts de un lado y descarta los que no entran con
        // separación legible, quedándose con las zonas de mayor superficie.
        function distributeCallouts(items, side) {
            const [top, bottom] = calloutRange(side);
            const candidates = items.filter(item => item.side === side);
            if (!candidates.length) return [];
            const capacity = calloutCapacity(items, side);
            const sorted = candidates
                .slice()
                .sort((a, b) => b.area - a.area)
                .slice(0, capacity)
                .sort((a, b) => a.y - b.y);
            sorted.forEach((item, index) => {
                item.labelY = top + ((index + 0.5) * (bottom - top)) / sorted.length;
            });
            return sorted;
        }

        function drawInternalLabels(g, labels) {
            const label = g.selectAll("text.area-label")
                .data(labels).join("text")
                .attr("class", "area-label")
                .attr("x", d => d.x)
                .attr("y", d => d.y - ((d.lines.length - 1) * d.fontSize * 0.55))
                .attr("text-anchor", "middle")
                .attr("dominant-baseline", "middle")
                .attr("font-size", d => d.fontSize)
                .attr("data-font-size", d => d.fontSize)
                .attr("fill", "#ffffff")
                .attr("font-weight", "900")
                .attr("paint-order", "stroke")
                .attr("stroke", "rgba(28,42,56,0.82)")
                .attr("stroke-width", "3")
                .attr("data-stroke-width", "3")
                .attr("stroke-linejoin", "round")
                .attr("pointer-events", "none");

            label.each(function (d) {
                const text = d3.select(this);
                d.lines.forEach((line, lineIndex) => {
                    text.append("tspan")
                        .attr("x", d.x)
                        .attr("dy", lineIndex === 0 ? 0 : d.fontSize * 1.12)
                        .text(line);
                });
            });
        }

        function renderCalloutLabels(g, items, level) {
            items.forEach(item => {
                item.side = item.x < W / 2 ? "left" : "right";
                item.lines = splitLabel(getAreaName(item.feature, level).toUpperCase(), level);
                item.fontSize = item.fontSize || 8.5;
            });

            balanceCalloutSides(items);
            const all = [
                ...distributeCallouts(items, "left"),
                ...distributeCallouts(items, "right")
            ];

            const callouts = g.append("g").attr("class", "callouts").attr("pointer-events", "none");
            all.forEach(item => {
                const isLeft = item.side === "left";
                const labelX = isLeft ? 8 : W - 8;
                const anchor = isLeft ? "start" : "end";
                const elbowX = isLeft ? 66 : W - 66;
                const textEndX = isLeft ? labelX + 4 : labelX - 4;

                callouts.append("path")
                    .attr("class", "callout-line")
                    .attr("d", `M${item.x},${item.y} L${elbowX},${item.labelY} L${textEndX},${item.labelY}`)
                    .attr("fill", "none")
                    .attr("stroke", "#3c4652")
                    .attr("stroke-width", 1.15)
                    .attr("data-stroke-width", 1.15)
                    .attr("opacity", 0.86);

                callouts.append("circle")
                    .attr("class", "callout-dot")
                    .attr("cx", item.x)
                    .attr("cy", item.y)
                    .attr("r", 1.7)
                    .attr("data-r", 1.7)
                    .attr("fill", "#243547")
                    .attr("stroke", "#ffffff")
                    .attr("stroke-width", 0.8);

                const text = callouts.append("text")
                    .attr("class", "callout-label")
                    .attr("x", labelX)
                    .attr("y", item.labelY - ((item.lines.length - 1) * item.fontSize * 0.55))
                    .attr("text-anchor", anchor)
                    .attr("dominant-baseline", "middle")
                    .attr("font-size", item.fontSize)
                    .attr("data-font-size", item.fontSize)
                    .attr("font-weight", "900")
                    .attr("fill", "#243547")
                    .attr("paint-order", "stroke")
                    .attr("stroke", "rgba(255,255,255,0.92)")
                    .attr("stroke-width", "3.5")
                    .attr("data-stroke-width", "3.5")
                    .attr("stroke-linejoin", "round");

                item.lines.forEach((line, lineIndex) => {
                    text.append("tspan")
                        .attr("x", labelX)
                        .attr("dy", lineIndex === 0 ? 0 : item.fontSize * 1.08)
                        .text(line);
                });
            });
        }

        function renderMap(svgId, features, level, onClick, focusCollection = null, statsConfig = null) {
            const svg = d3.select("#" + svgId);
            svg.selectAll("*").remove();
            svg.on(".zoom", null);
            renderGrid(svg);
            if (!features.length) {
                svg.append("text")
                    .attr("class", "empty-map")
                    .attr("x", W / 2)
                    .attr("y", H / 2)
                    .attr("text-anchor", "middle")
                    .text("Mapa no disponible para esta zona");
                if (statsConfig?.id) renderEmptyStats(statsConfig.id, "Sin mapa disponible");
                return;
            }
            if (statsConfig?.id) renderPozoStats(statsConfig.id, statsConfig.title, statsConfig.zone, statsConfig.detail);

            const collection = focusCollection || { type: "FeatureCollection", features };
            const useCallouts = level === "districts" && features.length > 10;
            const proj = d3.geoMercator().fitExtent(
                useCallouts ? [[72, 18], [W - 72, H - 18]] : [[12, 12], [W - 12, H - 12]],
                collection
            );
            const pathFn = d3.geoPath().projection(proj);
            const g = svg.append("g").attr("class", "zoom-layer");

            const paths = g.selectAll("path")
                .data(features).join("path")
                .attr("d", pathFn)
                .attr("stroke", d => {
                    if (level === "departments" && norm(getDeptName(d)) === norm(selectedDept)) return "#14324a";
                    if (level === "provinces" && norm(getProvinceName(d)) === norm(selectedProvince)) return "#14324a";
                    if (level === "districts" && selectedDistrict && norm(getDistrictName(d)) === norm(selectedDistrict)) return "#14324a";
                    return "#ffffff";
                })
                .attr("stroke-width", d => {
                    if (level === "departments" && norm(getDeptName(d)) === norm(selectedDept)) return 2.4;
                    if (level === "provinces" && norm(getProvinceName(d)) === norm(selectedProvince)) return 2.4;
                    if (level === "districts" && selectedDistrict && norm(getDistrictName(d)) === norm(selectedDistrict)) return 2.4;
                    return level === "districts" ? 1.15 : 1.35;
                })
                .attr("data-stroke-width", d => {
                    if (level === "departments" && norm(getDeptName(d)) === norm(selectedDept)) return 2.4;
                    if (level === "provinces" && norm(getProvinceName(d)) === norm(selectedProvince)) return 2.4;
                    if (level === "districts" && selectedDistrict && norm(getDistrictName(d)) === norm(selectedDistrict)) return 2.4;
                    return level === "districts" ? 1.15 : 1.35;
                })
                .attr("fill", (d, i) => getFill(d, i, level))
                .attr("class", "area-path " + level)
                .style("cursor", "pointer")
                .on("mouseover", function (e, d) {
                    d3.select(this).attr("fill", "#4fc3f7");
                    if (statsConfig?.id) {
                        renderPozoStats(
                            statsConfig.id,
                            getAreaName(d, level),
                            zoneForFeature(d, level),
                            "vista seleccionada"
                        );
                    }
                })
                .on("mouseout", function (e, d) {
                    const i = features.indexOf(d);
                    d3.select(this).attr("fill", getFill(d, i, level));
                    if (statsConfig?.id) renderPozoStats(statsConfig.id, statsConfig.title, statsConfig.zone, statsConfig.detail);
                })
                .on("click", (e, d) => onClick && onClick(d));
            const labelLimit = level === "districts" ? 95 : 220;
            if (features.length <= labelLimit) {
                const labels = buildLabels(features, level, pathFn);
                const nudged = placeLabelsWithNudge(labels.items, level, proj);
                drawInternalLabels(g, nudged.placed);
                if (level !== "departments" && nudged.skipped.length) renderCalloutLabels(g, nudged.skipped, level);
            }

            function updateZoomStyles(k) {
                const strokeDivisor = Math.max(k, 1);
                const minScreenFont = level === "districts" ? 10.8 : level === "provinces" ? 10.2 : 8.8;
                const maxScreenFont = level === "districts" ? 15.5 : level === "provinces" ? 14 : 12;
                const zoomBoost = 1 + Math.max(0, Math.log2(Math.max(k, 1))) * 0.18;
                g.selectAll("path.area-path,path.callout-line")
                    .attr("stroke-width", function () {
                        return Number(this.dataset.strokeWidth || 1.2) / strokeDivisor;
                    });
                g.selectAll("text.area-label,text.callout-label")
                    .attr("font-size", function () {
                        const base = Number(this.dataset.fontSize || 8);
                        const screenSize = Math.min(maxScreenFont, Math.max(minScreenFont, base * zoomBoost));
                        return screenSize / Math.max(k, 1);
                    })
                    .attr("stroke-width", function () {
                        const base = Number(this.dataset.strokeWidth || 3);
                        const screenStroke = Math.min(4.5, Math.max(3, base * 0.95));
                        return screenStroke / Math.max(k, 1);
                    });
                g.selectAll("circle.callout-dot")
                    .attr("r", function () { return Number(this.dataset.r || 1.7) / strokeDivisor; })
                    .attr("stroke-width", 0.8 / strokeDivisor);
            }

            const zoom = d3.zoom()
                .scaleExtent([1, 8])
                .translateExtent([[-90, -90], [W + 90, H + 90]])
                .extent([[0, 0], [W, H]])
                .on("zoom", e => {
                    g.attr("transform", e.transform);
                    updateZoomStyles(e.transform.k);
                });
            svg.call(zoom);
            updateZoomStyles(1);
        }

        function renderDepartments() {
            currentLevel = "departments";
            document.getElementById("deptMeta").textContent = "Pozos y petar por departamento";
            const selectedFeature = selectedDept
                ? geo.departments.features.find(f => norm(getDeptName(f)) === norm(selectedDept))
                : null;
            const statsTitle = selectedFeature ? titleCase(getDeptName(selectedFeature)) : "Perú completo";
            renderMap("deptMap", geo.departments.features, "departments", d => {
                showDepartment(getDeptName(d));
            }, geo.departments, {
                id: "deptStats",
                title: statsTitle,
                zone: selectedFeature ? { dept: getDeptName(selectedFeature) } : null,
                detail: selectedFeature ? "departamento" : "25 departamentos"
            });
        }

        function clearProvinces() {
            document.getElementById("provinceTitle").textContent = "Provincias";
            document.getElementById("provinceMeta").textContent = "Aparecen al elegir un departamento";
            renderEmpty("provinceMap", "Selecciona un departamento");
            renderEmptyStats("provinceStats", "Provincias");
        }

        function clearDistricts() {
            document.getElementById("districtTitle").textContent = "Distritos";
            document.getElementById("districtMeta").textContent = "Aparecen al elegir una provincia";
            renderEmpty("districtMap", "Selecciona una provincia");
            renderEmptyStats("districtStats", "Distritos");
            document.getElementById("districtNoMap").innerHTML = "";
        }

        function showDepartments() {
            selectedDept = null;
            selectedProvince = null;
            selectedDistrict = null;
            editingPanels.clear();
            renderDepartments();
            clearProvinces();
            clearDistricts();
        }

        function showDepartment(dept) {
            selectedDept = dept;
            selectedProvince = null;
            selectedDistrict = null;
            editingPanels.clear();
            renderDepartments();
            renderProvinces(dept);
            clearDistricts();
        }

        function renderProvinces(dept) {
            const features = provincesForDept(dept);
            const provinceCount = provinceRowsForDept(dept).length;
            const districtCount = districtRowsFor(dept).length;
            const niceDept = titleCase(dept);
            currentLevel = "provinces";
            document.getElementById("provinceTitle").textContent = `Provincias de ${niceDept}`;
            document.getElementById("provinceMeta").textContent = `${provinceCount} provincias · ${districtCount} distritos`;
            const selectedFeature = selectedProvince
                ? features.find(f => normProvince(getProvinceName(f)) === normProvince(selectedProvince))
                : null;
            renderMap("provinceMap", features, "provinces", d => {
                showProvince(dept, getProvinceName(d));
            }, null, {
                id: "provinceStats",
                title: selectedFeature ? titleCase(getProvinceName(selectedFeature)) : niceDept,
                zone: selectedFeature
                    ? { dept, prov: getProvinceName(selectedFeature) }
                    : { dept },
                detail: selectedFeature ? "provincia" : `${provinceCount} provincias`
            });
        }

        function showProvince(dept, province) {
            selectedDept = dept;
            selectedProvince = province;
            selectedDistrict = null;
            editingPanels.clear();
            renderDepartments();
            renderProvinces(dept);
            renderDistricts(dept, province);
        }

        function selectDistrict(district) {
            selectedDistrict = norm(district) === norm(selectedDistrict) ? null : district;
            editingPanels.clear();
            renderDistricts(selectedDept, selectedProvince);
        }

        function renderDistricts(dept, province) {
            const features = districtsFor(dept, province);
            const districtCount = districtRowsFor(dept, province).length;
            currentLevel = "districts";
            document.getElementById("districtTitle").textContent = `Distritos de ${titleCase(province)}`;
            const sinMapa = districtsWithoutMap(dept, province);
            document.getElementById("districtMeta").textContent = sinMapa.length
                ? `${districtCount} distritos · sin contorno: ${sinMapa.map(titleCase).join(", ")}`
                : `${districtCount} distritos`;
            document.getElementById("districtNoMap").innerHTML = sinMapa.map(name =>
                `<button class="nomap-chip" title="Sin contorno en el mapa — clic para cargar sus pozos"
                    onclick="openModal({ dept: ${jsArg(dept)}, prov: ${jsArg(province)}, dist: ${jsArg(name)} })">
                    ${esc(titleCase(name))} ⚑
                </button>`).join("");
            const selectedFeature = selectedDistrict
                ? features.find(f => norm(getDistrictName(f)) === norm(selectedDistrict))
                : null;
            renderMap("districtMap", features, "districts", d => {
                selectDistrict(getDistrictName(d));
            }, null, {
                id: "districtStats",
                title: selectedFeature ? titleCase(getDistrictName(selectedFeature)) : titleCase(province),
                zone: selectedFeature
                    ? { dept, prov: province, dist: getDistrictName(selectedFeature) }
                    : { dept, prov: province },
                detail: selectedFeature ? "distrito" : `${districtCount} distritos`
            });
        }

        function fillSelect(select, options, placeholder) {
            select.innerHTML = "";
            const blank = document.createElement("option");
            blank.value = "";
            blank.textContent = placeholder;
            select.appendChild(blank);
            options.forEach(name => {
                const opt = document.createElement("option");
                opt.value = name;
                opt.textContent = titleCase(name);
                select.appendChild(opt);
            });
        }

        function refreshProvOptions() {
            const dept = document.getElementById("zDept").value;
            const names = dept ? provinceRowsForDept(dept).map(r => r.provincia) : [];
            fillSelect(document.getElementById("zProv"), names, "— Todo el departamento —");
            refreshDistOptions();
        }

        function refreshDistOptions() {
            const dept = document.getElementById("zDept").value;
            const prov = document.getElementById("zProv").value;
            const names = dept && prov ? districtRowsFor(dept, prov).map(r => r.distrito) : [];
            fillSelect(document.getElementById("zDist"), names, "— Toda la provincia —");
        }

        // Al elegir una zona ya cargada, muestra sus valores para poder corregirlos.
        function loadZoneIntoForm() {
            const dept = document.getElementById("zDept").value;
            if (!dept) return;
            const prov = document.getElementById("zProv").value;
            const dist = document.getElementById("zDist").value;
            const row = pozosData.find(r =>
                norm(r.departamento) === norm(dept) &&
                norm(r.provincia) === norm(prov) &&
                norm(r.distrito) === norm(dist));
            document.getElementById("zPozos").value = row ? row.pozos : "";
            document.getElementById("zPetar").value = row && row.petar ? "1" : "0";
        }

        function pickOption(select, value, useProvinceAlias = false) {
            if (!value) return false;
            const same = useProvinceAlias
                ? (a, b) => normProvince(a) === normProvince(b)
                : (a, b) => norm(a) === norm(b);
            const match = [...select.options].find(o => same(o.value, value));
            if (match) select.value = match.value;
            return !!match;
        }

        function openModal(preset = null) {
            const dept = preset ? preset.dept : selectedDept;
            const prov = preset ? preset.prov : selectedProvince;
            const dist = preset ? preset.dist : null;
            const depts = ubigeo.departments.map(d => d.departamento);
            const zDept = document.getElementById("zDept");
            fillSelect(zDept, depts, "— Elige un departamento —");
            pickOption(zDept, dept);
            refreshProvOptions();
            if (pickOption(document.getElementById("zProv"), prov, true)) refreshDistOptions();
            pickOption(document.getElementById("zDist"), dist);
            loadZoneIntoForm();
            document.getElementById("mbg").classList.add("open");
        }

        function closeModal() {
            document.getElementById("mbg").classList.remove("open");
        }

        // Repinta los 3 mapas conservando lo que el usuario tenía seleccionado
        function refreshCurrentView() {
            renderDepartments();
            if (selectedDept) renderProvinces(selectedDept); else clearProvinces();
            if (selectedDept && selectedProvince) renderDistricts(selectedDept, selectedProvince); else clearDistricts();
        }

        async function savePozos() {
            const dept = document.getElementById("zDept").value;
            if (!dept) { alert("Elige un departamento"); return; }
            const cantidad = Number(document.getElementById("zPozos").value);
            if (!Number.isFinite(cantidad) || cantidad < 0) {
                alert("Ingresa una cantidad de pozos válida (0 o más)");
                return;
            }
            try {
                const res = await fetch("/api/pozos", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        departamento: dept,
                        provincia: document.getElementById("zProv").value,
                        distrito: document.getElementById("zDist").value,
                        pozos: cantidad,
                        petar: document.getElementById("zPetar").value === "1"
                    })
                });
                if (!res.ok) throw new Error("Error al guardar");
                closeModal();
                await loadPozos();
                refreshCurrentView();
            } catch (e) {
                alert("Error: " + e.message);
            }
        }

        async function init() {
            try {
                const [departments, provinces, districts, ubigeoDepartments, ubigeoProvinces, ubigeoDistricts] = await Promise.all([
                    fetch(DATA_URLS.departments).then(r => r.json()),
                    fetch(DATA_URLS.provinces).then(r => r.json()),
                    fetch(DATA_URLS.districts).then(r => r.json()),
                    fetch(DATA_URLS.ubigeoDepartments).then(r => r.json()),
                    fetch(DATA_URLS.ubigeoProvinces).then(r => r.json()),
                    fetch(DATA_URLS.ubigeoDistricts).then(r => r.json())
                ]);
                geo = { departments, provinces, districts };
                ubigeo = {
                    departments: ubigeoDepartments.ubigeo_departamentos,
                    provinces: ubigeoProvinces.ubigeo_provincias,
                    districts: ubigeoDistricts.ubigeo_distritos
                };
                showDepartments();
                await loadPozos();
            } catch (e) {
                console.error(e);
                setDbStatus("Error cargando mapa", true);
            }
        }

        init();
    </script>
</body>
</html>
    """

ARCHIVOS_DATOS = {
    'd3.v7.min.js',
    'peru_departamental_simple.geojson',
    'peru_provincial_simple.geojson',
    'peru_distrital_simple.geojson',
    'ubigeo_departamentos.json',
    'ubigeo_provincias.json',
    'ubigeo_distritos.json',
}

# Los mapas son estáticos y pesados: se comprimen una sola vez y se reutilizan.
_GZIP_CACHE = {}


def _gzip_datos(filename, ruta):
    marca = os.path.getmtime(ruta)
    guardado = _GZIP_CACHE.get(filename)
    if not guardado or guardado[0] != marca:
        with open(ruta, 'rb') as fh:
            guardado = (marca, gzip.compress(fh.read(), 6))
        _GZIP_CACHE[filename] = guardado
    return guardado


@app.route('/data/<path:filename>')
def data_file(filename):
    if filename not in ARCHIVOS_DATOS:
        return jsonify({"error": "Archivo no permitido"}), 404
    ruta = os.path.join(BASE_DIR, filename)
    tipo = 'application/javascript' if filename.endswith('.js') else 'application/json'
    cache = 'public, max-age=86400'

    if 'gzip' not in request.headers.get('Accept-Encoding', ''):
        respuesta = send_from_directory(BASE_DIR, filename)
        respuesta.headers['Cache-Control'] = cache
        return respuesta

    marca, comprimido = _gzip_datos(filename, ruta)
    respuesta = Response(comprimido, mimetype=tipo)
    respuesta.headers['Content-Encoding'] = 'gzip'
    respuesta.headers['Cache-Control'] = cache
    respuesta.headers['Vary'] = 'Accept-Encoding'
    respuesta.set_etag(f"{int(marca)}-{len(comprimido)}")
    return respuesta.make_conditional(request)

@app.route('/api/wells', methods=['GET'])
def get_wells():
    conteo = database.listar_conteo_por_departamento()
    result = {}
    for dept in conteo.keys():
        pozos = database.listar_pozos_por_departamento(dept)
        result[dept] = [
            {
                "id": p[0],
                "nombre": p[1],
                "profundidad": p[2],
                "produccion": p[3],
                "operador": p[4],
                "anio": p[5],
                "estado": p[6]
            }
            for p in pozos
        ]
    return jsonify(result)

@app.route('/api/wells', methods=['POST'])
def add_well():
    data = request.json
    database.insertar_pozo(
        departamento=data['departamento'],
        nombre=data['nombre'],
        profundidad=data['profundidad'],
        produccion=data['produccion'],
        operador=data['operador'],
        anio=data['anio'],
        estado=data['estado']
    )
    return jsonify({"success": True})

@app.route('/api/wells/<int:well_id>', methods=['DELETE'])
def delete_well(well_id):
    database.eliminar_pozo(well_id)
    return jsonify({"success": True})

@app.route('/api/pozos', methods=['GET'])
def get_pozos():
    return jsonify(database.listar_conteos())

@app.route('/api/pozos', methods=['POST'])
def save_pozos():
    data = request.json or {}
    departamento = (data.get('departamento') or '').strip()
    if not departamento:
        return jsonify({"success": False, "error": "Falta el departamento"}), 400
    try:
        pozos = int(data.get('pozos') or 0)
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Cantidad de pozos inválida"}), 400
    if pozos < 0:
        return jsonify({"success": False, "error": "La cantidad no puede ser negativa"}), 400
    database.guardar_conteo(
        departamento=departamento,
        provincia=(data.get('provincia') or '').strip(),
        distrito=(data.get('distrito') or '').strip(),
        pozos=pozos,
        petar=bool(data.get('petar'))
    )
    return jsonify({"success": True})

@app.route('/api/pozos/<int:conteo_id>', methods=['DELETE'])
def delete_pozos(conteo_id):
    database.eliminar_conteo(conteo_id)
    return jsonify({"success": True})

@app.after_request
def comprimir(respuesta):
    if (respuesta.status_code == 200
            and 'Content-Encoding' not in respuesta.headers
            and 'gzip' in request.headers.get('Accept-Encoding', '')
            and respuesta.mimetype in ('text/html', 'application/json', 'application/javascript')
            and not respuesta.direct_passthrough
            and (respuesta.content_length or 0) > 1024):
        datos = gzip.compress(respuesta.get_data(), 6)
        respuesta.set_data(datos)
        respuesta.headers['Content-Encoding'] = 'gzip'
        respuesta.headers['Vary'] = 'Accept-Encoding'
    return respuesta


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8051))
    app.run(debug=False, host='0.0.0.0', port=port)
