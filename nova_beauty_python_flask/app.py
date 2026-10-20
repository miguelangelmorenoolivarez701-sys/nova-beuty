from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "nova-beauty-cambia-esta-clave")
db_path = os.path.join(os.path.dirname(__file__), "nova_beauty.db")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", f"sqlite:///{db_path}")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Usuario(db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Producto(db.Model):
    __tablename__ = "productos"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    categoria = db.Column(db.String(80), nullable=False, default="General")
    precio = db.Column(db.Float, nullable=False)
    imagen = db.Column(db.String(255), nullable=True)
    descripcion = db.Column(db.String(255), nullable=True)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

def usuario_actual():
    uid = session.get("user_id")
    return Usuario.query.get(uid) if uid else None

@app.context_processor
def injectar_usuario():
    return {"usuario_actual": usuario_actual()}

def requiere_login():
    if not usuario_actual():
        flash("Debes iniciar sesión para continuar.", "error")
        return False
    return True

@app.route("/")
@app.route("/pagina del proyecto.html")
def pagina_proyecto():
    productos = Producto.query.order_by(Producto.id.asc()).all()
    return render_template("pagina del proyecto.html", productos=productos)

@app.route("/iniciarsesion.html", methods=["GET", "POST"])
def iniciar_sesion():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        user = Usuario.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            flash(f"Inicio de sesión exitoso. Bienvenido {user.nombre}", "success")
            return redirect(url_for("pagina_proyecto"))

        flash("Correo o contraseña incorrectos.", "error")
        return redirect(url_for("iniciar_sesion"))

    return render_template("iniciarsesion.html")

@app.route("/registro (1).html", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        confirm = request.form.get("confirm_password", "").strip()

        if not nombre or not email or not password or not confirm:
            flash("Por favor, completa todos los campos.", "error")
            return redirect(url_for("registro"))

        if password != confirm:
            flash("Las contraseñas no coinciden.", "error")
            return redirect(url_for("registro"))

        if len(password) < 6:
            flash("La contraseña debe tener al menos 6 caracteres.", "error")
            return redirect(url_for("registro"))

        if Usuario.query.filter_by(email=email).first():
            flash("Ese correo ya está registrado.", "error")
            return redirect(url_for("registro"))

        user = Usuario(nombre=nombre, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Registro exitoso. Ahora inicia sesión.", "success")
        return redirect(url_for("iniciar_sesion"))

    return render_template("registro (1).html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("iniciar_sesion"))

@app.route("/admin/productos/nuevo", methods=["POST"])
def producto_nuevo():
    if not requiere_login():
        return redirect(url_for("iniciar_sesion"))

    nombre = request.form.get("nombre", "").strip()
    categoria = request.form.get("categoria", "").strip() or "General"
    precio = request.form.get("precio", "").strip()
    imagen = request.form.get("imagen", "").strip()
    descripcion = request.form.get("descripcion", "").strip()

    if not nombre or not precio:
        flash("Nombre y precio son obligatorios.", "error")
        return redirect(url_for("pagina_proyecto"))

    try:
        precio = float(precio)
    except ValueError:
        flash("El precio debe ser numérico.", "error")
        return redirect(url_for("pagina_proyecto"))

    db.session.add(Producto(
        nombre=nombre, categoria=categoria, precio=precio,
        imagen=imagen or None, descripcion=descripcion or None
    ))
    db.session.commit()
    flash("Producto creado correctamente.", "success")
    return redirect(url_for("pagina_proyecto"))

@app.route("/admin/productos/<int:producto_id>/editar", methods=["GET", "POST"])
def producto_editar(producto_id):
    if not requiere_login():
        return redirect(url_for("iniciar_sesion"))
    producto = Producto.query.get_or_404(producto_id)

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        categoria = request.form.get("categoria", "").strip() or "General"
        precio = request.form.get("precio", "").strip()
        imagen = request.form.get("imagen", "").strip()
        descripcion = request.form.get("descripcion", "").strip()

        if not nombre or not precio:
            flash("Nombre y precio son obligatorios.", "error")
            return redirect(url_for("producto_editar", producto_id=producto_id))
        try:
            precio = float(precio)
        except ValueError:
            flash("El precio debe ser numérico.", "error")
            return redirect(url_for("producto_editar", producto_id=producto_id))

        producto.nombre = nombre
        producto.categoria = categoria
        producto.precio = precio
        producto.imagen = imagen or None
        producto.descripcion = descripcion or None
        db.session.commit()
        flash("Producto actualizado correctamente.", "success")
        return redirect(url_for("pagina_proyecto"))

    return render_template("editar_producto.html", producto=producto)

@app.route("/admin/productos/<int:producto_id>/eliminar", methods=["POST"])
def producto_eliminar(producto_id):
    if not requiere_login():
        return redirect(url_for("iniciar_sesion"))
    producto = Producto.query.get_or_404(producto_id)
    db.session.delete(producto)
    db.session.commit()
    flash("Producto eliminado.", "info")
    return redirect(url_for("pagina_proyecto"))

def seed_data():
    if Producto.query.count() == 0:
        productos = [{'nombre': 'Base Maybelline Fit Me', 'categoria': 'Rostro', 'precio': 59900.0, 'imagen': 'img/shopping.webp', 'descripcion': 'Cobertura media, acabado natural'}, {'nombre': "Base L'Oréal Infallible", 'categoria': 'Rostro', 'precio': 69900.0, 'imagen': 'img/base 2.png', 'descripcion': 'Cobertura alta, larga duración'}, {'nombre': 'Base Revlon Colorstay', 'categoria': 'Rostro', 'precio': 74900.0, 'imagen': 'img/base 3.png', 'descripcion': 'Matificante, para piel grasa'}, {'nombre': 'Base MAC Studio Fix', 'categoria': 'Rostro', 'precio': 159900.0, 'imagen': 'img/base 4.png', 'descripcion': 'Acabado profesional, SPF15'}, {'nombre': 'Base Fenty Beauty Pro Filt’r', 'categoria': 'Rostro', 'precio': 189900.0, 'imagen': 'img/base 5.png', 'descripcion': 'Variedad de tonos, acabado mate'}, {'nombre': 'Labial MAC Matte', 'categoria': 'Labios', 'precio': 79900.0, 'imagen': 'img/labial.png', 'descripcion': 'Alta pigmentación'}, {'nombre': 'Labial NYX Soft Matte', 'categoria': 'Labios', 'precio': 35900.0, 'imagen': 'img/labial 2.png', 'descripcion': 'Textura ligera, acabado suave'}, {'nombre': 'Labial MAC', 'categoria': 'Labios', 'precio': 75000.0, 'imagen': 'img/labial 4.png', 'descripcion': 'Color intenso y larga duración'}, {'nombre': 'Labial Dior', 'categoria': 'Labios', 'precio': 95000.0, 'imagen': 'img/labial 3.png', 'descripcion': 'Alta pigmentación y acabado elegante'}, {'nombre': 'Labial NYX', 'categoria': 'Labios', 'precio': 30000.0, 'imagen': 'img/labial 4.webp', 'descripcion': 'Tonos vibrantes y textura suave'}, {'nombre': "Delineador L'Oréal", 'categoria': 'Ojos', 'precio': 35000.0, 'imagen': 'img/delineador 1.png', 'descripcion': 'Trazo definido y duradero'}, {'nombre': 'Delineador Maybelline', 'categoria': 'Ojos', 'precio': 32000.0, 'imagen': 'img/delineador 2.jpg', 'descripcion': 'Resistente al agua y de fácil aplicación'}, {'nombre': 'Delineador MAC', 'categoria': 'Ojos', 'precio': 75000.0, 'imagen': 'img/delineador 3.png', 'descripcion': 'Color profundo y de alta duración'}, {'nombre': 'Delineador Dior', 'categoria': 'Ojos', 'precio': 95000.0, 'imagen': 'img/delineador 4.png', 'descripcion': 'Estilo elegante con acabado profesional'}, {'nombre': 'Delineador NYX', 'categoria': 'Ojos', 'precio': 28000.0, 'imagen': 'img/delineador 6.jpg', 'descripcion': 'Aplicador delgado para máxima precisión'}, {'nombre': "Pestañina L'Oréal", 'categoria': 'Ojos', 'precio': 45000.0, 'imagen': 'img/pestañina 1.jpg', 'descripcion': 'Máxima definición y volumen'}, {'nombre': 'Pestañina Maybelline', 'categoria': 'Ojos', 'precio': 40000.0, 'imagen': 'img/pestañina 2.jpg', 'descripcion': 'Alarga y da volumen a tus pestañas'}, {'nombre': 'Pestañina MAC', 'categoria': 'Ojos', 'precio': 85000.0, 'imagen': 'img/pestañina 3.jpg', 'descripcion': 'Acabado dramático y profesional'}, {'nombre': 'Pestañina Dior', 'categoria': 'Ojos', 'precio': 110000.0, 'imagen': 'img/pestañina 4.jpg', 'descripcion': 'Intensidad y elegancia en cada mirada'}, {'nombre': 'Pestañina NYX', 'categoria': 'Ojos', 'precio': 38000.0, 'imagen': 'img/pestañina 5.png', 'descripcion': 'Realza tus pestañas con intensidad'}, {'nombre': "Sombra L'Oréal", 'categoria': 'Ojos', 'precio': 65000.0, 'imagen': 'img/sombra 1.jpg', 'descripcion': 'Colores vibrantes y fáciles de aplicar'}, {'nombre': 'Sombra Maybelline', 'categoria': 'Ojos', 'precio': 58000.0, 'imagen': 'img/sombra 2.jpg', 'descripcion': 'Acabados suaves y naturales'}, {'nombre': 'Sombra MAC', 'categoria': 'Ojos', 'precio': 120000.0, 'imagen': 'img/sombra 3.jpg', 'descripcion': 'Colores profesionales de alta pigmentación'}, {'nombre': 'Sombra Dior', 'categoria': 'Ojos', 'precio': 160000.0, 'imagen': 'img/sombra 4.jpg', 'descripcion': 'Combinaciones sofisticadas para cada look'}, {'nombre': 'Sombra NYX', 'categoria': 'Ojos', 'precio': 50000.0, 'imagen': 'img/sombra 5.jpg', 'descripcion': 'Paleta versátil con tonos intensos'}]
        for p in productos:
            db.session.add(Producto(**p))
        db.session.commit()

with app.app_context():
    db.create_all()
    seed_data()

if __name__ == "__main__":
    app.run(debug=True)
