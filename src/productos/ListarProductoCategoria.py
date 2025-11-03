import boto3
from boto3.dynamodb.conditions import Attr

TABLE_NAME = 'ChinaWok-Productos'
CATEGORIAS_VALIDAS = [
    "Arroces","Tallarines","Pollo al wok","Carne de res","Cerdo",
    "Mariscos","Entradas","Guarniciones","Sopas","Combos","Bebidas","Postres"
]

def lambda_handler(event, context):
    params = event.get('pathParameters') or {}
    categoria = params.get('categoria')

    if categoria not in CATEGORIAS_VALIDAS:
        return {"message": "Categoria inválida", "code": 400}

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)

    items = []
    resp = table.scan(FilterExpression=Attr('categoria').eq(categoria))
    items.extend(resp.get('Items', []))
    while 'LastEvaluatedKey' in resp:
        resp = table.scan(
            FilterExpression=Attr('categoria').eq(categoria),
            ExclusiveStartKey=resp['LastEvaluatedKey']
        )
        items.extend(resp.get('Items', []))

    return {"items": items}
