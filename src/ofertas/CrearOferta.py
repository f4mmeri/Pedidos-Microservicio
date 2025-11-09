import boto3
import json
from datetime import datetime, timezone
import uuid

TABLE_NAME = "ChinaWok-Ofertas"

def lambda_handler(event, context):
    # Leer body del request
    try:
        body_raw = event.get("body")
        body = json.loads(body_raw or "{}") if isinstance(body_raw, str) else (body_raw or {})
    except Exception:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Body inválido; se esperaba JSON objeto"})
        }

    # Validar campos requeridos
    required_fields = ["local_id", "producto_nombre", "fecha_inicio", "fecha_limite", "porcentaje_descuento"]
    missing = [f for f in required_fields if f not in body]
    if missing:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": f"Faltan campos: {', '.join(missing)}"})
        }

    # Validar fechas
    try:
        inicio = datetime.fromisoformat(body["fecha_inicio"].replace("Z", "+00:00"))
        fin = datetime.fromisoformat(body["fecha_limite"].replace("Z", "+00:00"))
        if inicio >= fin:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "La fecha de inicio debe ser anterior a la fecha límite"})
            }
    except ValueError:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Formato de fecha inválido (usa ISO 8601)"})
        }

    # Validar descuento
    descuento = body["porcentaje_descuento"]
    if not isinstance(descuento, (int, float)) or descuento <= 0:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Descuento inválido"})
        }

    # Crear objeto de oferta
    oferta = {
        "oferta_id": body.get("oferta_id", str(uuid.uuid4())),
        "local_id": body["local_id"],
        "producto_nombre": body["producto_nombre"],
        "fecha_inicio": body["fecha_inicio"],
        "fecha_limite": body["fecha_limite"],
        "porcentaje_descuento": float(descuento),
        "activo": True,
        "creado_en": datetime.now(timezone.utc).isoformat()
    }

    # Guardar en DynamoDB
    try:
        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table(TABLE_NAME)
        table.put_item(Item=oferta)
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Error al guardar en DynamoDB", "error": str(e)})
        }

    return {
        "statusCode": 201,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "message": "Oferta creada exitosamente",
            "data": oferta
        })
    }
