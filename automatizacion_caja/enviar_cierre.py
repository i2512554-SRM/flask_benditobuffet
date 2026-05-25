#!/usr/bin/env python3
"""
Orquestador del sistema de cierre de caja.
Uso: python enviar_cierre.py --fecha <YYYY-MM-DD> --cajero <nombre> --total <num> --efectivo <num> --tarjeta <num> --transferencia <num> --destinatario <email>
"""

import argparse
import logging
import os
import sys
from datetime import datetime

from excel_generator import generar_excel
from mail_sender import enviar_correo

CARPETA_CIERRES = "cierres"
CARPETA_LOGS = "logs"

logger = logging.getLogger(__name__)


def configurar_logging():
    os.makedirs(CARPETA_LOGS, exist_ok=True)
    log_path = os.path.join(CARPETA_LOGS, "cierres.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def validar_fecha(fecha_str):
    try:
        datetime.strptime(fecha_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Formato de fecha invalido. Use YYYY-MM-DD (recibido: {fecha_str})")


def validar_numeros(valores):
    for nombre, valor in valores:
        try:
            float(valor)
        except (TypeError, ValueError):
            raise ValueError(
                f"{nombre} debe ser un numero valido (recibido: {valor})"
            )


def main():
    configurar_logging()

    parser = argparse.ArgumentParser(
        description="Genera y envia por correo un cierre de caja en Excel."
    )
    parser.add_argument("--fecha", required=True, help="Fecha del cierre (YYYY-MM-DD)")
    parser.add_argument("--cajero", required=True, help="Nombre del cajero")
    parser.add_argument("--total", required=True, type=float, help="Monto total")
    parser.add_argument("--efectivo", required=True, type=float, help="Monto en efectivo")
    parser.add_argument("--tarjeta", required=True, type=float, help="Monto con tarjeta")
    parser.add_argument("--transferencia", required=True, type=float, help="Monto por transferencia")
    parser.add_argument("--destinatario", required=True, help="Correo destinatario")
    args = parser.parse_args()

    try:
        validar_fecha(args.fecha)
        validar_numeros([
            ("total", args.total),
            ("efectivo", args.efectivo),
            ("tarjeta", args.tarjeta),
            ("transferencia", args.transferencia),
        ])

        suma_medios = args.efectivo + args.tarjeta + args.transferencia
        tolerancia = 0.01
        if abs(suma_medios - args.total) > tolerancia:
            logger.warning(
                "La suma de medios (%.2f) no coincide con el total (%.2f). Diferencia: %.2f",
                suma_medios, args.total, suma_medios - args.total,
            )

        os.makedirs(CARPETA_CIERRES, exist_ok=True)
        nombre_archivo = f"cierre_{args.fecha}_{args.cajero.replace(' ', '_')}.xlsx"
        ruta_excel = os.path.join(CARPETA_CIERRES, nombre_archivo)

        generar_excel(
            fecha=args.fecha,
            cajero=args.cajero,
            total=args.total,
            efectivo=args.efectivo,
            tarjeta=args.tarjeta,
            transferencia=args.transferencia,
            archivo_salida=ruta_excel,
        )

        enviar_correo(
            archivo_excel=ruta_excel,
            destinatario=args.destinatario,
            fecha=args.fecha,
            cajero=args.cajero,
        )

        logger.info("Proceso completado exitosamente")
        print(f"\n OK - Cierre enviado a {args.destinatario}")
        print(f"   Archivo: {ruta_excel}")
        return 0

    except (ValueError, FileNotFoundError, Exception) as e:
        logger.exception("Error durante la ejecucion")
        print(f"\n ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
