from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import pyrebase

firebaseConfig = {
  "apiKey": "AIzaSyAs-i5_c7iSqZs88U7xscV5T18pDkDdE7w",
  "authDomain": "memehub-db3bb.firebaseapp.com",
  "projectId": "memehub-db3bb",
  "storageBucket": "memehub-db3bb.appspot.com",
  "messagingSenderId": "1025202043089",
  "appId": "1:1025202043089:web:13f45e512358bc9a822df0",
  "measurementId": "G-PY47KSV4G6",
  "databaseURL": ""
}

firebase = pyrebase.initialize_app(firebaseConfig)

storage = firebase.storage()


app = Flask(__name__)

cwd = os.getcwd()
dir_path = os.path.dirname(os.path.realpath(__file__))

print(dir_path)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///memes.db'
app.config['UPLOAD_FOLDER'] = os.path.join(dir_path,'static','uploads')
print(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

class Meme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meme_type = db.Column(db.String(50), nullable=False)
    uploader_name = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
@app.route('/home')
def home():
    title="MemeHub"
    memes = Meme.query.all()
    return render_template("home.html", title=title, memes = memes)
@app.route('/<meme_type>')
def display_images_by_type(meme_type):
    # Query images by type directly in the query
    memes = Meme.query.filter(Meme.meme_type == meme_type).all()
    return render_template('display_images_by_type.html', memes=memes, meme_type=meme_type)

@app.route('/upload', methods=['GET','POST'])
def upload():
    title="Become a god"
    if request.method == 'POST':
        meme_type = request.form['memeType']
        uploader_name = request.form['uploaderName']
        file = request.files['memeImage']

        file_name=secure_filename(file.filename)
        # file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)

        # file.save(file_path)

        storage.child(f'uploads/{file_name}').put(file)
        url=storage.child(f'uploads/{file_name}').get_url(None)

        meme = Meme(uploader_name=uploader_name, meme_type = meme_type, filename=url)
        db.session.add(meme)
        db.session.commit()
        print(meme_type)
        
        Message = 'File successfully uploaded and saved to database'
        return render_template("upload.html", title=title, message=Message)
    return render_template("upload.html", title=title)

if __name__ == '__main__':
    app.run(host="localhost", port=8000, debug=True)