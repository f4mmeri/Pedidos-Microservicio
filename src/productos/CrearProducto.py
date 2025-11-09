import boto3
import json

TABLE_NAME = 'ChinaWok-Productos'
CATEGORIAS_VALIDAS = [
    "Arroces","Tallarines","Pollo al wok","Carne de res","Cerdo",
    "Mariscos","Entradas","Guarniciones","Sopas","Combos","Bebidas","Postres"
]

def _resp(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        "body": json.dumps(body, ensure_ascii=False)
    }

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

    # Rechazar claves extra
    permitidas = {"local_id","nombre","precio","descripcion","categoria","stock"}
    extras = set(prod.keys()) - permitidas
    if extras:
        return f"Propiedades no permitidas: {', '.join(sorted(extras))}"
    return None

def _check_token(headers):
    token = (headers or {}).get('Authorization')
    if not token:
        return False
    try:
        lambda_client = boto3.client('lambda')
        invoke_resp = lambda_client.invoke(
            FunctionName="ValidarTokenAcceso",
            InvocationType='RequestResponse',
            Payload=json.dumps({"token": token})
        )
        resp = json.loads(invoke_resp['Payload'].read())
        return resp.get('statusCode') != 403
    except Exception:
        return False

def lambda_handler(event, context):
    # Autenticación
    #if not _check_token(event.get('headers')):
    #    return _resp(403, {"message": "Forbidden"})

    # Parsear body correctamente
    try:
        body_raw = event.get('body')
        producto = json.loads(body_raw) if isinstance(body_raw, str) else (body_raw or {})
    except Exception:
        return _resp(400, {"message": "Body inválido; se esperaba JSON objeto"})

    err = _validar_producto(producto)
    if err:
        return _resp(400, {"message": err})

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)

    # Evitar duplicados
    key = {"local_id": producto["local_id"], "nombre": producto["nombre"]}
    if table.get_item(Key=key).get("Item"):
        return _resp(409, {"message": "Ya existe el producto (local_id + nombre)"})

    # Guardar producto
    table.put_item(Item=producto)
    return _resp(201, {"message": "Producto creado", "data": producto})
