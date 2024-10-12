# Detección de Emociones - Ingeniería de Muestra 2024

### Procedimiento para correr la API localmente

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/nsuruguay05/idm-emociones-be.git
   ```
2. **Instalar dependencias:**
   ```bash
   cd <NOMBRE_DEL_DIRECTORIO>
   pip install -r requirements.txt
   ```
3. **Configurar variables de entorno:** Crear un archivo `.env` en la carpeta principal del proyecto con las siguientes variables:
   ```
   MODEL_NAME=<NOMBRE_DEL_MODELO> # Modelo usado en IdM: nsuruguay05/Llama-3.2-1B-IdM2024
   USE_LORA=true  # o false si no se usa un modelo finetuneado (por ejemplo: meta-llama/Llama-3.2-1B-Instruct)
   CSV_PATH=<RUTA_DEL_ARCHIVO_CSV>
   WITH_NEUTRAL=true  # o false si no se desea incluir la emoción "Neutral"
   ```
   Usar `.env.sample` como referencia.

4. **Ejecutar la API:**
   ```bash
   uvicorn app:app --reload
   ```
   Se accede a la API en `http://localhost:8000`.

### Endpoints de la API

1. **GET /emotion**
   - **Descripción:** Detecta la emoción de una oración dada.
   - **Parámetros (query params):**
     - `sentence` (str): La oración a clasificar.
   - **Ejemplo de respuesta:**
     ```json
     {
       "id": "a3g1",
       "emocion": "Tristeza",
       "probs": {
         "Alegría": 0.1,
         "Tristeza": 0.3,
         "Ira": 0.05,
         "Miedo": 0.2,
         "Sorpresa": 0.15,
         "Neutral": 0.2
       }
     }
     ```

2. **POST /evaluate**
   - **Descripción:** Evalúa la clasificación de una oración previamente clasificada.
   - **Parámetros (query params):**
     - `id` (str): El identificador único de la oración.
     - `like` (bool): Indica si la clasificación es correcta (`true` o `false`).
     - `alternatives` (str, opcional): Las emociones consideradas correctas si la clasificación fue incorrecta. Separadas por comas.
   - **Respuesta:**
     ```json
     {
       "message": "Evaluation saved successfully."
     }
     ```