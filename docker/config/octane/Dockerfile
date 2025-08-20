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

COPY docker/config/php/conf.d /usr/local/etc/php/conf.d
COPY docker/config/octane/php/conf.d /usr/local/etc/php/conf.d

COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

WORKDIR /var/www/html
COPY docker/config/octane/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

COPY . /var/www/html

RUN if [ -f composer.json ]; then \
        composer install --no-dev --optimize-autoloader --no-scripts; \
        composer require laravel/octane spiral/roadrunner --no-scripts 2>/dev/null || true; \
        composer run-script post-autoload-dump 2>/dev/null || true; \
        php artisan octane:install --server=swoole --no-interaction 2>/dev/null || true; \
    fi

RUN if [ -d "/var/www/html/storage" ]; then \
        chown -R www-data:www-data /var/www/html/storage; \
        chmod -R 775 /var/www/html/storage; \
    fi \
    && if [ -d "/var/www/html/bootstrap/cache" ]; then \
        chown -R www-data:www-data /var/www/html/bootstrap/cache; \
        chmod -R 775 /var/www/html/bootstrap/cache; \
    fi

RUN chown -R www-data:www-data /var/www/html

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8000/status || exit 1

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
