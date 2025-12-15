import pandas as pd
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
import sys
from datetime import datetime
import time

try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut
except ImportError:
    print("❌ Error: Necesitas instalar 'geopy'. Ejecuta: pip install geopy")
    sys.exit(1)

CSV_FILE = 'dataset.csv'  
MONGO_URI = 'mongodb://localhost:27017/'
DB_NAME = 'earthquakesDB'
COLLECTION_NAME = 'events'

geolocator = Nominatim(user_agent="bigdata_practice_student_v1")

def get_real_location(lat, lon):
    """
    Consulta a OpenStreetMap qué país y región corresponden a estas coordenadas.
    """
    try:
        location = geolocator.reverse(f"{lat}, {lon}", language='en', exactly_one=True, timeout=10)
        
        if location:
            address = location.raw.get('address', {})
            country = address.get('country', "Unknown")
            region = address.get('state') or address.get('region') or address.get('county') or "Unknown"
            return country, region
    except Exception as e:
        pass
    
    return "Ocean/Unknown", "Unknown"

def transform_row_to_document(row):
    try:
        year_val = int(row.get('Year'))
        month_val = int(row.get('Month'))
        event_date = datetime(year=year_val, month=month_val, day=1)
        is_tsunami = bool(row.get('tsunami', False))
        
        lat = pd.to_numeric(row.get('latitude'))
        lon = pd.to_numeric(row.get('longitude'))

        real_country, real_region = get_real_location(lat, lon)
        
        print(f"🌍 Procesando: ({lat}, {lon}) -> Detectado: {real_country}, {real_region}")

        return {
            "eq_id": str(row.get('sig', None)), 
            "date": event_date, 
            "location": {
                "country": real_country,
                "region": real_region,
                "latitude": lat,
                "longitude": lon,
            },
            "magnitude": {
                "mw": pd.to_numeric(row.get('magnitude')), 
                "mb": pd.to_numeric(row.get('mb', None)), 
                "ms": pd.to_numeric(row.get('ms', None)), 
            },
            "depth_km": pd.to_numeric(row.get('depth')), 
            "energy_joule": pd.to_numeric(row.get('energy_joule', None)), 
            "intensity_mmi": pd.to_numeric(row.get('mmi')),
            "tsunami_risk": {
                "potential": is_tsunami, 
                "tsunami_height_m": pd.to_numeric(row.get('tsunami_height_m', None)), 
                "distance_to_coast_km": pd.to_numeric(row.get('distance_to_coast_km', None)), 
            },
            "fault_parameters": {
                "strike": pd.to_numeric(row.get('strike', None)), 
                "dip": pd.to_numeric(row.get('dip', None)), 
                "rake": pd.to_numeric(row.get('rake', None)), 
            },
            "seismic_zone": row.get('seismic_zone', None), 
            "casualties_est": pd.to_numeric(row.get('casualties_est', None)), 
            "updated_at": datetime.now()
        }
    except Exception as e:
        print(f"--- ERROR PROCESANDO FILA ---: {e}")
        return None

def main():
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        print(f"Conectado a MongoDB (DB: {DB_NAME})")
        
        collection.delete_many({})
        print("Colección limpiada.")

        df_full = pd.read_csv(CSV_FILE)
        df = df_full.sample(n=100).reset_index(drop=True)
        print(f"Comenzando procesamiento de {len(df)} registros con Geolocalización real...")

        documents = []
        for index, row in df.iterrows():
            doc = transform_row_to_document(row)
            if doc:
                documents.append(doc)
            time.sleep(0.5) 
        
        if documents:
            try:
                result = collection.insert_many(documents, ordered=False)
                print(f"\n✅ ¡Éxito! Insertados {len(result.inserted_ids)} documentos.")
                
                print("\n" + "="*50)
                print(" COMPARATIVA: DATOS CSV vs MONGODB (ENRIQUECIDOS)")
                print("="*50)
                print("Mostrando 10 ejemplos aleatorios de la BD:")
                
                ejemplos = collection.aggregate([{"$sample": {"size": 10}}])
                
                for i, doc in enumerate(ejemplos):
                    loc = doc['location']
                    print(f"\n[Ejemplo {i+1}]")
                    print(f"  - Coordenadas CSV:  Lat: {loc['latitude']}, Lon: {loc['longitude']}")
                    print(f"  - 📍 Ubicación REAL descubierta:  País: '{loc['country']}', Región: '{loc['region']}'")
                    print("-" * 30)

            except BulkWriteError as bwe:
                print(f"Error inserción: {bwe.details}")
        
    except Exception as e:
        print(f"Error crítico: {e}", file=sys.stderr)
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    main()