import boto3
import json
from datetime import datetime

TABLE_NAME = 'ChinaWok-Productos'

def lambda_handler(event, context):
    # Conectar con DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)

    # Realizar un scan para obtener productos con ofertas activas
    response = table.scan(
        FilterExpression="attribute_exists(oferta) AND oferta.activo = :activo AND oferta.fin >= :hoy",
        ExpressionAttributeValues={
            ":activo": True,
            ":hoy": datetime.utcnow().isoformat()
        }
    )

    items = response.get('Items', [])
    active_offers = [item['oferta'] for item in items if item.get('oferta')]

    return {"message": "Ofertas activas", "data": active_offers}
