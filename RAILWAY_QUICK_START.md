# Railway Deployment - Quick Start (Docker)

## Fast Track Deployment (5 minutes)

### 0. Test Locally First (Optional)
```bash
# Build and run with Docker
docker-compose up --build

# Test: http://localhost:8000/api/products/
```

### 1. Push to GitHub
```bash
git add .
git commit -m "Add Railway deployment configuration with Docker"
git push origin main
```

### 2. Deploy on Railway

1. Go to [railway.app](https://railway.app) and login with GitHub
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your `dz-fellah` repository
4. Railway will automatically detect your `Dockerfile` and `railway.json`
5. Click "Add PostgreSQL" database to add a database service

### 3. Configure Environment Variables

Click on your Django service → "Variables" → Add:

```
SECRET_KEY=<generate-random-key>
DEBUG=False
```

**Generate SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Note:** Railway automatically provides `DATABASE_URL` when you add PostgreSQL - no need to manually set DB variables!

### 4. Get Your URL
- Go to "Settings" → "Domains" → "Generate Domain"
- Your API: `https://your-app.up.railway.app/api/`

### 5. Setup Database (One-time)

Install Railway CLI:
```bash
npm i -g @railway/cli
railway login
railway link
```

Initialize database schema and demo data:
```bash
railway run python manage.py setup_db
railway run python manage.py create_demo_data
```

### Done!
Test your API: `https://your-app.up.railway.app/api/products/`

---

## Local Development with Docker

**Development mode (with hot reload):**
```bash
docker-compose up
```

**Production-like mode:**
```bash
docker-compose -f docker-compose.prod.yaml up --build
```

---

For detailed instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md)
