from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from transformers import AutoModelForCausalLM, AutoTokenizer
import dotenv
import os
import torch
import uuid

# Inicializar la aplicación FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar las variables de entorno
dotenv.load_dotenv()
MODEL_NAME = os.getenv("MODEL_NAME")
USE_LORA = os.getenv("USE_LORA") == "true"
CSV_PATH = os.getenv("CSV_PATH")

# Cargar tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

# Cargar modelo
model_llm = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    device_map="cpu"
)

# Definir las emociones
emotions = ["Alegría", "Tristeza", "Neutral", "Ira", "Miedo", "Sorpresa"]

def createPrompt(sentence):
    '''
    Dada una oración, crea la prompt para el modelo de lenguaje. Se usan prompts distintas en función de si es un finetuning o no.
    
    Args:
        sentence (str): La oración a clasificar.
        
    Returns:
        str: La prompt para el modelo de lenguaje.
    '''
    if USE_LORA:
        return f"### Texto:\n{sentence}\n\n### Emoción:\n"
    
    emotions_str = '\n'.join(emotions)

    system = f'''Tu tarea es clasificar el texto dado en una de las siguientes seis emociones básicas:

{emotions_str}

Responde únicamente con la palabra correspondiente a la emoción, sin añadir ningún otro texto o explicación.'''

    messages = [
        {
            "role": "system",
            "content": system
        },
        {
            "role": "user",
            "content": sentence
        }
    ]
    return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

def get_token_probabilities(prompt):
    '''
    Dada una prompt, obtiene las probabilidades de los tokens de las emociones.

    Args:
        prompt (str): La prompt para el modelo de lenguaje.
    
    Returns:
        np.array: Un array con las probabilidades de los tokens de las emociones.
    '''
    inputs = tokenizer(prompt, return_tensors="pt")

    with torch.no_grad():
        outputs = model_llm(**inputs)

    # Obtener las probabilidades de los tokens
    next_token_logits = outputs.logits[:, -1, :]
    next_token_probs = torch.softmax(next_token_logits, dim=-1)

    # Obtener el primer token de cada emoción
    emotion_ids = tokenizer(emotions, add_special_tokens=False).input_ids
    emotion_tokens = [e[0] for e in emotion_ids]
    emotion_tokens = torch.tensor(emotion_tokens)

    # Obtener las probabilidades de los tokens de las emociones
    emotion_probs = next_token_probs[0, emotion_tokens].cpu().numpy()

    # Normalizar las probabilidades
    emotion_probs /= emotion_probs.sum()

    return emotion_probs

@app.get("/emotion")
def get_emotion(sentence: str):
    """
    Endpoint para detectar la emoción de una oración. Guarda la oración en un archivo CSV.

    Args:
        sentence (str): La oración a clasificar.

    Returns:
        dict: Un diccionario con un identificador único, la emoción detectada y las probabilidades de cada emoción.
    """
    if not sentence:
        raise HTTPException(status_code=400, detail="Sentence parameter is required.")

    prompt = createPrompt(sentence)
    emotion_probs = get_token_probabilities(prompt)

    emotion_idx = emotion_probs.argmax()
    emotion = emotions[emotion_idx]

    id = str(uuid.uuid4())[:4]

    # Guardar la oración en el archivo CSV
    with open(CSV_PATH, "a", encoding="utf8") as f:
        f.write(f"{id},\"{sentence}\",{emotion},,\n")

    return {
        "id": id,
        "emocion": emotion,
        "probs": {e: p for e, p in zip(emotions, emotion_probs.tolist())}
    }

@app.post("/evaluate")
def evaluate(id: str, like: bool, alternatives : str = None):
    """
    Endpoint para evaluar la clasificación de una oración.

    Args:
        id (str): El identificador único de la oración.
        like (bool): Si la clasificación es correcta o no.
        alternatives (str, opcional): Las emociones que se consideran correctas. Se usa en caso de que la clasificación sea incorrecta.

    Returns:
        dict: Un diccionario con un mensaje de éxito.
    """
    if not id:
        raise HTTPException(status_code=400, detail="ID parameter is required.")
    if like is None:
        raise HTTPException(status_code=400, detail="like parameter is required.")

    # Leer el archivo CSV
    with open(CSV_PATH, "r", encoding="utf8") as f:
        lines = f.readlines()

    # Buscar la línea con el ID y sacarla de la lista
    line = None
    for i, l in enumerate(lines):
        if l.startswith(id):
            line = lines.pop(i)
            break

    if line is None:
        raise HTTPException(status_code=404, detail=f"Sentence with ID '{id}' not found.")
    
    # Obtener la información de la línea
    line = line.split(",")
    id = line[0]
    sentence = line[1]
    detected_emotion = line[2]

    # Guardar la evaluación en el archivo CSV
    with open(CSV_PATH, "w", encoding="utf8") as f:
        f.writelines(lines)
        if like:
            f.write(f"{id},{sentence},{detected_emotion},{like},\n")
        else:
            f.write(f"{id},{sentence},{detected_emotion},{like},\"{alternatives}\"\n")

    return {"message": "Evaluation saved successfully."}