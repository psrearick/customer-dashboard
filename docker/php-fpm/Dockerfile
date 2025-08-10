FROM php:8.4-fpm-bookworm

# Install system dependencies (this layer changes rarely, so it gets cached)
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
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install PHP extensions in one layer
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

# Install PECL extensions in one layer for better caching
RUN pecl install redis xdebug apcu xhprof \
    && docker-php-ext-enable redis xdebug apcu xhprof

# Install Blackfire probe (separate since it uses curl)
RUN version=$(php -r "echo PHP_MAJOR_VERSION.PHP_MINOR_VERSION;") \
    && architecture=$(uname -m) \
    && curl -A "Docker" -o /tmp/blackfire-probe.tar.gz -D - -L -s https://blackfire.io/api/v1/releases/probe/php/linux/$architecture/$version \
    && mkdir -p /tmp/blackfire \
    && tar zxpf /tmp/blackfire-probe.tar.gz -C /tmp/blackfire \
    && mv /tmp/blackfire/blackfire-*.so $(php -r "echo ini_get ('extension_dir');")/blackfire.so \
    && rm -rf /tmp/blackfire /tmp/blackfire-probe.tar.gz

# Get Composer (cached layer since composer image doesn't change often)
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# Set working directory
WORKDIR /var/www/html

# Copy configuration files first (they change less frequently than app code)
COPY docker/php/conf.d/performance.ini /usr/local/etc/php/conf.d/
COPY docker/php/conf.d/opcache.ini /usr/local/etc/php/conf.d/
COPY docker/php/conf.d/xdebug.ini /usr/local/etc/php/conf.d/
COPY docker/php-fpm/www.conf /usr/local/etc/php-fpm.d/www.conf

# Copy application code
COPY . /var/www/html

# Install composer dependencies if composer.json exists
RUN if [ -f composer.json ]; then \
        composer install --no-dev --optimize-autoloader --no-scripts; \
        composer run-script post-autoload-dump 2>/dev/null || true; \
    fi

# Install npm dependencies and build assets if package.json exists
RUN if [ -f package.json ]; then \
        npm ci --only=production; \
        npm run build; \
    fi

# Set permissions for Laravel directories if they exist
RUN if [ -d "/var/www/html/storage" ]; then \
        chown -R www-data:www-data /var/www/html/storage; \
        chmod -R 775 /var/www/html/storage; \
    fi \
    && if [ -d "/var/www/html/bootstrap/cache" ]; then \
        chown -R www-data:www-data /var/www/html/bootstrap/cache; \
        chmod -R 775 /var/www/html/bootstrap/cache; \
    fi

# Create Xdebug output directory
RUN mkdir -p /var/www/html/storage/logs/xdebug && chown -R www-data:www-data /var/www/html/storage/logs/xdebug

# Ensure proper ownership of all files
RUN chown -R www-data:www-data /var/www/html

# Expose port 9000
EXPOSE 9000

CMD ["php-fpm"]