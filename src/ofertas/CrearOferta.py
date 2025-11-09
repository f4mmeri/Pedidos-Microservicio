import boto3
import json
from datetime import datetime
import uuid
from decimal import Decimal

TABLE_NAME = 'ChinaWok-Ofertas'

def lambda_handler(event, context):
    # ✅ Acepta tanto string JSON como objeto ya parseado
    try:
        body_raw = event.get('body', {})
        if isinstance(body_raw, str):
            body = json.loads(body_raw)
        elif isinstance(body_raw, dict):
            body = body_raw
        else:
            raise ValueError("Formato inesperado en body")
    except Exception:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Body inválido; se esperaba JSON objeto"})
        }

    # Campos requeridos
    required_fields = ["local_id", "producto_nombre", "fecha_inicio", "fecha_limite", "porcentaje_descuento"]
    missing = [f for f in required_fields if f not in body]
    if missing:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": f"Faltan campos: {', '.join(missing)}"})
        }

    # Validar fechas
    try:
        inicio = datetime.fromisoformat(body["fecha_inicio"])
        fin = datetime.fromisoformat(body["fecha_limite"])
        if inicio >= fin:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "La fecha de inicio debe ser anterior a la fecha límite"})
            }
    except ValueError:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Formato de fecha inválido"})
        }

    # Validar descuento
    descuento = body["porcentaje_descuento"]
    if not isinstance(descuento, (int, float)) or descuento <= 0:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Descuento inválido"})
        }

    # Guardar en DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)

    oferta = {
        "oferta_id": body.get("oferta_id", str(uuid.uuid4())),
        "local_id": body["local_id"],
        "producto_nombre": body["producto_nombre"],
        "fecha_inicio": body["fecha_inicio"],
        "fecha_limite": body["fecha_limite"],
        "porcentaje_descuento": Decimal(str(descuento)),
        "activo": True
    }

    try:
        table.put_item(Item=oferta)
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Error al guardar en DynamoDB",
                "error": str(e)
            })
        }

    return {
        "statusCode": 201,
        "body": json.dumps({
            "message": "Oferta creada exitosamente",
            "data": oferta
        }, ensure_ascii=False, default=str)
    }
