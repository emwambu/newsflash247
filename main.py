from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import User, NewsArticle, NewsSubscriber, EmailLog, SiteSettings
from email_service import EmailService
import logging
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    # Get published news articles from database
    news_articles = NewsArticle.query.filter_by(is_published=True).order_by(NewsArticle.created_at.desc()).limit(10).all()
    
    # Convert to list of dicts for template compatibility
    news = []
    for article in news_articles:
        news.append({
            'id': article.id,
            'title': article.title,
            'content': article.summary or article.content[:300] + '...',
            'category': article.category,
            'timestamp': article.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'is_breaking': article.is_breaking,
            'views_count': article.views_count,
            'reading_time': article.reading_time
        })
    
    return render_template('index.html', news=news)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Please fill in all fields.', 'error')
            return render_template('login.html')
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        
        if not email or not password or not confirm_password:
            flash('Please fill in all required fields.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please use a different email.', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
            logging.error(f"Registration error: {str(e)}")
        
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Get statistics
    subscriber_count = NewsSubscriber.query.filter_by(is_active=True).count()
    article_count = NewsArticle.query.filter_by(is_published=True).count()
    total_views = db.session.query(db.func.sum(NewsArticle.views_count)).scalar() or 0
    
    # Get recent articles for admin users
    recent_articles = []
    if current_user.is_admin:
        recent_articles = NewsArticle.query.order_by(NewsArticle.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         user=current_user,
                         subscriber_count=subscriber_count,
                         article_count=article_count,
                         total_views=total_views,
                         recent_articles=recent_articles)

@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if not email:
            flash('Please enter a valid email address.', 'error')
            return render_template('subscribe.html')
        
        # Use EmailService to handle subscription
        success, message = EmailService.subscribe_email(email)
        
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error' if 'already subscribed' not in message else 'info')
        
        return render_template('subscribe.html')
    
    return render_template('subscribe.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('home'))

# Admin Panel Routes
@app.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get admin dashboard statistics
    stats = {
        'total_articles': NewsArticle.query.count(),
        'published_articles': NewsArticle.query.filter_by(is_published=True).count(),
        'breaking_news': NewsArticle.query.filter_by(is_breaking=True, is_published=True).count(),
        'total_subscribers': NewsSubscriber.query.filter_by(is_active=True).count(),
        'total_views': db.session.query(db.func.sum(NewsArticle.views_count)).scalar() or 0,
        'emails_sent': EmailLog.query.filter_by(status='sent').count(),
        'failed_emails': EmailLog.query.filter_by(status='failed').count()
    }
    
    # Get recent articles
    recent_articles = NewsArticle.query.order_by(NewsArticle.created_at.desc()).limit(10).all()
    
    # Get recent subscribers
    recent_subscribers = NewsSubscriber.query.order_by(NewsSubscriber.subscribed_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html', 
                         stats=stats,
                         recent_articles=recent_articles,
                         recent_subscribers=recent_subscribers)

@app.route('/admin/articles')
@login_required
def admin_articles():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    page = request.args.get('page', 1, type=int)
    articles = NewsArticle.query.order_by(NewsArticle.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('admin/articles.html', articles=articles)

@app.route('/admin/articles/new', methods=['GET', 'POST'])
@login_required
def admin_new_article():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        summary = request.form.get('summary', '').strip()
        category = request.form.get('category', 'General').strip()
        is_breaking = bool(request.form.get('is_breaking'))
        is_published = bool(request.form.get('is_published'))
        
        if not title or not content:
            flash('Title and content are required.', 'error')
            return render_template('admin/article_form.html')
        
        article = NewsArticle(
            title=title,
            content=content,
            summary=summary,
            category=category,
            is_breaking=is_breaking,
            is_published=is_published,
            author_id=current_user.id,
            published_at=datetime.utcnow() if is_published else None
        )
        
        try:
            db.session.add(article)
            db.session.commit()
            flash('Article created successfully!', 'success')
            return redirect(url_for('admin_articles'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to create article. Please try again.', 'error')
            logging.error(f"Article creation error: {str(e)}")
    
    return render_template('admin/article_form.html')

@app.route('/admin/articles/<int:article_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_article(article_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    article = NewsArticle.query.get_or_404(article_id)
    
    if request.method == 'POST':
        article.title = request.form.get('title', '').strip()
        article.content = request.form.get('content', '').strip()
        article.summary = request.form.get('summary', '').strip()
        article.category = request.form.get('category', 'General').strip()
        article.is_breaking = bool(request.form.get('is_breaking'))
        was_published = article.is_published
        article.is_published = bool(request.form.get('is_published'))
        
        # Set published_at if publishing for the first time
        if not was_published and article.is_published:
            article.published_at = datetime.utcnow()
        
        if not article.title or not article.content:
            flash('Title and content are required.', 'error')
            return render_template('admin/article_form.html', article=article)
        
        try:
            db.session.commit()
            flash('Article updated successfully!', 'success')
            return redirect(url_for('admin_articles'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to update article. Please try again.', 'error')
            logging.error(f"Article update error: {str(e)}")
    
    return render_template('admin/article_form.html', article=article)

@app.route('/admin/subscribers')
@login_required
def admin_subscribers():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    page = request.args.get('page', 1, type=int)
    subscribers = NewsSubscriber.query.order_by(NewsSubscriber.subscribed_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/subscribers.html', subscribers=subscribers)

@app.route('/admin/newsletter', methods=['GET', 'POST'])
@login_required
def admin_newsletter():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'send_newsletter':
            # Get recent published articles
            articles = NewsArticle.query.filter_by(is_published=True).order_by(
                NewsArticle.created_at.desc()
            ).limit(5).all()
            
            if not articles:
                flash('No articles available to send.', 'error')
                return render_template('admin/newsletter.html')
            
            sent_count, message = EmailService.send_newsletter(articles)
            flash(f'{message}', 'success' if sent_count > 0 else 'warning')
            
        elif action == 'send_test':
            test_email = request.form.get('test_email', '').strip()
            if not test_email:
                flash('Please enter a test email address.', 'error')
                return render_template('admin/newsletter.html')
            
            # Get recent published articles
            articles = NewsArticle.query.filter_by(is_published=True).order_by(
                NewsArticle.created_at.desc()
            ).limit(5).all()
            
            if not articles:
                flash('No articles available to send.', 'error')
                return render_template('admin/newsletter.html')
            
            sent_count, message = EmailService.send_newsletter(articles, test_email)
            flash(f'Test newsletter sent to {test_email}' if sent_count > 0 else 'Failed to send test newsletter', 
                  'success' if sent_count > 0 else 'error')
    
    # Get newsletter statistics
    stats = {
        'active_subscribers': NewsSubscriber.query.filter_by(is_active=True).count(),
        'recent_articles': NewsArticle.query.filter_by(is_published=True).count(),
        'emails_sent_today': EmailLog.query.filter(
            EmailLog.sent_at >= datetime.utcnow().date(),
            EmailLog.status == 'sent'
        ).count()
    }
    
    return render_template('admin/newsletter.html', stats=stats)

@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # Update site settings
        site_title = request.form.get('site_title', 'NewsFlash247')
        site_description = request.form.get('site_description', '')
        
        SiteSettings.set_setting('site_title', site_title, 'Website title')
        SiteSettings.set_setting('site_description', site_description, 'Website description')
        
        flash('Settings updated successfully!', 'success')
    
    # Get current settings
    settings = {
        'site_title': SiteSettings.get_setting('site_title', 'NewsFlash247'),
        'site_description': SiteSettings.get_setting('site_description', 'Your trusted source for breaking news')
    }
    
    return render_template('admin/settings.html', settings=settings)

# Initialize admin user and sample data
def init_database():
    with app.app_context():
        # Create admin user if none exists
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            admin_user = User(
                email='admin@newsflash247.com',
                first_name='Admin',
                last_name='User',
                is_admin=True
            )
            admin_user.set_password('admin123')
            
            try:
                db.session.add(admin_user)
                db.session.commit()
                logging.info("Admin user created: admin@newsflash247.com / admin123")
                
                # Create sample articles
                sample_articles = [
                    {
                        'title': 'Tech Innovation Summit 2025 Announces Breakthrough AI Developments',
                        'content': 'Leading technology companies unveiled groundbreaking artificial intelligence solutions at this year\'s summit, promising to revolutionize healthcare, education, and sustainable energy sectors. The innovations showcase practical applications that could transform how we interact with technology in our daily lives.',
                        'summary': 'Leading tech companies reveal groundbreaking AI solutions at the 2025 summit.',
                        'category': 'Technology',
                        'is_breaking': True,
                        'is_published': True
                    },
                    {
                        'title': 'Global Climate Initiative Reaches Historic Milestone',
                        'content': 'International cooperation efforts have successfully reduced carbon emissions by 15% this quarter, marking significant progress toward the 2030 sustainability goals. This achievement represents unprecedented collaboration between nations and demonstrates the effectiveness of coordinated environmental policies.',
                        'summary': 'International efforts reduce carbon emissions by 15% this quarter.',
                        'category': 'Environment',
                        'is_breaking': False,
                        'is_published': True
                    },
                    {
                        'title': 'Economic Markets Show Strong Recovery Signals',
                        'content': 'Financial analysts report positive trends across major stock exchanges, with renewable energy and healthcare sectors leading the growth trajectory. Market confidence continues to strengthen as investors respond to sustainable business practices and innovative healthcare solutions.',
                        'summary': 'Financial markets show positive trends with renewable energy leading growth.',
                        'category': 'Business',
                        'is_breaking': False,
                        'is_published': True
                    },
                    {
                        'title': 'Educational Reform Initiative Launches Nationwide',
                        'content': 'New educational programs focusing on digital literacy and critical thinking skills are being implemented across public schools, aiming to prepare students for the evolving job market. The comprehensive reform includes teacher training, curriculum updates, and technology integration.',
                        'summary': 'National education reform focuses on digital literacy and critical thinking.',
                        'category': 'Education',
                        'is_breaking': False,
                        'is_published': True
                    }
                ]
                
                for article_data in sample_articles:
                    article = NewsArticle(
                        title=article_data['title'],
                        content=article_data['content'],
                        summary=article_data['summary'],
                        category=article_data['category'],
                        is_breaking=article_data['is_breaking'],
                        is_published=article_data['is_published'],
                        author_id=admin_user.id,
                        published_at=datetime.utcnow()
                    )
                    db.session.add(article)
                
                db.session.commit()
                logging.info("Sample articles created")
                
            except Exception as e:
                db.session.rollback()
                logging.error(f"Failed to initialize database: {str(e)}")

# Initialize database on startup
init_database()

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
