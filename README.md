# NewsFlash247 - Breaking News Website

A modern Flask-based news website with user authentication, newsletter subscription, and admin panel for content management.

## Features

- **News Management**: Create, edit, and publish news articles with categories
- **User Authentication**: Secure registration and login system
- **Newsletter System**: Email subscription with automated welcome emails
- **Admin Panel**: Complete dashboard for managing content and subscribers
- **Responsive Design**: Mobile-friendly Bootstrap interface
- **Database Integration**: PostgreSQL with proper data models

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Email**: SMTP integration (Gmail)
- **Authentication**: Flask-Login with password hashing

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/newsflash247.git
cd newsflash247
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export DATABASE_URL="your_postgresql_url"
export SESSION_SECRET="your_secret_key"
export MAIL_USERNAME="your_email@gmail.com"
export MAIL_PASSWORD="your_app_password"
```

4. Run the application:
```bash
python main.py
```

## Usage

### Admin Access
- **Email**: admin@newsflash247.com
- **Password**: admin123

### Admin Features
- Create and manage news articles
- View subscriber statistics
- Send newsletters to subscribers
- Manage site settings

### User Features
- Register and login accounts
- Subscribe to newsletter
- View breaking news and articles
- Responsive mobile experience

## Project Structure

```
newsflash247/
├── app.py              # Flask application setup
├── main.py             # Main application routes
├── models.py           # Database models
├── email_service.py    # Email functionality
├── templates/          # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── admin/         # Admin panel templates
│   └── ...
├── static/            # CSS, JS, images
└── requirements.txt   # Python dependencies
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Contact

For questions or support, please open an issue on GitHub.