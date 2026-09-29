from datetime import date
from unittest.mock import patch

from bd import db
from models import CierreCaja, InventarioMovimiento, SueldoSemanal, TransaccionCaja
from automatizacion_caja.sembrar_historicos import MARCA, borrar_demo, diagnostico, sembrar
from tests.test_flows import BaseFlujos, instante

HOY = date(2026, 9, 28)


class DatosEjemploTest(BaseFlujos):
    def sembrar(self):
        resultado = sembrar(HOY)
        db.session.commit()
        return resultado

    def indicadores(self):
        with patch('api.indicadores.ahora', return_value=instante('2026-09-28T15:00:00')):
            respuesta = self.call('get', '/indicadores?periodo=mes&fecha=2026-09-28&refrescar=1')
        self.assertEqual(respuesta.status_code, 200)
        return {k['codigo']: k for k in respuesta.json['data']['kpis']}

    def test_genera_un_negocio_coherente(self):
        resultado = self.sembrar()
        self.assertGreater(resultado['cierres'], 140)
        self.assertEqual(CierreCaja.query.filter(CierreCaja.fecha_cierre > instante('2026-09-28T05:00:00')).count(), 0)
        kpis = self.indicadores()
        self.assertTrue(50 <= kpis['KPI-01']['valor'] <= 80, kpis['KPI-01']['valor'])
        self.assertIsNotNone(kpis['KPI-02']['valor'])
        self.assertEqual({s['etiqueta'] for s in kpis['KPI-03']['serie'][:2]}, {'Pollo entero (demo)', 'Tomate (demo)'})
        self.assertTrue(0 < kpis['KPI-04']['valor'] < 10, kpis['KPI-04']['valor'])
        self.assertTrue(0 < kpis['KPI-05']['valor'] < 45, kpis['KPI-05']['valor'])
        self.assertTrue(55 <= kpis['KPI-06']['valor'] <= 85, kpis['KPI-06']['valor'])
        self.assertLess(abs(kpis['KPI-07']['valor']), 2)
        self.assertTrue(0 < kpis['KPI-08']['valor'] < 30, kpis['KPI-08']['valor'])

    def test_respeta_los_dias_con_datos_manuales(self):
        db.session.add(TransaccionCaja(id_usuario=2, tipo='Venta', monto=50, metodo_pago='Yape',
                                       fecha=instante('2026-09-10T17:00:00')))
        db.session.commit()
        self.sembrar()
        del_dia = TransaccionCaja.query.filter(TransaccionCaja.fecha >= instante('2026-09-10T05:00:00'),
                                               TransaccionCaja.fecha < instante('2026-09-11T05:00:00')).all()
        self.assertEqual(len(del_dia), 1)
        self.assertEqual(diagnostico()['transacciones_reales'], 1)

    def test_reemplazar_borra_solo_lo_generado(self):
        db.session.add(TransaccionCaja(id_usuario=2, tipo='Venta', monto=50, metodo_pago='Yape',
                                       fecha=instante('2026-09-10T17:00:00')))
        db.session.commit()
        self.sembrar()
        borrar_demo()
        db.session.commit()
        self.assertEqual(TransaccionCaja.query.count(), 1)
        self.assertEqual(CierreCaja.query.count(), 0)
        self.assertEqual(InventarioMovimiento.query.filter(InventarioMovimiento.observacion.like(f'%{MARCA}%')).count(), 0)
        self.assertEqual(SueldoSemanal.query.count(), 0)
