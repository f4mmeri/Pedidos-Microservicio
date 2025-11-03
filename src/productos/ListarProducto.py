import boto3
from boto3.dynamodb.conditions import Key, Attr

TABLE_NAME = 'ChinaWok-Productos'

def lambda_handler(event, context):
    qs = event.get('queryStringParameters') or {}
    local_id = qs.get('local_id')
    categoria = qs.get('categoria')

    if not local_id:
        return {"message": "Falta query param local_id", "code": 400}

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)

    kwargs = {"KeyConditionExpression": Key('local_id').eq(local_id)}
    if categoria:
        kwargs["FilterExpression"] = Attr('categoria').eq(categoria)

    items, resp = [], table.query(**kwargs)
    items.extend(resp.get('Items', []))
    while 'LastEvaluatedKey' in resp:
        resp = table.query(ExclusiveStartKey=resp['LastEvaluatedKey'], **kwargs)
        items.extend(resp.get('Items', []))

    return {"items": items}
