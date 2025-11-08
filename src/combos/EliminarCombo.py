import boto3

TABLE_NAME = 'ChinaWok-Combos'

def lambda_handler(event, context):
    params = event.get('pathParameters') or {}
    local_id = params.get('local_id')
    combo_id = params.get('combo_id')

    if not local_id or not combo_id:
        return {"message": "Faltan parámetros local_id/combo_id", "code": 400}

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)

    # Verificar si el combo existe
    response = table.get_item(Key={'combo_id': combo_id, 'local_id': local_id})
    if 'Item' not in response:
        return {"message": "Combo no encontrado", "code": 404}

    # Eliminar Combo
    table.delete_item(Key={'combo_id': combo_id, 'local_id': local_id})

    return {"message": "Combo eliminado"}
