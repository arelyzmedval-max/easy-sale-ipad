class VentasView:
    def __init__(self, db, usuario, al_completar_venta=None):
        self.db = db
        self.usuario = usuario or {}
        self.al_completar_venta = al_completar_venta
        self.carrito = []
        self.cliente_seleccionado_id = None
        self.metodos_pago = self.cargar_metodos_pago()

    def _formatear_cantidad(self, cantidad_raw, tipo_venta):
        cant_val = float(cantidad_raw or 0.0)
        if tipo_venta == "por kilo":
            return f"{cant_val:.3f} kg"
        if cant_val.is_integer():
            return str(int(cant_val))
        return str(cant_val)

    def _obtener_id_venta(self, resultado_query):
        if not resultado_query:
            return None
        if hasattr(resultado_query, "lastrowid"):
            return resultado_query.lastrowid
        return resultado_query

    def cargar_metodos_pago(self):
        metodos = self.db.obtener_resultados("SELECT id_metodo, metodo FROM metodos_pago")
        if not metodos:
            return []
        return [
            {
                "id_metodo": m.get("id_metodo"),
                "key": str(m.get("id_metodo")),
                "metodo": str(m.get("metodo") or ""),
            }
            for m in metodos
        ]

    def filtrar_sugerencias_clientes(self, texto_raw):
        try:
            texto = str(texto_raw or "").strip()
            if not texto:
                self.cliente_seleccionado_id = None
                return {
                    "ok": True,
                    "mostrar": False,
                    "clientes": [],
                }

            res = self.db.obtener_resultados(
                "SELECT id_cliente, nombre, telefono FROM clientes WHERE nombre LIKE %s OR telefono LIKE %s LIMIT 5",
                (f"%{texto}%", f"%{texto}%"),
            )
            if not res:
                return {
                    "ok": True,
                    "mostrar": False,
                    "clientes": [],
                }

            clientes = []
            for cli in res:
                tel = cli.get("telefono") or "Sin tel"
                clientes.append({
                    "id_cliente": cli.get("id_cliente"),
                    "nombre": str(cli.get("nombre") or ""),
                    "telefono": str(tel),
                    "etiqueta": f"{cli.get('nombre', '')} ({tel})",
                })

            return {
                "ok": True,
                "mostrar": True,
                "clientes": clientes,
            }
        except Exception as ex:
            print(f"Error en filtrar_sugerencias_clientes: {ex}")
            return {
                "ok": False,
                "mostrar": False,
                "clientes": [],
            }

    def seleccionar_cliente(self, id_cliente, nombre=""):
        self.cliente_seleccionado_id = id_cliente
        return {
            "ok": True,
            "id_cliente": self.cliente_seleccionado_id,
            "nombre": str(nombre or ""),
        }

    def filtrar_sugerencias_productos(self, texto_raw):
        try:
            texto = str(texto_raw or "").strip()
            if not texto:
                return {
                    "ok": True,
                    "mostrar": False,
                    "productos": [],
                }

            res = self.db.obtener_resultados(
                "SELECT * FROM productos WHERE codigo = %s OR nombre LIKE %s LIMIT 5",
                (texto, f"%{texto}%"),
            )
            if not res:
                return {
                    "ok": True,
                    "mostrar": False,
                    "productos": [],
                }

            productos = []
            for prod in res:
                stock_actual = float(prod.get("stock") or 0.0)
                precio_val = float(prod.get("precio") or 0.0)
                productos.append({
                    "codigo": str(prod.get("codigo", "")),
                    "nombre": str(prod.get("nombre", "")),
                    "stock": stock_actual,
                    "precio": precio_val,
                    "tipo_venta": prod.get("tipo_venta") or "por unidad",
                    "subtitulo": f"Código: {prod.get('codigo', '')} | Stock: {stock_actual} | ${precio_val:.2f}",
                })

            return {
                "ok": True,
                "mostrar": True,
                "productos": productos,
            }
        except Exception as ex:
            print(f"Error en filtrar_sugerencias_productos: {ex}")
            return {
                "ok": False,
                "mostrar": False,
                "productos": [],
            }

    def buscar_producto_por_termino(self, texto_raw):
        texto = str(texto_raw or "").strip()
        if not texto:
            return {
                "ok": False,
                "mensaje": None,
                "producto": None,
            }

        res = self.db.obtener_resultados(
            "SELECT * FROM productos WHERE codigo = %s OR nombre LIKE %s LIMIT 1",
            (texto, f"%{texto}%"),
        )
        if res:
            prod = res[0]
            return {
                "ok": True,
                "mensaje": None,
                "producto": prod,
                "accion": self.evaluar_y_agregar(prod),
            }

        return {
            "ok": False,
            "mensaje": "❌ Producto no encontrado",
            "producto": None,
        }

    def evaluar_y_agregar(self, prod):
        if prod.get("tipo_venta") == "por kilo":
            return {
                "requiere_entrada": True,
                "modo": "peso",
                "titulo": f"Peso para: {prod.get('nombre', '')}",
                "label": "Kilos (ej. 0.750)",
                "valor_inicial": "1.0",
                "producto": prod,
            }
        return {
            "requiere_entrada": True,
            "modo": "cantidad",
            "titulo": f"Cantidad para: {prod.get('nombre', '')}",
            "label": "Cantidad",
            "valor_inicial": "1",
            "producto": prod,
        }

    def agregar_producto_con_valor(self, prod, valor_raw):
        try:
            cant = float(str(valor_raw).replace(",", ".").strip())
            if cant <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return {
                "ok": False,
                "mensaje": "⚠️ Ingresa una cantidad válida" if prod.get("tipo_venta") != "por kilo" else "⚠️ Ingresa un peso válido",
                "tipo": "error",
                "resumen": self.calcular_resumen(),
            }

        return self.procesar_item_al_carrito(prod, cant)

    def procesar_item_al_carrito(self, prod, cantidad=1.0):
        stock_disp = float(prod.get("stock") or 0.0)
        if stock_disp <= 0:
            return {
                "ok": False,
                "mensaje": "⚠️ Sin stock disponible",
                "tipo": "warning",
                "resumen": self.calcular_resumen(),
            }

        for item in self.carrito:
            if item["codigo"] == prod["codigo"]:
                item["cantidad"] += float(cantidad)
                return {
                    "ok": True,
                    "mensaje": None,
                    "resumen": self.calcular_resumen(),
                }

        self.carrito.append({
            "codigo": prod["codigo"],
            "nombre": prod["nombre"],
            "precio": float(prod["precio"]),
            "costo": float(prod.get("precio_costoi", 0.0) or 0.0),
            "cantidad": float(cantidad),
            "tipo_venta": prod.get("tipo_venta", "por unidad"),
            "stock": stock_disp,
        })
        return {
            "ok": True,
            "mensaje": None,
            "resumen": self.calcular_resumen(),
        }

    def quitar_item(self, indice):
        if 0 <= indice < len(self.carrito):
            self.carrito.pop(indice)
        return self.calcular_resumen()

    def calcular_resumen(self, impuesto_raw="0"):
        items_formateados = []
        subtotal_acum = 0.0

        for idx, item in enumerate(self.carrito):
            subtotal_item = float(item["precio"]) * float(item["cantidad"])
            subtotal_acum += subtotal_item
            cant_str = self._formatear_cantidad(item["cantidad"], item.get("tipo_venta", "por unidad"))

            items_formateados.append({
                "indice": idx,
                "codigo": str(item["codigo"]),
                "nombre": str(item["nombre"]),
                "cantidad_str": cant_str,
                "precio_unitario": f"${float(item['precio']):.2f}",
                "subtotal": f"${subtotal_item:.2f}",
            })

        try:
            imp_pct = float(str(impuesto_raw).replace(",", ".").strip()) if impuesto_raw not in (None, "") else 0.0
        except (ValueError, TypeError):
            imp_pct = 0.0

        monto_impuesto = subtotal_acum * (imp_pct / 100.0)
        total = subtotal_acum + monto_impuesto

        return {
            "items": items_formateados,
            "subtotal_num": subtotal_acum,
            "impuesto_pct": imp_pct,
            "impuesto_num": monto_impuesto,
            "total_num": total,
            "subtotal": f"${subtotal_acum:.2f}",
            "impuesto": f"${monto_impuesto:.2f}",
            "total": f"${total:.2f}",
        }

    def recalcular_totales(self, impuesto_raw="0"):
        return self.calcular_resumen(impuesto_raw)

    def procesar_venta(self, metodo_pago_id_raw, impuesto_raw="0", cliente_id_raw=None):
        if not self.carrito:
            return {
                "ok": False,
                "mensaje": "⚠️ El carrito está vacío",
                "tipo": "warning",
                "resumen": self.calcular_resumen(impuesto_raw),
            }

        id_usuario = self.usuario.get("id_usuario")
        q_caja = "SELECT id_caja FROM caja WHERE id_usuario = %s AND estado = 'ABIERTA' LIMIT 1"
        caja_activa = self.db.obtener_resultados(q_caja, (id_usuario,))

        if not caja_activa:
            return {
                "ok": False,
                "mensaje": "⚠️ Debe abrir caja antes de realizar una venta",
                "tipo": "error",
                "resumen": self.calcular_resumen(impuesto_raw),
            }

        if not metodo_pago_id_raw:
            return {
                "ok": False,
                "mensaje": "⚠️ Selecciona un método de pago",
                "tipo": "error",
                "resumen": self.calcular_resumen(impuesto_raw),
            }

        metodo_id = int(metodo_pago_id_raw)
        metodo_texto = ""
        for opt in self.metodos_pago:
            if str(opt.get("id_metodo")) == str(metodo_id):
                metodo_texto = str(opt.get("metodo") or "").lower()
                break

        es_fiado = "fiado" in metodo_texto or "crédito" in metodo_texto or "credito" in metodo_texto
        cliente_id = cliente_id_raw if cliente_id_raw is not None else self.cliente_seleccionado_id

        if es_fiado and not cliente_id:
            return {
                "ok": False,
                "mensaje": "⚠️ Debes buscar y seleccionar un cliente válido para el fiado",
                "tipo": "error",
                "resumen": self.calcular_resumen(impuesto_raw),
            }

        subtotal = sum(float(i["precio"]) * float(i["cantidad"]) for i in self.carrito)
        try:
            imp_pct = float(str(impuesto_raw).replace(",", ".").strip()) if impuesto_raw not in (None, "") else 0.0
        except (ValueError, TypeError):
            imp_pct = 0.0
        total = subtotal + (subtotal * (imp_pct / 100.0))

        q_venta = "INSERT INTO ventas (id_usuario, metodo_pago_id, impuesto, total_venta) VALUES (%s, %s, %s, %s)"
        res_venta = self.db.ejecutar_query(q_venta, (id_usuario, metodo_id, imp_pct, total))
        id_venta = self._obtener_id_venta(res_venta)

        if id_venta:
            if es_fiado:
                q_credito = (
                    "INSERT INTO creditos (id_cliente, id_venta, total_fiado, abono, estado) "
                    "VALUES (%s, %s, %s, 0.00, 'Pendiente')"
                )
                self.db.ejecutar_query(q_credito, (cliente_id, id_venta, total))

            for item in self.carrito:
                sub_item = float(item["precio"]) * float(item["cantidad"])
                self.db.ejecutar_query(
                    "INSERT INTO ventas_detalle (id_venta, codigo_producto, cantidad, precio_unitario, subtotal) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (id_venta, item["codigo"], item["cantidad"], item["precio"], sub_item),
                )
                self.db.ejecutar_query(
                    "UPDATE productos SET stock = stock - %s WHERE codigo = %s",
                    (item["cantidad"], item["codigo"]),
                )

            self.carrito.clear()
            self.cliente_seleccionado_id = None
            if callable(self.al_completar_venta):
                self.al_completar_venta()

            return {
                "ok": True,
                "mensaje": "✅ Venta procesada con éxito",
                "tipo": "success",
                "id_venta": id_venta,
                "resumen": self.calcular_resumen("0"),
            }

        return {
            "ok": False,
            "mensaje": "❌ Error al procesar venta",
            "tipo": "error",
            "resumen": self.calcular_resumen(impuesto_raw),
        }