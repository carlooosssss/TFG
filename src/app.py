from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, current_user, logout_user
from werkzeug.security import generate_password_hash
from forms import registerForm, loginForm, DonationForm, ContactForm
from models.modelUser import ModelUser
import os
from extensions import mysql
from dotenv import load_dotenv
from flask_mail import Mail, Message

load_dotenv()


app = Flask(__name__)

# Configuración de Flask-Mail usando variables de entorno
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

mail = Mail(app)


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

login_manager = LoginManager(app)

@login_manager.user_loader
def get_by_id(id):
    return ModelUser.get_by_id(mysql, id)

@app.route('/', methods=['GET'])
def inicio():
    return render_template("inicio.html")

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
        print(user)
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


@app.route('/incio', methods=['GET'])
def incio():
    return render_template('incio.html')


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
    
    print(animales_dict)

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
            subject=form.subject.data,
            sender=form.email.data,
            recipients=['carlosrs2210.crs@gmail.com'],
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

@app.route('/logout', methods=['GET'])
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash("Sesión cerrada")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)