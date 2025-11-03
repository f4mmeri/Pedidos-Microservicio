import boto3
import botocore

TABLE_NAME = 'ChinaWok-Productos'

def lambda_handler(event, context):
    params = event.get('pathParameters') or {}
    local_id = params.get('local_id')
    nombre = params.get('nombre')

    if not local_id or not nombre:
        return {"message": "Faltan parámetros local_id/nombre", "code": 400}

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)

    try:
        table.delete_item(
            Key={'local_id': local_id, 'nombre': nombre},
            ConditionExpression="attribute_exists(local_id) AND attribute_exists(nombre)"
        )
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return {"message": "Producto no encontrado", "code": 404}
        raise

    return {"message": "Producto eliminado"}
