import boto3
import json

TABLE_NAME = 'ChinaWok-Productos'
CATEGORIAS_VALIDAS = [
    "Arroces","Tallarines","Pollo al wok","Carne de res","Cerdo",
    "Mariscos","Entradas","Guarniciones","Sopas","Combos","Bebidas","Postres"
]

def _validar_producto(prod, es_completo=True):
    """Validar los campos del producto"""
    req = ["local_id", "nombre", "precio", "categoria", "stock"] if es_completo else []
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
    permitidas = set(["local_id", "nombre", "precio", "descripcion", "categoria", "stock"])
    extras = set(prod.keys()) - permitidas
    if extras:
        return f"Propiedades no permitidas: {', '.join(sorted(extras))}"
    return None

def lambda_handler(event, context):
    # Parámetros en la ruta
    params = event.get('pathParameters') or {}
    local_id = params.get('local_id')
    nombre = params.get('nombre')

    if not local_id or not nombre:
        return {"message": "Faltan parámetros local_id/nombre", "code": 400}

    # Body de la petición
    try:
        body = json.loads(event.get('body'))
    except Exception:
        return {"message": "Body inválido; se esperaba JSON objeto", "code": 400}

    # Validación de producto
    err = _validar_producto(body, es_completo=True)
    if err:
        return {"message": err, "code": 400}

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)

    # Verificar existencia del producto
    current = table.get_item(Key={'local_id': local_id, 'nombre': nombre}).get('Item')
    if not current:
        return {"message": "Producto no encontrado", "code": 404}

    # No permitir cambios en las claves de la PK/SK
    if "local_id" in body and body["local_id"] != local_id:
        return {"message": "No puedes cambiar local_id", "code": 400}
    if "nombre" in body and body["nombre"] != nombre:
        return {"message": "No puedes cambiar nombre", "code": 400}

    # Actualizar solo los campos que se recibieron en el body (actualización parcial)
    updated_item = {**current, **body}
    err = _validar_producto(updated_item, es_completo=False)  # Validación para campos actualizados
    if err:
        return {"message": err, "code": 400}

    # Guardar el producto actualizado en DynamoDB
    table.put_item(Item=updated_item)

    return {"message": "Producto actualizado", "data": updated_item}
