// NewsFlash247 JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Form validation enhancements
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Newsletter subscription form enhancement
    const subscribeForm = document.querySelector('form[action*="subscribe"]');
    if (subscribeForm) {
        subscribeForm.addEventListener('submit', function(event) {
            const emailInput = this.querySelector('input[type="email"]');
            const submitBtn = this.querySelector('button[type="submit"]');
            
            if (emailInput && emailInput.value && emailInput.checkValidity()) {
                // Add loading state
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Subscribing...';
                submitBtn.disabled = true;
                
                // Re-enable after form submission (handled by page reload)
                setTimeout(function() {
                    if (submitBtn) {
                        submitBtn.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Subscribe';
                        submitBtn.disabled = false;
                    }
                }, 3000);
            }
        });
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add reading time estimation
    const newsCards = document.querySelectorAll('.news-card');
    newsCards.forEach(function(card) {
        const content = card.querySelector('.card-text');
        if (content) {
            const wordCount = content.textContent.split(/\s+/).length;
            const readingTime = Math.ceil(wordCount / 200); // Average reading speed
            const timeElement = card.querySelector('.fa-eye')?.parentElement;
            if (timeElement) {
                timeElement.innerHTML = `<i class="fas fa-clock me-1"></i>~${readingTime} min read`;
            }
        }
    });

    // Share functionality (placeholder)
    document.querySelectorAll('.btn-outline-primary').forEach(function(shareBtn) {
        if (shareBtn.textContent.includes('Share')) {
            shareBtn.addEventListener('click', function(e) {
                e.preventDefault();
                if (navigator.share) {
                    const card = this.closest('.news-card');
                    const title = card.querySelector('.card-title').textContent;
                    const text = card.querySelector('.card-text').textContent;
                    
                    navigator.share({
                        title: title,
                        text: text,
                        url: window.location.href
                    });
                } else {
                    // Fallback: copy to clipboard
                    navigator.clipboard.writeText(window.location.href).then(function() {
                        // Show toast or alert
                        const toast = document.createElement('div');
                        toast.className = 'alert alert-success position-fixed top-0 end-0 m-3';
                        toast.innerHTML = '<i class="fas fa-check me-2"></i>Link copied to clipboard!';
                        document.body.appendChild(toast);
                        
                        setTimeout(function() {
                            toast.remove();
                        }, 3000);
                    });
                }
            });
        }
    });

    // Password strength indicator (for registration)
    const passwordInput = document.querySelector('#password');
    const confirmPasswordInput = document.querySelector('#confirm_password');
    
    if (passwordInput && confirmPasswordInput) {
        function checkPasswordMatch() {
            if (confirmPasswordInput.value && passwordInput.value !== confirmPasswordInput.value) {
                confirmPasswordInput.setCustomValidity('Passwords do not match');
                confirmPasswordInput.classList.add('is-invalid');
            } else {
                confirmPasswordInput.setCustomValidity('');
                confirmPasswordInput.classList.remove('is-invalid');
                if (confirmPasswordInput.value) {
                    confirmPasswordInput.classList.add('is-valid');
                }
            }
        }
        
        passwordInput.addEventListener('input', checkPasswordMatch);
        confirmPasswordInput.addEventListener('input', checkPasswordMatch);
    }

    // Dynamic news loading (placeholder for future enhancement)
    let newsOffset = 0;
    const loadMoreBtn = document.querySelector('#load-more-news');
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', function() {
            // This would typically make an AJAX request to load more news
            // For now, just show a message
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';
            this.disabled = true;
            
            setTimeout(() => {
                this.innerHTML = '<i class="fas fa-plus me-2"></i>Load More';
                this.disabled = false;
            }, 1000);
        });
    }

    // Theme toggle (for future enhancement)
    const themeToggle = document.querySelector('#theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }

    // Load saved theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.documentElement.setAttribute('data-bs-theme', savedTheme);
    }

    // Back to top button
    const backToTopBtn = document.createElement('button');
    backToTopBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
    backToTopBtn.className = 'btn btn-primary position-fixed bottom-0 end-0 m-3 rounded-circle';
    backToTopBtn.style.display = 'none';
    backToTopBtn.style.zIndex = '1000';
    backToTopBtn.setAttribute('aria-label', 'Back to top');
    document.body.appendChild(backToTopBtn);

    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopBtn.style.display = 'block';
        } else {
            backToTopBtn.style.display = 'none';
        }
    });

    backToTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // Console welcome message
    console.log('%cWelcome to NewsFlash247!', 'color: #0d6efd; font-size: 16px; font-weight: bold;');
    console.log('Stay informed with the latest news and updates.');
});

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction() {
        const context = this;
        const args = arguments;
        const later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
});
