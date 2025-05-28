# app.py (Código Completo y Modificado)

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import os
import secrets 
import MySQLdb.cursors 

app = Flask(__name__)

app.secret_key = secrets.token_hex(16) 

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345678' # ¡Asegúrate que esta es tu contraseña REAL de MySQL root!
app.config['MYSQL_DB'] = 'concurso_matematicas'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor' 

mysql = MySQL(app)

def _create_tables_and_insert_data_mysql():
    """
    Inicializa la base de datos: borra tablas existentes (en orden inverso de dependencia),
    las crea y inserta datos iniciales.
    Deshabilita y rehabilita FOREIGN_KEY_CHECKS para un borrado limpio.
    """
    try:
        cursor = mysql.connection.cursor() 

        # Deshabilitar la verificación de claves foráneas
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

        # Borrar tablas en orden inverso de dependencia (para evitar problemas de FK)
        cursor.execute("DROP TABLE IF EXISTS calificaciones;")
        cursor.execute("DROP TABLE IF EXISTS predicciones_resultados;")
        cursor.execute("DROP TABLE IF EXISTS respuestas_actividades;") 
        cursor.execute("DROP TABLE IF EXISTS actividades;")
        cursor.execute("DROP TABLE IF EXISTS participantes;")
        cursor.execute("DROP TABLE IF EXISTS criterios_evaluacion;")
        cursor.execute("DROP TABLE IF EXISTS usuarios;")

        # Crear tabla usuarios
        cursor.execute('''
            CREATE TABLE usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre_usuario VARCHAR(255) NOT NULL UNIQUE,
                contrasena VARCHAR(255) NOT NULL,
                rol VARCHAR(50) NOT NULL
            );
        ''')
        # Insertar usuarios de prueba (alumno y juez)
        cursor.execute("INSERT IGNORE INTO usuarios (id, nombre_usuario, contrasena, rol) VALUES (1, 'alumno_test', 'pass_alumno', 'alumno')")
        cursor.execute("INSERT IGNORE INTO usuarios (id, nombre_usuario, contrasena, rol) VALUES (2, 'juez_test', 'pass_juez', 'juez')")

        # Crear tabla criterios_evaluacion
        cursor.execute('''
            CREATE TABLE criterios_evaluacion (
                id INT AUTO_INCREMENT PRIMARY KEY,
                titulo VARCHAR(255) NOT NULL,
                descripcion TEXT,
                puntos INT,
                icono VARCHAR(255)
            );
        ''')
        # Insertar criterios de evaluación iniciales
        criterios_data = [
            (1, 'Comprensión del Problema y Enfoque', 'Entendimiento claro del problema y elección de una estrategia adecuada para su resolución.', 15, 'fas fa-lightbulb'),
            (2, 'Claridad y Organización de la Solución', 'Presentación ordenada y fácil de seguir de los pasos de la solución. Se valorará la estructura y la legibilidad.', 15, 'fas fa-sitemap'),
            (3, 'Precisión y Corrección Matemática', 'Exactitud en cálculos, uso correcto de fórmulas y conceptos matemáticos. Errores mínimos o ausentes.', 25, 'fas fa-check-circle'),
            (4, 'Completitud de la Solución', 'Abordaje de todas las partes del problema y respuesta a todas las preguntas planteadas de manera exhaustiva.', 15, 'fas fa-clipboard-check'),
            (5, 'Originalidad y Eficiencia', 'Para problemas complejos, se valorará la creatividad y la eficiencia del método utilizado. Soluciones innovadoras pueden obtener puntos extra.', 10, 'fas fa-rocket'),
            (6, 'Argumentación y Justificación', 'Capacidad de explicar el razonamiento detrás de la solución y justificar cada paso. Coherencia entre el planteamiento y la conclusión.', 10, 'fas fa-comment-dots'),
            (7, 'Uso Correcto de Notación y Terminología', 'Empleo adecuado de símbolos matemáticos, unidades y lenguaje técnico a lo largo de la solución.', 10, 'fas fa-pencil-ruler')
        ]
        for criterio in criterios_data:
            cursor.execute("INSERT IGNORE INTO criterios_evaluacion (id, titulo, descripcion, puntos, icono) VALUES (%s, %s, %s, %s, %s)", criterio)

        # Crear tabla participantes
        cursor.execute('''
            CREATE TABLE participantes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT, 
                nombre_completo VARCHAR(255) NOT NULL,
                edad INT,
                fecha_nacimiento DATE,
                genero VARCHAR(50),
                curp VARCHAR(18) UNIQUE,
                nombre_institucion VARCHAR(255),
                nivel_educativo VARCHAR(100),
                titulo_semestre VARCHAR(100),
                nombre_profesor_asesor VARCHAR(255),
                correo_institucional_asesor VARCHAR(255),
                correo_estudiante VARCHAR(255) NOT NULL UNIQUE,
                telefono_estudiante VARCHAR(20),
                municipio VARCHAR(100),
                estado VARCHAR(100),
                categoria_concurso VARCHAR(100),
                acepta_terminos BOOLEAN,
                consentimiento_datos_fotos BOOLEAN,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            );
        ''')
        # NOTA: No insertamos un participante aquí para 'alumno_test',
        # así se podrá registrar uno nuevo desde la aplicación.
        # cursor.execute("INSERT IGNORE INTO participantes (id, usuario_id, nombre_completo, edad, fecha_nacimiento, genero, curp, nombre_institucion, nivel_educativo, titulo_semestre, correo_estudiante, telefono_estudiante, municipio, estado, categoria_concurso, acepta_terminos, consentimiento_datos_fotos) VALUES (1, 1, 'Alumno Test', 18, '2006-01-01', 'Masculino', 'ALUMTEST123456XYZ', 'Universidad Ejemplo', 'Licenciatura', '1er Semestre', 'alumno@example.com', '1234567890', 'Centro', 'Tabasco', 'Superior', TRUE, TRUE)")


        # Crear tabla actividades
        cursor.execute('''
            CREATE TABLE actividades (
                id INT AUTO_INCREMENT PRIMARY KEY,
                titulo VARCHAR(255) NOT NULL,
                descripcion TEXT,
                tipo VARCHAR(50)
            );
        ''')
        # Insertar actividades de prueba
        cursor.execute("INSERT IGNORE INTO actividades (id, titulo, descripcion, tipo) VALUES (1, 'Actividad 1: Lógica - El acertijo de los sombreros', 'Hay tres cajas: una solo contiene manzanas, otra solo peras y la tercera contiene manzanas y peras. Las tres cajas están mal etiquetadas. Tienes permitido sacar solo una fruta de una sola caja. ¿Cómo puedes etiquetar correctamente todas las cajas?', 'Lógica')")
        cursor.execute("INSERT IGNORE INTO actividades (id, titulo, descripcion, tipo) VALUES (2, 'Actividad 2: Lógica - El problema de los caramelos', 'Un problema de lógica con caramelos.', 'Lógica')")
        cursor.execute("INSERT IGNORE INTO actividades (id, titulo, descripcion, tipo) VALUES (18, 'Actividad 18: Problema - Estadística (Media)', 'Las calificaciones de un estudiante en 5 exámenes fueron: 85, 92, 78, 90, 88. Calcula la calificación promedio (media) del estudiante.', 'Estadística')")
        cursor.execute("INSERT IGNORE INTO actividades (id, titulo, descripcion, tipo) VALUES (19, 'Actividad 19: Problema - Área y Perímetro', 'Un jardín rectangular tiene un largo de 15 metros y un ancho de 8 metros. Calcula el perímetro y el área del jardín.', 'Geometría')")
        cursor.execute("INSERT IGNORE INTO actividades (id, titulo, descripcion, tipo) VALUES (20, 'Actividad 20: Problema - Interés Simple', 'Si inviertes $5000 a una tasa de interés simple del 6% anual durante 3 años, ¿cuánto interés habrás ganado al final de ese período?', 'Finanzas')")


        # Crear tabla respuestas_actividades
        cursor.execute('''
            CREATE TABLE respuestas_actividades ( 
                id INT AUTO_INCREMENT PRIMARY KEY,
                participante_id INT, 
                actividad_id INT, 
                respuesta_texto TEXT NOT NULL,
                fecha_respuesta DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (participante_id) REFERENCES participantes(id) ON DELETE CASCADE,
                FOREIGN KEY (actividad_id) REFERENCES actividades(id) ON DELETE CASCADE
            );
        ''')
        # Insertar respuestas de prueba (para que el juez tenga algo que calificar)
        # Asegúrate de que el participante_id exista si no estás borrando todo.
        # En esta versión, si eliminas el participante_id 1 al reiniciar, estas inserciones fallarán.
        # Son solo ejemplos, puedes quitarlas si quieres empezar desde cero con las respuestas también.
        # cursor.execute("INSERT IGNORE INTO respuestas_actividades (id, participante_id, actividad_id, respuesta_texto) VALUES (1, 1, 1, 'Mi respuesta al acertijo de los sombreros es...')")
        # cursor.execute("INSERT IGNORE INTO respuestas_actividades (id, participante_id, actividad_id, respuesta_texto) VALUES (2, 1, 18, 'El promedio es 86.6')")


        # Crear tabla calificaciones
        cursor.execute('''
            CREATE TABLE calificaciones (
                id INT AUTO_INCREMENT PRIMARY KEY,
                respuesta_id INT, 
                juez_id INT, 
                criterio_id INT, 
                puntaje_obtenido INT NOT NULL, 
                comentarios TEXT,
                fecha_calificacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (respuesta_id) REFERENCES respuestas_actividades(id) ON DELETE CASCADE,
                FOREIGN KEY (juez_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                FOREIGN KEY (criterio_id) REFERENCES criterios_evaluacion(id) ON DELETE CASCADE,
                CONSTRAINT UQ_calificacion_juez_criterio UNIQUE (respuesta_id, juez_id, criterio_id) 
            );
        ''')
        # Insertar calificaciones de prueba (para el juez)
        # Estas también podrían fallar si las respuestas o participantes no existen.
        # cursor.execute("INSERT IGNORE INTO calificaciones (id, respuesta_id, juez_id, criterio_id, puntaje_obtenido, comentarios) VALUES (1, 1, 2, 1, 10, 'Buen entendimiento del problema.')")
        # cursor.execute("INSERT IGNORE INTO calificaciones (id, respuesta_id, juez_id, criterio_id, puntaje_obtenido, comentarios) VALUES (2, 1, 2, 2, 12, 'Solución clara.')")
        # cursor.execute("INSERT IGNORE INTO calificaciones (id, respuesta_id, juez_id, criterio_id, puntaje_obtenido, comentarios) VALUES (3, 2, 2, 3, 20, 'Cálculo correcto de la media.')")


        # Crear tabla predicciones_resultados
        cursor.execute('''
            CREATE TABLE predicciones_resultados (
                id INT AUTO_INCREMENT PRIMARY KEY,
                participante_id INT, 
                juez_id INT, 
                desempeno_general TEXT,
                resultado_final TEXT,
                fecha_prediccion DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (participante_id) REFERENCES participantes(id) ON DELETE CASCADE,
                FOREIGN KEY (juez_id) REFERENCES usuarios(id) ON DELETE CASCADE
            );
        ''')

        # Habilitar de nuevo la verificación de claves foráneas
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

        mysql.connection.commit()
        print("Base de datos MySQL inicializada y tablas creadas/actualizadas con éxito.")

    except Exception as e:
        print(f"Error crítico al inicializar la base de datos MySQL: {e}")
        # Intentar hacer rollback si hay una transacción activa
        if mysql.connection and mysql.connection.open:
            mysql.connection.rollback()
    finally:
        # Asegurarse de cerrar el cursor
        if 'cursor' in locals() and cursor:
            cursor.close()

# Ejecutar la función de inicialización al inicio de la aplicación
with app.app_context():
    _create_tables_and_insert_data_mysql()

# Rutas existentes de la aplicación

@app.route('/')
def index():
    if 'loggedin' in session:
        if session.get('rol') == 'alumno':
            return redirect(url_for('alumno_dashboard'))
        elif session.get('rol') == 'juez':
            return redirect(url_for('juez_dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'loggedin' in session:
        if session.get('rol') == 'alumno':
            return redirect(url_for('alumno_dashboard'))
        elif session.get('rol') == 'juez':
            return redirect(url_for('juez_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Por favor, ingresa usuario y contraseña.', 'danger')
            return render_template('login.html')

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        try:
            cursor.execute('SELECT * FROM usuarios WHERE nombre_usuario = %s AND contrasena = %s', (username, password))
            account = cursor.fetchone()
            if account:
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['nombre_usuario']
                session['rol'] = account['rol']
                flash('¡Bienvenido!', 'success')
                if account['rol'] == 'alumno':
                    return redirect(url_for('alumno_dashboard'))
                elif account['rol'] == 'juez':
                    return redirect(url_for('juez_dashboard'))
            else:
                flash('Usuario o contraseña incorrectos', 'danger')
        except Exception as e:
            flash(f'Error de base de datos al iniciar sesión: {e}', 'danger')
        finally:
            cursor.close()
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('rol', None)
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('login'))

@app.route('/alumno_dashboard')
def alumno_dashboard():
    if 'loggedin' in session and session.get('rol') == 'alumno':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        participante_registrado = False
        try:
            cursor.execute('SELECT id FROM participantes WHERE usuario_id = %s', (session['id'],))
            existing_participante = cursor.fetchone()
            if existing_participante:
                participante_registrado = True
        except Exception as e:
            print(f"Error al verificar si el participante está registrado: {e}")
        finally:
            cursor.close()
            
        return render_template('alumno_dashboard.html', 
                               username=session.get('username'), 
                               participante_registrado=participante_registrado)
    flash('Necesitas iniciar sesión como alumno para acceder a esta página.', 'danger')
    return redirect(url_for('login'))

@app.route('/alumno/registrar_participante', methods=['GET', 'POST'])
def registrar_participante():
    if 'loggedin' in session and session.get('rol') == 'alumno':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        try:
            cursor.execute('SELECT id FROM participantes WHERE usuario_id = %s', (session['id'],))
            existing_participante = cursor.fetchone()

            if existing_participante:
                flash('Ya has registrado un participante con esta cuenta. Si necesitas actualizarlo, contacta al administrador.', 'info')
                return redirect(url_for('alumno_dashboard'))

            if request.method == 'POST':
                nombre_completo = request.form.get('nombre_completo')
                edad = request.form.get('edad')
                fecha_nacimiento = request.form.get('fecha_nacimiento')
                genero = request.form.get('genero')
                curp = request.form.get('curp') 
                nombre_institucion = request.form.get('nombre_institucion')
                nivel_educativo = request.form.get('nivel_educativo')
                titulo_grado_semestre = request.form.get('titulo_grado_semestre')
                nombre_profesor_asesor = request.form.get('nombre_profesor_asesor') 
                correo_institucional_asesor = request.form.get('correo_institucional_asesor') 
                correo_estudiante = request.form.get('correo_electronico')
                telefono_estudiante = request.form.get('numero_telefono')
                municipio = request.form.get('municipio')
                estado = request.form.get('estado')
                categoria_concurso = request.form.get('categoria_concurso', 'General') 
                acepta_terminos = 'acepta_terminos' in request.form
                consentimiento_datos_fotos = 'consentimiento_datos_fotos' in request.form

                # Validar campos requeridos
                required_fields = [
                    nombre_completo, edad, fecha_nacimiento, genero, 
                    nombre_institucion, nivel_educativo, titulo_grado_semestre, 
                    correo_estudiante, telefono_estudiante, municipio, estado
                ]
                if not all(required_fields):
                    flash('Por favor, completa todos los campos obligatorios.', 'danger')
                    return render_template('registrar_participante.html')

                # Validar checkboxes
                if not acepta_terminos:
                    flash('Debes aceptar los términos y condiciones.', 'danger')
                    return render_template('registrar_participante.html')
                if not consentimiento_datos_fotos:
                    flash('Debes dar tu consentimiento para el uso de datos y fotos.', 'danger')
                    return render_template('registrar_participante.html')


                cursor.execute("""
                    INSERT INTO participantes (
                        usuario_id, nombre_completo, edad, fecha_nacimiento, genero, curp,
                        nombre_institucion, nivel_educativo, titulo_semestre,
                        nombre_profesor_asesor, correo_institucional_asesor,
                        correo_estudiante, telefono_estudiante, municipio, estado,
                        categoria_concurso, acepta_terminos, consentimiento_datos_fotos
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    session['id'], nombre_completo, edad, fecha_nacimiento, genero, curp,
                    nombre_institucion, nivel_educativo, titulo_grado_semestre,
                    nombre_profesor_asesor, correo_institucional_asesor,
                    correo_estudiante, telefono_estudiante, municipio, estado,
                    categoria_concurso, acepta_terminos, consentimiento_datos_fotos
                ))
                mysql.connection.commit()
                flash('¡Registro de participante exitoso!', 'success')
                return redirect(url_for('alumno_dashboard'))

        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error al registrar participante: {e}', 'danger')
        finally:
            cursor.close()

        return render_template('registrar_participante.html')
    
    flash('Necesitas iniciar sesión como alumno para acceder a esta página.', 'danger')
    return redirect(url_for('login'))


@app.route('/alumno/responder_actividades')
def responder_actividades():
    if 'loggedin' in session and session.get('rol') == 'alumno':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        actividades = []
        try:
            cursor.execute('SELECT id FROM participantes WHERE usuario_id = %s', (session['id'],))
            participante = cursor.fetchone()

            if not participante:
                flash('Primero debes registrar tus datos como participante para responder actividades.', 'info')
                return redirect(url_for('registrar_participante'))

            cursor.execute('SELECT * FROM actividades')
            actividades = cursor.fetchall()
        except Exception as e:
            flash(f'Error al cargar actividades: {e}', 'danger')
            actividades = []
        finally:
            cursor.close()
        return render_template('responder_actividades.html', actividades=actividades)
    flash('Necesitas iniciar sesión como alumno para acceder a esta página.', 'danger')
    return redirect(url_for('login'))

@app.route('/submit_activity/<int:activity_id>', methods=['POST'])
def submit_activity(activity_id):
    if 'loggedin' not in session or session.get('rol') != 'alumno':
        flash('Debes iniciar sesión como alumno para enviar respuestas.', 'danger')
        return redirect(url_for('login'))

    respuesta_texto = request.form.get('respuesta')

    if respuesta_texto:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        try:
            cursor.execute('SELECT id FROM participantes WHERE usuario_id = %s', (session['id'],))
            participante = cursor.fetchone()

            if participante:
                participante_id = participante['id']
                cursor.execute("""
                    INSERT INTO respuestas_actividades (participante_id, actividad_id, respuesta_texto)
                    VALUES (%s, %s, %s)
                """, (participante_id, activity_id, respuesta_texto))
                mysql.connection.commit()
                flash(f'¡Respuesta para Actividad {activity_id} enviada correctamente!', 'success')
            else:
                flash('Error: No se encontró tu perfil de participante. Por favor, regístrate primero.', 'danger')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error al enviar respuesta: {e}', 'danger')
        finally:
            cursor.close()
    else:
        flash(f'No puedes enviar una respuesta vacía para la Actividad {activity_id}.', 'danger')

    return redirect(url_for('responder_actividades'))

@app.route('/alumno/ver_predicciones_alumno')
def ver_predicciones_alumno():
    if 'loggedin' in session and session.get('rol') == 'alumno':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        predicciones = []
        try:
            cursor.execute('SELECT id FROM participantes WHERE usuario_id = %s', (session['id'],))
            participante = cursor.fetchone()

            if not participante:
                flash('Primero debes registrar tus datos como participante para ver predicciones.', 'info')
                return redirect(url_for('registrar_participante'))

            participante_id = participante['id']
            cursor.execute("""
                SELECT pr.*, u.nombre_usuario as juez_nombre
                FROM predicciones_resultados pr
                JOIN usuarios u ON pr.juez_id = u.id
                WHERE pr.participante_id = %s
                ORDER BY pr.fecha_prediccion DESC
            """, (participante_id,))
            predicciones = cursor.fetchall()
        except Exception as e:
            flash(f'Error al cargar predicciones: {e}', 'danger')
        finally:
            cursor.close()
        return render_template('ver_predicciones_alumno.html', predicciones=predicciones)
    flash('Necesitas iniciar sesión como alumno para ver tus predicciones.', 'danger')
    return redirect(url_for('login'))

@app.route('/juez_dashboard')
def juez_dashboard():
    if 'loggedin' in session and session.get('rol') == 'juez':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        try:
            cursor.execute("""
                SELECT ra.id AS id_respuesta, a.titulo AS actividad_titulo, p.nombre_completo, ra.fecha_respuesta
                FROM respuestas_actividades ra
                JOIN actividades a ON ra.actividad_id = a.id
                JOIN participantes p ON ra.participante_id = p.id
                LEFT JOIN (
                    SELECT DISTINCT respuesta_id
                    FROM calificaciones
                    WHERE juez_id = %s
                ) AS calificaciones_juez ON ra.id = calificaciones_juez.respuesta_id
                WHERE calificaciones_juez.respuesta_id IS NULL 
                ORDER BY ra.fecha_respuesta ASC
            """, (session['id'],))
            respuestas_pendientes = cursor.fetchall()
        except Exception as e:
            flash(f'Error al cargar respuestas pendientes: {e}', 'danger')
            respuestas_pendientes = []
        finally:
            cursor.close()
        return render_template('juez_dashboard.html', username=session.get('username'), respuestas_pendientes=respuestas_pendientes)
    flash('Necesitas iniciar sesión como juez para acceder a esta página.', 'danger')
    return redirect(url_for('login'))

@app.route('/juez/ver_participantes')
def ver_participantes_juez():
    if 'loggedin' in session and session.get('rol') == 'juez':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        participantes = []
        try:
            cursor.execute('SELECT p.*, u.nombre_usuario FROM participantes p JOIN usuarios u ON p.usuario_id = u.id')
            participantes = cursor.fetchall()
        except Exception as e:
            flash(f'Error al cargar participantes: {e}', 'danger')
        finally:
            cursor.close()
        return render_template('ver_participantes_juez.html', participantes=participantes)
    flash('Necesitas iniciar sesión como juez para acceder a esta página.', 'danger')
    return redirect(url_for('login'))

@app.route('/criterios_evaluacion') 
def criterios_evaluacion():
    if 'loggedin' not in session:
        flash('Debes iniciar sesión para ver los criterios de evaluación.', 'danger')
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    criterios = []
    total_puntos = 0
    try:
        cursor.execute('SELECT * FROM criterios_evaluacion ORDER BY id')
        criterios = cursor.fetchall()
        total_puntos = sum(criterio['puntos'] for criterio in criterios)
    except Exception as e:
        flash(f'Error al cargar criterios de evaluación: {e}', 'danger')
        criterios = []
        total_puntos = 0
    finally:
        cursor.close()

    return render_template('criterios_evaluacion.html', criterios=criterios, total_puntos=total_puntos)

@app.route('/juez/criterios_evaluacion') 
def ver_criterios_juez():
    if 'loggedin' in session and session.get('rol') == 'juez':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        criterios = []
        total_puntos = 0
        try:
            cursor.execute('SELECT * FROM criterios_evaluacion ORDER BY id')
            criterios = cursor.fetchall()
            total_puntos = sum(criterio['puntos'] for criterio in criterios)
        except Exception as e:
            flash(f'Error al cargar criterios de evaluación para el juez: {e}', 'danger')
            criterios = []
            total_puntos = 0
        finally:
            cursor.close()
        return render_template('criterios_evaluacion_juez.html', criterios=criterios, total_puntos=total_puntos)
    flash('Necesitas iniciar sesión como juez para acceder a esta página.', 'danger')
    return redirect(url_for('login'))


@app.route('/juez/calificar_actividades')
def calificar_actividades():
    """
    Muestra una lista de respuestas de actividades pendientes para que el juez las califique.
    """
    if 'loggedin' not in session or session.get('rol') != 'juez':
        flash('Necesitas iniciar sesión como juez para acceder a esta página.', 'danger')
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    respuestas_pendientes = []
    criterios_evaluacion = []

    try:
        # Consulta para obtener las respuestas pendientes de calificación para el juez actual.
        # Trae la información de la respuesta, la actividad y el participante.
        cursor.execute("""
            SELECT 
                ra.id AS respuesta_id, 
                ra.respuesta_texto, 
                ra.fecha_respuesta,
                a.titulo AS titulo_actividad, 
                a.descripcion AS descripcion_actividad,
                p.nombre_completo AS nombre_participante
            FROM respuestas_actividades ra
            JOIN actividades a ON ra.actividad_id = a.id
            JOIN participantes p ON ra.participante_id = p.id
            LEFT JOIN (
                SELECT DISTINCT respuesta_id
                FROM calificaciones
                WHERE juez_id = %s
            ) AS calificaciones_juez ON ra.id = calificaciones_juez.respuesta_id
            WHERE calificaciones_juez.respuesta_id IS NULL  -- Solo respuestas no calificadas por este juez
            ORDER BY ra.fecha_respuesta ASC
        """, (session['id'],)) 
        respuestas_pendientes = cursor.fetchall()

        # Obtener los criterios de evaluación para el formulario
        # Se renombra 'titulo' a 'nombre_criterio' y 'puntos' a 'puntaje_maximo'
        # para que coincida con lo que espera tu plantilla HTML.
        cursor.execute('SELECT id, titulo AS nombre_criterio, puntos AS puntaje_maximo FROM criterios_evaluacion ORDER BY id')
        criterios_evaluacion = cursor.fetchall()
            
    except Exception as e:
        flash(f'Error al cargar datos para calificación: {e}', 'danger')
    finally:
        cursor.close()

    return render_template(
        'calificar_actividades.html',
        respuestas=respuestas_pendientes, # Ahora pasamos una lista de respuestas
        criterios=criterios_evaluacion
    )

@app.route('/juez/guardar_calificacion', methods=['POST'])
def guardar_calificacion():
    """
    Guarda la calificación de una actividad por parte de un juez.
    """
    if 'loggedin' in session and session.get('rol') != 'juez':
        flash('Necesitas iniciar sesión como juez para guardar calificaciones.', 'danger')
        return redirect(url_for('login'))

    respuesta_id = request.form.get('respuesta_id') 
    juez_id = session['id']
    comentarios_generales = request.form.get('comentarios_generales') 

    if not respuesta_id or not juez_id:
        flash('Datos incompletos para guardar la calificación.', 'danger')
        return redirect(url_for('calificar_actividades')) 

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    try:
        # Obtener los criterios de la DB para validar los puntos
        cursor.execute('SELECT id, titulo, puntos FROM criterios_evaluacion')
        criterios_db = {c['id']: {'titulo': c['titulo'], 'puntos': c['puntos']} for c in cursor.fetchall()}

        # Eliminar calificaciones existentes para esta respuesta por este juez
        # Esto permite recalificar o actualizar la calificación si ya existe
        cursor.execute("DELETE FROM calificaciones WHERE respuesta_id = %s AND juez_id = %s", (respuesta_id, juez_id))

        for criterio_id_str, puntaje_str in request.form.items():
            if criterio_id_str.startswith('puntaje_'): 
                criterio_id = int(criterio_id_str.split('_')[1])
                
                if puntaje_str is None or puntaje_str.strip() == '':
                    puntaje_obtenido = 0 
                else:
                    try:
                        puntaje_obtenido = int(puntaje_str)
                    except ValueError:
                        flash(f'El puntaje para el criterio {criterios_db.get(criterio_id, {}).get("titulo", criterio_id)} no es un número válido.', 'danger')
                        mysql.connection.rollback()
                        return redirect(url_for('calificar_actividades')) 

                max_puntos = criterios_db.get(criterio_id, {}).get('puntos')
                if max_puntos is None:
                    flash(f'Error: Criterio ID {criterio_id} no encontrado en la base de datos.', 'danger')
                    mysql.connection.rollback()
                    return redirect(url_for('calificar_actividades')) 
                
                if not (0 <= puntaje_obtenido <= max_puntos):
                    flash(f'El puntaje para el criterio "{criterios_db.get(criterio_id, {}).get("titulo", criterio_id)}" ({puntaje_obtenido}) excede el máximo permitido ({max_puntos}).', 'danger')
                    mysql.connection.rollback()
                    return redirect(url_for('calificar_actividades')) 

                cursor.execute("""
                    INSERT INTO calificaciones (respuesta_id, juez_id, criterio_id, puntaje_obtenido, comentarios)
                    VALUES (%s, %s, %s, %s, %s)
                """, (respuesta_id, juez_id, criterio_id, puntaje_obtenido, comentarios_generales))

        mysql.connection.commit()
        flash('Calificación guardada exitosamente.', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error al guardar calificación: {e}', 'danger')
    finally:
        cursor.close()

    return redirect(url_for('calificar_actividades')) 

@app.route('/juez/dar_predicciones', methods=['GET', 'POST'])
def dar_predicciones_juez():
    if 'loggedin' in session and session.get('rol') == 'juez':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        participantes = []
        try:
            cursor.execute('SELECT id, nombre_completo FROM participantes')
            participantes = cursor.fetchall()

            if request.method == 'POST':
                participante_id = request.form.get('participante_id')
                desempeno_general = request.form.get('desempeno_general')
                resultado_final = request.form.get('resultado_final')
                juez_id = session['id']

                cursor.execute("""
                    SELECT id FROM predicciones_resultados
                    WHERE participante_id = %s AND juez_id = %s
                """, (participante_id, juez_id))
                existing_prediccion = cursor.fetchone()

                if existing_prediccion:
                    cursor.execute("""
                        UPDATE predicciones_resultados
                        SET desempeno_general = %s, resultado_final = %s, fecha_prediccion = NOW()
                        WHERE id = %s
                    """, (desempeno_general, resultado_final, existing_prediccion['id']))
                else:
                    cursor.execute("""
                        INSERT INTO predicciones_resultados (participante_id, juez_id, desempeno_general, resultado_final)
                        VALUES (%s, %s, %s, %s)
                    """, (participante_id, juez_id, desempeno_general, resultado_final))

                mysql.connection.commit()
                flash('Predicción/resultado guardado exitosamente para el participante.', 'success')
                return redirect(url_for('dar_predicciones_juez'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error al guardar predicción/resultado: {e}', 'danger')
        finally:
            cursor.close()

        return render_template('dar_predicciones_juez.html', participantes=participantes)
    flash('Necesitas iniciar sesión como juez para acceder a esta página.', 'danger')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
