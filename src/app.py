from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash
from forms import registerForm, loginForm, DonationForm, ContactForm
from models.modelUser import ModelUser
import os
from extensions import mysql
from dotenv import load_dotenv
from flask_mail import Message
from extensions import mail
from tokens import generate_token, confirm_token
from datetime import datetime


load_dotenv()


app = Flask(__name__)

# Configuración de Flask-Mail usando variables de entorno
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
mail.init_app(app)


app.config["MYSQL_USER"] = os.getenv("MYSQL_USER")
app.config["MYSQL_HOST"] = os.getenv("MYSQL_HOST")
app.config["MYSQL_PASSWORD"] = os.getenv("MYSQL_PASSWORD")
app.config["MYSQL_DB"] = os.getenv("MYSQL_DB")
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

mysql.init_app(app)

from perfil import perfil_bp
app.register_blueprint(perfil_bp)

from admin import admin_bp
app.register_blueprint(admin_bp)

from errors import errors
app.register_blueprint(errors)


login_manager = LoginManager(app)

@login_manager.user_loader
def get_by_id(id):
    return ModelUser.get_by_id(mysql, id)

@app.route('/', methods=['GET'])
def inicio():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM animales')
    animales = cursor.fetchall()  

    animales_dict = []
    for row in animales:
        animales_dict.append({
            'id': row[0],
            'nombre': row[1],
            'descripcion': row[2],
            'imagen': row[3]
        })

    return render_template("inicio.html", animales=animales_dict)

@app.route('/login', methods=['POST','GET'])
def login():
    form = loginForm()

    if request.method == 'POST':

        password = request.form.get('password')
        email = request.form.get('email')
    
        logged_user = ModelUser.login(mysql,email, password)

        if logged_user:
            if logged_user.password:

                login_user(logged_user)

                return redirect(url_for('inicio'))
            else:
                flash("Contraseña incorrecta", "error")
                return redirect(url_for('login'))

        else:
            flash("Usuario no encontrado", "error")
            return redirect(url_for('login'))
        
    else: 
        if current_user.is_authenticated:
            return redirect(url_for('inicio'))
        return render_template('login.html', form=form)

    
@app.route('/register', methods=['POST', 'GET'])
def register():
    form = registerForm()

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        password = request.form.get('password')
        telefono = request.form.get('telefono')
        email = request.form.get('email')

        hashed_password = generate_password_hash(password)

        try:
            cur = mysql.connection.cursor()

            sql = "INSERT INTO usuarios (nombre, contraseña, telefono, email) VALUES (%s, %s, %s, %s)"

            cur.execute(sql, (nombre, hashed_password, telefono, email))

            mysql.connection.commit()

        except Exception as e:
            flash("Error al registrar el usuario. Verifica que el correo no esté en uso.", "error")
            return redirect(url_for('register'))

        user = ModelUser.get_by_email(mysql, email) 
        if user:
            login_user(user) 
            flash("Registro exitoso. Bienvenido.", "success")
            return redirect(url_for('inicio'))
        else:
            flash("No se pudo iniciar sesión después del registro.", "error")
            return redirect(url_for('login'))

    else:
        if current_user.is_authenticated:
            return redirect(url_for('inicio'))
        return render_template('register.html', form=form)


@app.route('/adoptar', methods=['GET'])
def adoptar():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM animales')
    animales = cursor.fetchall()  

    animales_dict = []
    for row in animales:
        animales_dict.append({
            'id': row[0],
            'nombre': row[1],
            'descripcion': row[2],
            'imagen': row[3]
        })
    

    return render_template('adoptar.html', animales=animales_dict)

@app.route('/adoptar/<string:nombre>', methods=['GET'])
def adoptar_detalle(nombre):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM animales WHERE nombre = %s', (nombre,))
    animal = cursor.fetchone()
    if animal is not None:
        animal = {
            'id': animal[0],
            'nombre': animal[1],
            'descripcion': animal[2],
            'imagen': animal[3]
        }
    else:
        animal = None

    if animal is None:
        return "Animal no encontrado", 404
    return render_template('adoptar_detalle.html', animal=animal)

@app.route('/solicitar_adopcion/<int:animal_id>')
@login_required
def solicitar_adopcion(animal_id):
    usuario_id = current_user.id

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT * FROM solicitudes 
        WHERE usuario_id = %s AND animal_id = %s
    """, (usuario_id, animal_id))
    existe = cur.fetchone()

    if existe:
        flash('Ya has enviado una solicitud para este animal.', 'warning')
        cur.close()
        return redirect(url_for('adoptar')) 

    cur.execute("""
        INSERT INTO solicitudes (usuario_id, animal_id, fecha)
        VALUES (%s, %s, %s)
    """, (usuario_id, animal_id, datetime.now()))
    mysql.connection.commit()
    cur.close()

    return render_template('solicitud_enviada.html')


@app.route('/donaciones', methods=['GET', 'POST'])
def donaciones():
    form = DonationForm()

    if form.validate_on_submit():
        payment_method = form.payment_method.data

        if payment_method == 'card':
            if not form.card_number.data or not form.card_expiry.data:
                flash("Por favor, completa los datos de la tarjeta", "danger")
                return redirect(url_for('donaciones'))


        elif payment_method == 'paypal':
            if not form.paypal_email.data:
                flash("Introduce un correo electrónico de PayPal", "danger")
                return redirect(url_for('donaciones'))


        elif payment_method == 'bank':
            if not form.bank_account.data:
                flash("Introduce un número de cuenta bancaria", "danger")
                return redirect(url_for('donaciones'))

        flash("¡Gracias por tu donación!", "success")
        return redirect(url_for('donaciones'))
    
    return render_template('donaciones.html', form=form)
    
@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    form = ContactForm()

    if form.validate_on_submit():
        msg = Message(
            subject= form.subject.data,
            sender= 'tunuevamascotatfg@gmail.com',
            recipients=['tunuevamascotatfg@gmail.com'],
            body=f"De: {form.name.data} <{form.email.data}>\n\n{form.message.data}"
        )

        try:
            mail.send(msg)
            flash("¡Tu mensaje ha sido enviado con éxito!", "success")
        except Exception as e:
            flash("Error al enviar el mensaje. Inténtalo más tarde.", "danger")
            print(e)

        return redirect(url_for('contacto'))

    return render_template('contacto.html', form=form)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if request.method == 'POST':
        email = request.form['email']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT email FROM usuarios WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            token = generate_token(email)
            reset_url = url_for('reset_token', token=token, _external=True)
            msg = Message('Restablecer contraseña', 
                sender='tunuevamascotatfg@gmail.com',
                recipients=[email])
            msg.body = f'Para restablecer tu contraseña, haz clic en el siguiente enlace:\n{reset_url}\n\nEste enlace expira en 20 minutos.'
            mail.send(msg)

        flash('Si existe una cuenta con ese correo, se ha enviado un enlace para restablecer la contraseña.', 'info')
        return redirect(url_for('perfil.perfil'))

    return render_template('reset_request.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    email = confirm_token(token)
    if not email:
        flash('El enlace es inválido o ha expirado, intentalo de nuevo.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_password = request.form['password']
        hashed_password = generate_password_hash(new_password)

        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE usuarios SET contraseña = %s WHERE email = %s", (hashed_password, email))
        mysql.connection.commit()
        cursor.close()

        flash('Tu contraseña ha sido actualizada. Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('perfil.perfil'))

    return render_template('reset_token.html')

@app.route('/logout', methods=['GET'])
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash("Sesión cerrada")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)