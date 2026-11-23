import flet as ft


class InicioView:
    # ... mantén tu __init__, crear_tarjeta_metrica y cargar_datos_inicio igual ...

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

        # 1. Tarjetas de métricas
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

        # 2. Lista de alertas de stock bajo
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
