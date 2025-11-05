# Render Deployment - Quick Start Guide

## 🚀 Quick Deployment Steps

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### Step 2: Deploy on Render

#### Option A: Using Blueprint (Easiest)
1. Go to https://dashboard.render.com
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Render will detect `render.yaml` automatically
5. Click "Apply" and wait for deployment

#### Option B: Manual Setup
Follow the detailed guide in `DEPLOYMENT.md`

---

## 📋 Environment Variables to Set in Render Dashboard

After deployment, go to your Web Service → "Environment" and add/verify these:

### ✅ Required (Auto-set by Render)
- `DATABASE_URL` - Auto-set when database is linked
- `REDIS_URL` - Auto-set when Redis is linked
- `CELERY_BROKER_URL` - Same as REDIS_URL
- `CELERY_RESULT_BACKEND` - Same as REDIS_URL

### ✅ Required (You Must Set)
1. **SECRET_KEY**
   - Click "Generate" in Render dashboard
   - Or generate locally:
     ```python
     python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
     ```

2. **ALLOWED_HOSTS**
   - Value: `your-service-name.onrender.com`
   - Replace `your-service-name` with your actual service name

3. **CORS_ALLOWED_ORIGINS**
   - Value: `https://your-frontend-domain.com`
   - Add your frontend URL (comma-separated if multiple)

### ⚙️ Optional (Set if Needed)
- `USE_CLOUDINARY` = `True` (if using Cloudinary)
- `CLOUDINARY_CLOUD_NAME` = (from Cloudinary dashboard)
- `CLOUDINARY_API_KEY` = (from Cloudinary dashboard)
- `CLOUDINARY_API_SECRET` = (from Cloudinary dashboard)
- `EMAIL_HOST_USER` = (your email)
- `EMAIL_HOST_PASSWORD` = (your email app password)
- `SENTRY_DSN` = (from Sentry dashboard)

---

## 🗄️ Enable PostGIS Extension

**IMPORTANT**: After database is created, enable PostGIS:

1. Go to your Database dashboard → "Connect"
2. Click "psql" or use any PostgreSQL client
3. Run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS postgis;
   CREATE EXTENSION IF NOT EXISTS postgis_topology;
   ```
4. Verify:
   ```sql
   SELECT PostGIS_version();
   ```

---

## ✅ Post-Deployment Checklist

- [ ] Database migrations completed (check build logs)
- [ ] PostGIS extension enabled
- [ ] Environment variables set correctly
- [ ] Static files collected (check build logs)
- [ ] Service is running (check "Events" tab)
- [ ] API docs accessible: `https://your-service.onrender.com/api/docs/`
- [ ] Create superuser (in Shell):
  ```bash
  python manage.py createsuperuser
  ```

---

## 🔍 Troubleshooting

### Service won't start
- Check "Logs" tab for errors
- Verify all required environment variables are set
- Check "Events" tab for build errors

### Database connection errors
- Verify `DATABASE_URL` is set
- Ensure database and web service are in same region
- Use Internal Database URL (not External)

### PostGIS errors
- Ensure PostGIS extension is enabled (see above)
- Check database logs

### Static files not loading
- Check build logs for `collectstatic` output
- Verify `STATIC_ROOT` is set correctly

---

## 📞 Need Help?

1. Check `DEPLOYMENT.md` for detailed instructions
2. Check Render logs: Service Dashboard → "Logs"
3. Check build logs: Service Dashboard → "Events"

---

**That's it! Your backend should be live at:**
`https://your-service-name.onrender.com`

**API Documentation:**
`https://your-service-name.onrender.com/api/docs/`

