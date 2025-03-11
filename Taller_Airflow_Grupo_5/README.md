# Taller 3 Airflow: MLOps - Airflow (Grupo 5 - Clase de los Martes)

## Descripción
Este proyecto configura un entorno de trabajo con Apache Airflow, MySQL y FastAPI utilizando Docker Compose. Se implementa una estructura optimizada con un solo volumen compartido llamado `data`, en el cual cada servicio almacena sus archivos en directorios específicos para evitar conflictos y mejorar la organización.

## Estructura del Proyecto
El volumen `data` contiene los siguientes subdirectorios:

```
./data
├── mysql          # Datos de MySQL
├── dags           # DAGs de Airflow
├── logs           # Logs de Airflow
├── plugins        # Plugins de Airflow
├── models         # Modelos usados por FastAPI
```

### Servicios Implementados
- **MySQL**: Base de datos para Airflow.
- **Redis**: Broker de mensajes para Celery Executor en Airflow.
- **Apache Airflow**:
  - `airflow-webserver`: Interfaz web de Airflow.
  - `airflow-scheduler`: Planificador de tareas de Airflow.
  - `airflow-worker`: Trabajadores de Celery para ejecución distribuida.
  - `airflow-triggerer`: Servicio de ejecución de triggers en Airflow.
  - `airflow-init`: Inicialización y configuración de Airflow.
- **FastAPI**: Servicio backend construido con FastAPI.


## Pasos para la Ejecución
1. **Clonar el repositorio:**
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd <NOMBRE_DEL_REPOSITORIO>
   ```

2. **Construir y levantar los contenedores:**
   ```bash
   docker-compose up -d --build
   ```

3. **Verificar que los contenedores estén corriendo:**
   ```bash
   docker ps
   ```

4. **Acceder a Airflow:**
   - URL: [http://localhost:8080](http://localhost:8080)
   - Usuario: `airflow`
   - Contraseña: `airflow`

5. **Acceder a FastAPI:**
   - Documentación Swagger UI: [http://localhost:8888/docs](http://localhost:8888/docs)

6. **Parámetros para predicción**
   Se recomienda utilizar los siguientes para generar la predicción dentro de la api:
   ```bash
      {
        "island": "Biscoe",
        "culmen_length_mm": 50.0,
        "culmen_depth_mm": 18.5,
        "flipper_length_mm": 200.0,
        "body_mass_g": 4000.0,
        "sex": "MALE"
      }
   ```

## Comandos Útiles
### Parar los contenedores sin eliminarlos:
```bash
docker-compose stop
```

### Reiniciar los contenedores:
```bash
docker-compose restart
```

### Eliminar todos los contenedores y volúmenes:
```bash
docker-compose down -v
```

### Acceder a MySQL dentro del contenedor:
```bash
docker exec -it <ID_DEL_CONTENEDOR_MYSQL> mysql -u airflow -pairflow
```

### Listar las bases de datos en MySQL:
```sql
SHOW DATABASES;
```

### Seleccionar una base de datos y listar sus tablas:
```sql
USE airflow;
SHOW TABLES;
```

### Consultar datos de una tabla específica:
```sql
SELECT * FROM <nombre_de_la_tabla> LIMIT 10;
```

### Credenciales de MySQL:
- **Usuario:** `airflow`
- **Contraseña:** `airflow`
- **Base de datos predeterminada:** `airflow`

## Notas Adicionales
- Se recomienda definir un archivo `.env` para personalizar variables de entorno.
- Airflow y MySQL puede tardar unos segundos en iniciar debido a la inicialización de la base de datos.

---

## Autores
Desarrollado por Grupo 5.

