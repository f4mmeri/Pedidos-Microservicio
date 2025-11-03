import boto3
import json

TABLE_NAME = 'ChinaWok-Pedidos'

def lambda_handler(event, context):
    params = event.get('pathParameters') or {}
    pedido_id = params.get('pedido_id')

    if not pedido_id:
        return {"message": "Falta parámetro pedido_id", "code": 400}

    try:
        pedido = json.loads(event['body'])
    except Exception:
        return {"message": "Body inválido; se esperaba JSON objeto", "code": 400}

    # Validaciones
    if "estado" in pedido and pedido["estado"] not in ["pendiente", "enviado", "entregado"]:
        return {"message": "Estado inválido", "code": 400}

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)

    # Verificar si el pedido existe
    response = table.get_item(Key={'pedido_id': pedido_id})
    if 'Item' not in response:
        return {"message": "Pedido no encontrado", "code": 404}

    # Actualizar pedido
    table.put_item(Item=pedido)

    return {"message": "Pedido actualizado", "data": pedido}
