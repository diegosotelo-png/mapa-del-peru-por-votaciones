from flask import Flask, jsonify, request, send_from_directory
import os
import database

# Inicializar BD
database.crear_tabla()
database.insertar_datos_ejemplo()

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
            pointer-events: none;
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
                <h1>Mapa de Estadísticas de Votos — Perú</h1>
                <p>Keiko Fujimori vs Roberto Sánchez · resultados por departamento, provincia y distrito</p>
            </div>
            <div class="db-bar">
                <div class="db-dot" id="dbdot"></div>
                <span id="dbmsg">Cargando datos electorales...</span>
            </div>
            <div class="legend">
                <div class="lr"><div class="ld" style="background: #E8752A;"></div>Naranja: Keiko Fujimori</div>
                <div class="lr"><div class="ld" style="background: #1FA64A;"></div>Verde: Roberto Sánchez</div>
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
                    <div class="vote-card" id="districtStats"></div>
                </section>
            </div>
        </div>
    </div>
    
    <div class="modal-bg" id="mbg">
        <div class="modal">
            <h3 id="mtitle">Agregar pozo</h3>
            <div class="fr"><label>Nombre del pozo</label><input id="fn" placeholder="Ej: Pozo Talara 3"/></div>
            <div class="fr"><label>Profundidad (m)</label><input id="fd" type="number" placeholder="2500"/></div>
            <div class="fr"><label>Producción (BPD)</label><input id="fp" type="number" placeholder="1200"/></div>
            <div class="fr"><label>Operador</label><input id="fo" placeholder="Ej: Petroperú"/></div>
            <div class="fr"><label>Año inicio</label><input id="fy" type="number" placeholder="2020"/></div>
            <div class="fr">
                <label>Estado</label>
                <select id="fe">
                    <option value="Activo">Activo</option>
                    <option value="Inactivo">Inactivo</option>
                    <option value="Perforación">Perforación</option>
                </select>
            </div>
            <div class="mbtns">
                <button onclick="closeModal()">Cancelar</button>
                <button class="ok" onclick="saveWell()">Guardar</button>
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
            ubigeoDistricts: "/data/ubigeo_distritos.json",
            electionResults: "/data/election_results_ubigeo.json"
        };
        let wells = {};
        let geo = { departments: null, provinces: null, districts: null };
        let ubigeo = { departments: [], provinces: [], districts: [] };
        let electionGeo = { departments: {}, provinces: {}, districts: {} };
        let currentLevel = "departments";
        let selectedDept = null;
        let selectedProvince = null;
        const W = 360, H = 560;
        const palette = [
            "#F3D483", "#C8D99A", "#F0B088", "#A9C9EB", "#E4A7C0",
            "#9FD4C1", "#B4C4E6", "#F2C18C", "#B9D58E", "#D9B5E8",
            "#9FD6E0", "#F0A6A6", "#C7B7EA", "#A9D6A5", "#E8CB92"
        ];
        const electionResults = {
            "AMAZONAS": { winner: "sanchez", keiko: 28403, sanchez: 59302 },
            "ANCASH": { winner: "keiko", keiko: 97743, sanchez: 81477 },
            "APURIMAC": { winner: "sanchez", keiko: 13861, sanchez: 82531 },
            "AREQUIPA": { winner: "sanchez", keiko: null, sanchez: 88766 },
            "AYACUCHO": { winner: "sanchez", keiko: 23058, sanchez: 89314 },
            "CAJAMARCA": { winner: "sanchez", keiko: 89279, sanchez: 268961 },
            "CALLAO": { winner: "keiko", keiko: 119476, sanchez: null },
            "CUSCO": { winner: "sanchez", keiko: null, sanchez: 158426 },
            "HUANCAVELICA": { winner: "sanchez", keiko: 12238, sanchez: 75063 },
            "HUANUCO": { winner: "sanchez", keiko: 52987, sanchez: 102366 },
            "ICA": { winner: "keiko", keiko: 98055, sanchez: null },
            "JUNIN": { winner: "keiko", keiko: 108631, sanchez: 78227 },
            "LA LIBERTAD": { winner: "keiko", keiko: 188993, sanchez: 88291 },
            "LAMBAYEQUE": { winner: "keiko", keiko: 176103, sanchez: 71644 },
            "LIMA": { winner: "keiko", keiko: 1089534, sanchez: null },
            "LORETO": { winner: "keiko", keiko: 96815, sanchez: 33655 },
            "MADRE DE DIOS": { winner: "sanchez", keiko: 10948, sanchez: 18948 },
            "MOQUEGUA": { winner: "sanchez", keiko: null, sanchez: 14718 },
            "PASCO": { winner: "keiko", keiko: 21842, sanchez: 21606 },
            "PIURA": { winner: "keiko", keiko: 246696, sanchez: 100908 },
            "PUNO": { winner: "sanchez", keiko: null, sanchez: 162460 },
            "SAN MARTIN": { winner: "sanchez", keiko: 90655, sanchez: 93288 },
            "TACNA": { winner: "sanchez", keiko: null, sanchez: 26302 },
            "TUMBES": { winner: "keiko", keiko: 37850, sanchez: 7748 },
            "UCAYALI": { winner: "keiko", keiko: 66994, sanchez: 29038 }
        };
        const provinceElectionOverrides = {
            "PIURA|AYABACA": { winner: "sanchez" },
            "PIURA|HUANCABAMBA": { winner: "sanchez" }
        };
        const districtElectionOverrides = {};

        function setDbStatus(msg, isError = false) {
            document.getElementById("dbdot").style.background = isError ? "#f44336" : "#1D9E75";
            document.getElementById("dbmsg").textContent = msg;
        }

        async function loadWells() {
            try {
                const res = await fetch("/api/wells");
                wells = await res.json();
                const total = Object.values(wells).reduce((s, a) => s + a.length, 0);
                setDbStatus(`Base local conectada — ${total} registro${total !== 1 ? "s" : ""} de referencia`);
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
            return String(p.IDDIST || p.FIRST_IDDI || p.IDDISTRITO || "").padStart(6, "0");
        }

        function wellKeyForDept(dept) {
            const found = Object.keys(wells).find(k => norm(k) === norm(dept));
            return found || titleCase(dept);
        }

        function wellsForDept(dept) {
            return wells[wellKeyForDept(dept)] || [];
        }

        function electionForDept(dept) {
            const feature = geo.departments?.features?.find(f => norm(getDeptName(f)) === norm(dept));
            const byCode = feature ? electionGeo.departments[featureUbigeo(feature, "departments")] : null;
            return byCode || electionResults[norm(dept)] || null;
        }

        function electionForProvince(dept, province) {
            const feature = geo.provinces?.features?.find(f => norm(getDeptName(f)) === norm(dept) && norm(getProvinceName(f)) === norm(province));
            const byCode = feature ? electionGeo.provinces[featureUbigeo(feature, "provinces")] : null;
            return byCode || provinceElectionOverrides[`${norm(dept)}|${norm(province)}`] || electionForDept(dept);
        }

        function electionForDistrict(dept, province, district) {
            const feature = geo.districts?.features?.find(f =>
                norm(getDeptName(f)) === norm(dept) &&
                norm(getProvinceName(f)) === norm(province) &&
                norm(getDistrictName(f)) === norm(district)
            );
            const byCode = feature ? electionGeo.districts[featureUbigeo(feature, "districts")] : null;
            return byCode || districtElectionOverrides[`${norm(dept)}|${norm(province)}|${norm(district)}`] || electionForProvince(dept, province);
        }

        function winnerName(result) {
            if (!result) return "Sin dato";
            return result.winner === "keiko" ? "Keiko Fujimori" : "Roberto Sánchez / JP";
        }

        function resultForFeature(feature, level) {
            if (!feature) return null;
            const byCode = electionGeo[level]?.[featureUbigeo(feature, level)];
            if (byCode) return byCode;
            if (level === "departments") return electionForDept(getDeptName(feature));
            if (level === "provinces") return electionForProvince(getDeptName(feature), getProvinceName(feature));
            return electionForDistrict(getDeptName(feature), getProvinceName(feature), getDistrictName(feature));
        }

        function aggregateResults(features, level) {
            return features.reduce((acc, feature) => {
                const result = resultForFeature(feature, level);
                if (!result) return acc;
                acc.keiko += Number(result.keiko || 0);
                acc.sanchez += Number(result.sanchez || 0);
                acc.mesas += Number(result.mesas || 0);
                return acc;
            }, { keiko: 0, sanchez: 0, mesas: 0 });
        }

        function completeResult(result) {
            if (!result) return null;
            const keiko = Number(result.keiko || 0);
            const sanchez = Number(result.sanchez || 0);
            return {
                ...result,
                keiko,
                sanchez,
                mesas: Number(result.mesas || 0),
                winner: keiko >= sanchez ? "keiko" : "sanchez",
                margin: Math.abs(keiko - sanchez)
            };
        }

        function formatNumber(value) {
            return Math.round(Number(value || 0)).toLocaleString("es-PE");
        }

        function pct(value, total) {
            if (!total) return "0.0%";
            return `${((Number(value || 0) / total) * 100).toFixed(1)}%`;
        }

        function renderVoteStats(elementId, title, result, detail = "") {
            const el = document.getElementById(elementId);
            if (!el) return;
            const data = completeResult(result);
            if (!data || (!data.keiko && !data.sanchez)) {
                el.innerHTML = `
                    <div class="vote-title">${esc(title)}</div>
                    <div class="vote-foot">Sin datos de votación para esta vista</div>
                `;
                return;
            }
            const total = data.keiko + data.sanchez;
            const winner = winnerName(data);
            el.innerHTML = `
                <div class="vote-title">${esc(title)}</div>
                <div class="vote-row">
                    <span>Keiko</span>
                    <div class="vote-bar"><div class="vote-fill keiko" style="width:${pct(data.keiko, total)}"></div></div>
                    <span>${pct(data.keiko, total)}</span>
                </div>
                <div class="vote-row">
                    <span>JP</span>
                    <div class="vote-bar"><div class="vote-fill sanchez" style="width:${pct(data.sanchez, total)}"></div></div>
                    <span>${pct(data.sanchez, total)}</span>
                </div>
                <div class="vote-foot">${esc(winner)} gana · ${formatNumber(total)} votos${detail ? ` · ${esc(detail)}` : ""}</div>
            `;
        }

        function provincesForDept(dept) {
            return geo.provinces.features
                .filter(f => norm(getDeptName(f)) === norm(dept))
                .sort((a, b) => getProvinceName(a).localeCompare(getProvinceName(b), "es"));
        }

        function districtsFor(dept, province = null) {
            return geo.districts.features
                .filter(f => norm(getDeptName(f)) === norm(dept))
                .filter(f => !province || norm(getProvinceName(f)) === norm(province))
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
                const provRow = ubigeo.provinces.find(p => p.departamento_id === deptRow.id && norm(p.provincia) === norm(province));
                rows = provRow ? rows.filter(d => d.provincia_id === provRow.id) : [];
            }
            return rows.sort((a, b) => a.distrito.localeCompare(b.distrito, "es"));
        }

        function hasWellsForFeature(feature) {
            return wellsForDept(getDeptName(feature)).length > 0;
        }

        function getFill(feature, index, level) {
            const result = resultForFeature(feature, level);
            if (!result) return palette[index % palette.length];
            return result.winner === "keiko" ? "#E8752A" : "#1FA64A";
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

        function boxesOverlap(a, b) {
            return !(a.x2 < b.x1 || a.x1 > b.x2 || a.y2 < b.y1 || a.y1 > b.y2);
        }

        function buildLabels(features, level, pathFn) {
            const fontSize = labelFontSize(level, features.length);
            const items = features.map((feature, index) => {
                const [baseX, baseY] = pathFn.centroid(feature);
                const [nudgeX, nudgeY] = labelCenterNudge(feature, level);
                const x = baseX + nudgeX;
                const y = baseY + nudgeY;
                const bounds = pathFn.bounds(feature);
                const area = Math.abs((bounds[1][0] - bounds[0][0]) * (bounds[1][1] - bounds[0][1]));
                const lines = splitLabel(getAreaName(feature, level), level);
                const maxLine = Math.max(...lines.map(line => line.length));
                const width = maxLine * fontSize * 0.64 + 8;
                const height = lines.length * fontSize * 1.18 + 6;
                return {
                    feature,
                    index,
                    x,
                    y,
                    area,
                    lines,
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
            }).sort((a, b) => b.area - a.area);

            const placed = [];
            const skipped = [];
            items.forEach(item => {
                const insideCanvas = item.box.x1 >= 0 && item.box.y1 >= 0 && item.box.x2 <= W && item.box.y2 <= H;
                const collides = placed.some(other => boxesOverlap(item.box, other.box));
                if (insideCanvas && !collides) placed.push(item);
                else skipped.push(item);
            });
            return { placed, skipped, items };
        }

        function movedLabel(item, dx, dy, scale = 1) {
            const fontSize = item.fontSize * scale;
            const width = item.width * scale;
            const height = item.height * scale;
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
                            const insideCanvas = candidate.box.x1 >= 2 && candidate.box.y1 >= 2 && candidate.box.x2 <= W - 2 && candidate.box.y2 <= H - 2;
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
                                const insideCanvas = candidate.box.x1 >= 2 && candidate.box.y1 >= 2 && candidate.box.x2 <= W - 2 && candidate.box.y2 <= H - 2;
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

        function distributeCallouts(items, side) {
            const top = 28;
            const bottom = H - 28;
            const sorted = items
                .filter(item => item.side === side)
                .sort((a, b) => a.y - b.y);
            sorted.forEach((item, index) => {
                item.labelY = top + ((index + 0.5) * (bottom - top)) / Math.max(sorted.length, 1);
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
            if (statsConfig?.id) renderVoteStats(statsConfig.id, statsConfig.title, statsConfig.result, statsConfig.detail);

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
                    return "#ffffff";
                })
                .attr("stroke-width", d => {
                    if (level === "departments" && norm(getDeptName(d)) === norm(selectedDept)) return 2.4;
                    if (level === "provinces" && norm(getProvinceName(d)) === norm(selectedProvince)) return 2.4;
                    return level === "districts" ? 1.15 : 1.35;
                })
                .attr("data-stroke-width", d => {
                    if (level === "departments" && norm(getDeptName(d)) === norm(selectedDept)) return 2.4;
                    if (level === "provinces" && norm(getProvinceName(d)) === norm(selectedProvince)) return 2.4;
                    return level === "districts" ? 1.15 : 1.35;
                })
                .attr("fill", (d, i) => getFill(d, i, level))
                .attr("class", "area-path " + level)
                .style("cursor", "pointer")
                .on("mouseover", function (e, d) {
                    d3.select(this).attr("fill", "#4fc3f7");
                    if (statsConfig?.id) {
                        renderVoteStats(
                            statsConfig.id,
                            getAreaName(d, level),
                            resultForFeature(d, level),
                            "vista seleccionada"
                        );
                    }
                })
                .on("mouseout", function (e, d) {
                    const i = features.indexOf(d);
                    d3.select(this).attr("fill", getFill(d, i, level));
                    if (statsConfig?.id) renderVoteStats(statsConfig.id, statsConfig.title, statsConfig.result, statsConfig.detail);
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
                const labelDivisor = Math.pow(k, 1.25);
                const strokeDivisor = Math.max(k, 1);
                g.selectAll("path.area-path,path.callout-line")
                    .attr("stroke-width", function () {
                        return Number(this.dataset.strokeWidth || 1.2) / strokeDivisor;
                    });
                g.selectAll("text.area-label,text.callout-label")
                    .attr("font-size", function () {
                        return Number(this.dataset.fontSize || 8) / labelDivisor;
                    })
                    .attr("stroke-width", function () {
                        return Number(this.dataset.strokeWidth || 3) / Math.pow(k, 1.15);
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
            document.getElementById("deptMeta").textContent = "Naranja Keiko · verde JP";
            const selectedFeature = selectedDept
                ? geo.departments.features.find(f => norm(getDeptName(f)) === norm(selectedDept))
                : null;
            const statsTitle = selectedFeature ? titleCase(getDeptName(selectedFeature)) : "Perú completo";
            const statsResult = selectedFeature
                ? resultForFeature(selectedFeature, "departments")
                : aggregateResults(geo.departments.features, "departments");
            renderMap("deptMap", geo.departments.features, "departments", d => {
                showDepartment(getDeptName(d));
            }, geo.departments, {
                id: "deptStats",
                title: statsTitle,
                result: statsResult,
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
        }

        function showDepartments() {
            selectedDept = null;
            selectedProvince = null;
            renderDepartments();
            clearProvinces();
            clearDistricts();
        }

        function showDepartment(dept) {
            selectedDept = dept;
            selectedProvince = null;
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
            document.getElementById("provinceMeta").textContent = `Naranja Keiko · verde JP · ${provinceCount} provincias · ${districtCount} distritos`;
            const selectedFeature = selectedProvince
                ? features.find(f => norm(getProvinceName(f)) === norm(selectedProvince))
                : null;
            renderMap("provinceMap", features, "provinces", d => {
                showProvince(dept, getProvinceName(d));
            }, null, {
                id: "provinceStats",
                title: selectedFeature ? titleCase(getProvinceName(selectedFeature)) : niceDept,
                result: selectedFeature ? resultForFeature(selectedFeature, "provinces") : aggregateResults(features, "provinces"),
                detail: selectedFeature ? "provincia" : `${provinceCount} provincias`
            });
        }

        function showProvince(dept, province) {
            selectedDept = dept;
            selectedProvince = province;
            renderDepartments();
            renderProvinces(dept);
            renderDistricts(dept, province);
        }

        function renderDistricts(dept, province) {
            const features = districtsFor(dept, province);
            const districtCount = districtRowsFor(dept, province).length;
            const result = electionForProvince(dept, province);
            currentLevel = "districts";
            document.getElementById("districtTitle").textContent = `Distritos de ${titleCase(province)}`;
            document.getElementById("districtMeta").textContent = `${winnerName(result)} en ${titleCase(province)} · ${districtCount} distritos`;
            renderMap("districtMap", features, "districts", null, null, {
                id: "districtStats",
                title: titleCase(province),
                result: aggregateResults(features, "districts"),
                detail: `${districtCount} distritos`
            });
        }

        function openModal(dept) {
            document.getElementById("mtitle").textContent = "Agregar pozo — " + dept;
            document.getElementById("mbg").dataset.dept = dept;
            ["fn", "fd", "fp", "fo", "fy"].forEach(id => document.getElementById(id).value = "");
            document.getElementById("fe").value = "Activo";
            document.getElementById("mbg").classList.add("open");
        }

        function closeModal() {
            document.getElementById("mbg").classList.remove("open");
        }

        async function saveWell() {
            const dept = document.getElementById("mbg").dataset.dept;
            const nombre = document.getElementById("fn").value.trim();
            if (!nombre) { alert("Ingresa el nombre del pozo"); return; }
            
            try {
                const res = await fetch("/api/wells", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        departamento: dept,
                        nombre: nombre,
                        profundidad: Number(document.getElementById("fd").value) || 0,
                        produccion: Number(document.getElementById("fp").value) || 0,
                        operador: document.getElementById("fo").value || "—",
                        anio: Number(document.getElementById("fy").value) || 0,
                        estado: document.getElementById("fe").value
                    })
                });
                if (!res.ok) throw new Error("Error al guardar");
                closeModal();
                await loadWells();
                redrawMap();
                if (selectedDept && selectedProvince) showProvince(selectedDept, selectedProvince);
                else if (selectedDept) showDepartment(selectedDept);
                else showDepartments();
            } catch (e) {
                alert("Error: " + e.message);
            }
        }

        async function delWell(dept, id) {
            if (!confirm("¿Eliminar este pozo?")) return;
            try {
                const res = await fetch("/api/wells/" + id, { method: "DELETE" });
                if (!res.ok) throw new Error("Error al eliminar");
                await loadWells();
                redrawMap();
                if (selectedDept && selectedProvince) showProvince(selectedDept, selectedProvince);
                else if (selectedDept) showDepartment(selectedDept);
                else showDepartments();
            } catch (e) {
                alert("Error: " + e.message);
            }
        }

        async function init() {
            await loadWells();

            try {
                const [departments, provinces, districts, ubigeoDepartments, ubigeoProvinces, ubigeoDistricts, electionResultsByUbigeo] = await Promise.all([
                    fetch(DATA_URLS.departments).then(r => r.json()),
                    fetch(DATA_URLS.provinces).then(r => r.json()),
                    fetch(DATA_URLS.districts).then(r => r.json()),
                    fetch(DATA_URLS.ubigeoDepartments).then(r => r.json()),
                    fetch(DATA_URLS.ubigeoProvinces).then(r => r.json()),
                    fetch(DATA_URLS.ubigeoDistricts).then(r => r.json()),
                    fetch(DATA_URLS.electionResults).then(r => r.json())
                ]);
                geo = { departments, provinces, districts };
                electionGeo = {
                    departments: electionResultsByUbigeo.departments || {},
                    provinces: electionResultsByUbigeo.provinces || {},
                    districts: electionResultsByUbigeo.districts || {}
                };
                ubigeo = {
                    departments: ubigeoDepartments.ubigeo_departamentos,
                    provinces: ubigeoProvinces.ubigeo_provincias,
                    districts: ubigeoDistricts.ubigeo_distritos
                };
                showDepartments();
                setDbStatus("Datos electorales cargados — departamentos, provincias y distritos");

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

@app.route('/data/<path:filename>')
def data_file(filename):
    allowed = {
        'd3.v7.min.js',
        'peru_departamental_simple.geojson',
        'peru_provincial_simple.geojson',
        'peru_distrital_simple.geojson',
        'ubigeo_departamentos.json',
        'ubigeo_provincias.json',
        'ubigeo_distritos.json',
        'election_results_ubigeo.json',
    }
    if filename not in allowed:
        return jsonify({"error": "Archivo no permitido"}), 404
    return send_from_directory(BASE_DIR, filename)

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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8051))
    app.run(debug=False, host='0.0.0.0', port=port)
