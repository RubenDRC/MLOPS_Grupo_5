# Taller 3 Locust: MLOps - Despliegue y Monitoreo (Grupo 5 - Clase de los Martes)

## Descripción

Este proyecto configura un entorno de pruebas de carga utilizando **Locust**, junto con un servicio backend que expone modelos de Machine Learning a través de una API construida en **FastAPI**. El entorno se orquesta usando **Docker Compose**, permitiendo simular usuarios concurrentes para evaluar el rendimiento del sistema de inferencia.

## Estructura del Proyecto

```
./locust
├── data                  # Datos de entrada para entrenamiento/pruebas
│   ├── penguins_lter.csv
│   └── penguins_size.csv
├── models                # Modelos de machine learning entrenados (pkl)
│   ├── model_lr.pkl
│   ├── model_rf.pkl
│   └── model_svm.pkl
├── locustfile.py         # Script principal para pruebas de carga con Locust
├── main.py               # API con FastAPI para exponer modelos
├── Dockerfile            # Imagen base para la API
├── Dockerfile.locust     # Imagen base para los tests con Locust
├── requirements.txt      # Requisitos para la API
├── requirements-locust.txt # Requisitos para Locust
├── docker-compose.yaml   # Orquestación de API y dependencias
└── docker-compose.locust.yaml # Orquestación para pruebas con Locust
```

## Servicios Implementados

- **FastAPI**: Servicio backend con endpoints para inferencia de modelos de clasificación.
- **Locust**: Framework para pruebas de carga y simulación de usuarios concurrentes.

## Pasos para la Ejecución

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd locust
```

### 2. Construir y levantar la API

```bash
docker-compose -f docker-compose.yaml up -d --build
```

### 3. Acceder a la documentación de la API

- URL: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Ejecutar Locust para pruebas de carga

```bash
docker-compose -f docker-compose.locust.yaml up -d --build
```

- Acceder a la interfaz de Locust:
  - URL: [http://localhost:8089](http://localhost:8089)

- Parámetros sugeridos:
  - Número de usuarios: 10000
  - Agregación de usuarios: 500
  - Endpoint a probar: `/predict` con el siguiente body:

```json
{
  "island": "Biscoe",
  "culmen_length_mm": 50.0,
  "culmen_depth_mm": 18.5,
  "flipper_length_mm": 200.0,
  "body_mass_g": 4000.0,
  "sex": "MALE"
}
```

### 5. Validación limitando recursos
- Se realiza validación de carga con diferentes iteraciones sobre memoria, CPU y número de réplicas.
- Quedan documentados en el archivo "DOCUMENTACIÓN ITERACIONES".


## Comandos Útiles

- Parar los contenedores sin eliminar:
  ```bash
  docker-compose -f docker-compose.yaml stop
  docker-compose -f docker-compose.locust.yaml stop
  ```

- Reiniciar los contenedores:
  ```bash
  docker-compose restart
  ```

- Eliminar contenedores y volúmenes:
  ```bash
  docker-compose down -v
  docker-compose -f docker-compose.locust.yaml down -v
  ```

## Autores

Desarrollado por Grupo 5.
