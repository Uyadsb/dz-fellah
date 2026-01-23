# DZ-Fellah Deployment Guide - Railway (Docker)

This guide will help you deploy your DZ-Fellah Django API to Railway using Docker for your academic project.

## Prerequisites

- A GitHub account
- Your code pushed to a GitHub repository
- A Railway account (free tier available)
- Docker installed locally (for testing)

## Step-by-Step Deployment

### 1. Prepare Your Repository

First, make sure all deployment files are committed to your repository:

```bash
git add .
git commit -m "Add Railway deployment configuration"
git push origin main
```

### 2. Create a Railway Account

1. Go to [railway.app](https://railway.app)
2. Click "Login" and sign in with your GitHub account
3. Authorize Railway to access your repositories

### 3. Create a New Project

1. Click "New Project" on your Railway dashboard
2. Select "Deploy from GitHub repo"
3. Choose your `dz-fellah` repository
4. Railway will detect the Dockerfile and use it automatically for deployment

### 4. Add PostgreSQL Database

1. In your Railway project, click "New" → "Database" → "Add PostgreSQL"
2. Railway will automatically:
   - Create a PostgreSQL database
   - Generate a `DATABASE_URL` environment variable
   - Link it to your Django service

### 5. Configure Environment Variables

Click on your Django service, then go to "Variables" tab and add:

**Required Variables:**
```
SECRET_KEY=your-super-secret-key-change-this-to-something-random
DEBUG=False
```

**Optional Variables (Railway auto-provides DATABASE_URL):**
```
FRONTEND_URL=https://your-frontend-domain.com
```

**To generate a secure SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 6. Initialize Database Schema

After the first deployment, you need to set up your database schema:

1. Go to your Django service in Railway
2. Click on "Deployments" tab
3. Click on the latest deployment
4. Click "View Logs"
5. Once deployed, go to the service settings
6. Click on "Settings" → scroll to "Deploy"
7. You'll need to run custom commands via the Railway CLI or by modifying the start command temporarily

**Option A: Using Railway CLI (Recommended)**

Install Railway CLI:
```bash
npm i -g @railway/cli
```

Login and link to your project:
```bash
railway login
railway link
```

Run database setup commands:
```bash
railway run python manage.py setup_db
railway run python manage.py create_demo_data
```

**Option B: Via Web Interface**

Temporarily modify your `Procfile` to run setup commands:
```
web: python manage.py setup_db && python manage.py create_demo_data && python manage.py migrate && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

After first deployment, change it back to:
```
web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

### 7. Access Your Deployed API

1. Go to "Settings" tab in your Django service
2. Under "Domains", click "Generate Domain"
3. Railway will provide you with a URL like: `https://your-app-name.up.railway.app`
4. Your API will be available at: `https://your-app-name.up.railway.app/api/`

### 8. Test Your Deployment

Visit these endpoints to verify:
- Health check: `https://your-app-name.up.railway.app/api/`
- Products: `https://your-app-name.up.railway.app/api/products/`
- Register: `https://your-app-name.up.railway.app/api/auth/register/` (POST)

## API Documentation

Your Swagger documentation files are included:
- Main API: See `swagger.yaml`
- Cart/Orders: See `swagger_cart_order.yaml`

You can use tools like [Swagger Editor](https://editor.swagger.io/) to view them.

## Database Management

### View Database
```bash
railway run python manage.py dbshell
```

### Create Superuser
```bash
railway run python manage.py createsuperuser
```

### Clear Demo Data
```bash
railway run python manage.py clear_demo_data --yes
```

## Monitoring and Logs

### View Logs
1. Go to your service in Railway dashboard
2. Click "Deployments"
3. Click on the active deployment
4. View real-time logs

### Monitor Usage
Railway free tier includes:
- $5 monthly credit
- 500 hours of execution time
- 1GB RAM
- Shared CPU

Check your usage in the project "Settings" → "Usage"

## Custom Domain (Optional)

To use your own domain:
1. Go to "Settings" → "Domains"
2. Click "Custom Domain"
3. Enter your domain name
4. Add the CNAME record to your DNS provider

## Troubleshooting

### Deployment Fails

Check the logs for errors:
- Database connection issues: Verify `DATABASE_URL` is set
- Missing dependencies: Ensure `requirements.txt` is complete
- Static files: Ensure `collectstatic` runs successfully

### Database Connection Errors

Railway automatically provides `DATABASE_URL`. Make sure:
- PostgreSQL service is running
- Services are linked (go to PostgreSQL settings → "Connect" → link to Django service)

### Static Files Not Loading

Ensure WhiteNoise is installed and configured (already done in `settings.py`):
- WhiteNoise is in `MIDDLEWARE`
- `STATICFILES_STORAGE` is set
- `collectstatic` runs before `gunicorn` in `Procfile`

### CORS Errors

Add your frontend URL to environment variables:
```
FRONTEND_URL=https://your-frontend-domain.com
```

## Environment Files Reference

### .env.example (Local Development)
```env
SECRET_KEY=your-local-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=dzfellah
DB_USER=postgres
DB_PASSWORD=amdjed
DB_HOST=dzfellah-db
DB_PORT=5432
```

### Railway Environment Variables (Production)
```
SECRET_KEY=<generate-random-key>
DEBUG=False
DATABASE_URL=<auto-provided-by-railway>
RAILWAY_STATIC_URL=<auto-provided-by-railway>
RAILWAY_PUBLIC_DOMAIN=<auto-provided-by-railway>
```

## Cost Optimization Tips

For academic projects on Railway's free tier:
1. Use the $5 monthly credit wisely
2. Stop services when not actively demonstrating
3. Monitor usage regularly
4. Consider using Railway's sleep mode for non-active hours

## Academic Presentation Tips

For showcasing to professors/reviewers:
1. Share your Railway URL in documentation
2. Keep demo data populated for easy testing
3. Share API credentials in your presentation materials
4. Use Swagger/OpenAPI docs to demonstrate endpoints
5. Monitor logs during live demonstrations

## Useful Commands

```bash
# Check deployment status
railway status

# View logs
railway logs

# Open database shell
railway run python manage.py dbshell

# Run migrations
railway run python manage.py migrate

# Create superuser
railway run python manage.py createsuperuser

# SSH into container (for debugging)
railway shell
```

## Support Resources

- Railway Documentation: https://docs.railway.app/
- Railway Discord: https://discord.gg/railway
- Django Documentation: https://docs.djangoproject.com/
- DRF Documentation: https://www.django-rest-framework.org/

## Next Steps

After deployment:
1. Test all API endpoints
2. Verify database operations
3. Check user authentication (register/login)
4. Test product CRUD operations
5. Verify cart and order functionality
6. Share the API URL with your team/professor

## Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` generated
- [ ] Database credentials are secure (managed by Railway)
- [ ] CORS configured properly
- [ ] HTTPS enabled (automatic on Railway)
- [ ] No sensitive data in repository
- [ ] `.env` files are in `.gitignore`

---

**Congratulations!** Your DZ-Fellah API is now deployed and ready for your academic project demonstration.

For questions or issues, refer to the main `readme.md` file or Railway's documentation.
