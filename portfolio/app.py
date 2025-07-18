from flask import Flask, render_template, redirect, url_for, request, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename

os.makedirs(os.path.join(os.path.dirname(__file__), 'instance'), exist_ok=True)
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'portfolio.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static')
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max upload size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# Set login view after initialization
login_manager.login_view = 'login'  # type: ignore

# Models
class AdminUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class PortfolioContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    text = db.Column(db.Text)
    image = db.Column(db.String(300))

class About(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    tagline = db.Column(db.String(200))
    bio = db.Column(db.Text)
    photo = db.Column(db.String(300))

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(30))
    linkedin = db.Column(db.String(200))
    github = db.Column(db.String(200))
    address = db.Column(db.String(200))

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    level = db.Column(db.String(50))  # e.g., Beginner, Intermediate, Expert

class Experience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    company = db.Column(db.String(200))
    start_year = db.Column(db.String(20))
    end_year = db.Column(db.String(20))
    description = db.Column(db.Text)

class SocialHandle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50))
    url = db.Column(db.String(300))

@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))

# Create tables and default admin at startup
with app.app_context():
    db.create_all()
    if not AdminUser.query.filter_by(username='admin').first():
        admin = AdminUser(username='admin', password=generate_password_hash('admin123'))  # type: ignore
        db.session.add(admin)
        db.session.commit()
    # Insert sample About if not present
    if not About.query.first():
        about = About(
            name='Amit Sharma',
            tagline='Full Stack Developer | Python & JS Enthusiast',
            bio='I am a passionate developer with experience in building beautiful web apps using Python, Flask, React, and more. I love solving problems and learning new technologies.',
            photo='https://randomuser.me/api/portraits/men/32.jpg'
        )
        db.session.add(about)
        db.session.commit()
    # Insert sample Contact if not present
    if not Contact.query.first():
        contact = Contact(
            email='amit.sharma@email.com',
            phone='+91-9876543210',
            linkedin='https://linkedin.com/in/amitsharma',
            github='https://github.com/amitsharma',
            address='Delhi, India'
        )
        db.session.add(contact)
        db.session.commit()
    # Insert sample Skills if not present
    if not Skill.query.first():
        skills = [
            Skill(name='Python', level='Expert'),
            Skill(name='Flask', level='Expert'),
            Skill(name='JavaScript', level='Intermediate'),
            Skill(name='React', level='Intermediate'),
            Skill(name='SQL', level='Intermediate'),
        ]
        db.session.add_all(skills)
        db.session.commit()
    # Insert sample Experience if not present
    if not Experience.query.first():
        exp1 = Experience(title='Software Engineer', company='Tech Solutions', start_year='2021', end_year='Present', description='Developed scalable web applications and APIs using Flask and React.')
        exp2 = Experience(title='Intern', company='StartupX', start_year='2020', end_year='2021', description='Worked on automation scripts and data analysis.')
        db.session.add_all([exp1, exp2])
        db.session.commit()
    # Insert sample SocialHandles if not present
    if not SocialHandle.query.first():
        handles = [
            SocialHandle(platform='LinkedIn', url='https://linkedin.com/in/amitsharma'),
            SocialHandle(platform='GitHub', url='https://github.com/amitsharma'),
            SocialHandle(platform='Twitter', url='https://twitter.com/amitsharma'),
        ]
        db.session.add_all(handles)
        db.session.commit()

@app.route('/')
def index():
    content = PortfolioContent.query.all()
    about = About.query.first()
    contact = Contact.query.first()
    skills = Skill.query.all()
    experience = Experience.query.all()
    handles = SocialHandle.query.all()
    return render_template('index.html', content=content, about=about, contact=contact, skills=skills, experience=experience, handles=handles)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username') or ''
        password = request.form.get('password') or ''
        user = AdminUser.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('admin'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    about = About.query.first()
    contact = Contact.query.first()
    skills = Skill.query.all()
    experience = Experience.query.all()
    content = PortfolioContent.query.all()
    handles = SocialHandle.query.all()
    # Handle About update
    if request.method == 'POST' and 'about_form' in request.form:
        about.name = request.form.get('name') or about.name
        about.tagline = request.form.get('tagline') or about.tagline
        about.bio = request.form.get('bio') or about.bio
        # Handle profile photo upload
        if 'photo_file' in request.files and request.files['photo_file'].filename != '':
            file = request.files['photo_file']
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                about.photo = url_for('static', filename=filename)
        else:
            about.photo = request.form.get('photo') or about.photo
        db.session.commit()
        flash('About updated!', 'success')
    # Handle Contact update
    if request.method == 'POST' and 'contact_form' in request.form:
        contact.email = request.form.get('email') or ''
        contact.phone = request.form.get('phone') or ''
        contact.linkedin = request.form.get('linkedin') or ''
        contact.github = request.form.get('github') or ''
        contact.address = request.form.get('address') or ''
        db.session.commit()
        flash('Contact updated!', 'success')
    # Handle Skill add
    if request.method == 'POST' and 'skill_form' in request.form:
        skill_name = request.form.get('skill_name')
        skill_level = request.form.get('skill_level')
        if skill_name and skill_level:
            db.session.add(Skill(name=skill_name, level=skill_level))
            db.session.commit()
            flash('Skill added!', 'success')
    # Handle Experience add
    if request.method == 'POST' and 'exp_form' in request.form:
        title = request.form.get('exp_title')
        company = request.form.get('exp_company')
        start_year = request.form.get('exp_start')
        end_year = request.form.get('exp_end')
        description = request.form.get('exp_desc')
        if title and company and start_year and end_year and description:
            db.session.add(Experience(title=title, company=company, start_year=start_year, end_year=end_year, description=description))
            db.session.commit()
            flash('Experience added!', 'success')
    # Handle SocialHandle add
    if request.method == 'POST' and 'handle_form' in request.form:
        platform = request.form.get('platform')
        url = request.form.get('handle_url')
        if platform and url:
            db.session.add(SocialHandle(platform=platform, url=url))
            db.session.commit()
            flash('Social handle added!', 'success')
    return render_template('admin.html', about=about, contact=contact, skills=skills, experience=experience, content=content, handles=handles)

@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_content(id):
    item = PortfolioContent.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Content deleted!', 'success')
    return redirect(url_for('admin'))

# Delete Skill
@app.route('/delete_skill/<int:id>', methods=['POST'])
@login_required
def delete_skill(id):
    skill = Skill.query.get_or_404(id)
    db.session.delete(skill)
    db.session.commit()
    flash('Skill deleted!', 'success')
    return redirect(url_for('admin'))

# Delete Experience
@app.route('/delete_experience/<int:id>', methods=['POST'])
@login_required
def delete_experience(id):
    exp = Experience.query.get_or_404(id)
    db.session.delete(exp)
    db.session.commit()
    flash('Experience deleted!', 'success')
    return redirect(url_for('admin'))

@app.route('/delete_handle/<int:id>', methods=['POST'])
@login_required
def delete_handle(id):
    handle = SocialHandle.query.get_or_404(id)
    db.session.delete(handle)
    db.session.commit()
    flash('Social handle deleted!', 'success')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)

