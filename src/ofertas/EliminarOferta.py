# src/ofertas/EliminarOferta.py
import json
import boto3

TABLE_NAME = 'ChinaWok-Productos'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

def _resp(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(body, ensure_ascii=False)
    }

def lambda_handler(event, context):
    params = event.get("pathParameters") or {}
    local_id = params.get("local_id")
    nombre = params.get("nombre")

    if not local_id or not nombre:
        return _resp(400, {"message": "Faltan parámetros local_id/nombre"})

    # Verifica existencia
    resp = table.get_item(Key={"local_id": local_id, "nombre": nombre})
    item = resp.get("Item")
    if not item:
        return _resp(404, {"message": "Producto no encontrado"})

    if "oferta" not in item:
        return _resp(404, {"message": "No existe una oferta en este producto"})

    # Elimina el atributo 'oferta'
    table.update_item(
        Key={"local_id": local_id, "nombre": nombre},
        UpdateExpression="REMOVE oferta",
        ReturnValues="ALL_NEW"
    )

    return _resp(200, {"message": "Oferta eliminada", "local_id": local_id, "nombre": nombre})
