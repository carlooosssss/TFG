from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from forms import AnimalForm
from extensions import mysql


admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/animales')
@login_required
def listar_animales():
    if not (current_user.email == 'admin@admin.admin'):
            flash('Acceso restringido solo para el administrador.', 'danger')
            return redirect(url_for('inicio')) 
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM animales")
    animales = cur.fetchall()
    return render_template('admin/listar_animales.html', animales=animales)


@admin_bp.route('/animales/agregar', methods=['GET', 'POST'])
@login_required
def agregar_animal():
    if not (current_user.email == 'admin@admin.admin'):
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
    if not (current_user.email == 'admin@admin.admin'):
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
    if not (current_user.email == 'admin@admin.admin'):
            flash('Acceso restringido solo para el administrador.', 'danger')
            return redirect(url_for('inicio')) 

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM animales WHERE id = %s", (id,))
    mysql.connection.commit()
    flash('Animal eliminado', 'success')
    return redirect(url_for('admin.listar_animales'))
