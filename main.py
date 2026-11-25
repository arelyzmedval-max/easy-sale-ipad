1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
68
69
70
71
72
73
74
75
76
77
78
79
80
81
82
83
84
85
86
87
88
89
90
91
92
93
94
95
96
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
