import os
import mysql.connector
from mysql.connector import Error


class Database:
    def __init__(self):
        self.host = os.getenv("DB_HOST", "gateway01.ap-northeast-1.prod.aws.tidbcloud.com")
        self.database = os.getenv("DB_NAME", "punto_venta_lucero")
        self.user = os.getenv("DB_USER", "2vQtzbmmMG6qQ7s.root")
        self.password = os.getenv("DB_PASSWORD", "Rm284HCXt9XFwBJn")
        self.port = int(os.getenv("DB_PORT", "4000"))
        self.connection = None

    def conectar(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port,
                connection_timeout=10,
                autocommit=False
            )
            return self.connection.is_connected()
        except Error as e:
            print(f"Error de conexión: {e}")
            self.connection = None
            return False

    def desconectar(self):
        if self.connection and self.connection.is_connected():
            try:
                self.connection.close()
            except Error:
                pass
        self.connection = None

    def _asegurar_conexion(self):
        try:
            if self.connection and self.connection.is_connected():
                self.connection.ping(reconnect=True, attempts=2, delay=1)
                return True
        except Error:
            pass
        return self.conectar()

    def ejecutar_query(self, query, params=None):
        if not self._asegurar_conexion():
            print("❌ No se pudo establecer conexión con la base de datos.")
            return None

        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            self.connection.commit()
            return cursor
        except Error as e:
            print(f"Error ejecutando query: {e}")
            try:
                if self.connection and self.connection.is_connected():
                    self.connection.rollback()
            except Error:
                pass
            return None
        finally:
            if cursor:
                try:
                    cursor.close()
                except Error:
                    pass

    def obtener_resultados(self, query, params=None):
        if not self._asegurar_conexion():
            print("❌ No se pudo establecer conexión con la base de datos.")
            return None

        cursor = None
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            resultados = cursor.fetchall()
            return resultados
        except Error as e:
            print(f"Error obteniendo resultados: {e}")
            return None
        finally:
            if cursor:
                try:
                    cursor.close()
                except Error:
                    pass