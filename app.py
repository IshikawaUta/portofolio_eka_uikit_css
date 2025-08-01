import os
from flask import Flask, render_template, request, redirect, url_for, flash, Response
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson.objectid import ObjectId, InvalidId
from datetime import datetime
from markupsafe import Markup
import cloudinary
import cloudinary.uploader
import cloudinary.api
from config import Config
import json

app = Flask(__name__)
app.config.from_object(Config)

client = MongoClient(app.config['MONGO_URI'])
db = client.UIkit_CSS_db
projects_collection = db.projects
users_collection = db.users

cloudinary.config(
    cloud_name=app.config['CLOUDINARY_CLOUD_NAME'],
    api_key=app.config['CLOUDINARY_API_KEY'],
    api_secret=app.config['CLOUDINARY_API_SECRET']
)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'komikers09@gmail.com')

mail = Mail(app)

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.password_hash = user_data['password']

    @staticmethod
    def get(user_id):
        user_data = users_collection.find_one({"_id": ObjectId(user_id)})
        if user_data:
            return User(user_data)
        return None

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

STATIC_URLS = [
    'index',
    'about',
    'contact',
    'projects',
    'tools',
    'admin_login'
]

@app.template_filter('nl2br')
def nl2br_filter(s):
    if not isinstance(s, str):
        return s
    
    return Markup(s.replace('\n', '<br>'))

@app.template_filter('strftime')
def datetime_format(value, format_string='%Y-%m-%d'):
    if isinstance(value, datetime):
        return value.strftime(format_string)
    if value == 'now':
        return datetime.now().strftime(format_string)
    return value

@app.route('/')
def index():
    return render_template('index.html', now=datetime.now())

@app.route('/about')
def about():
    return render_template('about.html', now=datetime.now())

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message_body = request.form['message']

        recipient_email = 'komikers09@gmail.com'

        try:
            msg = Message(
                subject=f"Templates Portofolio Eka saputra: {subject}",
                recipients=[recipient_email],
                html=render_template(
                    'emails/contact_email.html',
                    name=name,
                    email=email,
                    subject=subject,
                    message_body=message_body
                ),
                sender=app.config['MAIL_DEFAULT_SENDER']
            )
            mail.send(msg)

            flash('Pesan Anda berhasil dikirim! Saya akan segera menghubungi Anda.', 'success')
            return redirect(url_for('contact'))
        except Exception as e:
            flash(f'Maaf, terjadi kesalahan saat mengirim pesan Anda: {e}', 'danger')
            app.logger.error(f"Error sending contact email: {e}")
            return redirect(url_for('contact'))

    return render_template('contact.html', now=datetime.now())

@app.route('/projects')
def projects():
    all_projects = list(projects_collection.find().sort("date_created", -1))
    return render_template('projects.html', projects=all_projects, now=datetime.now())

@app.route('/projects/<project_id>')
def project_detail(project_id):
    project = None
    try:
        project = projects_collection.find_one({'_id': ObjectId(project_id)})
    except InvalidId:
        print(f"ID '{project_id}' bukan ObjectId yang valid. Mencoba mencari sebagai string...")
        project = projects_collection.find_one({'_id': project_id})

    print(f"Mencari proyek dengan ID: {project_id}")
    print(f"Proyek ditemukan: {project}")

    if not project:
        return render_template('errors/404.html', now=datetime.now()), 404

    return render_template('project_detail.html', project=project, now=datetime.now())

@app.route('/tools')
def tools():
    return render_template('tools.html', now=datetime.now())

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_projects'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_data = users_collection.find_one({'username': username})

        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_data)
            login_user(user)
            flash('Login berhasil!', 'success')
            return redirect(url_for('admin_projects'))
        else:
            flash('Username atau password salah.', 'danger')
    return render_template('admin/login.html', now=datetime.now())

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin/projects')
@login_required
def admin_projects():
    all_projects = list(projects_collection.find().sort("date_created", -1))
    return render_template('admin/project_list.html', projects=all_projects, now=datetime.now())

@app.route('/admin/projects/add', methods=['GET', 'POST'])
@login_required
def add_project():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        technologies = [tech.strip() for tech in request.form['technologies'].split(',')]
        project_url = request.form['project_url']
        github_url = request.form.get('github_url', '')
        image_url = ''

        if 'image' in request.files and request.files['image'].filename != '':
            image_file = request.files['image']
            upload_result = cloudinary.uploader.upload(image_file, folder="portfolio_projects")
            image_url = upload_result['secure_url']

        new_project = {
            'title': title,
            'description': description,
            'technologies': technologies,
            'project_url': project_url,
            'github_url': github_url,
            'image_url': image_url,
            'date_created': datetime.utcnow()
        }
        projects_collection.insert_one(new_project)
        flash('Proyek berhasil ditambahkan!', 'success')
        return redirect(url_for('admin_projects'))
    return render_template('admin/add_edit_project.html', project=None, now=datetime.now())

@app.route('/admin/projects/edit/<project_id>', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = projects_collection.find_one({"_id": ObjectId(project_id)})
    if not project:
        flash('Proyek tidak ditemukan.', 'danger')
        return redirect(url_for('admin_projects'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        technologies = [tech.strip() for tech in request.form['technologies'].split(',')]
        project_url = request.form['project_url']
        github_url = request.form.get('github_url', '')
        current_image_url = project.get('image_url', '')

        if 'image' in request.files and request.files['image'].filename != '':
            image_file = request.files['image']
            upload_result = cloudinary.uploader.upload(image_file, folder="portfolio_projects")
            image_url = upload_result['secure_url']
            if current_image_url:
                public_id = current_image_url.split('/')[-1].split('.')[0]
                cloudinary.uploader.destroy(f"portfolio_projects/{public_id}")
        else:
            image_url = current_image_url

        projects_collection.update_one(
            {"_id": ObjectId(project_id)},
            {"$set": {
                'title': title,
                'description': description,
                'technologies': technologies,
                'project_url': project_url,
                'github_url': github_url,
                'image_url': image_url
            }}
        )
        flash('Proyek berhasil diperbarui!', 'success')
        return redirect(url_for('admin_projects'))
    return render_template('admin/add_edit_project.html', project=project, now=datetime.now())

@app.route('/admin/projects/delete/<project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    project = projects_collection.find_one({"_id": ObjectId(project_id)})
    if project:
        image_url = project.get('image_url')
        if image_url:
            public_id = image_url.split('/')[-1].split('.')[0]
            cloudinary.uploader.destroy(f"portfolio_projects/{public_id}")
        
        projects_collection.delete_one({"_id": ObjectId(project_id)})
        flash('Proyek berhasil dihapus!', 'success')
    else:
        flash('Proyek tidak ditemukan.', 'danger')
    return redirect(url_for('admin_projects'))

@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    projects_data = projects_collection.find()

    project_urls = []
    for project in projects_data:
        project_urls.append(url_for('project_detail', project_id=str(project['_id']), _external=True))

    static_urls = [
        url_for('index', _external=True),
        url_for('about', _external=True),
        url_for('contact', _external=True),
        url_for('projects', _external=True),
        url_for('tools', _external=True),
        url_for('admin_login', _external=True)
    ]

    all_urls = project_urls + static_urls

    sitemap_xml = render_template('sitemap.xml', all_urls=all_urls)
    response = Response(sitemap_xml, mimetype='application/xml')
    return response

@app.route('/robots.txt')
def robots_txt():
    robots_content = """
User-agent: *
Allow: /

Sitemap: {}/sitemap.xml
""".format(request.url_root.rstrip('/'))
    return Response(robots_content, mimetype='text/plain')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html', now=datetime.now()), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html', now=datetime.now()), 500

if __name__ == '__main__':
    from datetime import datetime
    app.run(debug=True)