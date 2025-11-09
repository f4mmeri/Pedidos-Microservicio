import boto3
import json
from decimal import Decimal

TABLE_NAME = 'ChinaWok-Combos'

# --- Custom encoder para Decimal → float ---
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)  # ✅ usar la constante directamente

    try:
        # --- Obtener todos los items ---
        response = table.scan()
        items = response.get('Items', [])

        # --- Respuesta bonita JSON ---
        return {
            "statusCode": 200,
            "body": json.dumps(
                {"data": items},
                cls=DecimalEncoder,
                ensure_ascii=False,
                indent=2
            ),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps(
                {"message": f"Error al listar items: {str(e)}"},
                ensure_ascii=False,
                indent=2
            ),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        }
