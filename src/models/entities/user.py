from flask_login import UserMixin
from werkzeug.security import check_password_hash

class User(UserMixin):
    def __init__(self, id, nombre, password, telefono, email):

        self.id = id
        self.nombre = nombre
        self.password = password
        self.telefono = telefono
        self.email = email

    @staticmethod
    def check_password(contraseña_almacenada, contraseña_proporcionada):
        return check_password_hash(contraseña_almacenada, contraseña_proporcionada)