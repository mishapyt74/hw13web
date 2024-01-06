from fastapi import FastAPI, Request, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from pymongo import MongoClient
import cloudinary
import cloudinary.uploader
import os

app = FastAPI()

# Налаштування CORS для дозволу на всі запити
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = MongoClient(os.environ['MONGO_URI'])
db = client['your_database']

cloudinary.config(
    cloud_name=os.environ['CLOUDINARY_CLOUD_NAME'],
    api_key=os.environ['CLOUDINARY_API_KEY'],
    api_secret=os.environ['CLOUDINARY_API_SECRET']
)

limiter = FastAPILimiter(key_func=lambda _: "global", rate_limits="10 per minute")

@app.post('/api/verify-email')
@limiter.limit("5 per minute")
async def verify_email(request: Request):
    data = await request.json()
    email = data.get('email')

    user = db.users.find_one({'email': email})
    if user:
        return JSONResponse(content='Пошта верифікована', status_code=200)
    else:
        raise HTTPException(status_code=404, detail='Користувача не знайдено')

@app.post('/api/update-avatar')
async def update_avatar(file: UploadFile = File(...)):
    try:
        result = await cloudinary.uploader.upload(file.file)

        db.users.update_one({'user_id': user_id}, {'$set': {'avatar_url': result['secure_url']}})
        return JSONResponse(content={'url': result['secure_url']}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Помилка завантаження аватара: {e}')

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
