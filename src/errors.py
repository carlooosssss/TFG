from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)

@errors.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/error.html', error_code=404, error_message='La página que buscas no existe.'), 404

@errors.app_errorhandler(500)
def internal_error(error):
    return render_template('errors/error.html', error_code=500, error_message='Error interno del servidor.'), 500

@errors.app_errorhandler(403)
def forbidden_error(error):
    return render_template('errors/error.html', error_code=403, error_message='Acceso denegado.'), 403

@errors.app_errorhandler(401)
def forbidden_error(error):
    return render_template('errors/error.html', error_code=403, error_message='Acceso denegado. Prueba a iniciar sesión, sino esta ruta no es de tu incumbencia'), 401

@errors.app_errorhandler(405)
def method_not_allowed_error(error):
    return render_template('errors/error.html', error_code=405, error_message='Método no permitido en esta URL.'), 405