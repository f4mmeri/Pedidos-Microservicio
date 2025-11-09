import boto3
import json
import uuid
from decimal import Decimal

TABLE_NAME = 'ChinaWok-Productos'
CATEGORIAS_VALIDAS = [
    "Arroces", "Tallarines", "Pollo al wok", "Carne de res", "Cerdo",
    "Mariscos", "Entradas", "Guarniciones", "Sopas", "Combos", "Bebidas", "Postres"
]

def _resp(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(body, ensure_ascii=False)
    }

def _validar_producto(prod):
    req = ["nombre", "precio", "categoria", "stock"]
    for k in req:
        if k not in prod:
            return f"Falta {k}"
    if not isinstance(prod["nombre"], str) or not prod["nombre"]:
        return "nombre inválido"
    if not isinstance(prod["precio"], (int, float, Decimal)) or prod["precio"] < 0:
        return "precio inválido (>= 0)"
    if not isinstance(prod["stock"], int) or prod["stock"] < 0:
        return "stock inválido (entero >= 0)"
    if prod["categoria"] not in CATEGORIAS_VALIDAS:
        return "categoria inválida"

    permitidas = {"nombre", "precio", "descripcion", "categoria", "stock"}
    extras = set(prod.keys()) - permitidas
    if extras:
        return f"Propiedades no permitidas: {', '.join(sorted(extras))}"
    return None

def lambda_handler(event, context):
    try:
        body_raw = event.get('body')
        producto = json.loads(body_raw, parse_float=Decimal) if isinstance(body_raw, str) else (body_raw or {})
    except Exception:
        return _resp(400, {"message": "Body inválido; se esperaba JSON objeto"})

    err = _validar_producto(producto)
    if err:
        return _resp(400, {"message": err})

    producto_id = str(uuid.uuid4())
    producto["producto_id"] = producto_id

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)

    existing = table.scan(
        FilterExpression="nombre = :nom",
        ExpressionAttributeValues={":nom": producto["nombre"]}
    )
    if existing["Items"]:
        return _resp(409, {"message": "Ya existe un producto con ese nombre"})

    table.put_item(Item=producto)

    return _resp(201, {"message": "Producto creado", "data": producto})
