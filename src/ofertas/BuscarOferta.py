import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = "ChinaWok-Ofertas"
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
    oferta_id = params.get("oferta_id")

    if not local_id or not oferta_id:
        return _resp(400, {"message": "Faltan parámetros local_id/oferta_id"})

    try:
        resp = table.get_item(Key={"local_id": local_id, "oferta_id": oferta_id})
    except Exception as e:
        return _resp(500, {"message": f"Error al acceder a DynamoDB: {str(e)}"})

    oferta = resp.get("Item")
    if not oferta:
        return _resp(404, {"message": "Oferta no encontrada"})

    return _resp(200, {"message": "Oferta encontrada", "data": oferta})
