#!/usr/bin/env bash
# Post-deployment script for Render
# This script runs after the build to set up the database and initial data

set -o errexit  # Exit on error

echo "🚀 Running post-deployment tasks..."

# Enable PostGIS extension
echo "🗺️  Enabling PostGIS extension..."
python manage.py shell << EOF
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
    cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis_topology;")
    print("✅ PostGIS extensions enabled")
EOF

# Create default roles if they don't exist
echo "👥 Creating default roles..."
python manage.py create_default_roles || echo "⚠️  Default roles command not found or failed"

# Optional: Create test data (uncomment if needed)
# echo "🌱 Creating test data..."
# python manage.py create_test_data || echo "⚠️  Test data creation failed"

echo "✅ Post-deployment tasks completed!"

