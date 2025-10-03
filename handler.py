# handler.py
import json
import random
import os
import boto3
import uuid
from datetime import datetime

# Inicializamos el cliente de DynamoDB fuera de la función
dynamodb = boto3.resource('dynamodb')
# Obtenemos el nombre de la tabla de las variables de entorno definidas en serverless.yml
table_name = os.environ.get('LEADS_TABLE_NAME')
if not table_name:
    # Fallback si por alguna razón la variable de entorno no se carga
    table_name = 'leadsTable' 
table = dynamodb.Table(table_name)

def main(event, context):
    try:
        # Configuración de CORS para todas las respuestas
        headers = {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*", # Permite acceso desde cualquier origen (para desarrollo)
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
            "Access-Control-Allow-Methods": "OPTIONS,POST" # Métodos permitidos
        }

        # Manejo de la solicitud OPTIONS (preflight request de CORS)
        if event.get('httpMethod') == 'OPTIONS':
            return {
                "statusCode": 204,
                "headers": headers
            }

        # 1. Parsear los datos de entrada
        # API Gateway envía el cuerpo de la petición como string JSON
        body_data = json.loads(event.get('body', '{}'))

        # Los 10 campos que esperamos del frontend
        email_contacto = body_data.get('emailContacto', 'N/A')
        numero_viajeros = body_data.get('numeroViajeros', 0)
        destino_interes = body_data.get('destinoInteres', 'N/A')
        fechas_tentativas = body_data.get('fechasTentativas', 'N/A')
        duracion_max_dias = body_data.get('duracionMaxDias', 0)
        presupuesto_max_usd = body_data.get('presupuestoMaxUsd', 0)
        tipo_alojamiento = body_data.get('tipoAlojamiento', 'N/A')
        intereses_especiales = body_data.get('interesesEspeciales', [])
        ha_viajado_antes = body_data.get('haViajadoAntes', 'No')
        frecuencia_viaje_anual = body_data.get('frecuenciaViajeAnual', 0)

        # 2. Generar una probabilidad de compra aleatoria (1-100)
        probabilidad_compra = random.randint(1, 100)

        # 3. Generar un ID único para el lead
        lead_id = str(uuid.uuid4())

        # 4. Preparar el item para guardar en DynamoDB
        lead_item = {
            'leadId': lead_id,
            'emailContacto': email_contacto,
            'numeroViajeros': numero_viajeros,
            'destinoInteres': destino_interes,
            'fechasTentativas': fechas_tentativas,
            'duracionMaxDias': duracion_max_dias,
            'presupuestoMaxUsd': presupuesto_max_usd,
            'tipoAlojamiento': tipo_alojamiento,
            'interesesEspeciales': intereses_especiales,
            'haViajadoAntes': ha_viajado_antes,
            'frecuenciaViajeAnual': frecuencia_viaje_anual,
            'probabilidadCompra': probabilidad_compra,
            'fechaCreacion': datetime.now().isoformat() # Timestamp de creación
        }

        # 5. Guardar el lead en DynamoDB
        table.put_item(Item=lead_item)

        # 6. Preparar la respuesta para el frontend
        response_body = {
            "message": "Lead procesado y guardado exitosamente.",
            "leadId": lead_id,
            "probabilidadCompra": probabilidad_compra,
            "clasificacion": ""
        }

        if probabilidad_compra > 75:
            response_body["clasificacion"] = "Altamente Probable"
        elif 50 <= probabilidad_compra <= 75:
            response_body["clasificacion"] = "Medianamente Probable"
        else:
            response_body["clasificacion"] = "Poco Probable"

        return {
            "statusCode": 200,
            "headers": headers, # Usamos las cabeceras definidas arriba
            "body": json.dumps(response_body)
        }

    except Exception as e:
        print(f"Error procesando el lead: {e}")
        return {
            "statusCode": 500,
            "headers": headers, # Usamos las cabeceras definidas arriba
            "body": json.dumps({"message": f"Error interno del servidor: {str(e)}"})
        }