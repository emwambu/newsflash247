# Deployment Guide for NewsFlash247

## Environment Variables Required

Before deploying, set up these environment variables:

```bash
DATABASE_URL=postgresql://username:password@host:port/database
SESSION_SECRET=your-secure-random-string
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-gmail-app-password
```

## Local Development Setup

1. **Clone the repository:**
```bash
git clone https://github.com/emwambu/newsflash247.git
cd newsflash247
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install flask flask-sqlalchemy flask-login werkzeug psycopg2-binary jinja2 email-validator gunicorn
```

4. **Set environment variables:**
```bash
export DATABASE_URL="sqlite:///newsflash247.db"  # For local development
export SESSION_SECRET="your-secret-key"
export MAIL_USERNAME="your-email@gmail.com"
export MAIL_PASSWORD="your-app-password"
```

5. **Run the application:**
```bash
python main.py
```

## Production Deployment Options

### Heroku (Free Tier Available)
1. Install Heroku CLI
2. Create Heroku app: `heroku create your-app-name`
3. Add PostgreSQL: `heroku addons:create heroku-postgresql:hobby-dev`
4. Set environment variables: `heroku config:set SESSION_SECRET=your-secret`
5. Deploy: `git push heroku main`

### Railway (Free Tier)
1. Connect GitHub repository
2. Add PostgreSQL database
3. Set environment variables in dashboard
4. Deploy automatically

### Render (Free Tier)
1. Connect GitHub repository
2. Create PostgreSQL database
3. Configure environment variables
4. Deploy with automatic builds

## Database Setup

The application automatically creates tables on first run. The default admin account:
- **Email:** 
- **Password:**

Change this password immediately after first login.

## Email Configuration

For Gmail SMTP:
1. Enable 2-factor authentication
2. Generate App Password in Google Account settings
3. Use the app password (not your regular password)

## Security Notes

- Change default admin credentials
- Use strong SESSION_SECRET in production
- Keep email credentials secure
- Regular database backups recommended
