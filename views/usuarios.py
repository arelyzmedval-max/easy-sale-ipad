class UsuariosView:
    def __init__(self, db):
        self.db = db
        self.usuario_editando_id = None
        self.usuarios = []
        self.cargar_usuarios()

    def cargar_usuarios(self):
        self.usuarios = []
        resultados = self.db.obtener_resultados("SELECT id_usuario, nombre, usuario, rol FROM usuarios")
        if resultados:
            for usr in resultados:
                self.usuarios.append({
                    "id_usuario": usr.get("id_usuario"),
                    "nombre": str(usr.get("nombre") or ""),
                    "usuario": str(usr.get("usuario") or ""),
                    "rol": str(usr.get("rol") or "usuario"),
                })
        return self.usuarios

    def preparar_edicion(self, id_usuario):
        res = self.db.obtener_resultados(
            "SELECT id_usuario, nombre, usuario, rol FROM usuarios WHERE id_usuario = %s",
            (id_usuario,),
        )
        if not res:
            return {
                "ok": False,
                "mensaje": "⚠️ Usuario no encontrado",
                "tipo": "error",
            }

        usr = res[0]
        self.usuario_editando_id = usr["id_usuario"]
        return {
            "ok": True,
            "editando": True,
            "btn_texto": "Actualizar Usuario",
            "mostrar_cancelar": True,
            "password_hint": "Dejar en blanco para mantener la actual",
            "usuario": {
                "id_usuario": usr.get("id_usuario"),
                "nombre": str(usr.get("nombre") or ""),
                "usuario": str(usr.get("usuario") or ""),
                "password": "",
                "rol": str(usr.get("rol") or "usuario"),
            },
        }

    def eliminar_usuario(self, id_usuario):
        if id_usuario == 1:
            return {
                "ok": False,
                "mensaje": "⚠️ No se puede eliminar al usuario administrador principal",
                "tipo": "warning",
                "usuarios": self.usuarios,
            }

        self.db.ejecutar_query("DELETE FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        if self.usuario_editando_id == id_usuario:
            self.limpiar_formulario()
        usuarios_actualizados = self.cargar_usuarios()
        return {
            "ok": True,
            "mensaje": "🗑️ Usuario eliminado",
            "tipo": "error",
            "usuarios": usuarios_actualizados,
        }

    def guardar_usuario(self, datos):
        datos = datos or {}
        nombre = str(datos.get("nombre") or "").strip()
        usuario = str(datos.get("usuario") or "").strip()
        password = str(datos.get("password") or "").strip()
        rol = str(datos.get("rol") or "usuario").strip() or "usuario"

        if not nombre or not usuario:
            return {
                "ok": False,
                "mensaje": "⚠️ El nombre y el usuario son obligatorios",
                "tipo": "error",
            }

        if self.usuario_editando_id:
            if password:
                self.db.ejecutar_query(
                    "UPDATE usuarios SET nombre = %s, usuario = %s, password = %s, rol = %s WHERE id_usuario = %s",
                    (nombre, usuario, password, rol, self.usuario_editando_id),
                )
            else:
                self.db.ejecutar_query(
                    "UPDATE usuarios SET nombre = %s, usuario = %s, rol = %s WHERE id_usuario = %s",
                    (nombre, usuario, rol, self.usuario_editando_id),
                )
            mensaje = "✅ Usuario actualizado con éxito"
        else:
            if not password:
                return {
                    "ok": False,
                    "mensaje": "⚠️ La contraseña es obligatoria para nuevos usuarios",
                    "tipo": "error",
                }
            existe = self.db.obtener_resultados("SELECT * FROM usuarios WHERE usuario = %s", (usuario,))
            if existe:
                return {
                    "ok": False,
                    "mensaje": "⚠️ El nombre de usuario ya está registrado",
                    "tipo": "error",
                }
            self.db.ejecutar_query(
                "INSERT INTO usuarios (nombre, usuario, password, rol) VALUES (%s, %s, %s, %s)",
                (nombre, usuario, password, rol),
            )
            mensaje = "✅ Usuario registrado con éxito"

        self.limpiar_formulario()
        usuarios_actualizados = self.cargar_usuarios()
        return {
            "ok": True,
            "mensaje": mensaje,
            "tipo": "success",
            "usuarios": usuarios_actualizados,
            "formulario": self.obtener_estado_formulario(),
        }

    def limpiar_formulario(self):
        self.usuario_editando_id = None
        return self.obtener_estado_formulario()

    def obtener_estado_formulario(self):
        return {
            "editando": bool(self.usuario_editando_id),
            "btn_texto": "Actualizar Usuario" if self.usuario_editando_id else "Guardar Usuario",
            "mostrar_cancelar": bool(self.usuario_editando_id),
            "password_hint": "Dejar en blanco para mantener la actual" if self.usuario_editando_id else "",
            "valores": {
                "nombre": "",
                "usuario": "",
                "password": "",
                "rol": "usuario",
            },
        }