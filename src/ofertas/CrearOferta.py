import boto3
import json
from datetime import datetime
import uuid
from decimal import Decimal

TABLE_NAME = 'ChinaWok-Ofertas'

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
    except Exception:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Body inválido; se esperaba JSON objeto"})
        }

    required_fields = ["local_id", "producto_nombre", "fecha_inicio", "fecha_limite", "porcentaje_descuento"]
    missing = [f for f in required_fields if f not in body]
    if missing:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": f"Faltan campos: {', '.join(missing)}"})
        }

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

    descuento = body["porcentaje_descuento"]
    if not isinstance(descuento, (int, float)) or descuento <= 0:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Descuento inválido"})
        }

    # ✅ Convertimos el descuento a Decimal antes de guardar
    descuento_decimal = Decimal(str(descuento))

    oferta = {
        "oferta_id": body.get("oferta_id", str(uuid.uuid4())),
        "local_id": body["local_id"],
        "producto_nombre": body["producto_nombre"],
        "fecha_inicio": body["fecha_inicio"],
        "fecha_limite": body["fecha_limite"],
        "porcentaje_descuento": descuento_decimal,
        "activo": True  # opcional: para manejar estado
    }

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)

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
        }, ensure_ascii=False, default=str)  # default=str para manejar Decimal
    }
