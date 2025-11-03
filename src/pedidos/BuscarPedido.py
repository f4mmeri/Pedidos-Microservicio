import boto3

TABLE_NAME = 'ChinaWok-Pedidos'

def lambda_handler(event, context):
    params = event.get('pathParameters') or {}
    pedido_id = params.get('pedido_id')

    if not pedido_id:
        return {"message": "Falta parámetro pedido_id", "code": 400}

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)

    response = table.get_item(Key={'pedido_id': pedido_id})
    if 'Item' not in response:
        return {"message": "Pedido no encontrado", "code": 404}

    return response['Item']
