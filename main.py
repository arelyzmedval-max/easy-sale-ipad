import os
from flask import Flask, jsonify, render_template_string, request, session
from database import Database
from views.login import LoginView
from views.inicio import InicioView
from views.ventas import VentasView
from views.inventario import InventarioView
from views.historial import HistorialView
from views.reportes import ReportesView
from views.usuarios import UsuariosView
from views.caja import CajaView
from views.configuracion import ConfiguracionView


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "easy-sale-ipad-secret-key")

db = Database()


def _crear_vista(index, usuario_actual):
    if index == 0:
        return InicioView(db, usuario_actual)
    if index == 1:
        return VentasView(db, usuario_actual)
    if index == 2:
        return InventarioView(db)
    if index == 3:
        return HistorialView(db)
    if index == 4:
        return ReportesView(db)
    if index == 5:
        return UsuariosView(db)
    if index == 6:
        return CajaView(db, usuario_actual)
    if index == 7:
        return InicioView(db, usuario_actual)
    if index == 8:
        return ConfiguracionView(db)
    return InicioView(db, usuario_actual)


def _render_app_shell(usuario_actual=None):
    secciones = [
        {"index": 0, "label": "Inicio"},
        {"index": 1, "label": "Ventas"},
        {"index": 2, "label": "Inventario"},
        {"index": 3, "label": "Historial"},
        {"index": 4, "label": "Reportes"},
        {"index": 5, "label": "Usuarios"},
        {"index": 6, "label": "Caja"},
        {"index": 7, "label": "Clientes"},
        {"index": 8, "label": "Configuración"},
    ]
    usuario_json = usuario_actual if usuario_actual else {}

    html = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Easy Sale - Punto de Venta</title>
  <style>
    * { box-sizing: border-box; }
    body {
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif;
      background: #f3f4f6;
      color: #111827;
    }
    .header {
      background: #1e3a8a;
      color: #ffffff;
      padding: 10px 16px;
      display: -webkit-flex;
      display: flex;
      -webkit-justify-content: space-between;
      justify-content: space-between;
      -webkit-align-items: center;
      align-items: center;
    }
    .header-title {
      font-size: 16px;
      font-weight: 700;
    }
    .header-user {
      display: -webkit-flex;
      display: flex;
      -webkit-align-items: center;
      align-items: center;
      font-size: 14px;
    }
    .btn-logout {
      margin-left: 12px;
      background: #dc2626;
      color: #ffffff;
      border: none;
      border-radius: 6px;
      padding: 6px 10px;
      font-size: 13px;
      font-weight: 600;
    }
    .layout {
      display: -webkit-flex;
      display: flex;
      min-height: calc(100vh - 48px);
    }
    .sidebar {
      width: 150px;
      background: #ffffff;
      border-right: 1px solid #e5e7eb;
      padding: 8px 0;
      -webkit-flex-shrink: 0;
      flex-shrink: 0;
    }
    .nav-btn {
      display: block;
      width: 100%;
      text-align: left;
      background: transparent;
      border: none;
      padding: 12px 14px;
      font-size: 14px;
      font-weight: 600;
      color: #374151;
    }
    .nav-btn.active {
      background: #dbeafe;
      color: #1d4ed8;
      border-left: 4px solid #1d4ed8;
    }
    .main-content {
      -webkit-flex: 1;
      flex: 1;
      padding: 20px;
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
    }
    .box {
      background: #ffffff;
      border-radius: 10px;
      padding: 20px;
      box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
      max-width: 1040px;
    }
    .section-header {
      margin-bottom: 16px;
      padding-bottom: 10px;
      border-bottom: 1px solid #e5e7eb;
    }
    .section-title {
      margin: 0 0 4px 0;
      font-size: 20px;
      font-weight: 700;
      color: #111827;
    }
    .section-subtitle {
      margin: 0;
      font-size: 13px;
      color: #6b7280;
    }
    .cards-grid {
      display: -webkit-flex;
      display: flex;
      -webkit-flex-wrap: wrap;
      flex-wrap: wrap;
      margin: 0 -6px 16px -6px;
    }
    .metric-card {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      padding: 14px 16px;
      margin: 6px;
      min-width: 190px;
      -webkit-flex: 1;
      flex: 1;
    }
    .metric-label {
      font-size: 13px;
      font-weight: 600;
      color: #4b5563;
      margin-bottom: 6px;
    }
    .metric-value {
      font-size: 22px;
      font-weight: 700;
      color: #1d4ed8;
    }
    .metric-value.blue { color: #2563eb; }
    .metric-value.orange { color: #d97706; }
    .metric-value.red { color: #dc2626; }
    .metric-value.green { color: #15803d; }

    .alert-card {
      background: #ffffff;
      border: 1px solid #e5e7eb;
      border-radius: 8px;
      padding: 12px 14px;
      margin-bottom: 8px;
      display: -webkit-flex;
      display: flex;
      -webkit-justify-content: space-between;
      justify-content: space-between;
      -webkit-align-items: center;
      align-items: center;
    }
    .alert-title {
      font-size: 14px;
      font-weight: 700;
      color: #111827;
      margin-bottom: 2px;
    }
    .alert-sub {
      font-size: 12px;
      color: #6b7280;
    }
    .badge-danger {
      background: #fee2e2;
      color: #991b1b;
      font-size: 12px;
      font-weight: 700;
      padding: 5px 10px;
      border-radius: 999px;
      white-space: nowrap;
      margin-left: 10px;
    }
    .badge-info {
      background: #dbeafe;
      color: #1e40af;
      font-size: 12px;
      font-weight: 700;
      padding: 4px 8px;
      border-radius: 999px;
      white-space: nowrap;
    }
    .data-table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 8px;
      margin-bottom: 16px;
      font-size: 13px;
    }
    .data-table th {
      background: #f1f5f9;
      color: #334155;
      font-weight: 700;
      text-align: left;
      padding: 10px 12px;
      border-bottom: 2px solid #cbd5e1;
    }
    .data-table td {
      padding: 10px 12px;
      border-bottom: 1px solid #e5e7eb;
      color: #1f2937;
      vertical-align: top;
    }
    .kv-list {
      border: 1px solid #e5e7eb;
      border-radius: 8px;
      overflow: hidden;
      margin-bottom: 14px;
    }
    .kv-row {
      display: -webkit-flex;
      display: flex;
      -webkit-justify-content: space-between;
      justify-content: space-between;
      padding: 10px 14px;
      border-bottom: 1px solid #f1f5f9;
      font-size: 13px;
    }
    .kv-row:last-child { border-bottom: none; }
    .kv-key { font-weight: 700; color: #374151; margin-right: 12px; }
    .kv-val { color: #111827; text-align: right; word-break: break-word; }
    .empty-msg {
      padding: 14px;
      background: #f9fafb;
      border: 1px dashed #d1d5db;
      border-radius: 8px;
      color: #4b5563;
      font-size: 13px;
      margin-bottom: 12px;
    }
    .login-box {
      max-width: 380px;
      margin: 40px auto;
      background: #ffffff;
      padding: 24px;
      border-radius: 10px;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.12);
    }
    .field {
      margin-bottom: 12px;
    }
    .field label {
      display: block;
      font-size: 13px;
      font-weight: 600;
      margin-bottom: 4px;
    }
    .field input {
      width: 100%;
      padding: 9px 10px;
      font-size: 15px;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
    }
    .btn-primary {
      background: #1d4ed8;
      color: #ffffff;
      border: none;
      border-radius: 6px;
      padding: 10px 16px;
      font-size: 14px;
      font-weight: 700;
    }
    .error-msg {
      color: #dc2626;
      font-size: 13px;
      margin-bottom: 10px;
      min-height: 18px;
    }
  </style>
</head>
<body>
  <div id="app-root"></div>

  <script>
    var usuarioActual = {{ usuario_json | tojson }};
    var secciones = {{ secciones | tojson }};
    var vistaActual = 0;

    function escapeHtml(val) {
      if (val === null || val === undefined) return "";
      return String(val)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
    }

    function formatLabel(key) {
      return String(key || "")
        .replace(/_/g, " ")
        .replace(/\b\w/g, function (c) { return c.toUpperCase(); });
    }

    function formatValue(val) {
      if (val === null || val === undefined || val === "") return "-";
      if (typeof val === "boolean") return val ? "Sí" : "No";
      if (typeof val === "object") {
        if (Array.isArray(val)) return val.length + " elemento(s)";
        return Object.keys(val).map(function (k) {
          return formatLabel(k) + ": " + formatValue(val[k]);
        }).join(" | ");
      }
      return escapeHtml(val);
    }

    function renderTablaArray(items) {
      if (!Array.isArray(items) || items.length === 0) {
        return '<div class="empty-msg">No hay registros disponibles para mostrar.</div>';
      }
      if (typeof items[0] !== "object" || items[0] === null) {
        var listHtml = '<ul style="margin:0 0 14px 0;padding-left:20px;">';
        for (var i = 0; i < items.length; i++) {
          listHtml += '<li style="margin-bottom:4px;">' + escapeHtml(items[i]) + '</li>';
        }
        return listHtml + '</ul>';
      }

      var cols = [];
      for (var r = 0; r < items.length; r++) {
        var row = items[r];
        if (row && typeof row === "object") {
          for (var k in row) {
            if (Object.prototype.hasOwnProperty.call(row, k) && cols.indexOf(k) === -1) {
              cols.push(k);
            }
          }
        }
      }

      var html = '<div style="overflow-x:auto;"><table class="data-table"><thead><tr>';
      for (var c = 0; c < cols.length; c++) {
        html += '<th>' + escapeHtml(formatLabel(cols[c])) + '</th>';
      }
      html += '</tr></thead><tbody>';

      for (var i = 0; i < items.length; i++) {
        var item = items[i] || {};
        html += '<tr>';
        for (var c = 0; c < cols.length; c++) {
          var colName = cols[c];
          html += '<td>' + formatValue(item[colName]) + '</td>';
        }
        html += '</tr>';
      }
      html += '</tbody></table></div>';
      return html;
    }

    function renderDiccionario(obj) {
      if (!obj || typeof obj !== "object" || Array.isArray(obj)) {
        return '<div class="empty-msg">' + formatValue(obj) + '</div>';
      }
      var keys = Object.keys(obj);
      if (keys.length === 0) {
        return '<div class="empty-msg">Sin información adicional.</div>';
      }

      var html = "";
      var simpleKeys = [];

      for (var i = 0; i < keys.length; i++) {
        var k = keys[i];
        var v = obj[k];
        if (Array.isArray(v)) {
          html += '<h4 style="margin:14px 0 6px 0;font-size:15px;">' + escapeHtml(formatLabel(k)) + '</h4>';
          html += renderTablaArray(v);
        } else if (v && typeof v === "object") {
          html += '<h4 style="margin:14px 0 6px 0;font-size:15px;">' + escapeHtml(formatLabel(k)) + '</h4>';
          html += renderDiccionario(v);
        } else {
          simpleKeys.push(k);
        }
      }

      if (simpleKeys.length > 0) {
        html = '<div class="kv-list">' + simpleKeys.map(function (k) {
          return '<div class="kv-row">' +
            '<span class="kv-key">' + escapeHtml(formatLabel(k)) + '</span>' +
            '<span class="kv-val">' + formatValue(obj[k]) + '</span>' +
          '</div>';
        }).join("") + '</div>' + html;
      }

      return html;
    }

    function renderInicio(seccion, payload) {
      var data = payload || {};
      var saludo = data.saludo || ("Sección: " + seccion);
      var subtitulo = data.subtitulo || "Resumen general del sistema.";
      var metricas = Array.isArray(data.metricas) ? data.metricas : [];
      var alertas = Array.isArray(data.alertas) ? data.alertas : [];

      var html =
        '<div class="section-header">' +
          '<h2 class="section-title">' + escapeHtml(saludo) + '</h2>' +
          '<p class="section-subtitle">' + escapeHtml(subtitulo) + '</p>' +
        '</div>';

      if (metricas.length > 0) {
        html += '<div class="cards-grid">';
        for (var i = 0; i < metricas.length; i++) {
          var m = metricas[i] || {};
          var colorClass = ["blue", "orange", "red", "green"].indexOf(String(m.color || "").toLowerCase()) !== -1
            ? String(m.color).toLowerCase()
            : "blue";
          html +=
            '<div class="metric-card">' +
              '<div class="metric-label">' + escapeHtml(m.titulo || "Métrica") + '</div>' +
              '<div class="metric-value ' + colorClass + '">' + escapeHtml(m.valor) + '</div>' +
            '</div>';
        }
        html += '</div>';
      }

      html +=
        '<h3 style="margin:14px 0 4px 0;font-size:16px;">' +
          escapeHtml(data.titulo_alertas || "Alertas de Inventario") +
        '</h3>' +
        '<p class="section-subtitle" style="margin-bottom:10px;">' +
          escapeHtml(data.descripcion_alertas || "") +
        '</p>';

      if (alertas.length === 0) {
        html += '<div class="empty-msg">No hay alertas pendientes por el momento.</div>';
      } else {
        for (var j = 0; j < alertas.length; j++) {
          var a = alertas[j] || {};
          var tituloAlerta = a.titulo || a.nombre || ("Producto " + (a.codigo || ""));
          var subAlerta = a.subtitulo || ((a.descripcion || "") + (a.precio ? " | Precio: $" + a.precio : ""));
          var badgeText = a.badge || (a.stock_str ? "¡Quedan " + a.stock_str + "!" : "Alerta");

          html +=
            '<div class="alert-card">' +
              '<div>' +
                '<div class="alert-title">' + escapeHtml(tituloAlerta) + '</div>' +
                '<div class="alert-sub">' + escapeHtml(subAlerta) + '</div>' +
              '</div>' +
              '<span class="badge-danger">' + escapeHtml(badgeText) + '</span>' +
            '</div>';
        }
      }

      return html;
    }

    function renderSeccion(index, seccion, payload) {
      if (index === 0) {
        return renderInicio(seccion, payload);
      }

      var header =
        '<div class="section-header">' +
          '<h2 class="section-title">' + escapeHtml(seccion || "Sección") + '</h2>' +
          '<p class="section-subtitle">Vista web adaptada para Easy Sale iPad.</p>' +
        '</div>';

      if (payload === null || payload === undefined) {
        return header + '<div class="empty-msg">Sin datos disponibles para esta sección.</div>';
      }

      if (typeof payload === "object" && Object.keys(payload).length === 1 && payload.estado === "cargada") {
        return header +
          '<div class="empty-msg">La sección <strong>' + escapeHtml(seccion) + '</strong> está conectada y lista para cargar sus datos o controles interactivos.</div>';
      }

      if (Array.isArray(payload)) {
        return header + renderTablaArray(payload);
      }

      if (typeof payload === "object") {
        return header + renderDiccionario(payload);
      }

      return header + '<div class="empty-msg">' + escapeHtml(payload) + '</div>';
    }

    function renderLogin(errorText) {
      var root = document.getElementById("app-root");
      root.innerHTML =
        '<div class="login-box">' +
          '<h2 style="margin-top:0;">Iniciar Sesión - Easy Sale</h2>' +
          '<div class="field"><label>Usuario</label><input type="text" id="txt-usuario"></div>' +
          '<div class="field"><label>Contraseña</label><input type="password" id="txt-password"></div>' +
          '<div id="lbl-error" class="error-msg">' + escapeHtml(errorText || "") + '</div>' +
          '<button type="button" class="btn-primary" style="width:100%;" onclick="doLogin()">Ingresar</button>' +
        '</div>';
    }

    function doLogin() {
      var u = document.getElementById("txt-usuario").value;
      var p = document.getElementById("txt-password").value;
      var xhr = new XMLHttpRequest();
      xhr.open("POST", "/api/login", true);
      xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
      xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
          var res = JSON.parse(xhr.responseText);
          if (res.ok) {
            usuarioActual = res.usuario;
            vistaActual = 0;
            renderDashboard();
            cargarVista(0);
          } else {
            renderLogin(res.error);
          }
        }
      };
      xhr.send(JSON.stringify({ usuario: u, password: p }));
    }

    function doLogout() {
      var xhr = new XMLHttpRequest();
      xhr.open("POST", "/api/logout", true);
      xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
          usuarioActual = null;
          renderLogin("");
        }
      };
      xhr.send();
    }

    function renderDashboard() {
      var root = document.getElementById("app-root");
      var navHtml = "";
      for (var i = 0; i < secciones.length; i++) {
        var s = secciones[i];
        var activeClass = (s.index === vistaActual) ? "nav-btn active" : "nav-btn";
        navHtml += '<button type="button" class="' + activeClass + '" onclick="seleccionarVista(' + s.index + ')">' + escapeHtml(s.label) + '</button>';
      }
      var nombre = (usuarioActual && usuarioActual.nombre) ? usuarioActual.nombre : "";
      var rol = (usuarioActual && usuarioActual.rol) ? usuarioActual.rol : "";

      root.innerHTML =
        '<div class="header">' +
          '<div class="header-title">Easy Sale - Punto de Venta</div>' +
          '<div class="header-user">' +
            '<span>Usuario: ' + escapeHtml(nombre) + ' (' + escapeHtml(rol) + ')</span>' +
            '<button type="button" class="btn-logout" onclick="doLogout()">Cerrar Sesión</button>' +
          '</div>' +
        '</div>' +
        '<div class="layout">' +
          '<div class="sidebar">' + navHtml + '</div>' +
          '<div class="main-content"><div id="vista-body" class="box">Cargando...</div></div>' +
        '</div>';
    }

    function seleccionarVista(index) {
      vistaActual = index;
      renderDashboard();
      cargarVista(index);
    }

    function cargarVista(index) {
      var body = document.getElementById("vista-body");
      if (body) {
        body.innerHTML = '<div class="empty-msg">Cargando sección...</div>';
      }
      var xhr = new XMLHttpRequest();
      xhr.open("GET", "/api/vista/" + index, true);
      xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
          var currentBody = document.getElementById("vista-body");
          if (!currentBody) return;
          if (xhr.status === 200) {
            var data = JSON.parse(xhr.responseText);
            currentBody.innerHTML = renderSeccion(data.index, data.seccion, data.payload);
          } else {
            currentBody.innerHTML = '<div class="error-msg">Error al cargar la sección (código ' + xhr.status + ').</div>';
          }
        }
      };
      xhr.send();
    }

    if (usuarioActual && usuarioActual.id_usuario) {
      renderDashboard();
      cargarVista(0);
    } else {
      renderLogin("");
    }
  </script>
</body>
</html>"""

    return render_template_string(
        html,
        usuario_json=usuario_json,
        secciones=secciones,
    )


@app.route("/")
def index():
    usuario_actual = session.get("usuario_actual")
    return _render_app_shell(usuario_actual)


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    login_view = LoginView(db)
    res = login_view.intentar_login(data.get("usuario"), data.get("password"))
    if res.get("ok"):
        session["usuario_actual"] = res.get("usuario")
    return jsonify(res)


@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.pop("usuario_actual", None)
    return jsonify({"ok": True})


@app.route("/api/vista/<int:index>", methods=["GET"])
def api_vista(index):
    usuario_actual = session.get("usuario_actual")
    if not usuario_actual:
        return jsonify({"ok": False, "error": "Sesión no iniciada"}), 401

    vista = _crear_vista(index, usuario_actual)
    nombres = {
        0: "Inicio",
        1: "Ventas",
        2: "Inventario",
        3: "Historial",
        4: "Reportes",
        5: "Usuarios",
        6: "Caja",
        7: "Clientes",
        8: "Configuración",
    }

    if index == 0 and hasattr(vista, "cargar_datos_inicio"):
        payload = vista.cargar_datos_inicio()
    elif index == 2 and hasattr(vista, "cargar_productos"):
        payload = {"productos": vista.cargar_productos(), "formulario": vista.obtener_estado_formulario()}
    elif index == 3 and hasattr(vista, "mostrar_historial"):
        payload = {"ventas": vista.mostrar_historial()}
    elif index == 6 and hasattr(vista, "verificar_estado_caja"):
        payload = vista.verificar_estado_caja()
    elif index == 8 and hasattr(vista, "cargar_configuracion"):
        payload = vista.cargar_configuracion()
    else:
        payload = {"estado": "cargada"}

    return jsonify({
        "ok": True,
        "index": index,
        "seccion": nombres.get(index, "Inicio"),
        "payload": payload,
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
