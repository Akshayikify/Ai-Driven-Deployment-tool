from typing import Dict, Any
from .base import DockerTemplate

class JavaDockerTemplate(DockerTemplate):
    def generate_dockerfile(self, findings: Dict[str, Any]) -> str:
        """
        Generates a multi-stage Dockerfile for a Spring Boot Maven project.
        """
        return (
            "FROM eclipse-temurin:17-alpine AS builder\n"
            "WORKDIR /app\n"
            "\n"
            "COPY .mvn ./.mvn\n"
            "COPY mvnw ./mvnw\n"
            "COPY mvnw.cmd ./mvnw.cmd\n"
            "COPY pom.xml ./pom.xml\n"
            "COPY src ./src\n"
            "\n"
            "RUN ./mvnw package -DskipTests\n"
            "\n"
            "FROM eclipse-temurin:17-alpine\n"
            "WORKDIR /app\n"
            "\n"
            "COPY --from=builder /app/target/*.jar app.jar\n"
            "\n"
            "EXPOSE 8080\n"
            "\n"
            "ENTRYPOINT [\"java\", \"-jar\", \"app.jar\"]\n"
        )

    def generate_dockerignore(self, findings: Dict[str, Any]) -> str:
        """
        Generates a .dockerignore file for Java projects.
        """
        return ".git\ntarget/\n*.class\n.mvn/\nmvnw\nmvnw.cmd\n"

    def generate_cicd_workflow(self, findings: Dict[str, Any]) -> str:
        """
        Generates a Java-specific GitHub Actions workflow.
        """
        return """name: Java Spring Boot CI/CD

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up JDK 17
        uses: actions/setup-java@v3
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: maven

      - name: Make mvnw executable
        run: chmod +x mvnw

      - name: Build with Maven
        run: ./mvnw -B package --file pom.xml -DskipTests

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:latest
            ghcr.io/${{ github.repository }}:${{ github.sha }}
"""
