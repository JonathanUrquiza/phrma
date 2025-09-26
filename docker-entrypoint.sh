#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Django application...${NC}"

# Wait for database to be ready
echo -e "${YELLOW}⏳ Waiting for database...${NC}"
python manage.py check --database default

# Run migrations
echo -e "${YELLOW}📦 Running database migrations...${NC}"
python manage.py migrate --noinput

# Create superuser if it doesn't exist (only in development)
if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ] && [ "$DJANGO_SUPERUSER_EMAIL" ]; then
    echo -e "${YELLOW}👤 Creating superuser...${NC}"
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
" || echo -e "${YELLOW}⚠️ Superuser creation skipped${NC}"
fi

# Collect static files (in case they weren't collected during build)
echo -e "${YELLOW}📦 Collecting static files...${NC}"
python manage.py collectstatic --noinput --clear

echo -e "${GREEN}✅ Django application is ready!${NC}"

# Execute the command passed as arguments
exec "$@"
