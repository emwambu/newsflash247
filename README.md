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
