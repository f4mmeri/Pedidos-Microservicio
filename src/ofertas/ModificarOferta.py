import json
import boto3
from datetime import datetime, timezone

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

    # Obtener la oferta
    resp = table.get_item(Key={"local_id": local_id, "oferta_id": oferta_id})
    item = resp.get("Item")
    if not item:
        return _resp(404, {"message": "Oferta no encontrada"})

    # Verificar expiración automática
    now = datetime.now(timezone.utc)
    try:
        fin = datetime.fromisoformat(item["fin"].replace("Z", "+00:00"))
    except Exception:
        fin = None

    if fin and now > fin and item.get("activo", True):
        # Desactivar automáticamente
        table.update_item(
            Key={"local_id": local_id, "oferta_id": oferta_id},
            UpdateExpression="SET activo = :a",
            ExpressionAttributeValues={":a": False}
        )
        item["activo"] = False

    return _resp(200, {"message": "Oferta consultada", "data": item})
