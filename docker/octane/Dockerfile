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
    zip \
    unzip \
    default-mysql-client \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Install PHP extensions for Laravel and Octane
RUN docker-php-ext-install \
    bcmath \
    ctype \
    fileinfo \
    mbstring \
    pdo_mysql \
    tokenizer \
    xml \
    zip \
    intl \
    pcntl \
    sockets

# Install and configure OPcache for CLI
RUN docker-php-ext-install opcache

# Install Redis extension
RUN pecl install redis && docker-php-ext-enable redis

# Install Swoole extension for Octane
RUN pecl install swoole && docker-php-ext-enable swoole

# Install additional performance extensions
RUN pecl install apcu && docker-php-ext-enable apcu

# Install XHProf for profiling
RUN pecl install xhprof && docker-php-ext-enable xhprof

# Get Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# Set working directory
WORKDIR /app

# Copy application files
COPY . /app

# Install Composer dependencies with Octane
RUN composer install --no-dev --optimize-autoloader
RUN composer require laravel/octane spiral/roadrunner

# Copy custom PHP configuration optimized for Octane
COPY docker/php/conf.d/performance.ini /usr/local/etc/php/conf.d/
COPY docker/php/conf.d/opcache.ini /usr/local/etc/php/conf.d/

# Copy Octane-specific configuration
COPY docker/octane/octane.conf /usr/local/etc/php/conf.d/octane.ini
COPY docker/octane/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Set permissions
RUN chown -R www-data:www-data /app/storage /app/bootstrap/cache
RUN chmod -R 775 /app/storage /app/bootstrap/cache

# Install Octane server
RUN php artisan octane:install --server=swoole

# Create startup script
RUN echo '#!/bin/bash\n\
php artisan config:cache\n\
php artisan route:cache\n\
php artisan view:cache\n\
exec php artisan octane:start --server=swoole --host=0.0.0.0 --port=8000 --workers=4 --task-workers=6 --max-requests=500' > /app/start-octane.sh
RUN chmod +x /app/start-octane.sh

# Expose port 8000
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["/app/start-octane.sh"]