import boto3
import json
from boto3.dynamodb.conditions import Key, Attr

TABLE_NAME = 'ChinaWok-Combos'

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)

    try:
        # Escanear todos los elementos de la tabla
        response = table.scan()
        combos = response.get('Items', [])

        # Manejar paginación (si hay más de 1 MB de datos)
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            combos.extend(response.get('Items', []))

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Listado de combos obtenido correctamente",
                "data": combos
            }),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": f"Error al listar combos: {str(e)}"
            }),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        }
