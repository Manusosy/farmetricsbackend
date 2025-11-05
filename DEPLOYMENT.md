# Farmetrics Backend - Render Deployment Guide

This guide will walk you through deploying the Farmetrics Django backend to Render.

## Prerequisites

- A GitHub account with your code pushed to a repository
- A Render account (sign up at https://render.com)
- (Optional) Cloudinary account for media storage
- (Optional) Sentry account for error tracking

---

## Step 1: Prepare Your Repository

1. **Ensure all changes are committed and pushed to GitHub:**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Verify your repository structure:**
   - Make sure `render.yaml` is in the `backend/` directory
   - Ensure `requirements/production.txt` exists
   - Check that `manage.py` is in the `backend/` directory

---

## Step 2: Create Services on Render

### Option A: Using render.yaml (Recommended - Automated Setup)

1. **Go to Render Dashboard:**
   - Navigate to https://dashboard.render.com
   - Click "New +" → "Blueprint"

2. **Connect Your Repository:**
   - Select your GitHub repository
   - Render will detect `render.yaml` automatically
   - Click "Apply"

3. **Review and Confirm:**
   - Render will create 3 services:
     - `farmetrics-backend` (Web Service)
     - `farmetrics-db` (PostgreSQL Database)
     - `farmetrics-redis` (Redis Cache)
   - Review the configuration and click "Apply"

### Option B: Manual Setup (If Blueprint doesn't work)

#### 2.1 Create PostgreSQL Database

1. Go to Render Dashboard → "New +" → "PostgreSQL"
2. Configure:
   - **Name**: `farmetrics-db`
   - **Database**: `farmetrics_db`
   - **User**: `farmetrics_user`
   - **Region**: Choose closest to your users (e.g., Oregon)
   - **PostgreSQL Version**: 15
   - **Plan**: Starter (upgrade later if needed)
3. Click "Create Database"
4. **IMPORTANT**: After creation, go to the database dashboard → "Connect" → Copy the **Internal Database URL** (you'll need this)

#### 2.2 Enable PostGIS Extension

1. Go to your database dashboard
2. Click "Connect" → "psql" (or use any PostgreSQL client)
3. Run this SQL command:
   ```sql
   CREATE EXTENSION IF NOT EXISTS postgis;
   CREATE EXTENSION IF NOT EXISTS postgis_topology;
   ```
4. Verify it worked:
   ```sql
   SELECT PostGIS_version();
   ```

#### 2.3 Create Redis Instance

1. Go to Render Dashboard → "New +" → "Redis"
2. Configure:
   - **Name**: `farmetrics-redis`
   - **Region**: Same as database
   - **Plan**: Starter
3. Click "Create Redis"
4. Copy the **Internal Redis URL** from the dashboard

#### 2.4 Create Web Service

1. Go to Render Dashboard → "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure the service:

   **Basic Settings:**
   - **Name**: `farmetrics-backend`
   - **Region**: Same as database
   - **Branch**: `main` (or your main branch)
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install --upgrade pip && pip install -r requirements/production.txt && python manage.py collectstatic --noinput
     ```
   - **Start Command**:
     ```bash
     gunicorn farmetrics.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
     ```

---

## Step 3: Configure Environment Variables

Go to your Web Service dashboard → "Environment" tab and add these variables:

### Required Variables

1. **DJANGO_ENVIRONMENT**
   - Value: `production`

2. **DJANGO_SETTINGS_MODULE**
   - Value: `farmetrics.settings.production`

3. **SECRET_KEY**
   - **IMPORTANT**: Generate a strong secret key
   - You can generate one using:
     ```python
     python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
     ```
   - Or use Render's "Generate" button next to the field
   - **Copy this value** - you'll need it later

4. **DEBUG**
   - Value: `False`

5. **ALLOWED_HOSTS**
   - Value: `your-service-name.onrender.com` (replace with your actual service name)
   - Add your custom domain if you have one: `your-service-name.onrender.com,yourdomain.com`

6. **DATABASE_URL**
   - **This should be auto-set** if you linked the database
   - If not, go to your database dashboard → "Connect" → Copy "Internal Database URL"
   - Format: `postgresql://user:password@host:port/dbname`

7. **REDIS_URL**
   - Go to Redis dashboard → Copy "Internal Redis URL"
   - Format: `redis://:password@host:port`

8. **CELERY_BROKER_URL**
   - Same as REDIS_URL: `redis://:password@host:port`

9. **CELERY_RESULT_BACKEND**
   - Same as REDIS_URL: `redis://:password@host:port`

10. **CORS_ALLOWED_ORIGINS**
    - Value: `https://your-frontend-domain.com` (replace with your frontend URL)
    - For local testing: `http://localhost:3000,https://your-frontend-domain.com`

### Optional Variables (Set as needed)

11. **USE_CLOUDINARY**
    - Value: `True` (if using Cloudinary for media)

12. **CLOUDINARY_CLOUD_NAME**
    - Get from Cloudinary dashboard

13. **CLOUDINARY_API_KEY**
    - Get from Cloudinary dashboard

14. **CLOUDINARY_API_SECRET**
    - Get from Cloudinary dashboard

15. **EMAIL_HOST**
    - Value: `smtp.gmail.com` (or your SMTP server)

16. **EMAIL_PORT**
    - Value: `587`

17. **EMAIL_USE_TLS**
    - Value: `True`

18. **EMAIL_HOST_USER**
    - Your email address

19. **EMAIL_HOST_PASSWORD**
    - Your email app password (not regular password)

20. **DEFAULT_FROM_EMAIL**
    - Value: `noreply@farmetrics.com`

21. **SENTRY_DSN**
    - Get from Sentry dashboard (if using Sentry)

22. **ENVIRONMENT**
    - Value: `production`

---

## Step 4: Run Database Migrations

After the first deployment:

1. Go to your Web Service dashboard
2. Click "Shell" (or use "Manual Deploy" → "Run Shell Command")
3. Run:
   ```bash
   python manage.py migrate
   ```
4. (Optional) Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```
5. (Optional) Create default roles:
   ```bash
   python manage.py create_default_roles
   ```

---

## Step 5: Verify Deployment

1. **Check Logs:**
   - Go to your Web Service dashboard → "Logs" tab
   - Look for "🚀 Running in PRODUCTION mode"
   - Check for any errors

2. **Test Endpoints:**
   - Health check: `https://your-service-name.onrender.com/api/docs/`
   - API docs should load at `/api/docs/`

3. **Test Database Connection:**
   - In the shell, run:
     ```bash
     python manage.py dbshell
     ```
   - This should connect to your PostgreSQL database

---

## Step 6: Post-Deployment Checklist

- [ ] Database migrations completed successfully
- [ ] Static files collected (check logs for "Collecting static files")
- [ ] PostGIS extension enabled in database
- [ ] Environment variables set correctly
- [ ] CORS origins configured for your frontend
- [ ] Superuser created (if needed)
- [ ] Default roles created (if needed)
- [ ] API documentation accessible at `/api/docs/`
- [ ] Test API endpoint (e.g., `/api/v1/auth/login/`)

---

## Troubleshooting

### Issue: "No module named 'django.contrib.gis'"

**Solution**: Ensure PostGIS libraries are available. Render's PostgreSQL includes PostGIS, but if you see this error, check that you're using the correct database URL.

### Issue: "Connection refused" to database

**Solution**: 
- Use the **Internal Database URL** (not External) for the DATABASE_URL
- Ensure the database and web service are in the same region

### Issue: Static files not loading

**Solution**:
- Check that `collectstatic` ran successfully in build logs
- Verify `STATIC_ROOT` is set correctly
- Ensure WhiteNoise middleware is in `MIDDLEWARE`

### Issue: "ALLOWED_HOSTS" error

**Solution**:
- Add your Render service URL to ALLOWED_HOSTS
- Format: `your-service-name.onrender.com`

### Issue: CORS errors from frontend

**Solution**:
- Add your frontend URL to `CORS_ALLOWED_ORIGINS`
- Include protocol: `https://your-frontend.com` (not just `your-frontend.com`)

### Issue: Database migrations fail

**Solution**:
- Ensure PostGIS extension is enabled (see Step 2.2)
- Check database permissions
- Verify DATABASE_URL is correct

---

## Environment Variables Reference

Copy this list and fill in the values in Render:

```
DJANGO_ENVIRONMENT=production
DJANGO_SETTINGS_MODULE=farmetrics.settings.production
SECRET_KEY=<generate-strong-key>
DEBUG=False
ALLOWED_HOSTS=your-service-name.onrender.com
DATABASE_URL=<auto-set-by-render>
REDIS_URL=<from-redis-dashboard>
CELERY_BROKER_URL=<same-as-redis-url>
CELERY_RESULT_BACKEND=<same-as-redis-url>
CORS_ALLOWED_ORIGINS=https://your-frontend.com
USE_CLOUDINARY=True
CLOUDINARY_CLOUD_NAME=<your-cloud-name>
CLOUDINARY_API_KEY=<your-api-key>
CLOUDINARY_API_SECRET=<your-api-secret>
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<your-email>
EMAIL_HOST_PASSWORD=<your-app-password>
DEFAULT_FROM_EMAIL=noreply@farmetrics.com
ENVIRONMENT=production
```

---

## Next Steps

1. **Set up Custom Domain** (optional):
   - Go to your service → "Settings" → "Custom Domains"
   - Add your domain and configure DNS

2. **Set up Monitoring** (recommended):
   - Configure Sentry for error tracking
   - Set up Render's built-in monitoring

3. **Set up SSL**:
   - Render provides SSL automatically for `.onrender.com` domains
   - For custom domains, configure in "Custom Domains" section

4. **Scale Resources** (as needed):
   - Upgrade database plan if needed
   - Increase Redis memory if needed
   - Scale web service workers if needed

---

## Support

If you encounter issues:
1. Check Render logs: Service Dashboard → "Logs"
2. Check build logs for errors during deployment
3. Verify all environment variables are set correctly
4. Ensure PostGIS extension is enabled in database

---

**Last Updated**: Current  
**Version**: 1.0.0  
**Status**: Ready for Deployment 🚀

