import boto3

TABLE_NAME = 'ChinaWok-Combos'

def lambda_handler(event, context):
    params = event.get('pathParameters') or {}
    combo_id = params.get('combo_id')
    local_id = params.get('local_id')

    if not combo_id or not local_id:
        return {"message": "Faltan parámetros combo_id/local_id", "code": 400}

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)

    response = table.get_item(Key={'combo_id': combo_id, 'local_id': local_id})
    if 'Item' not in response:
        return {"message": "Combo no encontrado", "code": 404}

    return response['Item']
