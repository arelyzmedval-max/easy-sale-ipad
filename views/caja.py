class CajaView:
    def __init__(self, db, usuario):
        self.db = db
        self.usuario = usuario or {}
        self.estado_info = self.verificar_estado_caja()

    def verificar_estado_caja(self):
        id_usuario = self.usuario.get("id_usuario")
        q = (
            "SELECT id_caja, fondo_inicial, fecha_apertura "
            "FROM caja "
            "WHERE id_usuario = %s AND estado = 'ABIERTA' "
            "LIMIT 1"
        )
        caja_activa = self.db.obtener_resultados(q, (id_usuario,))

        if caja_activa:
            caja = caja_activa[0]
            fecha_apertura = caja["fecha_apertura"]
            fondo_inicial = float(caja.get("fondo_inicial") or 0.0)

            q_ventas = """
                SELECT SUM(v.total_venta) AS total_vendido,
                       SUM((vd.precio_unitario - p.precio_costoi) * vd.cantidad) AS ganancia_neta
                FROM ventas v
                JOIN ventas_detalle vd ON v.id_venta = vd.id_venta
                JOIN productos p ON vd.codigo_producto = p.codigo
                WHERE v.id_usuario = %s AND v.fecha >= %s
            """
            res_stats = self.db.obtener_resultados(q_ventas, (id_usuario, fecha_apertura))

            total_vendido = 0.0
            ganancia_neta = 0.0
            if res_stats and res_stats[0].get("total_vendido"):
                total_vendido = float(res_stats[0]["total_vendido"])
                ganancia_neta = float(res_stats[0].get("ganancia_neta") or 0.0)

            self.estado_info = {
                "abierta": True,
                "id_caja": caja["id_caja"],
                "fecha_apertura": str(fecha_apertura),
                "fondo_inicial": fondo_inicial,
                "total_vendido": total_vendido,
                "ganancia_neta": ganancia_neta,
                "mensaje_estado": (
                    f"Caja Abierta el {fecha_apertura} | "
                    f"Fondo Inicial: ${fondo_inicial:.2f} | "
                    f"Vendido en Turno: ${total_vendido:.2f}"
                ),
                "mensaje_ganancia": f"Ganancia Neta (Utilidad) en este turno: ${ganancia_neta:.2f}",
            }
        else:
            self.estado_info = {
                "abierta": False,
                "id_caja": None,
                "fecha_apertura": None,
                "fondo_inicial": 0.0,
                "total_vendido": 0.0,
                "ganancia_neta": 0.0,
                "mensaje_estado": "No hay caja abierta. Ingrese el fondo inicial para comenzar su turno.",
                "mensaje_ganancia": "",
            }

        return self.estado_info

    def abrir_caja(self, fondo_raw):
        try:
            fondo = float(str(fondo_raw).replace(",", ".").strip())
            if fondo < 0:
                raise ValueError
        except (ValueError, TypeError):
            return {
                "ok": False,
                "mensaje": "Ingrese un fondo inicial válido",
                "tipo": "error",
                "estado": self.verificar_estado_caja(),
            }

        id_usuario = self.usuario.get("id_usuario")
        q = "INSERT INTO caja (id_usuario, fondo_inicial, estado) VALUES (%s, %s, 'ABIERTA')"
        res = self.db.ejecutar_query(q, (id_usuario, fondo))
        if res is None:
            return {
                "ok": False,
                "mensaje": "No se pudo abrir la caja",
                "tipo": "error",
                "estado": self.verificar_estado_caja(),
            }

        return {
            "ok": True,
            "mensaje": "Caja abierta con éxito",
            "tipo": "success",
            "estado": self.verificar_estado_caja(),
        }

    def cerrar_caja(self):
        id_usuario = self.usuario.get("id_usuario")
        q = (
            "UPDATE caja "
            "SET estado = 'CERRADA', fecha_cierre = NOW() "
            "WHERE id_usuario = %s AND estado = 'ABIERTA'"
        )
        res = self.db.ejecutar_query(q, (id_usuario,))
        if res is None:
            return {
                "ok": False,
                "mensaje": "No se pudo cerrar la caja",
                "tipo": "error",
                "estado": self.verificar_estado_caja(),
            }

        return {
            "ok": True,
            "mensaje": "Caja cerrada (Corte realizado)",
            "tipo": "warning",
            "estado": self.verificar_estado_caja(),
        }