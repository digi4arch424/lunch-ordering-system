from app import app, db

# Initialize database tables
with app.app_context():
    db.create_all()
    
    # Create admin user if not exists
    from app import User
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            name='Administrator',
            email='admin@company.com',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

# This is required for Vercel
export = app
