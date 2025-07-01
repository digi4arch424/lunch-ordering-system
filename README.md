# 🍽️ Company Lunch Ordering System

A simple web application for employees to confirm their lunch participation daily.

## ✨ Features

- **User Authentication**
  - Secure login for employees and admin
  - Password hashing

- **Employee Dashboard**
  - Submit lunch preference (Yes/No)
  - Provide reason for not having lunch
  - View submission history

- **Admin Dashboard**
  - View all employee submissions
  - See statistics and analytics
  - Track who hasn't submitted yet

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/company-lunch-ordering.git
   cd company-lunch-ordering
   ```

2. **Set up the environment**
   - Copy `.env.example` to `.env`
   - (Optional) Update any settings in `.env`

3. **Run the setup script** (Windows)
   ```
   setup.bat
   ```
   This will:
   - Create a virtual environment
   - Install dependencies
   - Initialize the database
   - Create an admin user

4. **Start the development server**
   ```
   run.bat
   ```
   Or manually:
   ```bash
   # On Windows
   venv\Scripts\activate
   flask run
   
   # On macOS/Linux
   source venv/bin/activate
   flask run
   ```

5. **Access the application**
   - Open your browser and go to: http://localhost:5000
   - Log in with:
     - Admin: `admin` / `admin123`
     - Test user: `john` / `password123`

## 📂 Project Structure

```
├── app.py                 # Main application
├── init_db.py            # Database initialization
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
├── static/               # Static files (CSS, JS)
│   ├── css/
│   └── js/
└── templates/            # HTML templates
    ├── admin/            # Admin templates
    └── *.html            # Main templates
```

## 🌐 Deployment

### Vercel Deployment

1. Push your code to a GitHub repository
2. Import the repository to Vercel
3. Configure the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Output Directory: `(leave empty)`
   - Install Command: `python -m pip install --upgrade pip`

4. Add environment variables from `.env.example` to Vercel's environment variables

5. Deploy!

## 🔧 Troubleshooting

- If you get a database error, try deleting the `instance` folder and running `python init_db.py`
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check the console for any error messages

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

---

Built with ❤️ using Flask and Tailwind CSS
"# lunch-ordering-system" 
