#!/usr/bin/env bash
# Render build script for Farmetrics Django backend
set -o errexit  # Exit on error

echo "🔨 Starting build process..."

# Install GDAL and PostGIS dependencies
echo "📦 Installing system dependencies..."
apt-get update
apt-get install -y gdal-bin libgdal-dev python3-dev build-essential

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements/production.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p staticfiles
mkdir -p logs

# Collect static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "🗄️  Running database migrations..."
python manage.py migrate --noinput

echo "✅ Build completed successfully!"

