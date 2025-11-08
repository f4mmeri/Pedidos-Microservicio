import boto3
import json
from decimal import Decimal

TABLE_NAME = 'ChinaWok-Combos'

# Custom encoder for Decimal → float
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)  # or str(obj) if you want to preserve exact format
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)

    try:
        # Scan all combos
        response = table.scan()
        combos = response.get('Items', [])

        # Return JSON safely (convert Decimals)
        return {
            "statusCode": 200,
            "body": json.dumps({"data": combos}, cls=DecimalEncoder),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"  # Enables frontend calls (CORS)
            }
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": f"Error al listar combos: {str(e)}"}),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        }
