from flask_wtf import FlaskForm 
from wtforms import PasswordField, EmailField, SubmitField, StringField, DecimalField, RadioField, TextAreaField
from wtforms.validators import DataRequired, Length, Regexp, Email, Optional

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

class DonationForm(FlaskForm):
    amount = DecimalField('Cantidad a donar (€)',
        places=2, 
        validators=[DataRequired()])
    
    payment_method = RadioField('Método de pago',
        choices=[
            ('card', 'Tarjeta de crédito'),
            ('paypal', 'PayPal'),
            ('bank', 'Transferencia bancaria')
        ], validators=[DataRequired()])

    card_number = StringField('Número de tarjeta', 
        validators=[Optional()])
    
    card_expiry = StringField('Fecha de vencimiento (MM/AA)',
        validators=[Optional()])

    # PayPal
    paypal_email = StringField('Correo de PayPal', 
        validators=[
            Optional(),
            Email()])

    # Transferencia
    bank_account = StringField('Número de cuenta bancaria',
        validators=[Optional()])

    submit = SubmitField('Donar')

class ContactForm(FlaskForm):
    name = StringField('Nombre', 
        validators=[
            DataRequired(),
            Length(max=50)])
    
    email = EmailField('Correo electrónico',
        validators=[
            DataRequired(),
            Email(),
            Length(max=120)])
    
    subject = StringField('Asunto', 
        validators=[DataRequired(),
        Length(max=100)])
    
    message = TextAreaField('Mensaje', 
        validators=[DataRequired(),
        Length(max=500)])
    
    submit = SubmitField('Enviar')

class PerfilForm(FlaskForm):
    
    nombre = StringField('Nombre completo',
        validators=[DataRequired()])
    
    correo = StringField('Correo electrónico',
        validators=[DataRequired(), Email()])
    
    telefono = StringField('Teléfono',
        validators=[DataRequired()])
    
    password = PasswordField('Nueva contraseña (opcional)',
        validators=[Optional(), Length(min=6)])
    
    submit = SubmitField('Guardar')

class AnimalForm(FlaskForm):

    nombre = StringField('Nombre',
        validators=[DataRequired()])
    
    descripcion = TextAreaField('Descripción',
        validators=[DataRequired()])
    
    imagen = StringField('URL de imagen',
        validators=[DataRequired()])
    
    submit = SubmitField('Guardar')