# Práctica Big Data NoSQL: Análisis de Terremotos con MongoDB

Este proyecto implementa una solución de almacenamiento y análisis de datos sísmicos utilizando MongoDB. Incluye scripts para la ingesta, limpieza, enriquecimiento geográfico (Reverse Geocoding) y consulta de datos.

## 📋 Requisitos Previos

- **Python 3.10** o superior.
- **MongoDB Community Server** instalado y ejecutándose en `localhost:27017` (puerto por defecto).
- Archivo `dataset.csv` ubicado en la raíz del proyecto.

## 🚀 Instalación

1.  Clona este repositorio o descarga los archivos.
2.  Instala las dependencias necesarias ejecutando:

```bash
pip install -r requirements.txt
```

## ⚙️ Ejecución

El proyecto consta de dos scripts principales que deben ejecutarse en orden:

1. Carga y Enriquecimiento de Datos

```bash
python insert_data.py
```

2. Validación y Consultas

```bash
python check_all.py
```
