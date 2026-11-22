class AdminView:
    def __init__(self, db, usuario):
        self.db = db
        self.usuario = usuario or {}
        self.ventas_hoy = 0.0
        self.num_ventas = 0
        self.productos_bajo_stock = 0
        self.alertas = []

        self.cargar_datos_dashboard()

    def cargar_datos_dashboard(self):
        # 1. Total ventas de hoy
        q_ventas_hoy = """
            SELECT COALESCE(SUM(total_venta), 0) AS total, COUNT(*) AS cantidad
            FROM ventas
            WHERE DATE(fecha) = CURRENT_DATE
        """
        res_ventas = self.db.obtener_resultados(q_ventas_hoy)
        if res_ventas:
            self.ventas_hoy = float(res_ventas[0].get("total") or 0.0)
            self.num_ventas = int(res_ventas[0].get("cantidad") or 0)
        else:
            self.ventas_hoy = 0.0
            self.num_ventas = 0

        # 2. Productos bajo stock (<= 5)
        q_bajo_stock = (
            "SELECT codigo, nombre, stock, precio "
            "FROM productos "
            "WHERE stock <= 5 "
            "ORDER BY stock ASC"
        )
        res_stock = self.db.obtener_resultados(q_bajo_stock)

        self.alertas = []
        if res_stock:
            self.productos_bajo_stock = len(res_stock)
            for p in res_stock:
                self.alertas.append({
                    "codigo": str(p.get("codigo", "")),
                    "nombre": str(p.get("nombre", "")),
                    "stock": int(p.get("stock") or 0),
                    "precio": float(p.get("precio") or 0.0),
                })
        else:
            self.productos_bajo_stock = 0

    def mostrar_dashboard(self):
        self.cargar_datos_dashboard()
        nombre_usuario = self.usuario.get("nombre") or "Administrador"
        return {
            "saludo": f"Bienvenido(a), {nombre_usuario}",
            "ventas_hoy": f"${self.ventas_hoy:.2f}",
            "num_ventas": str(self.num_ventas),
            "productos_bajo_stock": str(self.productos_bajo_stock),
            "alertas": self.alertas,
        }