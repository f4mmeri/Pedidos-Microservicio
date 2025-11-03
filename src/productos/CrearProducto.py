import boto3
import json

TABLE_NAME = 'ChinaWok-Productos'
CATEGORIAS_VALIDAS = [
    "Arroces","Tallarines","Pollo al wok","Carne de res","Cerdo",
    "Mariscos","Entradas","Guarniciones","Sopas","Combos","Bebidas","Postres"
]

def _validar_producto(prod):
    req = ["local_id", "nombre", "precio", "categoria", "stock"]
    for k in req:
        if k not in prod:
            return f"Falta {k}"
    if not isinstance(prod["local_id"], str) or not prod["local_id"]:
        return "local_id inválido"
    if not isinstance(prod["nombre"], str) or not prod["nombre"]:
        return "nombre inválido"
    if not isinstance(prod["precio"], (int, float)) or prod["precio"] < 0:
        return "precio inválido (>= 0)"
    if not isinstance(prod["stock"], int) or prod["stock"] < 0:
        return "stock inválido (entero >= 0)"
    if prod["categoria"] not in CATEGORIAS_VALIDAS:
        return "categoria inválida"
    # additionalProperties: false (rechazar claves extra)
    permitidas = set(["local_id","nombre","precio","descripcion","categoria","stock"])
    extras = set(prod.keys()) - permitidas
    if extras:
        return f"Propiedades no permitidas: {', '.join(sorted(extras))}"
    return None

def _check_token(headers):
    token = (headers or {}).get('Authorization')
    if not token:
        return False
    lambda_client = boto3.client('lambda')
    invoke_resp = lambda_client.invoke(
        FunctionName="ValidarTokenAcceso",
        InvocationType='RequestResponse',
        Payload=json.dumps({"token": token})
    )
    resp = json.loads(invoke_resp['Payload'].read())
    return resp.get('statusCode') != 403

def lambda_handler(event, context):
    # Protección (opcional, igual a tu ejemplo)
    if not _check_token(event.get('headers')):
        return {"message": "Forbidden", "code": 403}

    producto = event.get('body')          # Viene como OBJETO (no string)
    if not isinstance(producto, dict):
        return {"message": "Body inválido; se esperaba JSON objeto", "code": 400}

    err = _validar_producto(producto)
    if err:
        return {"message": err, "code": 400}

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)

    # Evitar duplicados PK/SK
    key = {"local_id": producto["local_id"], "nombre": producto["nombre"]}
    if table.get_item(Key=key).get("Item"):
        return {"message": "Ya existe el producto (local_id + nombre)", "code": 409}

    table.put_item(Item=producto)
    return {"message": "Producto creado", "data": producto}
