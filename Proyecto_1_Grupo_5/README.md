# Proyecto 1: MLOps - TFX (Grupo 5 - Clase de los Martes)

Este repositorio contiene un entorno de desarrollo para pipelines de **TensorFlow Extended (TFX)** dentro de **Docker** y **docker-compose**, brindando un flujo de trabajo reproducible para proyectos de Machine Learning.  

## Desarrollo en Rasgos Generales

La configuración está diseñada mediante las siguientes etapas:
1. **Ingesta de Datos**: Utilizando `CsvExampleGen` u otros componentes para convertir datos en TFRecords.
2. **Análisis Estadístico**: Generación de estadísticas con `StatisticsGen`, detección de anomalías y creación de esquemas.
3. **Curación de Esquema**: Ajuste de rangos, tipos de datos y configuración de entornos (entrenamiento vs. servicio).
4. **Transformaciones e Ingeniería de Características**: Uso de `Transform` para estandarizar o escalar columnas, generar vocabularios y garantizar consistencia entre entrenamiento e inferencia.
5. **Metadatos de ML**: Rastreo de artefactos y ejecuciones con ML Metadata, facilitando auditoría y reproducibilidad.

## Estructura del Proyecto

- **Dockerfile** y **docker-compose.yml**  
  Configuran un contenedor que incluye **Jupyter**, **TensorFlow**, **TFX** y librerías.
- **pyproject.toml**  
  Lista las dependencias necesarias para el entorno (TFX, TensorFlow, etc.).
- **notebooks/**  
  Carpeta para almacenar los Jupyter Notebooks y scripts principales del pipeline.

## Uso con Docker Compose

Para iniciar el contenedor TFX:

```bash
docker-compose up --build
