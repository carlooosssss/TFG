from .entities.user import User

class ModelUser():
    @classmethod
    def login(self, db, email, password):
        try:
            cursor = db.connection.cursor()
            sql = 'SELECT * FROM usuarios WHERE email=%s'
            cursor.execute(sql, (email,))
            row = cursor.fetchone()

            if row:
                id = row[0]
                nombre = row[1]
                password = User.check_password(row[2], password)
                telefono = row[3]
                email = row[4]

                user = User(id, nombre, password, telefono, email)
                
                return user
            else:
                return None
                
        except Exception as e:

            raise Exception(e)
    
    @classmethod
    def get_by_id(cls, db, id):
        try:
            cursor = db.connection.cursor()
            sql = 'SELECT id, nombre, contraseña, telefono, email FROM usuarios WHERE id=%s'
            cursor.execute(sql, (id,))
            row = cursor.fetchone()

            if row:
                id = row[0]
                nombre = row[1]
                telefono = row[3]
                email = row[4]

                user = User(id, nombre, None, telefono, email )
                
                return user
            else:
                return None
                
        except Exception as e:

            raise Exception(e)
        
    @classmethod
    def get_by_email(cls, db, email):
        try:
            cursor = db.connection.cursor()
            sql = 'SELECT * FROM usuarios WHERE email = %s'
            cursor.execute(sql, (email,))
            row = cursor.fetchone()

            if row:
                return User(*row)
            return None
        
        except Exception as e:
            raise Exception(e)
    
    @classmethod
    def update_user_data(cls, db, id, nombre, email, telefono, password=None):
        try:
            cursor = db.connection.cursor()
            if password:
                sql = 'UPDATE usuarios SET nombre=%s, email=%s, telefono=%s, contraseña=%s WHERE id=%s'
                cursor.execute(sql, (nombre, email, telefono, password, id))
            else:
                sql = 'UPDATE usuarios SET nombre=%s, email=%s, telefono=%s WHERE id=%s'
                cursor.execute(sql, (nombre, email, telefono, id))
            db.connection.commit()
        except Exception as e:
            raise Exception(e)