class ConfiguracionView:
    def __init__(self, db):
        self.db = db
        self.config = {
            "nombre_tienda": "",
            "rfc": "",
            "direccion": "",
            "telefono": "",
            "mensaje_ticket": "¡Gracias por su compra!",
        }
        self.cargar_configuracion()

    def cargar_configuracion(self):
        res = self.db.obtener_resultados("SELECT clave, valor FROM configuracion")
        if res:
            config_dict = {row["clave"]: row["valor"] for row in res}
            self.config = {
                "nombre_tienda": config_dict.get("nombre_tienda", ""),
                "rfc": config_dict.get("rfc", ""),
                "direccion": config_dict.get("direccion", ""),
                "telefono": config_dict.get("telefono", ""),
                "mensaje_ticket": config_dict.get("mensaje_ticket", "¡Gracias por su compra!"),
            }
        return self.config

    def guardar_configuracion(self, datos_form):
        datos_form = datos_form or {}
        datos = {
            "nombre_tienda": str(datos_form.get("nombre_tienda") or ""),
            "rfc": str(datos_form.get("rfc") or ""),
            "direccion": str(datos_form.get("direccion") or ""),
            "telefono": str(datos_form.get("telefono") or ""),
            "mensaje_ticket": str(datos_form.get("mensaje_ticket") or "¡Gracias por su compra!"),
        }

        for clave, valor in datos.items():
            existe = self.db.obtener_resultados("SELECT * FROM configuracion WHERE clave = %s", (clave,))
            if existe:
                self.db.ejecutar_query("UPDATE configuracion SET valor = %s WHERE clave = %s", (valor, clave))
            else:
                self.db.ejecutar_query("INSERT INTO configuracion (clave, valor) VALUES (%s, %s)", (clave, valor))

        self.config = datos
        return {
            "ok": True,
            "mensaje": "✅ Configuración guardada correctamente",
            "config": self.config,
        }