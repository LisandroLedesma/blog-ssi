from flask import Flask, render_template
import os
import markdown
from drive_loader import DriveLoader

app = Flask(__name__)


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(PROJECT_ROOT, 'config', 'service-account.json')
drive_loader = DriveLoader(CREDENTIALS_PATH)
POSTS_FOLDER = 'posts'
os.makedirs(POSTS_FOLDER, exist_ok=True)
drive_loader.download_markdown_files(POSTS_FOLDER)


def get_posts():
    """Obtiene todos los posts en formato Markdown"""
    drive_loader.download_markdown_files(POSTS_FOLDER)
    posts = []
    for filename in os.listdir(POSTS_FOLDER):
        if filename.endswith('.md'):
            with open(os.path.join(POSTS_FOLDER, filename), 'r', encoding='utf-8') as f:
                content = f.read()
                # Extrae el título y contenido del Markdown
                title = filename.replace('.md', '').replace('_', ' ').title()
                posts.append({
                    'title': title,
                    'slug': filename.replace('.md', ''),
                    'content': markdown.markdown(content)
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


if __name__ == '__main__':
    app.run(debug=True)
