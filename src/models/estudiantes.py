from . import db

class Estudiante(db.Model):
    __tablename__ = 'estudiante'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    apellido = db.Column(db.String(100))
    curso = db.Column(db.String(50))
    correo = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)  # Texto plano

    def __repr__(self):
        return f'<Estudiante {self.id} {self.nombre} {self.apellido} {self.curso}>'