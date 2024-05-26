from flask import Flask, request, redirect, url_for, send_file, render_template, jsonify
import yt_dlp as youtube_dl
import os
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

MONGO_URI = "mongodb+srv://inostrozatomas91:NEr1n0w9E2SQAucX@tubetomp3.zhs0swj.mongodb.net/tubetomp3?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true"
client = MongoClient(MONGO_URI)
db = client.get_database("tubetomp3")
downloads_collection = db.downloads

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'temp/%(title)s.%(ext)s',
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            title = info_dict.get('title', None)
            filename = f"temp/{title}.mp3"
            new_filename = f"downloads/{title}.mp3"
            
            # Verificar si el archivo existe y eliminarlo si es necesario
            if os.path.exists(new_filename):
                os.remove(new_filename)
            
            os.rename(filename, new_filename)
            
            # Guardar información en la base de datos
            download_record = {
                "title": title,
                "filename": new_filename
            }
            downloads_collection.insert_one(download_record)
            
            return send_file(new_filename, as_attachment=True)
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(debug=True)