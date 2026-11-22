class HistorialView:
    def __init__(self, db):
        self.db = db
        self.ventas = []
        self.cargar_datos_historial()

    def cargar_datos_historial(self, termino=""):
        termino = (termino or "").strip()
        self.ventas = []

        if termino:
            query = """
                SELECT v.id_venta, v.fecha, u.nombre AS usuario, m.metodo, v.impuesto, v.total_venta
                FROM ventas v
                JOIN usuarios u ON v.id_usuario = u.id_usuario
                JOIN metodos_pago m ON v.metodo_pago_id = m.id_metodo
                WHERE v.id_venta LIKE %s OR u.nombre LIKE %s
                ORDER BY v.fecha DESC
            """
            res = self.db.obtener_resultados(query, (f"%{termino}%", f"%{termino}%"))
        else:
            query = """
                SELECT v.id_venta, v.fecha, u.nombre AS usuario, m.metodo, v.impuesto, v.total_venta
                FROM ventas v
                JOIN usuarios u ON v.id_usuario = u.id_usuario
                JOIN metodos_pago m ON v.metodo_pago_id = m.id_metodo
                ORDER BY v.fecha DESC
            """
            res = self.db.obtener_resultados(query)

        if res:
            for v in res:
                self.ventas.append({
                    "id_venta": v.get("id_venta"),
                    "folio": f"#{v.get('id_venta')}",
                    "fecha": str(v.get("fecha") or ""),
                    "usuario": str(v.get("usuario") or ""),
                    "metodo": str(v.get("metodo") or ""),
                    "impuesto": f"{v.get('impuesto')}%",
                    "total_venta": f"${float(v.get('total_venta') or 0.0):.2f}",
                })

        return self.ventas

    def mostrar_historial(self):
        return self.cargar_datos_historial("")

    def filtrar_historial(self, termino=""):
        return self.cargar_datos_historial(termino)

    def mostrar_detalle_venta(self, id_venta):
        query = """
            SELECT d.codigo_producto, p.nombre, d.cantidad, d.precio_unitario,
                   (d.cantidad * d.precio_unitario) AS subtotal
            FROM ventas_detalle d
            JOIN productos p ON d.codigo_producto = p.codigo
            WHERE d.id_venta = %s
        """
        detalles = self.db.obtener_resultados(query, (id_venta,))
        items = []

        if detalles:
            for d in detalles:
                items.append({
                    "codigo": str(d.get("codigo_producto") or ""),
                    "nombre": str(d.get("nombre") or ""),
                    "cantidad": str(d.get("cantidad") or 0),
                    "precio_unitario": f"${float(d.get('precio_unitario') or 0.0):.2f}",
                    "subtotal": f"${float(d.get('subtotal') or 0.0):.2f}",
                })

        return {
            "id_venta": id_venta,
            "titulo": f"Detalle de Venta #{id_venta}",
            "detalles": items,
        }