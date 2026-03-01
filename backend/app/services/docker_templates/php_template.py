from typing import Dict, Any
from .base import DockerTemplate

class PHPDockerTemplate(DockerTemplate):
    def generate_dockerfile(self, findings: Dict[str, Any]) -> str:
        """Generates a Dockerfile for PHP projects."""
        has_composer = "composer.json" in findings.get("detected_files", [])
        
        content = [
            "FROM php:8.2-apache",
            "",
            "# Install system dependencies and PHP extensions",
            "RUN apt-get update && apt-get install -y \\",
            "    libzip-dev \\",
            "    zip \\",
            "    unzip \\",
            "    git \\",
            "    && docker-php-ext-install pdo_mysql zip",
            "",
            "# Enable Apache Mod Rewrite",
            "RUN a2enmod rewrite",
            "",
            "WORKDIR /var/www/html",
        ]
        
        if has_composer:
            content.extend([
                "",
                "# Install Composer",
                "COPY --from=composer:latest /usr/bin/composer /usr/bin/composer",
                "",
                "# Copy composer files",
                "COPY composer.json composer.lock* ./",
                "RUN composer install --no-dev --optimize-autoloader --no-scripts",
            ])
            
        content.extend([
            "",
            "# Copy application files",
            "COPY . .",
            "",
            "# Set permissions",
            "RUN chown -R www-data:www-data /var/www/html",
            "",
            "EXPOSE 80",
            ""
        ])
        
        return "\n".join(content)
