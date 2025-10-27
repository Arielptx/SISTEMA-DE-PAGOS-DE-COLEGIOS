from . import db 

class Administrador(db.Model):
    __tablename__ = 'administrador'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    apellido = db.Column(db.String(100))
    correo = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  # texto plano

    def verificar_password(self, contraseña):
        # comparar directamente
        return self.password == contraseña

    def __repr__(self):
        return f"<Administrador {self.correo}>"
