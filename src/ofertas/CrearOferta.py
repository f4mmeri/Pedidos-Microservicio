import boto3
import json
from datetime import datetime

TABLE_NAME = 'ChinaWok-Ofertas'

def lambda_handler(event, context):
    # Obtener parámetros de la URL
    params = event.get('pathParameters') or {}
    local_id = params.get('local_id')
    nombre = params.get('nombre')

    if not local_id or not nombre:
        return {"message": "Faltan parámetros local_id/nombre", "code": 400}

    # Leer el body del evento (información de la oferta)
    try:
        body = json.loads(event['body'])
    except Exception:
        return {"message": "Body inválido; se esperaba JSON objeto", "code": 400}

    # Validaciones de la oferta
    if "descuento" not in body or not isinstance(body["descuento"], (int, float)) or body["descuento"] <= 0:
        return {"message": "Descuento inválido", "code": 400}
    
    if "inicio" not in body or "fin" not in body:
        return {"message": "Faltan fechas de inicio/fin", "code": 400}

    try:
        inicio = datetime.fromisoformat(body["inicio"])
        fin = datetime.fromisoformat(body["fin"])
    except ValueError:
        return {"message": "Formato de fecha inválido", "code": 400}

    if inicio >= fin:
        return {"message": "La fecha de inicio debe ser anterior a la fecha de fin", "code": 400}

    # Definir el objeto oferta
    oferta = {
        "descuento": body["descuento"],
        "inicio": body["inicio"],
        "fin": body["fin"],
        "activo": body.get("activo", True)  # Por defecto, la oferta está activa
    }

    # Conectar con DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)

    # Obtener el producto existente
    response = table.get_item(Key={'local_id': local_id, 'nombre': nombre})
    if 'Item' not in response:
        return {"message": "Producto no encontrado", "code": 404}

    # Actualizar la oferta en el producto
    producto = response['Item']
    producto['oferta'] = oferta

    # Guardar el producto con la nueva oferta
    table.put_item(Item=producto)

    return {"message": "Oferta creada", "data": oferta}
