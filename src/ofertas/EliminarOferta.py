import boto3
import json

TABLE_NAME = 'ChinaWok-Productos'

def lambda_handler(event, context):
    # Obtener parámetros de la URL
    params = event.get('pathParameters') or {}
    local_id = params.get('local_id')
    nombre = params.get('nombre')

    if not local_id or not nombre:
        return {"message": "Faltan parámetros local_id/nombre", "code": 400}

    # Conectar con DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)

    # Obtener el producto
    response = table.get_item(Key={'local_id': local_id, 'nombre': nombre})
    if 'Item' not in response:
        return {"message": "Producto no encontrado", "code": 404}

    producto = response['Item']
    if 'oferta' not in producto:
        return {"message": "No existe una oferta en este producto", "code": 404}

    # Eliminar la oferta
    producto['oferta'] = None
    table.put_item(Item=producto)

    return {"message": "Oferta eliminada", "data": producto}
