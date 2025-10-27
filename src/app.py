from flask import Flask, render_template, redirect, url_for, flash, session, request
from config import config
from models.administrador import Administrador
from models.estudiantes import Estudiante
from models.pago import Pago
from models import db
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
import logging

# Configurar logging para depurar errores
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(config['development'])
csrf = CSRFProtect(app)  # Habilitar protección CSRF
db.init_app(app)

# Formulario de login
class LoginForm(FlaskForm):
    correo = StringField('Correo', validators=[DataRequired(message='El correo es obligatorio')])
    password = PasswordField('Contraseña', validators=[DataRequired(message='La contraseña es obligatoria')])
    submit = SubmitField('Ingresar')

# Rutas
@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        logger.debug(f"Intento de login con correo: {form.correo.data}")
        admin = Administrador.query.filter_by(correo=form.correo.data).first()
        if admin and admin.verificar_password(form.password.data):
            session['user_id'] = admin.id
            flash('Inicio de sesión exitoso ✅', 'success')
            logger.info("Inicio de sesión exitoso")
            return redirect(url_for('panel'))
        else:
            flash('Correo o contraseña incorrectos ❌', 'danger')
            logger.error("Correo o contraseña incorrectos")
    return render_template('login.html', form=form)

@app.route('/panel')
def panel():
    if 'user_id' not in session:
        flash('Por favor, inicia sesión primero', 'danger')
        logger.warning("Acceso no autorizado a /panel")
        return redirect(url_for('login'))
    return render_template('base.html')

@app.route('/estudiantes')
def estudiantes():
    if 'user_id' not in session:
        flash('Por favor, inicia sesión primero', 'danger')
        logger.warning("Acceso no autorizado a /estudiantes")
        return redirect(url_for('login'))
    estudiantes = Estudiante.query.all()
    return render_template('estudiantes.html', estudiantes=estudiantes)

@app.route('/estudiantes/create', methods=['GET'], endpoint='create_student')
def create():
    if 'user_id' not in session:
        flash('Por favor, inicia sesión primero', 'danger')
        logger.warning("Acceso no autorizado a /estudiantes/create")
        return redirect(url_for('login'))
    return render_template('createstudiantes.html')

@app.route('/estudiantes/insert', methods=['POST'])
def insert():
    if 'user_id' not in session:
        flash('Por favor, inicia sesión primero', 'danger')
        logger.warning("Acceso no autorizado a /estudiantes/insert")
        return redirect(url_for('login'))
    
    try:
        logger.debug(f"Datos recibidos en POST /estudiantes/insert: {request.form}")
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        correo = request.form.get('correo')
        curso = request.form.get('curso')
        password = request.form.get('password')

        # Validación manual básica
        if not all([nombre, apellido, correo, curso, password]):
            flash('Todos los campos son obligatorios ❌', 'danger')
            logger.error("Faltan campos obligatorios")
            return render_template('createstudiantes.html')

        # Validar longitud de los campos según la base de datos
        if len(nombre) > 100:
            flash('El nombre no puede exceder los 100 caracteres ❌', 'danger')
            logger.error("Nombre excede 100 caracteres")
            return render_template('createstudiantes.html')
        if len(apellido) > 100:
            flash('El apellido no puede exceder los 100 caracteres ❌', 'danger')
            logger.error("Apellido excede 100 caracteres")
            return render_template('createstudiantes.html')
        if len(curso) > 50:
            flash('El curso no puede exceder los 50 caracteres ❌', 'danger')
            logger.error("Curso excede 50 caracteres")
            return render_template('createstudiantes.html')
        if len(correo) > 100:
            flash('El correo no puede exceder los 100 caracteres ❌', 'danger')
            logger.error("Correo excede 100 caracteres")
            return render_template('createstudiantes.html')
        if len(password) > 100:
            flash('La contraseña no puede exceder los 100 caracteres ❌', 'danger')
            logger.error("Contraseña excede 100 caracteres")
            return render_template('createstudiantes.html')

        estudiante = Estudiante(
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            curso=curso,
            password=password  # TODO: Considerar hashear la contraseña
        )
        db.session.add(estudiante)
        db.session.commit()
        flash('Estudiante creado exitosamente ✅', 'success')
        logger.info("Estudiante creado exitosamente")
        return redirect(url_for('estudiantes'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear estudiante: {str(e)} ❌', 'danger')
        logger.error(f"Error al crear estudiante: {str(e)}")
        return render_template('createstudiantes.html')

@app.route('/estudiantes/edit/<int:id>', methods=['GET'], endpoint='edit_student')
def edit(id):
    if 'user_id' not in session:
        flash('Por favor, inicia sesión primero', 'danger')
        logger.warning("Acceso no autorizado a /estudiantes/edit")
        return redirect(url_for('login'))
    estudiante = Estudiante.query.get_or_404(id)
    return render_template('editestudiante.html', estudiante=estudiante)

@app.route('/estudiantes/update/<int:id>', methods=['POST'], endpoint='update_student')
def update(id):
    if 'user_id' not in session:
        flash('Por favor, inicia sesión primero', 'danger')
        logger.warning("Acceso no autorizado a /estudiantes/update")
        return redirect(url_for('login'))
    
    try:
        estudiante = Estudiante.query.get_or_404(id)
        logger.debug(f"Datos recibidos en POST /estudiantes/update/{id}: {request.form}")
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        correo = request.form.get('correo')
        curso = request.form.get('curso')
        password = request.form.get('password')

        # Validación manual básica
        if not all([nombre, apellido, correo, curso, password]):
            flash('Todos los campos son obligatorios ❌', 'danger')
            logger.error("Faltan campos obligatorios")
            return render_template('editestudiante.html', estudiante=estudiante)

        # Validar longitud de los campos según la base de datos
        if len(nombre) > 100:
            flash('El nombre no puede exceder los 100 caracteres ❌', 'danger')
            logger.error("Nombre excede 100 caracteres")
            return render_template('editestudiante.html', estudiante=estudiante)
        if len(apellido) > 100:
            flash('El apellido no puede exceder los 100 caracteres ❌', 'danger')
            logger.error("Apellido excede 100 caracteres")
            return render_template('editestudiante.html', estudiante=estudiante)
        if len(curso) > 50:
            flash('El curso no puede exceder los 50 caracteres ❌', 'danger')
            logger.error("Curso excede 50 caracteres")
            return render_template('editestudiante.html', estudiante=estudiante)
        if len(correo) > 100:
            flash('El correo no puede exceder los 100 caracteres ❌', 'danger')
            logger.error("Correo excede 100 caracteres")
            return render_template('editestudiante.html', estudiante=estudiante)
        if len(password) > 100:
            flash('La contraseña no puede exceder los 100 caracteres ❌', 'danger')
            logger.error("Contraseña excede 100 caracteres")
            return render_template('editestudiante.html', estudiante=estudiante)

        # Actualizar los campos del estudiante
        estudiante.nombre = nombre
        estudiante.apellido = apellido
        estudiante.correo = correo
        estudiante.curso = curso
        estudiante.password = password  # TODO: Considerar hashear la contraseña
        db.session.commit()
        flash('Estudiante actualizado exitosamente ✅', 'success')
        logger.info("Estudiante actualizado exitosamente")
        return redirect(url_for('estudiantes'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar estudiante: {str(e)} ❌', 'danger')
        logger.error(f"Error al actualizar estudiante: {str(e)}")
        return render_template('editestudiante.html', estudiante=estudiante)

@app.route('/estudiantes/delete/<int:id>', methods=['POST'], endpoint='delete_student')
def delete(id):
    if 'user_id' not in session:
        flash('Por favor, inicia sesión primero', 'danger')
        logger.warning("Acceso no autorizado a /estudiantes/delete")
        return redirect(url_for('login'))
    
    try:
        logger.debug(f"Intento de eliminar estudiante con ID: {id}")
        estudiante = Estudiante.query.get_or_404(id)
        db.session.delete(estudiante)
        db.session.commit()
        flash('Estudiante eliminado exitosamente ✅', 'success')
        logger.info("Estudiante eliminado exitosamente")
        return redirect(url_for('estudiantes'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar estudiante: {str(e)} ❌', 'danger')
        logger.error(f"Error al eliminar estudiante: {str(e)}")
        return redirect(url_for('estudiantes'))

@app.route('/payment')
def payment():
    if 'user_id' not in session:
        flash('Por favor, inicia sesión primero', 'danger')
        logger.warning("Acceso no autorizado a /payment")
        return redirect(url_for('login'))
    pagos = db.session.query(Pago, Estudiante).join(Estudiante, Pago.estudiante_id == Estudiante.id).all()
    estudiantes = Estudiante.query.all()
    return render_template('payment.html', pagos=pagos, estudiantes=estudiantes)

@app.route('/payment/assign')
def payment_assign_form():
    if 'user_id' not in session:
        flash('Por favor, inicia sesión primero', 'danger')
        logger.warning("Acceso no autorizado a /payment/assign")
        return redirect(url_for('login'))
    estudiantes = Estudiante.query.all()
    return render_template('payment_assign.html', estudiantes=estudiantes)

@app.route('/payment/assign', methods=['POST'])
def payment_assign():
    if 'user_id' not in session:
        flash('Por favor, inicia sesión primero', 'danger')
        logger.warning("Acceso no autorizado a /payment/assign")
        return redirect(url_for('login'))
    
    try:
        logger.debug(f"Datos recibidos en POST /payment/assign: {request.form}")
        estudiante_id = request.form.get('estudiante_id', type=int)
        monto = request.form.get('monto', type=float)
        observacion = request.form.get('observacion')

        # Validar datos
        if not estudiante_id or not Estudiante.query.get(estudiante_id):
            flash('Estudiante no válido', 'danger')
            logger.error("Estudiante no válido")
            return redirect(url_for('payment'))
        if not monto or monto <= 0 or monto > 99999999.99:
            flash('Monto no válido', 'danger')
            logger.error("Monto no válido")
            return redirect(url_for('payment'))

        # Crear nuevo pago
        nuevo_pago = Pago(
            estudiante_id=estudiante_id,
            monto=monto,
            estado='Pendiente',
            observacion=observacion if observacion else None
        )
        db.session.add(nuevo_pago)
        db.session.commit()
        flash('Pago asignado correctamente', 'success')
        logger.info("Pago asignado correctamente")
        return redirect(url_for('payment'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error al asignar pago: {str(e)}', 'danger')
        logger.error(f"Error al asignar pago: {str(e)}")
        return redirect(url_for('payment'))

@app.route('/payment/confirm/<int:pago_id>', methods=['POST'])
def payment_confirm(pago_id):
    if 'user_id' not in session:
        flash('Por favor, inicia sesión primero', 'danger')
        logger.warning("Acceso no autorizado a /payment/confirm")
        return redirect(url_for('login'))
    
    try:
        logger.debug(f"Intento de confirmar pago con ID: {pago_id}")
        pago = Pago.query.get_or_404(pago_id)
        if pago.estado != 'Pendiente':
            flash('El pago no está en estado Pendiente', 'danger')
            logger.error(f"El pago con ID {pago_id} no está en estado Pendiente")
            return redirect(url_for('payment'))

        pago.estado = 'Pagado'
        pago.fecha_confirmacion = db.func.current_timestamp()
        db.session.commit()
        flash('Pago confirmado correctamente ✅', 'success')
        logger.info("Pago confirmado correctamente")
        return redirect(url_for('payment'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error al confirmar pago: {str(e)} ❌', 'danger')
        logger.error(f"Error al confirmar pago: {str(e)}")
        return redirect(url_for('payment'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)