FROM php:8.4-apache-bookworm

# Rquired extensions
RUN docker-php-ext-install pdo_mysql

# XHProf
RUN pecl install xhprof && docker-php-ext-enable xhprof

# Apache rewrite module
RUN a2enmod rewrite

# XHProf interface
COPY docker/config/xhprof/index.php /var/www/html/index.php

# Set permissions
RUN chown -R www-data:www-data /var/www/html

EXPOSE 80
