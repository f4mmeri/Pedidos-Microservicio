import boto3
import json
from decimal import Decimal

# --- Custom encoder para Decimal → float ---
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def lambda_handler(event, context):
    # --- Configura la tabla desde el evento o hardcode ---
    table_name = event.get('table_name', 'NombreDeTuTabla')  # o hardcode 'ChinaWok-Productos'
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

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
