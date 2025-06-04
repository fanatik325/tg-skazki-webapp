from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from mangum import Mangum
import os
import json
import openai

app = FastAPI()
handler = Mangum(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Пути
prompt_path = "api/prompt.txt"
user_data_path = "api/user_data.json"
story_archive_path = "api/story_archive.json"

# Ключ OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Загрузка профилей
if os.path.exists(user_data_path):
    with open(user_data_path, "r", encoding="utf-8") as f:
        user_profiles = json.load(f)
else:
    user_profiles = {}

# Загрузка архива сказок
if os.path.exists(story_archive_path):
    with open(story_archive_path, "r", encoding="utf-8") as f:
        story_archive = json.load(f)
else:
    story_archive = {}

# Модель запроса
class StoryRequest(BaseModel):
    user_id: int
    name: str
    age: int
    interests: str

# Получение использованных элементов
def get_used_elements(user_id: str):
    enemies, helpers, quests = set(), set(), set()
    if user_id in story_archive:
        for entry in story_archive[user_id]:
            story_text = entry.get("story", "")
            for line in story_text.splitlines():
                if any(mark in line for mark in ["🐍", "🕷️", "🐸", "🔥", "🧠"]):
                    enemies.add(line.strip())
                if any(hint in line.lower() for hint in ["жужа", "помощник", "облачный кекс", "медведь"]):
                    helpers.add(line.strip())
                if any(kw in line.lower() for kw in ["испытание", "ловушка"]):
                    quests.add(line.strip())
    return {
        "enemies": list(enemies),
        "helpers": list(helpers),
        "quests": list(quests)
    }

# Сборка промпта
def build_prompt(name: str, age: str, topic: str, user_id: str):
    with open(prompt_path, "r", encoding="utf-8") as f:
        base_prompt = f.read()

    personalization = f"""
---
Главный герой — сам ребёнок:
Имя: {name}
Возраст: {age}
Выбранная тема сказки: {topic}
"""

    used = get_used_elements(user_id)
    archive_block = f"""
---
✨ Уже использовались ранее у этого ребёнка:
- Злодеи: {", ".join(used['enemies']) or 'нет'}
- Помощники: {", ".join(used['helpers']) or 'нет'}
- Испытания: {", ".join(used['quests']) or 'нет'}

⚠️ Не повторяй их. Придумай новых, оригинальных и смешных персонажей и сцен.
"""

    return base_prompt + personalization + archive_block

# Улучшение сказки
def improve_story(story: str, age: str, name: str, topic: str):
    prompt = f"""
Ты — ребёнок {age} лет по имени {name}, для которого писалась эта сказка на тему «{topic}». Вот текст сказки:

{story}

Проанализируй её как ребёнок {age} лет:
1. Найди слабые места
2. Предложи улучшения
3. Перепиши сказку, устранив все замечания, добавив эмоции, детали, магию, юмор, диалоги, вовлекающие элементы.

Не включай анализ — только итоговую сказку!
"""
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.95,
        max_tokens=6000
    )
    return response.choices[0].message.content.strip()

@app.get("/")
def read_root():
    return {"msg": "Привет от FastAPI"}

@app.post("/generate")
async def generate_story(data: StoryRequest):
    name, age, topic, user_id = data.name, str(data.age), data.interests, str(data.user_id)

    # Сохраняем профиль
    user_profiles[user_id] = {"name": name, "age": age, "topic": topic}
    with open(user_data_path, "w", encoding="utf-8") as f:
        json.dump(user_profiles, f, ensure_ascii=False, indent=2)

    # Генерация
    base_prompt = build_prompt(name, age, topic, user_id)
    raw = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": base_prompt}],
        temperature=0.9,
        max_tokens=3000
    )
    rough_story = raw.choices[0].message.content.strip()
    final_story = improve_story(rough_story, age, name, topic)

    # Сохраняем в архив
    story_archive.setdefault(user_id, []).append({"story": final_story})
    with open(story_archive_path, "w", encoding="utf-8") as f:
        json.dump(story_archive, f, ensure_ascii=False, indent=2)

    return {"story": final_story}
