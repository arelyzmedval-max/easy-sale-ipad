class InventarioView:
    def __init__(self, db):
        self.db = db
        self.producto_editando_codigo = None
        self.productos = []
        self.cargar_productos()

    def _formatear_stock(self, stock_raw, tipo_venta):
        stock_val = float(stock_raw or 0.0)
        if tipo_venta == "por kilo":
            return f"{stock_val:.3f} kg"
        if stock_val.is_integer():
            return str(int(stock_val))
        return str(stock_val)

    def cargar_productos(self):
        self.productos = []
        resultados = self.db.obtener_resultados("SELECT * FROM productos")
        if resultados:
            for prod in resultados:
                tipo_v = prod.get("tipo_venta") or "por unidad"
                costo_val = float(prod.get("precio_costoi") or 0.0)
                precio_val = float(prod.get("precio") or 0.0)
                stock_val = float(prod.get("stock") or 0.0)

                self.productos.append({
                    "codigo": str(prod.get("codigo", "")),
                    "nombre": str(prod.get("nombre", "")),
                    "descripcion": str(prod.get("descripcion") or ""),
                    "precio_costoi": costo_val,
                    "costo_fmt": f"${costo_val:.2f}",
                    "precio": precio_val,
                    "precio_fmt": f"${precio_val:.2f}",
                    "stock": stock_val,
                    "stock_fmt": self._formatear_stock(stock_val, tipo_v),
                    "tipo_venta": tipo_v,
                })
        return self.productos

    def preparar_edicion(self, codigo):
        res = self.db.obtener_resultados("SELECT * FROM productos WHERE codigo = %s", (codigo,))
        if not res:
            return {
                "ok": False,
                "mensaje": "⚠️ Producto no encontrado",
                "tipo": "error",
            }
        prod = res[0]
        tipo_v = prod.get("tipo_venta") or "por unidad"
        self.producto_editando_codigo = str(prod["codigo"])
        return {
            "ok": True,
            "editando": True,
            "codigo_disabled": True,
            "btn_texto": "Actualizar Producto",
            "producto": {
                "codigo": str(prod.get("codigo", "")),
                "nombre": str(prod.get("nombre", "")),
                "descripcion": str(prod.get("descripcion") or ""),
                "precio_costoi": str(prod.get("precio_costoi") if prod.get("precio_costoi") is not None else 0.0),
                "precio": str(prod.get("precio") if prod.get("precio") is not None else 0.0),
                "stock": str(prod.get("stock") if prod.get("stock") is not None else 0.0),
                "tipo_venta": tipo_v,
            },
        }

    def eliminar_producto(self, codigo):
        self.db.ejecutar_query("DELETE FROM productos WHERE codigo = %s", (codigo,))
        if self.producto_editando_codigo == str(codigo):
            self.limpiar_formulario()
        productos_actualizados = self.cargar_productos()
        return {
            "ok": True,
            "mensaje": "🗑️ Producto eliminado",
            "tipo": "error",
            "productos": productos_actualizados,
        }

    def guardar_producto(self, datos):
        datos = datos or {}
        codigo = str(datos.get("codigo") or "").strip()
        nombre = str(datos.get("nombre") or "").strip()
        descripcion = str(datos.get("descripcion") or "").strip()
        tipo_v = str(datos.get("tipo_venta") or "por unidad").strip() or "por unidad"

        try:
            costo_raw = datos.get("precio_costoi")
            precio_raw = datos.get("precio")
            stock_raw = datos.get("stock")

            costo = float(str(costo_raw).replace(",", ".").strip()) if costo_raw not in (None, "") else 0.0
            precio = float(str(precio_raw).replace(",", ".").strip()) if precio_raw not in (None, "") else 0.0
            stock = float(str(stock_raw).replace(",", ".").strip()) if stock_raw not in (None, "") else 0.0
        except (ValueError, TypeError):
            return {
                "ok": False,
                "mensaje": "⚠️ Costo, precio y stock deben ser numéricos",
                "tipo": "error",
            }

        if not codigo or not nombre:
            return {
                "ok": False,
                "mensaje": "⚠️ El código y el nombre son obligatorios",
                "tipo": "error",
            }

        if self.producto_editando_codigo:
            self.db.ejecutar_query(
                "UPDATE productos "
                "SET nombre = %s, descripcion = %s, precio_costoi = %s, precio = %s, stock = %s, tipo_venta = %s "
                "WHERE codigo = %s",
                (nombre, descripcion, costo, precio, stock, tipo_v, self.producto_editando_codigo),
            )
            mensaje = "✅ Producto actualizado con éxito"
        else:
            existe = self.db.obtener_resultados("SELECT * FROM productos WHERE codigo = %s", (codigo,))
            if existe:
                return {
                    "ok": False,
                    "mensaje": "⚠️ Ya existe un producto con ese código",
                    "tipo": "error",
                }
            self.db.ejecutar_query(
                "INSERT INTO productos (codigo, nombre, descripcion, precio_costoi, precio, stock, tipo_venta) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (codigo, nombre, descripcion, costo, precio, stock, tipo_v),
            )
            mensaje = "✅ Producto guardado con éxito"

        self.limpiar_formulario()
        productos_actualizados = self.cargar_productos()
        return {
            "ok": True,
            "mensaje": mensaje,
            "tipo": "success",
            "productos": productos_actualizados,
            "formulario": self.obtener_estado_formulario(),
        }

    def limpiar_formulario(self):
        self.producto_editando_codigo = None
        return self.obtener_estado_formulario()

    def obtener_estado_formulario(self):
        return {
            "editando": bool(self.producto_editando_codigo),
            "codigo_disabled": bool(self.producto_editando_codigo),
            "btn_texto": "Actualizar Producto" if self.producto_editando_codigo else "Guardar Producto",
            "mostrar_cancelar": bool(self.producto_editando_codigo),
            "valores": {
                "codigo": "",
                "nombre": "",
                "descripcion": "",
                "precio_costoi": "",
                "precio": "",
                "stock": "",
                "tipo_venta": "por unidad",
            },
        }