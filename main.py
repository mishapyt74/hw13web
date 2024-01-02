from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from pymongo import MongoClient
import cloudinary
import cloudinary.uploader
import os

app = Flask(__name__)
CORS(app)

client = MongoClient(os.environ['MONGO_URI'])
db = client['your_database']

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per 15 minutes"]
)

cloudinary.config(
    cloud_name=os.environ['CLOUDINARY_CLOUD_NAME'],
    api_key=os.environ['CLOUDINARY_API_KEY'],
    api_secret=os.environ['CLOUDINARY_API_SECRET']
)

@app.route('/api/verify-email', methods=['POST'])
@limiter.limit("10 per minute")  # Обмеження частоти
def verify_email():
    email = request.json.get('email')

    user = db.users.find_one({'email': email})
    if user:
        return 'Пошта верифікована', 200
    else:
        return 'Користувача не знайдено', 404

@app.route('/api/update-avatar', methods=['POST'])
def update_avatar():
    if 'file' not in request.files:
        return 'Файл не знайдено', 400

    file = request.files['file']
    try:
        result = cloudinary.uploader.upload(file)
        db.users.update_one({'user_id': user_id}, {'$set': {'avatar_url': result['secure_url']}})
        return jsonify({'url': result['secure_url']}), 200
    except Exception as e:
        return 'Помилка завантаження аватара: ' + str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
