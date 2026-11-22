class ReportesView:
    def __init__(self, db):
        self.db = db
        self.filas = []
        self.total_acumulado = 0.0

    def generar_reporte(self):
        self.filas = []
        self.total_acumulado = 0.0

        query = """
            SELECT DATE(v.fecha) AS dia, u.nombre AS nombre_usuario,
                   SUM(v.total_venta) AS total_vendido, COUNT(*) AS num_ventas
            FROM ventas v
            JOIN usuarios u ON v.id_usuario = u.id_usuario
            GROUP BY DATE(v.fecha), u.nombre
            ORDER BY dia DESC
        """
        resultados = self.db.obtener_resultados(query)

        if resultados:
            for fila in resultados:
                val_total = float(fila.get("total_vendido") or 0.0)
                self.total_acumulado += val_total

                self.filas.append({
                    "dia": str(fila.get("dia") or ""),
                    "nombre_usuario": str(fila.get("nombre_usuario") or ""),
                    "total_vendido_num": val_total,
                    "total_vendido": f"${val_total:.2f}",
                    "num_ventas": int(fila.get("num_ventas") or 0),
                })

            return {
                "ok": True,
                "titulo": "Reporte de Ventas por Usuario y Día",
                "filas": self.filas,
                "total_general": f"${self.total_acumulado:.2f}",
                "total_acumulado": self.total_acumulado,
                "mensaje": None,
            }

        return {
            "ok": True,
            "titulo": "Reporte de Ventas por Usuario y Día",
            "filas": [],
            "total_general": "$0.00",
            "total_acumulado": 0.0,
            "mensaje": "No hay registros para generar reporte",
        }