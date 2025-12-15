from pymongo import MongoClient
import time
from datetime import datetime
import pprint

MONGO_URI = 'mongodb://localhost:27017/'
DB_NAME = 'earthquakesDB'
COLLECTION_NAME = 'events'

def main():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    
    print("="*60)
    print("GENERADOR DE EVIDENCIAS PARA LA PRÁCTICA")
    print("="*60)

    print("\n[ TAREA 1/2 ] Muestra del Esquema JSON (Un documento completo)")
    print("-" * 60)
    sample_doc = collection.find_one({"location.country": {"$ne": "Ocean/Unknown"}})
    pprint.pprint(sample_doc)

    print("\n\n[ TAREA 4 ] Modificación de datos (Update)")
    print("-" * 60)
    
    target = collection.find_one({"location.country": "Japan"})
    
    if target:
        print(f"1. Antes del cambio (ID: {target['eq_id']}):")
        print(f"   Región: {target['location']['region']}")

        new_region = target['location']['region'].upper()
        
        collection.update_one(
            {"_id": target['_id']},
            {"$set": {"location.region": new_region}}
        )
        
        updated_doc = collection.find_one({"_id": target['_id']})
        print(f"2. Después del cambio:")
        print(f"   Región: {updated_doc['location']['region']}")
    else:
        print("No se encontró un documento de prueba para modificar.")

    print("\n\n[ TAREA 5 ] Consultas y Tiempos de Ejecución")
    print("-" * 60)

    def measure_query(title, query_filter):
        start = time.time()
        results = list(collection.find(query_filter))
        end = time.time()
        duration_ms = (end - start) * 1000
        
        print(f"\n>>> Consulta: {title}")
        print(f"    Filtro: {query_filter}")
        print(f"    Resultados encontrados: {len(results)}")
        print(f"    Tiempo: {duration_ms:.4f} ms")
        if results:
            loc = results[0].get('location', {})
            mag = results[0].get('magnitude', {})
            print(f"    Ejemplo encontrado: País={loc.get('country')}, Mag={mag.get('mw')}")

    date_threshold = datetime(2016, 1, 1)
    measure_query("Año > 2015", {"date": {"$gt": date_threshold}})

    measure_query("País empieza por 'Japa...'", {"location.country": {"$regex": "^Japa"}})

    measure_query("Indonesia con Magnitud > 7.0", {
        "location.country": "Indonesia",
        "magnitude.mw": {"$gt": 7.0}
    })

    measure_query("Indonesia con Riesgo de Tsunami", {
        "location.country": "Indonesia",
        "tsunami_risk.potential": True
    })

    client.close()

if __name__ == "__main__":
    main()