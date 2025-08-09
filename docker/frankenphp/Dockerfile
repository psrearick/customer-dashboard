FROM dunglas/frankenphp:1-php8.4-bookworm

# Install system dependencies
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

# Install PHP extensions for performance and profiling
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
    pcntl

# Install and configure OPcache
RUN docker-php-ext-install opcache

# Install Redis extension
RUN pecl install redis && docker-php-ext-enable redis

# Install Xdebug for profiling
RUN pecl install xdebug && docker-php-ext-enable xdebug

# Install additional performance profiling extensions
RUN pecl install apcu && docker-php-ext-enable apcu

# Install XHProf for detailed profiling
RUN pecl install xhprof && docker-php-ext-enable xhprof

# Install Blackfire probe for production profiling
RUN version=$(php -r "echo PHP_MAJOR_VERSION.PHP_MINOR_VERSION;") \
    && architecture=$(uname -m) \
    && curl -A "Docker" -o /tmp/blackfire-probe.tar.gz -D - -L -s https://blackfire.io/api/v1/releases/probe/php/linux/$architecture/$version \
    && mkdir -p /tmp/blackfire \
    && tar zxpf /tmp/blackfire-probe.tar.gz -C /tmp/blackfire \
    && mv /tmp/blackfire/blackfire-*.so $(php -r "echo ini_get ('extension_dir');")/blackfire.so \
    && rm -rf /tmp/blackfire /tmp/blackfire-probe.tar.gz

# Get Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# Set working directory
WORKDIR /app

# Copy application files
COPY . /app

# Install Composer dependencies
RUN composer install --no-dev --optimize-autoloader

# Copy custom PHP configuration
COPY docker/php/conf.d/performance.ini /usr/local/etc/php/conf.d/
COPY docker/php/conf.d/xdebug.ini /usr/local/etc/php/conf.d/
COPY docker/php/conf.d/opcache.ini /usr/local/etc/php/conf.d/

# Copy FrankenPHP Caddyfile
COPY docker/frankenphp/Caddyfile /etc/caddy/Caddyfile

# Set permissions
RUN chown -R www-data:www-data /app/storage /app/bootstrap/cache
RUN chmod -R 775 /app/storage /app/bootstrap/cache

# Expose port
EXPOSE 80 443

CMD ["frankenphp", "run", "--config", "/etc/caddy/Caddyfile"]