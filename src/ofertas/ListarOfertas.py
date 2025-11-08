import boto3
import json
from datetime import datetime, timezone
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal

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
        "body": json.dumps(_to_jsonable(body), ensure_ascii=False)
    }

def _to_jsonable(o):
    if isinstance(o, list):
        return [_to_jsonable(x) for x in o]
    if isinstance(o, dict):
        return {k: _to_jsonable(v) for k, v in o.items()}
    if isinstance(o, Decimal):
        return float(o)
    return o

def _parse_bool(s, default=False):
    if s is None:
        return default
    return str(s).lower() in ("1", "true", "t", "yes", "y")

def _now_iso():
    return datetime.now(timezone.utc).isoformat()

def lambda_handler(event, context):
    qs = event.get("queryStringParameters") or {}
    local_id = qs.get("local_id")
    solo_activas = _parse_bool(qs.get("solo_activas"), False)
    vigentes_ahora = _parse_bool(qs.get("vigentes_ahora"), False)

    items = []
    if local_id:
        # Query por local_id + filtro de existencia de oferta
        fe = Attr('oferta').exists()
        if solo_activas:
            fe = fe & Attr('oferta.activo').eq(True)
        # Nota: 'vigentes_ahora' se evalúa en app por fecha
        resp = table.query(
            KeyConditionExpression=Key('local_id').eq(local_id),
            FilterExpression=fe
        )
        items = resp.get("Items", [])
        # Paginación simple
        while 'LastEvaluatedKey' in resp:
            resp = table.query(
                KeyConditionExpression=Key('local_id').eq(local_id),
                FilterExpression=fe,
                ExclusiveStartKey=resp['LastEvaluatedKey']
            )
            items.extend(resp.get("Items", []))
    else:
        # Scan de toda la tabla filtrando por existencia de 'oferta'
        fe = Attr('oferta').exists()
        if solo_activas:
            fe = fe & Attr('oferta.activo').eq(True)
        resp = table.scan(FilterExpression=fe)
        items = resp.get("Items", [])
        while 'LastEvaluatedKey' in resp:
            resp = table.scan(
                FilterExpression=fe,
                ExclusiveStartKey=resp['LastEvaluatedKey']
            )
            items.extend(resp.get("Items", []))

    # Filtro de vigencia temporal en app (inicio <= now < fin)
    if vigentes_ahora:
        now = datetime.fromisoformat(_now_iso())
        def _is_vigente(ofe):
            try:
                ini = datetime.fromisoformat(ofe['inicio'].replace('Z', '+00:00'))
                fin = datetime.fromisoformat(ofe['fin'].replace('Z', '+00:00'))
                return ini <= now < fin
            except Exception:
                return False
        items = [it for it in items if 'oferta' in it and _is_vigente(it['oferta'])]

    # Devuelve solo lo útil: local_id, nombre, oferta
    ofertas = [
        {
            "local_id": it.get("local_id"),
            "nombre": it.get("nombre"),
            "oferta": it.get("oferta")
        }
        for it in items
        if it.get("oferta") is not None
    ]

    return _resp(200, {"count": len(ofertas), "ofertas": ofertas})
