from app import app, db, User
from werkzeug.security import generate_password_hash

def init_database():
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
            db.session.add(admin)
            
            # Create a regular user
            user = User(
                username='john',
                name='John Doe',
                email='john@example.com',
                is_admin=False
            )
            user.set_password('password123')
            db.session.add(user)
            
            db.session.commit()
            print("Database initialized successfully!")
            print("Admin credentials:")
            print("  Username: admin")
            print("  Password: admin123")
            print("\nRegular user:")
            print("  Username: john")
            print("  Password: password123")
        else:
            print("Database already initialized.")

if __name__ == '__main__':
    init_database()
