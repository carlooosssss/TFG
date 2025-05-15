from flask_wtf import FlaskForm 
from wtforms import PasswordField, EmailField, SubmitField, StringField
from wtforms.validators import DataRequired, Length, Regexp

class registerForm(FlaskForm):
    nombre = StringField('Nombre completo', validators=[
        Length(min=3, max=100),
        DataRequired()
    ])

    email = EmailField('Email', validators=[
        Length(min=10, max=50),
        DataRequired()
    ])

    password = PasswordField('Password', validators=[
        Length(min=6, max=50),
        DataRequired()
    ])

    telefono = StringField('Teléfono', validators=[
        Length(min=9, max=15),
        DataRequired(),
        Regexp(r'^\d+$', message="El teléfono solo debe contener números")
    ])

    submit = SubmitField('Crear cuenta')


class loginForm(FlaskForm):
    email = EmailField('Email', validators=[
        Length(min=10, max=50),
        DataRequired()
    ])

    password = PasswordField('Password', validators=[
        Length(min=6, max=255),
        DataRequired()
    ])

    submit = SubmitField('Iniciar sesión')
