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