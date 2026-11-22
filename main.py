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
      max-width: 960px;
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
    pre {
      background: #f8fafc;
      padding: 12px;
      border-radius: 8px;
      overflow-x: auto;
      font-size: 13px;
    }
  </style>
</head>
<body>
  <div id="app-root"></div>

  <script>
    var usuarioActual = {{ usuario_json | tojson }};
    var secciones = {{ secciones | tojson }};
    var vistaActual = 0;

    function renderLogin(errorText) {
      var root = document.getElementById("app-root");
      root.innerHTML =
        '<div class="login-box">' +
          '<h2 style="margin-top:0;">Iniciar Sesión - Easy Sale</h2>' +
          '<div class="field"><label>Usuario</label><input type="text" id="txt-usuario"></div>' +
          '<div class="field"><label>Contraseña</label><input type="password" id="txt-password"></div>' +
          '<div id="lbl-error" class="error-msg">' + (errorText || "") + '</div>' +
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
        navHtml += '<button type="button" class="' + activeClass + '" onclick="seleccionarVista(' + s.index + ')">' + s.label + '</button>';
      }
      var nombre = (usuarioActual && usuarioActual.nombre) ? usuarioActual.nombre : "";
      var rol = (usuarioActual && usuarioActual.rol) ? usuarioActual.rol : "";

      root.innerHTML =
        '<div class="header">' +
          '<div class="header-title">Easy Sale - Punto de Venta</div>' +
          '<div class="header-user">' +
            '<span>Usuario: ' + nombre + ' (' + rol + ')</span>' +
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
      var xhr = new XMLHttpRequest();
      xhr.open("GET", "/api/vista/" + index, true);
      xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
          var data = JSON.parse(xhr.responseText);
          var body = document.getElementById("vista-body");
          if (body) {
            body.innerHTML =
              '<h3 style="margin-top:0;">Sección: ' + data.seccion + '</h3>' +
              '<pre>' + JSON.stringify(data.payload, null, 2) + '</pre>';
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
