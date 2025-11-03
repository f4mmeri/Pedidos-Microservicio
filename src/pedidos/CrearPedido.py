import boto3
import json
from datetime import datetime

TABLE_NAME = 'ChinaWok-Pedidos'

def lambda_handler(event, context):
    try:
        pedido = json.loads(event['body'])
    except Exception:
        return {"message": "Body inválido; se esperaba JSON objeto", "code": 400}

    # Validación de campos
    if "pedido_id" not in pedido or "cliente_id" not in pedido or "productos" not in pedido:
        return {"message": "Faltan campos obligatorios", "code": 400}

    if "total" not in pedido or pedido["total"] <= 0:
        return {"message": "Total inválido", "code": 400}

    if "estado" not in pedido or pedido["estado"] not in ["pendiente", "enviado", "entregado"]:
        return {"message": "Estado inválido", "code": 400}

    if "fecha_pedido" not in pedido:
        return {"message": "Fecha de pedido es obligatoria", "code": 400}

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)

    # Verificar si el pedido ya existe
    response = table.get_item(Key={'pedido_id': pedido['pedido_id']})
    if 'Item' in response:
        return {"message": "Pedido ya existe", "code": 409}

    # Agregar fecha actual si no está presente
    if 'fecha_pedido' not in pedido:
        pedido['fecha_pedido'] = datetime.utcnow().isoformat()

    # Insertar pedido en DynamoDB
    table.put_item(Item=pedido)

    return {"message": "Pedido creado", "data": pedido}
