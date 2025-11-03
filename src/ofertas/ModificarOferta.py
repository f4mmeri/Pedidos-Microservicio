import boto3
import json
from datetime import datetime

TABLE_NAME = 'ChinaWok-Productos'

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
    if "descuento" in body and (not isinstance(body["descuento"], (int, float)) or body["descuento"] <= 0):
        return {"message": "Descuento inválido", "code": 400}
    
    if "inicio" in body or "fin" in body:
        try:
            if "inicio" in body:
                inicio = datetime.fromisoformat(body["inicio"])
            if "fin" in body:
                fin = datetime.fromisoformat(body["fin"])
        except ValueError:
            return {"message": "Formato de fecha inválido", "code": 400}

        if inicio >= fin:
            return {"message": "La fecha de inicio debe ser anterior a la fecha de fin", "code": 400}

    # Conectar con DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)

    # Obtener el producto existente
    response = table.get_item(Key={'local_id': local_id, 'nombre': nombre})
    if 'Item' not in response:
        return {"message": "Producto no encontrado", "code": 404}

    # Actualizar la oferta
    producto = response['Item']
    oferta = producto.get('oferta', {})

    # Actualizar solo los campos proporcionados
    if "descuento" in body:
        oferta["descuento"] = body["descuento"]
    if "inicio" in body:
        oferta["inicio"] = body["inicio"]
    if "fin" in body:
        oferta["fin"] = body["fin"]
    if "activo" in body:
        oferta["activo"] = body["activo"]

    producto['oferta'] = oferta

    # Guardar el producto con la oferta actualizada
    table.put_item(Item=producto)

    return {"message": "Oferta actualizada", "data": oferta}
