class LoginView:
    def __init__(self, db, al_ingresar=None):
        self.db = db
        self.al_ingresar = al_ingresar

    def intentar_login(self, usuario_raw, password_raw):
        usuario = str(usuario_raw or "").strip()
        password = str(password_raw or "").strip()

        if not usuario or not password:
            return {
                "ok": False,
                "error": "Por favor, ingresa usuario y contraseña.",
                "usuario": None,
            }

        query = (
            "SELECT id_usuario, nombre, rol "
            "FROM usuarios "
            "WHERE usuario = %s AND password = %s"
        )
        resultado = self.db.obtener_resultados(query, (usuario, password))

        if resultado:
            usuario_actual = resultado[0]
            if callable(self.al_ingresar):
                self.al_ingresar(usuario_actual)
            return {
                "ok": True,
                "error": "",
                "usuario": usuario_actual,
            }

        return {
            "ok": False,
            "error": "Usuario o contraseña incorrectos.",
            "usuario": None,
        }