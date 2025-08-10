FROM php:8.4-cli-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    libpng-dev \
    libonig-dev \
    libxml2-dev \
    libzip-dev \
    libicu-dev \
    libpq-dev \
    libbrotli-dev \
    zip \
    unzip \
    default-mysql-client \
    supervisor \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install PHP extensions for Laravel and Octane
RUN docker-php-ext-install \
    bcmath \
    fileinfo \
    mbstring \
    pdo_mysql \
    xml \
    zip \
    intl \
    pcntl \
    sockets \
    opcache

# Install PECL extensions including Swoole for Octane
RUN pecl install redis swoole apcu xhprof \
    && docker-php-ext-enable redis swoole apcu xhprof

# Get Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# Set working directory
WORKDIR /app

# Copy configuration files first
COPY docker/php/conf.d/performance.ini /usr/local/etc/php/conf.d/
COPY docker/php/conf.d/opcache.ini /usr/local/etc/php/conf.d/
COPY docker/octane/octane.conf /usr/local/etc/php/conf.d/octane.ini
COPY docker/octane/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copy application files
COPY . /app

# Install composer dependencies and Octane if composer.json exists
RUN if [ -f composer.json ]; then \
        composer install --no-dev --optimize-autoloader --no-scripts; \
        composer require laravel/octane spiral/roadrunner --no-scripts 2>/dev/null || true; \
        composer run-script post-autoload-dump 2>/dev/null || true; \
        php artisan octane:install --server=swoole --no-interaction 2>/dev/null || true; \
    fi

# Install npm dependencies and build assets if package.json exists
RUN if [ -f package.json ]; then \
        npm ci --only=production; \
        npm run build; \
    fi

# Set permissions for Laravel directories if they exist
RUN if [ -d "/app/storage" ]; then \
        chown -R www-data:www-data /app/storage; \
        chmod -R 775 /app/storage; \
    fi \
    && if [ -d "/app/bootstrap/cache" ]; then \
        chown -R www-data:www-data /app/bootstrap/cache; \
        chmod -R 775 /app/bootstrap/cache; \
    fi

# Ensure proper ownership of all files
RUN chown -R www-data:www-data /app

# Create startup script
RUN echo '#!/bin/bash\n\
php artisan config:cache\n\
php artisan route:cache\n\
php artisan view:cache\n\
exec php artisan octane:start --server=swoole --host=0.0.0.0 --port=8000 --workers=4 --task-workers=6 --max-requests=500' > /app/start-octane.sh \
    && chmod +x /app/start-octane.sh

# Expose port 8000
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["/app/start-octane.sh"]