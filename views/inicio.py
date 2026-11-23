import flet as ft


class InicioView:
    def __init__(self, db, usuario):
        self.db = db
        self.usuario = usuario or {}
        self.metricas = []
        self.alertas = []
        self.datos_inicio = {
            "saludo": f"¡Bienvenido de nuevo, {self.usuario.get('nombre', 'Admin')}!",
            "subtitulo": "Aquí tienes el resumen y las alertas importantes de tu inventario.",
            "titulo_alertas": "⚠️ Alertas de Reabastecimiento (Stock Bajo)",
            "descripcion_alertas": "Productos con 2 unidades o menos que requieren pedido urgente:",
            "metricas": [],
            "alertas": [],
        }

    def crear_tarjeta_metrica(self, titulo, valor, icono, color):
        return {
            "titulo": titulo,
            "valor": valor,
            "icono": icono,
            "color": color,
        }

    def cargar_datos_inicio(self):
        try:
            self.metricas = []
            self.alertas = []

            # 1. Obtener total de productos
            res_total = self.db.obtener_resultados("SELECT COUNT(*) as total FROM productos")
            total_productos = res_total[0]["total"] if res_total else 0

            # 2. Obtener productos con stock bajo (<= 2)
            productos_bajos = self.db.obtener_resultados(
                "SELECT * FROM productos WHERE stock <= 2 ORDER BY stock ASC"
            )
            cantidad_bajos = len(productos_bajos) if productos_bajos else 0

            # 3. Obtener total de deuda pendiente en fiados (protegido si aún no existe)
            try:
                res_deuda = self.db.obtener_resultados(
                    "SELECT COALESCE(SUM(total_fiado - abono), 0) as deuda_total "
                    "FROM creditos WHERE estado = 'Pendiente'"
                )
                deuda_total = float(res_deuda[0]["deuda_total"]) if res_deuda else 0.0
            except Exception:
                deuda_total = 0.0

            self.metricas = [
                self.crear_tarjeta_metrica("Total Productos", str(total_productos), "inventory", "blue"),
                self.crear_tarjeta_metrica("Productos por Agotar", str(cantidad_bajos), "warning_amber", "orange"),
                self.crear_tarjeta_metrica("Total Fiados Pendientes", f"${deuda_total:.2f}", "account_balance_wallet", "red"),
            ]

            if productos_bajos:
                for p in productos_bajos:
                    stock_val = float(p["stock"])
                    if p.get("tipo_venta") == "por kilo":
                        stock_str = f"{stock_val:.3f} kg"
                    else:
                        stock_str = str(int(stock_val) if stock_val.is_integer() else stock_val)

                    descripcion = p.get("descripcion") or "Sin descripción"
                    precio = float(p.get("precio") or 0.0)

                    self.alertas.append({
                        "codigo": str(p.get("codigo", "")),
                        "nombre": str(p.get("nombre", "")),
                        "titulo": f"{p.get('nombre', '')} (Código: {p.get('codigo', '')})",
                        "subtitulo": f"Descripción: {descripcion} | Precio: ${precio:.2f}",
                        "badge": f"¡Quedan {stock_str}!",
                        "stock_str": stock_str,
                    })

            nombre_usuario = self.usuario.get("nombre") or "Admin"
            self.datos_inicio = {
                "saludo": f"¡Bienvenido de nuevo, {nombre_usuario}!",
                "subtitulo": "Aquí tienes el resumen y las alertas importantes de tu inventario.",
                "titulo_alertas": "⚠️ Alertas de Reabastecimiento (Stock Bajo)",
                "descripcion_alertas": "Productos con 2 unidades o menos que requieren pedido urgente:",
                "metricas": self.metricas,
                "alertas": self.alertas,
            }
            return self.datos_inicio
        except Exception as ex:
            print(f"Error al cargar datos de inicio: {ex}")
            return self.datos_inicio

    def _color_flet(self, color_str):
        mapa = {
            "blue": ft.Colors.BLUE_600,
            "orange": ft.Colors.ORANGE_700,
            "red": ft.Colors.RED_600,
        }
        return mapa.get((color_str or "").lower(), ft.Colors.BLUE_600)

    def _icono_flet(self, icono_str):
        mapa = {
            "inventory": ft.Icons.INVENTORY_2,
            "warning_amber": ft.Icons.WARNING_AMBER,
            "account_balance_wallet": ft.Icons.ACCOUNT_BALANCE_WALLET,
        }
        return mapa.get((icono_str or "").lower(), ft.Icons.INFO)

    def construir_vista(self):
        datos = self.cargar_datos_inicio()

        tarjetas_metricas = []
        for m in datos.get("metricas", []):
            color = self._color_flet(m.get("color"))
            tarjetas_metricas.append(
                ft.Card(
                    content=ft.Container(
                        padding=16,
                        width=240,
                        content=ft.Column(
                            spacing=6,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text(m.get("titulo", ""), size=14, weight=ft.FontWeight.W_500),
                                        ft.Icon(self._icono_flet(m.get("icono")), color=color),
                                    ],
                                ),
                                ft.Text(
                                    str(m.get("valor", "")),
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                    color=color,
                                ),
                            ],
                        ),
                    )
                )
            )

        items_alerta = []
        for a in datos.get("alertas", []):
            items_alerta.append(
                ft.Card(
                    content=ft.Container(
                        padding=12,
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Column(
                                    spacing=2,
                                    expand=True,
                                    controls=[
                                        ft.Text(a.get("titulo", ""), weight=ft.FontWeight.BOLD, size=14),
                                        ft.Text(a.get("subtitulo", ""), size=12, color=ft.Colors.GREY_700),
                                    ],
                                ),
                                ft.Container(
                                    padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                    bgcolor=ft.Colors.RED_100,
                                    border_radius=12,
                                    content=ft.Text(
                                        a.get("badge", ""),
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.RED_900,
                                    ),
                                ),
                            ],
                        ),
                    )
                )
            )

        if not items_alerta:
            items_alerta.append(
                ft.Text("No hay productos con stock bajo por el momento.", color=ft.Colors.GREEN_700)
            )

        return ft.Column(
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text(datos.get("saludo", ""), size=22, weight=ft.FontWeight.BOLD),
                ft.Text(datos.get("subtitulo", ""), size=14, color=ft.Colors.GREY_700),
                ft.Row(wrap=True, spacing=12, run_spacing=12, controls=tarjetas_metricas),
                ft.Divider(),
                ft.Text(datos.get("titulo_alertas", ""), size=18, weight=ft.FontWeight.BOLD),
                ft.Text(datos.get("descripcion_alertas", ""), size=13, color=ft.Colors.GREY_700),
                ft.Column(spacing=8, controls=items_alerta),
            ],
        )
