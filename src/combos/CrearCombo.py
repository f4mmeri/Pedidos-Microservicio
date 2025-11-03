import boto3
import json

TABLE_NAME = 'ChinaWok-Combos'

def lambda_handler(event, context):
    # Leer body de la solicitud
    try:
        combo = json.loads(event['body'])
    except Exception:
        return {"message": "Body inválido; se esperaba JSON objeto", "code": 400}

    # Validar Combo
    if "combo_id" not in combo or "nombre" not in combo or "productos" not in combo:
        return {"message": "Faltan campos obligatorios: combo_id, nombre, productos", "code": 400}

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)

    # Verificar si el combo ya existe
    response = table.get_item(Key={'combo_id': combo['combo_id']})
    if 'Item' in response:
        return {"message": "Combo ya existe", "code": 409}

    # Insertar Combo
    table.put_item(Item=combo)

    return {"message": "Combo creado", "data": combo}
