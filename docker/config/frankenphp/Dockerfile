FROM dunglas/frankenphp:1-php8.4-bookworm

# System dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    libpng-dev \
    libonig-dev \
    libxml2-dev \
    zip \
    unzip \
    libzip-dev \
    libicu-dev \
    libpq-dev \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

# PHP extensions for performance and profiling
RUN docker-php-ext-install \
    bcmath \
    fileinfo \
    mbstring \
    pdo_mysql \
    xml \
    zip \
    intl \
    pcntl \
    opcache

# PECL extensions
RUN pecl install redis xdebug apcu xhprof \
    && docker-php-ext-enable redis xdebug apcu xhprof

# Blackfire
RUN version=$(php -r "echo PHP_MAJOR_VERSION.PHP_MINOR_VERSION;") \
    && architecture=$(uname -m) \
    && curl -A "Docker" -o /tmp/blackfire-probe.tar.gz -D - -L -s https://blackfire.io/api/v1/releases/probe/php/linux/$architecture/$version \
    && mkdir -p /tmp/blackfire \
    && tar zxpf /tmp/blackfire-probe.tar.gz -C /tmp/blackfire \
    && mv /tmp/blackfire/blackfire-*.so $(php -r "echo ini_get ('extension_dir');")/blackfire.so \
    && rm -rf /tmp/blackfire /tmp/blackfire-probe.tar.gz

COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

WORKDIR /var/www/html

# Configuration files
COPY docker/config/php/conf.d/performance.ini /usr/local/etc/php/conf.d/
COPY docker/config/php/conf.d/xdebug.ini /usr/local/etc/php/conf.d/
COPY docker/config/php/conf.d/opcache.ini /usr/local/etc/php/conf.d/
COPY docker/config/php/conf.d/pdo_mysql.ini /usr/local/etc/php/conf.d/
COPY docker/config/php/conf.d/docker-php-ext-redis.ini /usr/local/etc/php/conf.d/
COPY docker/config/frankenphp/Caddyfile /etc/caddy/Caddyfile

# Application files
COPY . /var/www/html

RUN if [ -f composer.json ]; then \
        composer install --no-dev --optimize-autoloader --no-scripts; \
        composer run-script post-autoload-dump 2>/dev/null || true; \
    fi

# Set permissions for Laravel directories
RUN if [ -d "/var/www/html/storage" ]; then \
        chown -R www-data:www-data /var/www/html/storage; \
        chmod -R 775 /var/www/html/storage; \
    fi \
    && if [ -d "/var/www/html/bootstrap/cache" ]; then \
        chown -R www-data:www-data /var/www/html/bootstrap/cache; \
        chmod -R 775 /var/www/html/bootstrap/cache; \
    fi

RUN chown -R www-data:www-data /var/www/html

EXPOSE 80 443

CMD ["frankenphp", "run", "--config", "/etc/caddy/Caddyfile"]