from .base import DockerTemplate
from typing import Dict, Any
import os

class RubyDockerTemplate(DockerTemplate):
    def generate_dockerfile(self, findings: Dict[str, Any]) -> str:
        """
        Generates a robust multi-stage Dockerfile for Ruby projects.
        Handles missing Gemfile.lock by ensuring the bundle is initialized correctly.
        """
        detected = findings.get("detected_files", [])
        entry_point = findings.get("entry_point", "main.rb")
        
        content = [
            "FROM ruby:3.2-slim AS builder",
            "WORKDIR /app",
            "",
            "RUN apt-get update && apt-get install -y --no-install-recommends \\",
            "    build-essential \\",
            "    && rm -rf /var/lib/apt/lists/*",
            "",
        ]

        if "Gemfile" in detected:
            content.append("COPY Gemfile ./")
            if "Gemfile.lock" in detected:
                content.append("COPY Gemfile.lock ./")
            
            content.append("RUN bundle install --jobs 4 --retry 3")
        
        content.extend([
            "",
            "FROM ruby:3.2-slim",
            "WORKDIR /app",
            "",
            "# Create a non-root user",
            "RUN groupadd -r appuser && useradd -r -g appuser appuser",
            "",
            "COPY --from=builder /usr/local/bundle /usr/local/bundle",
            "COPY . .",
            "",
            "RUN chown -R appuser:appuser /app",
            "USER appuser",
            "",
        ])

        if entry_point:
            content.append(f'CMD ["ruby", "{entry_point}"]')
        else:
            content.append('CMD ["irb"]')

        return "\n".join(content)

    def generate_dockerignore(self, findings: Dict[str, Any]) -> str:
        return """
.git
.bundle
log/*
tmp/*
vendor/bundle
*.swp
*.bak
"""
