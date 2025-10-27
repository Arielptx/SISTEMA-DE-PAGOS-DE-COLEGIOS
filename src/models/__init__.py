from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .estudiantes import Estudiante
from .administrador import Administrador
from .pago import Pago