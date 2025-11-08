import json
import boto3
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
# Si usas variable de entorno, cambia por os.environ["OFFERS_TABLE"]
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
    # path params
    params = event.get("pathParameters") or {}
    local_id = params.get("local_id")
    oferta_id = params.get("oferta_id")

    if not local_id or not oferta_id:
        return _resp(400, {"message": "Faltan parámetros local_id/oferta_id"})

    # body
    try:
        body_raw = event.get("body")
        body = json.loads(body_raw or "{}") if isinstance(body_raw, str) else (body_raw or {})
    except Exception:
        return _resp(400, {"message": "Body inválido; se esperaba JSON"})

    # Campos permitidos (todos opcionales en PUT parcial)
    # ejemplo: descuento (float>0), inicio/fin (ISO 8601), activo (bool), nombre_producto, notas
    allowed = {"descuento", "inicio", "fin", "activo", "nombre_producto", "notas"}
    to_update = {k: v for k, v in body.items() if k in allowed}

    if not to_update:
        return _resp(400, {"message": "No hay campos válidos para actualizar"})

    # Validaciones básicas
    if "descuento" in to_update:
        d = to_update["descuento"]
        if not isinstance(d, (int, float)) or d <= 0:
            return _resp(400, {"message": "descuento inválido"})

    # fechas (si vienen). Acepta ...Z convirtiendo a +00:00
    def _parse_iso(s):
        return datetime.fromisoformat(str(s).replace("Z", "+00:00"))

    inicio = fin = None
    if "inicio" in to_update:
        try:
            inicio = _parse_iso(to_update["inicio"])
        except Exception:
            return _resp(400, {"message": "inicio con formato inválido (ISO 8601)"})
    if "fin" in to_update:
        try:
            fin = _parse_iso(to_update["fin"])
        except Exception:
            return _resp(400, {"message": "fin con formato inválido (ISO 8601)"})
    if inicio and fin and inicio >= fin:
        return _resp(400, {"message": "inicio debe ser anterior a fin"})

    # Verifica existencia
    existing = table.get_item(Key={"local_id": local_id, "oferta_id": oferta_id}).get("Item")
    if not existing:
        return _resp(404, {"message": "Oferta no encontrada"})

    # Build UpdateExpression dinámico
    expr_names, expr_vals, sets = {}, {}, []
    for k, v in to_update.items():
        expr_names[f"#{k}"] = k
        expr_vals[f":{k}"] = v
        sets.append(f"#{k} = :{k}")

    update_expr = "SET " + ", ".join(sets)

    try:
        resp = table.update_item(
            Key={"local_id": local_id, "oferta_id": oferta_id},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_vals,
            ReturnValues="ALL_NEW"
        )
        return _resp(200, {"message": "Oferta actualizada", "data": resp.get("Attributes")})
    except Exception as e:
        return _resp(500, {"message": "Error al actualizar", "error": str(e)})
