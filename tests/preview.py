"""Vista local de revisión con datos ficticios; nunca utiliza la conexión real."""
from pathlib import Path
from datetime import timedelta
import bcrypt
from flask import send_from_directory
from tests.test_flows import FlujosTest, db, Usuario, PagoEmpleado, Adelanto, TransaccionCaja
from api.auth import auth_bp
from api.cocina import cocina_bp
from api.fechas import ahora

fixture = FlujosTest()
fixture.setUp()
app = fixture.app
app.register_blueprint(auth_bp)
app.register_blueprint(cocina_bp)
with app.app_context():
    for u in Usuario.query.all():
        u.clave = bcrypt.hashpw(b'demo-local-2026', bcrypt.gensalt()).decode()
    fixture.producto(25)
    db.session.add(PagoEmpleado(id_usuario=2,monto=250,estado='Pagado',fecha_pago=ahora(),descripcion='Salario semanal'))
    db.session.add(Adelanto(id_usuario=2,monto=30,estado='Pendiente',fecha=ahora(),motivo='Transporte'))
    for dia in range(8):
        db.session.add(TransaccionCaja(id_usuario=2,tipo='Venta',monto=150+dia*15,fecha=ahora()-timedelta(days=dia),metodo_pago='Yape',descripcion='Ventas de prueba'))
        db.session.add(TransaccionCaja(id_usuario=2,tipo='Gasto',monto=30+dia*3,fecha=ahora()-timedelta(days=dia),metodo_pago='Efectivo',descripcion='Gasto de prueba'))
    db.session.commit()

dist = Path(__file__).resolve().parents[1] / 'frontend' / 'dist'
@app.route('/', defaults={'path':''})
@app.route('/<path:path>')
def frontend(path):
    return send_from_directory(dist, path if path and (dist/path).is_file() else 'index.html')

@app.route('/uploads/perfiles/<path:filename>')
def foto(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5056, debug=False)
