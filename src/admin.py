from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from forms import AnimalForm
from extensions import mysql
from flask_mail import Message
from extensions import mail 


admin_bp = Blueprint('admin', __name__)



@admin_bp.route('/solicitudes')
@login_required 
def listar_solicitudes():
    if not (current_user.email == 'admin@admin.com'):
            flash('Acceso restringido solo para el administrador.', 'danger')
            return redirect(url_for('inicio'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM solicitudes")
    solicitudes = cur.fetchall()
    print(solicitudes)
    
    return render_template('admin/listar_solicitudes.html', solicitudes=solicitudes)

@admin_bp.route('/usuarios')
@login_required
def listar_usuarios():
    if not (current_user.email == 'admin@admin.com'):
            flash('Acceso restringido solo para el administrador.', 'danger')
            return redirect(url_for('inicio'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios")
    usuarios = cur.fetchall()
    return render_template('admin/listar_usuarios.html', usuarios=usuarios)

@admin_bp.route('/animales')
@login_required
def listar_animales():
    if not (current_user.email == 'admin@admin.com'):
            flash('Acceso restringido solo para el administrador.', 'danger')
            return redirect(url_for('inicio')) 
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM animales")
    animales = cur.fetchall()
    return render_template('admin/listar_animales.html', animales=animales)


@admin_bp.route('/animales/agregar', methods=['GET', 'POST'])
@login_required
def agregar_animal():
    if not (current_user.email == 'admin@admin.com'):
            flash('Acceso restringido solo para el administrador.', 'danger')
            return redirect(url_for('inicio')) 
    form = AnimalForm()
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        sql = "INSERT INTO animales (nombre, descripcion, imagen) VALUES (%s, %s, %s)"
        cur.execute(sql, (form.nombre.data, form.descripcion.data, form.imagen.data))
        mysql.connection.commit()
        flash('Animal agregado correctamente', 'success')
        return redirect(url_for('admin.listar_animales'))
    return render_template('admin/form_animal.html', form=form, accion='Agregar')


@admin_bp.route('/animales/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_animal(id):
    if not (current_user.email == 'admin@admin.com'):
            flash('Acceso restringido solo para el administrador.', 'danger')
            return redirect(url_for('inicio')) 
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM animales WHERE id = %s", (id,))
    animal = cur.fetchone()

    if not animal:
        flash('Animal no encontrado', 'danger')
        return redirect(url_for('admin.listar_animales'))

    form = AnimalForm(data={
        'nombre': animal[1],
        'descripcion': animal[2],
        'imagen': animal[3]
    })

    if form.validate_on_submit():
        cur.execute("""
            UPDATE animales SET nombre=%s, descripcion=%s, imagen=%s WHERE id=%s
        """, (form.nombre.data, form.descripcion.data, form.imagen.data, id))
        mysql.connection.commit()
        flash('Animal actualizado', 'success')
        return redirect(url_for('admin.listar_animales'))

    return render_template('admin/editar_animal.html', form=form, accion='Editar')


@admin_bp.route('/animales/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_animal(id):
    if not (current_user.email == 'admin@admin.com'):
            flash('Acceso restringido solo para el administrador.', 'danger')
            return redirect(url_for('inicio')) 

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM animales WHERE id = %s", (id,))
    mysql.connection.commit()
    flash('Animal eliminado', 'success')
    return redirect(url_for('admin.listar_animales'))


@admin_bp.route('/solicitudes/aprobar/<int:id>', methods=['POST'])
@login_required
def aprobar_solicitud(id):
    if current_user.email != 'admin@admin.com':
        flash('Acceso restringido solo para el administrador.', 'danger')
        return redirect(url_for('inicio'))

    cur = mysql.connection.cursor()

    cur.execute("SELECT usuario_id FROM solicitudes WHERE id = %s", (id,))
    result = cur.fetchone()
    if not result:
        flash('Solicitud no encontrada.', 'danger')
        return redirect(url_for('admin.listar_solicitudes'))
    usuario_id = result[0]

    cur.execute("SELECT email, nombre FROM usuarios WHERE id = %s", (usuario_id,))
    usuario = cur.fetchone()
    if not usuario:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('admin.listar_solicitudes'))

    email_usuario = usuario[0]
    nombre_usuario = usuario[1]

    cur.execute("UPDATE solicitudes SET estado = 'Aprobada' WHERE id = %s", (id,))
    mysql.connection.commit()

    msg = Message(
        subject="Solicitud de adopción aprobada",
        sender='tunuevamascotatfg@gmail.com',
        recipients=[email_usuario],
        body=f"Hola {nombre_usuario},\n\n¡Tu solicitud de adopción ha sido aprobada! Pronto nos pondremos en contacto contigo para continuar el proceso.\n\nGracias."
    )

    try:
        mail.send(msg)
        flash('Solicitud aprobada y correo enviado al usuario.', 'success')
    except Exception as e:
        flash('Solicitud aprobada, pero falló el envío del correo.', 'warning')
        print("Error enviando el correo:", e)

    return redirect(url_for('admin.listar_solicitudes'))

@admin_bp.route('/solicitudes/rechazar/<int:id>', methods=['POST'])
@login_required
def rechazar_solicitud(id):
    if current_user.email != 'admin@admin.com':
        flash('Acceso restringido solo para el administrador.', 'danger')
        return redirect(url_for('inicio'))

    cur = mysql.connection.cursor()

    cur.execute("SELECT usuario_id FROM solicitudes WHERE id = %s", (id,))
    result = cur.fetchone()
    if not result:
        flash('Solicitud no encontrada.', 'danger')
        return redirect(url_for('admin.listar_solicitudes'))
    usuario_id = result[0]

    cur.execute("SELECT email, nombre FROM usuarios WHERE id = %s", (usuario_id,))
    usuario = cur.fetchone()
    if not usuario:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('admin.listar_solicitudes'))

    email_usuario = usuario[0]
    nombre_usuario = usuario[1]

    cur.execute("UPDATE solicitudes SET estado = 'Rechazada' WHERE id = %s", (id,))
    mysql.connection.commit()

    msg = Message(
        subject="Solicitud de adopción rechazada",
        recipients=[email_usuario],
        sender="tunuevamascotatfg@gmail.com",
        body=f"Hola {nombre_usuario},\n\nLamentablemente, tu solicitud de adopción ha sido rechazada. Puedes intentarlo de nuevo más adelante o consultar con el equipo para más detalles.\n\nGracias."
    )

    try:
        mail.send(msg)
        flash('Solicitud rechazada y correo enviado al usuario.', 'danger')
    except Exception as e:
        flash('Solicitud aprobada, pero falló el envío del correo.', 'warning')
        print("Error enviando el correo:", e)

    return redirect(url_for('admin.listar_solicitudes'))