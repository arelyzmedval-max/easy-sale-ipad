import shutil
import subprocess


class ImpresoraTexsonMac:
    def __init__(self, nombre_impresora=None, ancho=32):
        self.nombre_impresora = nombre_impresora if nombre_impresora is not None else "EML_Printer"
        self.ancho = int(ancho)

    def _centrar(self, texto):
        return str(texto)[: self.ancho].center(self.ancho)

    def _linea_izq_der(self, izq, der):
        izq_str = str(izq)
        der_str = str(der)
        espacios = self.ancho - len(izq_str) - len(der_str)
        if espacios < 1:
            izq_str = izq_str[: max(0, self.ancho - len(der_str) - 1)]
            espacios = 1
        return f"{izq_str}{' ' * espacios}{der_str}"

    def construir_ticket_prueba(self):
        sep = "-" * self.ancho
        lineas = [
            self._centrar("MI NEGOCIO POS"),
            self._centrar("TICKET DE PRUEBA"),
            sep,
            self._linea_izq_der("2x Refresco", "$36.00"),
            self._linea_izq_der("1x Pan dulce", "$14.00"),
            sep,
            self._linea_izq_der("TOTAL:", "$50.00"),
            sep,
            self._centrar("Gracias por su compra"),
            "\n\n\n",
        ]
        return "\n".join(lineas)

    def construir_ticket_venta(self, folio, fecha, items, total, pago=0.0):
        sep = "-" * self.ancho
        total_val = float(total or 0.0)
        pago_val = float(pago or 0.0)

        lineas = [
            self._centrar("MI NEGOCIO POS"),
            self._centrar("TICKET DE VENTA"),
            sep,
            f"Folio: {folio}"[: self.ancho],
            f"Fecha: {fecha}"[: self.ancho],
            sep,
        ]

        for item in items or []:
            cant = item.get("cantidad", 1)
            nombre = item.get("nombre", "")
            desc = f"{cant}x {nombre}"
            subtotal = float(item.get("subtotal", 0.0))
            lineas.append(self._linea_izq_der(desc, f"${subtotal:.2f}"))

        lineas.append(sep)
        lineas.append(self._linea_izq_der("TOTAL:", f"${total_val:.2f}"))

        if pago_val > 0:
            cambio = pago_val - total_val
            lineas.append(self._linea_izq_der("PAGO:", f"${pago_val:.2f}"))
            lineas.append(self._linea_izq_der("CAMBIO:", f"${cambio:.2f}"))

        lineas.extend([
            sep,
            self._centrar("Gracias por su compra"),
            "\n\n\n",
        ])
        return "\n".join(lineas)

    def imprimir_texto(self, texto):
        if shutil.which("lp") is None or not self.nombre_impresora:
            return {
                "ok": True,
                "modo": "texto_web",
                "mensaje": "Ticket generado para vista/descarga en iPad (sin impresora local en servidor)",
                "ticket": texto,
            }

        try:
            proc = subprocess.run(
                ["lp", "-d", self.nombre_impresora],
                input=texto.encode("utf-8"),
                capture_output=True,
                timeout=10,
                check=False,
            )
            if proc.returncode == 0:
                return {
                    "ok": True,
                    "modo": "lp",
                    "mensaje": "Ticket enviado a impresora",
                    "ticket": texto,
                }
            return {
                "ok": False,
                "modo": "lp",
                "mensaje": proc.stderr.decode("utf-8", errors="ignore").strip() or "Error al imprimir",
                "ticket": texto,
            }
        except Exception as ex:
            return {
                "ok": False,
                "modo": "lp",
                "mensaje": str(ex),
                "ticket": texto,
            }