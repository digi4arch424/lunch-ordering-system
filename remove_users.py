from init_database import app, db, User

def list_users():
    """List all users in the database"""
    with app.app_context():
        users = User.query.order_by(User.username).all()
        if not users:
            print("No users found in the database.")
            return []
        
        print("\nCurrent Users:")
        print("-" * 80)
        print(f"{'ID':<5} {'Username':<15} {'Name':<20} {'Email':<25} {'Admin'}")
        print("-" * 80)
        
        for user in users:
            admin_status = "Yes" if user.is_admin else "No"
            print(f"{user.id:<5} {user.username:<15} {user.name:<20} {user.email:<25} {admin_status}")
        
        return users

def remove_user(username):
    """Remove a specific user by username"""
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"\nError: User '{username}' not found.")
            return False
        
        if user.is_admin:
            print(f"\nError: Cannot remove admin user '{username}'.")
            return False
            
        db.session.delete(user)
        db.session.commit()
        print(f"\nSuccessfully removed user: {username}")
        return True

def remove_all_users(confirm=False):
    """Remove all non-admin users"""
    if not confirm:
        print("\nWARNING: This will remove ALL non-admin users from the database!")
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Operation cancelled.")
            return
    
    with app.app_context():
        # Get all non-admin users
        users = User.query.filter_by(is_admin=False).all()
        if not users:
            print("\nNo non-admin users found to remove.")
            return
        
        # Remove all non-admin users
        for user in users:
            db.session.delete(user)
        
        db.session.commit()
        print(f"\nSuccessfully removed {len(users)} non-admin users from the database.")

def main():
    print("\n=== User Management Tool ===")
    print("1. List all users")
    print("2. Remove a specific user")
    print("3. Remove all non-admin users")
    print("4. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-4): ")
            
            if choice == '1':
                list_users()
            elif choice == '2':
                username = input("Enter username to remove: ").strip()
                if username:
                    remove_user(username)
            elif choice == '3':
                remove_all_users()
            elif choice == '4':
                print("\nExiting...")
                break
            else:
                print("\nInvalid choice. Please enter a number between 1 and 4.")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            break
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")

if __name__ == '__main__':
    main()
