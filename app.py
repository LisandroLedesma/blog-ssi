from flask import Flask, render_template, redirect, url_for
import os
import markdown

from drive_loader import DriveLoader


app = Flask(__name__)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(PROJECT_ROOT, 'config', 'service-account.json')
drive_loader = DriveLoader(CREDENTIALS_PATH)
POSTS_FOLDER = 'posts'
PRACTICO_FOLDER = 'practico'
os.makedirs(POSTS_FOLDER, exist_ok=True)
drive_loader.download_markdown_files(POSTS_FOLDER)


def get_posts():
    """Obtiene todos los posts en formato Markdown"""
    return load_markdown_files(POSTS_FOLDER)


def get_practico():
    """Obtiene todos los archivos de Práctico en formato Markdown"""
    return load_markdown_files(PRACTICO_FOLDER)


def load_markdown_files(folder):
    """Carga archivos Markdown desde un directorio específico"""
    posts = []
    extensions = [
        'tables',
        'fenced_code',
        'codehilite',
        'nl2br',
        'sane_lists',
        'smarty',
    ]
    for filename in os.listdir(folder):
        if filename.endswith('.md'):
            with open(os.path.join(folder, filename), 'r', encoding='utf-8') as f:
                content = f.read()
                title = filename.replace('.md', '').replace('_', ' ').title()
                posts.append({
                    'title': title,
                    'slug': filename.replace('.md', ''),
                    'content': markdown.markdown(content, extensions=extensions)
                })
    return sorted(posts, key=lambda x: x['title'])


@app.route('/')
def index():
    practico = get_practico()
    posts = get_posts()
    return render_template('index.html', posts=posts, active_post=None, practico=practico)


@app.route('/post/<slug>')
def post(slug):
    posts = get_posts()
    practico = get_practico()
    entries = posts + practico
    active_post = next((e for e in entries if e['slug'] == slug), None)
    return render_template('index.html', posts=posts, active_post=active_post, practico=practico)


@app.route('/update_posts', methods=['POST'])
def update_posts():
    """Actualiza las entradas descargando los archivos Markdown del Drive"""
    for filename in os.listdir(POSTS_FOLDER):
        file_path = os.path.join(POSTS_FOLDER, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error al eliminar el archivo {file_path}: {e}")

    drive_loader.download_markdown_files(POSTS_FOLDER)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
