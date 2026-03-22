# Everest Cakes - Django E-Commerce Platform

A production-ready, responsive e-commerce platform for a bakery built with Django 5, HTMX, and Django Unfold.

## 🚀 Features

- **Modern Admin Interface** - Django Unfold with custom styling and dashboard
- **HTMX Integration** - Dynamic updates without full page reloads
- **Animated Hero Sections** - Fully configurable from admin panel
- **Featured Cards** - Animated cards controlled from admin
- **Product Management** - Categories, variants, reviews, tags
- **Shopping Cart** - Session-based cart with HTMX updates
- **Order Management** - Cash/COD and M-Pesa payment support
- **Import/Export** - CSV/Excel import/export for products and orders
- **Social Sharing** - Facebook, Twitter, WhatsApp, Pinterest sharing
- **SEO Optimized** - Meta tags, sitemaps, structured data
- **Blog System** - Posts, categories, comments
- **Responsive Design** - Mobile-first Tailwind CSS

## 📁 Project Structure

```
everest_cakes/
├── config/              # Project settings
├── apps/
│   ├── core/           # User model, site settings, pages
│   ├── products/       # Products, categories, reviews
│   ├── cart/           # Shopping cart
│   ├── orders/         # Orders, payments
│   └── blog/           # Blog posts
├── templates/          # All HTML templates
├── static/             # CSS, JS, images
├── media/              # User uploaded files
└── requirements.txt    # Python dependencies
```

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/everest-cakes.git
   cd everest-cakes
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the site**
   - Frontend: http://localhost:8000
   - Admin: http://localhost:8000/admin

## 📱 Features in Detail

### Admin Panel
- Custom dashboard with order statistics
- Product management with variants and reviews
- Order management with status tracking
- Hero sections and featured cards configuration
- Import/Export functionality

### E-Commerce
- Product catalog with categories
- Product variants (sizes, weights)
- Customer reviews and ratings
- Shopping cart with HTMX updates
- Cash on Delivery and M-Pesa payments
- Order tracking

### Content Management
- CMS pages (About, Terms, Privacy)
- Blog with categories and comments
- Testimonials
- SEO meta tags

## 🔧 Configuration

### M-Pesa Integration
1. Register on [Safaricom Developer Portal](https://developer.safaricom.co.ke)
2. Create an app and get credentials
3. Add credentials to `.env`:
   ```
   MPESA_CONSUMER_KEY=your-key
   MPESA_CONSUMER_SECRET=your-secret
   MPESA_PASSKEY=your-passkey
   MPESA_SHORTCODE=your-shortcode
   ```

### WhatsApp Integration
1. Set up [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)
2. Add credentials to `.env`:
   ```
   WHATSAPP_PHONE_NUMBER_ID=your-id
   WHATSAPP_ACCESS_TOKEN=your-token
   ```

## 🚀 Deployment

### Using Gunicorn
```bash
gunicorn config.wsgi:application
```

### Using Docker
```bash
docker build -t everest-cakes .
docker run -p 8000:8000 everest-cakes
```

## 📄 License

This project is licensed under the MIT License.

## 👥 Support

For support, email info@everestcakes.com or WhatsApp +254 700 000 000.
