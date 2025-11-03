import boto3

TABLE_NAME = 'ChinaWok-Productos'

def lambda_handler(event, context):
    params = (event.get('pathParameters') or {})
    local_id = params.get('local_id')
    nombre = params.get('nombre')

    if not local_id or not nombre:
        return {"message": "Faltan parámetros local_id/nombre", "code": 400}

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)
    resp = table.get_item(Key={'local_id': local_id, 'nombre': nombre})
    item = resp.get('Item')
    if not item:
        return {"message": "Producto no encontrado", "code": 404}

    return item
