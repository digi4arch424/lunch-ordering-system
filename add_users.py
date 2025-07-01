from init_database import app, db, User

def add_users():
    with app.app_context():
        # List of users to add with male names
        new_users = [
            {'username': 'michaelb', 'name': 'Michael Brooks', 'email': 'michael.brooks@example.com'},
            {'username': 'davidm', 'name': 'David Mitchell', 'email': 'david.mitchell@example.com'},
            {'username': 'robertl', 'name': 'Robert Lawson', 'email': 'robert.lawson@example.com'},
            {'username': 'jamesp', 'name': 'James Peterson', 'email': 'james.peterson@example.com'},
            {'username': 'williamt', 'name': 'William Thompson', 'email': 'william.thompson@example.com'},
            {'username': 'christopherb', 'name': 'Christopher Brown', 'email': 'christopher.brown@example.com'},
            {'username': 'thomasc', 'name': 'Thomas Clark', 'email': 'thomas.clark@example.com'},
            {'username': 'danielw', 'name': 'Daniel Wilson', 'email': 'daniel.wilson@example.com'},
            {'username': 'matthewh', 'name': 'Matthew Henderson', 'email': 'matthew.henderson@example.com'}
        ]
        
        added_count = 0
        
        for user_data in new_users:
            # Check if user already exists
            if not User.query.filter_by(username=user_data['username']).first():
                user = User(
                    username=user_data['username'],
                    name=user_data['name'],
                    email=user_data['email'],
                    is_admin=False
                )
                user.set_password('password123')  # Default password
                db.session.add(user)
                added_count += 1
        
        if added_count > 0:
            db.session.commit()
            print(f'\nSuccessfully added {added_count} new users to the database.')
            print('All users have been created with the default password: password123')
            print('Users should change their password after first login.')
        else:
            print('\nAll users already exist in the database.')

if __name__ == '__main__':
    add_users()
