import boto3
import json

TABLE_NAME = 'ChinaWok-Combos'

def lambda_handler(event, context):
    params = event.get('pathParameters') or {}
    local_id = params.get('local_id')
    combo_id = params.get('combo_id')

    if not combo_id or not local_id:
        return {"message": "Faltan parámetros combo_id/local_id", "code": 400}

    try:
        combo = json.loads(event['body'])
    except Exception:
        return {"message": "Body inválido; se esperaba JSON objeto", "code": 400}

    # Validación de campos
    if "combo_id" not in combo or "nombre" not in combo or "productos" not in combo:
        return {"message": "Faltan campos obligatorios: combo_id, nombre, productos", "code": 400}

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)

    # Verificar si el combo existe
    response = table.get_item(Key={'combo_id': combo_id, 'local_id': local_id})
    if 'Item' not in response:
        return {"message": "Combo no encontrado", "code": 404}

    # Actualizar Combo
    table.put_item(Item=combo)

    return {"message": "Combo actualizado", "data": combo}
