import boto3
import json
from decimal import Decimal

TABLE_NAME = 'ChinaWok-Combos'

# --- Custom encoder para Decimal → float ---
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            # Convertimos a float con 2 decimales para que se vea más limpio
            return float(round(obj, 2))
        return super().default(obj)

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)

    try:
        # --- Obtener todos los combos ---
        response = table.scan()
        items = response.get('Items', [])

        # --- Formatear la data para que solo contenga campos importantes ---
        formatted = []
        for combo in items:
            formatted.append({
                "local_id": combo.get("local_id"),
                "combo_id": combo.get("combo_id"),
                "nombre": combo.get("nombre"),
                "productos_nombres": [p.get("nombre") for p in combo.get("productos", [])],
                "precio": combo.get("precio"),
                "disponible": combo.get("disponible", True)
            })

        # --- Retornar JSON “bonito” ---
        return {
            "statusCode": 200,
            "body": json.dumps(formatted, ensure_ascii=False, cls=DecimalEncoder),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps(
                {"message": f"Error al listar combos: {str(e)}"},
                ensure_ascii=False
            ),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        }
