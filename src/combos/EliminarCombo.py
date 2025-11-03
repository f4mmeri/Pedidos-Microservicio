import boto3

TABLE_NAME = 'ChinaWok-Combos'

def lambda_handler(event, context):
    params = event.get('pathParameters') or {}
    combo_id = params.get('combo_id')

    if not combo_id:
        return {"message": "Falta parámetro combo_id", "code": 400}

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)

    # Verificar si el combo existe
    response = table.get_item(Key={'combo_id': combo_id})
    if 'Item' not in response:
        return {"message": "Combo no encontrado", "code": 404}

    # Eliminar Combo
    table.delete_item(Key={'combo_id': combo_id})

    return {"message": "Combo eliminado"}
