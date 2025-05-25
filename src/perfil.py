from flask import Blueprint, render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from models.modelUser import ModelUser
from flask_login import login_required, current_user
from forms import PerfilForm
from extensions import mysql


perfil_bp = Blueprint('perfil', __name__)

@perfil_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    user = current_user  

    form = PerfilForm(data={
        'nombre': user.nombre,
        'correo': user.email,
        'telefono': user.telefono
    })

    if form.validate_on_submit():
        nombre = form.nombre.data
        correo = form.correo.data
        telefono = form.telefono.data
        password = form.password.data

        hashed_password = generate_password_hash(password) if password else None

        ModelUser.update_user_data(mysql, user.id, nombre, correo, telefono, hashed_password)
        flash("Perfil actualizado correctamente", "success")
        return redirect(url_for('perfil.perfil'))

    return render_template('perfil.html', form=form)
