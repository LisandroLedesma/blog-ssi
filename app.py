from flask import Flask, render_template, redirect, url_for
import os
import markdown
from dotenv import load_dotenv

from drive_loader import DriveLoader

load_dotenv()

app = Flask(__name__)


CREDENTIALS_PATH = os.getenv('CREDENTIALS_PATH')
drive_loader = DriveLoader(CREDENTIALS_PATH)
POSTS_FOLDER = 'posts'
os.makedirs(POSTS_FOLDER, exist_ok=True)
drive_loader.download_markdown_files(POSTS_FOLDER)


def get_posts():
    """Obtiene todos los posts en formato Markdown"""
    posts = []
    extensions = [
        'tables',  # Tablas
        'fenced_code',  # Bloques de código con acentos
        'codehilite',  # Resaltado de sintaxis
        'nl2br',  # Saltos de línea
        'sane_lists',  # Listas más precisas
        'smarty',  # Tipografía inteligente
    ]

    for filename in os.listdir(POSTS_FOLDER):
        if filename.endswith('.md'):
            with open(os.path.join(POSTS_FOLDER, filename), 'r', encoding='utf-8') as f:
                content = f.read()
                # Extrae el título y contenido del Markdown
                title = filename.replace('.md', '').replace('_', ' ').title()
                posts.append({
                    'title': title,
                    'slug': filename.replace('.md', ''),
                    'content': markdown.markdown(content, extensions=extensions)
                })
    return sorted(posts, key=lambda x: x['title'])


@app.route('/')
def index():
    posts = get_posts()
    return render_template('index.html', posts=posts, active_post=None)


@app.route('/post/<slug>')
def post(slug):
    posts = get_posts()
    active_post = next((post for post in posts if post['slug'] == slug), None)
    return render_template('index.html', posts=posts, active_post=active_post)

@app.route('/update_posts', methods=['POST'])
def update_posts():
    """Actualiza las entradas descargando los archivos Markdown del Drive"""
    drive_loader.download_markdown_files(POSTS_FOLDER)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
