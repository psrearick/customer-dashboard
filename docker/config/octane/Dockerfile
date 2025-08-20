FROM php:8.4-cli-bookworm

RUN apt-get update && apt-get install -y \
    git \
    zip \
    unzip \
    curl \
    supervisor \
    libpng-dev \
    libonig-dev \
    libxml2-dev \
    libzip-dev \
    libicu-dev \
    libpq-dev \
    libbrotli-dev \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

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

RUN pecl install redis swoole apcu xhprof \
    && docker-php-ext-enable redis swoole apcu xhprof

COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

WORKDIR /app

COPY docker/config/octane/octane.conf /usr/local/etc/php/conf.d/octane.ini
COPY docker/config/octane/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

COPY . /app

RUN if [ -f composer.json ]; then \
        composer install --no-dev --optimize-autoloader --no-scripts; \
        composer require laravel/octane spiral/roadrunner --no-scripts 2>/dev/null || true; \
        composer run-script post-autoload-dump 2>/dev/null || true; \
        php artisan octane:install --server=swoole --no-interaction 2>/dev/null || true; \
    fi

RUN if [ -d "/app/storage" ]; then \
        chown -R www-data:www-data /app/storage; \
        chmod -R 775 /app/storage; \
    fi \
    && if [ -d "/app/bootstrap/cache" ]; then \
        chown -R www-data:www-data /app/bootstrap/cache; \
        chmod -R 775 /app/bootstrap/cache; \
    fi

RUN chown -R www-data:www-data /app

RUN echo '#!/bin/bash\n\
php artisan config:cache\n\
php artisan route:cache\n\
php artisan view:cache\n\
exec php artisan octane:start --server=swoole --host=0.0.0.0 --port=8000 --workers=4 --task-workers=6 --max-requests=500' > /app/start-octane.sh \
    && chmod +x /app/start-octane.sh

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8000/status || exit 1

CMD ["/app/start-octane.sh"]
