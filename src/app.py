from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import registerForm, loginForm
from models.modelUser import ModelUser
from flask_mysqldb import MySQL

import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config["MYSQL_USER"] = os.getenv("MYSQL_USER")
app.config["MYSQL_HOST"] = os.getenv("MYSQL_HOST")
app.config["MYSQL_PASSWORD"] = os.getenv("MYSQL_PASSWORD")
app.config["MYSQL_DB"] = os.getenv("MYSQL_DB")
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

db = MySQL(app)
login_manager = LoginManager(app)

@login_manager.user_loader
def get_by_id(id):
    return ModelUser.get_by_id(db, id)

@app.route('/', methods=['GET'])
def inicio():
    return render_template("inicio.html")

@app.route('/login', methods=['POST','GET'])
def login():
    form = loginForm()

    if request.method == 'POST':

        password = request.form.get('password')
        email = request.form.get('email')
    
        logged_user = ModelUser.login(db,email, password)

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
            cur = db.connection.cursor()

            sql = "INSERT INTO usuarios (nombre, contraseña, telefono, email) VALUES (%s, %s, %s, %s)"

            cur.execute(sql, (nombre, hashed_password, telefono, email))

            db.connection.commit()

        except Exception as e:
            flash("Error al registrar el usuario. Verifica que el correo no esté en uso.", "error")
            return redirect(url_for('register'))

        # Obtener el usuario recién creado
        user = ModelUser.get_by_email(db, email) 
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
    cursor = db.connection.cursor()
    cursor.execute('SELECT * FROM animales')
    animales = cursor.fetchall()  # Esto devuelve una lista de tuplas

    # Opcional: convertir a lista de dicts si lo necesitas así en tu plantilla
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
    cursor = db.connection.cursor()
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

@app.route('/donaciones', methods=['GET'])
def donaciones():
    return render_template('donaciones.html')

@app.route('/contacto', methods=['GET'])
def contacto():
    return render_template('contacto.html')

@app.route('/perfil', methods=['GET'])
def perfil():
    if current_user.is_authenticated:
        return render_template('perfil.html', user=current_user)
    else:
        return redirect(url_for('login'))

@app.route('/logout', methods=['GET'])
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash("Sesión cerrada")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)