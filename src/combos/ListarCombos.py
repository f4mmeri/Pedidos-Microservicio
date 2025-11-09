import boto3
import json
from decimal import Decimal

TABLE_NAME = 'ChinaWok-Combos'

# --- Función para convertir Decimal a int o float según corresponda ---
def fix_types(item):
    for p in item.get("productos", []):
        if isinstance(p.get("cantidad"), Decimal):
            # si es entero, convertir a int; si tiene decimales, float
            if p["cantidad"] % 1 == 0:
                p["cantidad"] = int(p["cantidad"])
            else:
                p["cantidad"] = float(p["cantidad"])
    return item

# --- Custom encoder para otros Decimals (por seguridad) ---
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)

    try:
        # --- Obtener todos los combos ---
        response = table.scan()
        items = response.get('Items', [])

        # --- Arreglar tipos de cantidad ---
        items = [fix_types(c) for c in items]

        # --- Retornar JSON compacto y limpio ---
        return {
            "statusCode": 200,
            "body": json.dumps({"data": items}, cls=DecimalEncoder, ensure_ascii=False),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": f"Error al listar combos: {str(e)}"}, ensure_ascii=False),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        }
