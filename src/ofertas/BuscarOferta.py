import json
import boto3

from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = "ChinaWok-Productos"
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
    nombre = params.get("oferta_id")  # <-- si mantienes la ruta actual, 'oferta_id' sería en realidad el nombre del producto (confuso)

    if not local_id or not nombre:
        return _resp(400, {"message": "Faltan parámetros local_id/nombre"})

    resp = table.get_item(Key={"local_id": local_id, "nombre": nombre})
    item = resp.get("Item")
    if not item:
        return _resp(404, {"message": "Producto no encontrado"})

    oferta = item.get("oferta")
    if not oferta:
        return _resp(404, {"message": "Producto sin oferta"})

    return _resp(200, {"message": "Oferta del producto", "data": {"local_id": local_id, "nombre": nombre, "oferta": oferta}})
