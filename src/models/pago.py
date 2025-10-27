from . import db

class Pago(db.Model):
    __tablename__ = 'pago'
    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('estudiante.id'), nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    fecha_asignacion = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    fecha_confirmacion = db.Column(db.DateTime, nullable=True)
    estado = db.Column(db.String(20), nullable=False, default='Pendiente')
    observacion = db.Column(db.Text, nullable=True)
    estudiante = db.relationship('Estudiante', backref=db.backref('pagos', lazy=True))

    def __repr__(self):
        return f'<Pago {self.id} - Estudiante {self.estudiante_id} - Monto {self.monto} - Estado {self.estado}>'