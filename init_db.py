from app import app, db, User, LunchEntry
from datetime import datetime, timedelta
import random

def init_db():
    with app.app_context():
        # Drop all existing tables and recreate them
        db.drop_all()
        db.create_all()
        
        # Create admin user
        admin = User(
            username='admin',
            name='Administrator',
            email='admin@company.com',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create sample users
        users = [
            User(username='john', name='John Doe', email='john@example.com'),
            User(username='jane', name='Jane Smith', email='jane@example.com'),
            User(username='bob', name='Bob Johnson', email='bob@example.com'),
            User(username='alice', name='Alice Williams', email='alice@example.com'),
        ]
        
        # Set passwords for all users
        for user in users:
            user.set_password('password123')
        
        db.session.add_all(users)
        db.session.commit()
        
        # Create some sample lunch entries
        reasons = [
            'Working from home',
            'Out of office',
            'In a meeting',
            'On leave',
            'Not hungry',
            'Bringing own lunch'
        ]
        
        # Create entries for the past 7 days
        for i in range(7):
            date = datetime.utcnow().date() - timedelta(days=i)
            
            for user in [admin] + users:
                # Skip some random entries to simulate missing data
                if random.random() < 0.2:  # 20% chance to skip
                    continue
                    
                has_lunch = random.choice([True, False])
                reason = random.choice(reasons) if not has_lunch else None
                
                entry = LunchEntry(
                    user_id=user.id,
                    date=date,
                    has_lunch=has_lunch,
                    reason=reason,
                    timestamp=datetime.combine(date, datetime.min.time())
                )
                db.session.add(entry)
        
        db.session.commit()
        
        print('\n=== Database initialized successfully! ===')
        print('Admin login: username=admin, password=admin123')
        print('User logins: username=<username>, password=password123')
        print('Example: username=john, password=password123\n')

if __name__ == '__main__':
    init_db()
