from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, session, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, time, timedelta, timezone
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///lunch.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# CSRF protection
def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = os.urandom(24).hex()
    return session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    lunch_entries = db.relationship('LunchEntry', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_submitted_today(self):
        today = datetime.now(timezone.utc).date()
        return LunchEntry.query.filter_by(
            user_id=self.id, 
            date=today
        ).first() is not None
    
    def __repr__(self):
        return f'<User {self.username}>'

class LunchEntry(db.Model):
    __tablename__ = 'lunch_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    has_lunch = db.Column(db.Boolean, nullable=False)
    reason = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<LunchEntry {self.user_id} {self.date} {self.has_lunch}>'

# Login manager
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Context processor to make 'now' available in all templates
@app.context_processor
def inject_now():
    return {'now': datetime.now(timezone.utc)}

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # Verify CSRF token
        form_token = request.form.get('csrf_token')
        session_token = session.get('_csrf_token')
        
        if not form_token or form_token != session_token:
            flash('Invalid form submission. Please try again.', 'danger')
            return redirect(url_for('login'))
        
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            flash('Invalid username or password. Please try again.', 'danger')
            return redirect(url_for('login'))
        
        # Regenerate CSRF token after successful login
        session.pop('_csrf_token', None)
        login_user(user, remember=remember)
        
        if user.is_admin:
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))
    
    # Generate CSRF token for the login form
    if '_csrf_token' not in session:
        session['_csrf_token'] = os.urandom(24).hex()
    
    return render_template('login.html', csrf_token=session['_csrf_token'])

def is_within_lunch_window():
    """Check if current time is within the lunch ordering window (8 AM - 9 AM)"""
    now = datetime.now(timezone.utc)
    start_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
    end_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
    return start_time <= now <= end_time

@app.route('/dashboard')
@login_required
def dashboard():
    today = datetime.now(timezone.utc).date()
    user_entry = LunchEntry.query.filter_by(user_id=current_user.id, date=today).first()
    
    # Get recent entries for the user
    recent_entries = LunchEntry.query.filter_by(user_id=current_user.id)\
        .order_by(LunchEntry.date.desc())\
        .limit(5).all()
    
    return render_template(
        'dashboard.html',
        entry=user_entry,
        within_window=is_within_lunch_window(),
        recent_entries=recent_entries,
        now=datetime.utcnow()
    )

@app.route('/submit_lunch', methods=['POST'])
@login_required
def submit_lunch():
    if request.method == 'POST':
        has_lunch = request.form.get('has_lunch') == 'yes'
        reason = request.form.get('reason', '').strip()
        
        # For demo purposes, we'll allow submissions at any time
        today = datetime.now(timezone.utc).date()
        
        # Check if user already submitted for today
        existing_entry = LunchEntry.query.filter_by(
            user_id=current_user.id,
            date=today
        ).first()
        
        if existing_entry:
            # Update existing entry
            existing_entry.has_lunch = has_lunch
            existing_entry.reason = reason if not has_lunch else None
            existing_entry.timestamp = datetime.utcnow()
            db.session.commit()
            flash('Your lunch preference has been updated!', 'success')
        else:
            # Create new entry
            entry = LunchEntry(
                user_id=current_user.id,
                date=today,
                has_lunch=has_lunch,
                reason=reason if not has_lunch else None
            )
            db.session.add(entry)
            db.session.commit()
            flash('Your lunch preference has been saved!', 'success')
        
    return redirect(url_for('dashboard'))

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get today's date
    today = datetime.now(timezone.utc).date()
    
    # Get all non-admin users
    users = User.query.filter_by(is_admin=False).all()
    
    # Get today's lunch entries with user details
    today_entries = db.session.query(
        LunchEntry,
        User
    ).join(
        User, User.id == LunchEntry.user_id
    ).filter(
        LunchEntry.date == today
    ).all()
    
    # Get all entries for the last 7 days for the chart
    seven_days_ago = today - timedelta(days=6)
    recent_entries = db.session.query(
        LunchEntry.date,
        db.func.sum(db.case((LunchEntry.has_lunch == True, 1), else_=0)).label('yes_count'),
        db.func.count().label('total_count')
    ).filter(
        LunchEntry.date >= seven_days_ago,
        LunchEntry.date <= today
    ).group_by(LunchEntry.date).order_by(LunchEntry.date).all()
    
    # Prepare data for the chart
    chart_data = {
        'labels': [],
        'yes': [],
        'no': []
    }
    
    for entry in recent_entries:
        chart_data['labels'].append(entry.date.strftime('%a, %b %d'))
        chart_data['yes'].append(entry.yes_count)
        chart_data['no'].append(entry.total_count - entry.yes_count)
    
    # Get users who haven't submitted for today
    submitted_user_ids = [entry.LunchEntry.user_id for entry in today_entries]
    pending_users = [user for user in users if user.id not in submitted_user_ids]
    
    # Get top reasons for not having lunch
    top_reasons = db.session.query(
        LunchEntry.reason,
        db.func.count(LunchEntry.id).label('count')
    ).filter(
        LunchEntry.date == today,
        LunchEntry.has_lunch == False,
        LunchEntry.reason.isnot(None)
    ).group_by(LunchEntry.reason).order_by(db.desc('count')).limit(5).all()
    
    # Calculate statistics
    total_users = len(users)
    submitted_count = len(today_entries)
    pending_count = total_users - submitted_count
    
    # Get yes/no counts for today
    yes_count = sum(1 for entry in today_entries if entry.LunchEntry.has_lunch)
    no_count = submitted_count - yes_count
    
    return render_template(
        'admin/dashboard.html',
        today=today,
        users=users,
        today_entries=today_entries,
        pending_users=pending_users,
        top_reasons=top_reasons,
        chart_data=chart_data,
        total_users=total_users,
        submitted_count=submitted_count,
        pending_count=pending_count,
        yes_count=yes_count,
        no_count=no_count
    )

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Initialize database
def init_db():
    with app.app_context():
        # Create all database tables
        db.create_all()
        
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Create admin user
            admin = User(
                username='admin',
                name='Administrator',
                email='admin@company.com',
                is_admin=True
            )
            admin.set_password('admin123')

# Serve static files for Vercel
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/export_pdf')
@login_required
def export_pdf():
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get today's date
    today = datetime.now(timezone.utc).date()
    
    # Get all users and their lunch status for today
    users = User.query.filter_by(is_admin=False).order_by(User.name).all()
    
    # Prepare data for the PDF
    data = [['Employee Name', 'Lunch Status', 'Reason']]
    
    for user in users:
        entry = LunchEntry.query.filter_by(user_id=user.id, date=today).first()
        if entry:
            status = 'Yes' if entry.has_lunch else 'No'
            reason = entry.reason if entry.reason else 'N/A'
        else:
            status = 'No response'
            reason = 'N/A'
        data.append([user.name, status, reason])
    
    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()
    
    # Create the PDF object, using the buffer as its "file"
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Add title
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=20,
        alignment=1  # Center aligned
    )
    
    title = Paragraph(f"Lunch Order Report - {today.strftime('%A, %B %d, %Y')}", title_style)
    elements.append(title)
    
    # Create the table
    table = Table(data)
    
    # Add style to the table
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
    ])
    
    # Apply the style to the table
    table.setStyle(style)
    
    # Add the table to the elements
    elements.append(table)
    
    # Add some space
    elements.append(Spacer(1, 20))
    
    # Add a footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=1  # Center aligned
    )
    
    footer = Paragraph(f"Generated on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC", footer_style)
    elements.append(footer)
    
    # Build the PDF
    doc.build(elements)
    
    # File response
    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.mimetype = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=lunch_report_{today.strftime("%Y%m%d")}.pdf'
    
    return response

@app.route('/export_csv')
@login_required
def export_csv():
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get today's date
    today = datetime.now(timezone.utc).date()
    
    # Get all users and their lunch status for today
    users = User.query.filter_by(is_admin=False).order_by(User.name).all()
    
    # Create a file-like buffer to receive CSV data
    buffer = []
    
    # Add CSV header
    buffer.append('Employee Name,Lunch Status,Reason\n')
    
    # Add data rows
    for user in users:
        entry = LunchEntry.query.filter_by(user_id=user.id, date=today).first()
        if entry:
            status = 'Yes' if entry.has_lunch else 'No'
            reason = f'"{entry.reason}"' if entry.reason else 'N/A'
        else:
            status = 'No response'
            reason = 'N/A'
        
        # Escape any commas in the name
        name = f'"{user.name}"'
        
        buffer.append(f'{name},{status},{reason}\n')
    
    # Create the response
    response = make_response(''.join(buffer))
    response.mimetype = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=lunch_report_{today.strftime("%Y%m%d")}.csv'
    
    return response

if __name__ == '__main__':
    # Initialize the database
    init_db()
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
