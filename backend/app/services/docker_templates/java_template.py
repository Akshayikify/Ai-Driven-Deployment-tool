from typing import Dict, Any
from .base import DockerTemplate

class JavaDockerTemplate(DockerTemplate):
    def generate_dockerfile(self, findings: Dict[str, Any]) -> str:
        """
        Generates a more robust multi-stage Dockerfile for a Spring Boot Maven project.
        """
        file_names = findings.get("file_index", {}).get("by_name", {})
        has_mvnw = "mvnw" in file_names
        has_mvn_dir = ".mvn" in file_names or any(".mvn/" in f for f in findings.get("file_index", {}).get("all_files", []))

        content = [
            "FROM maven:3-eclipse-temurin-17-alpine AS builder",
            "WORKDIR /app",
            "",
            "COPY pom.xml .",
        ]

        if has_mvn_dir:
            content.append("COPY .mvn ./.mvn")
        
        if has_mvnw:
            content.append("COPY mvnw ./")
            content.append("COPY mvnw.cmd ./")
        
        content.extend([
            "COPY src ./src",
            "",
            "# Fix line endings for the wrapper and prefer system mvn if wrapper fails",
            "RUN if [ -f \"./mvnw\" ]; then sed -i 's/\\r$//' mvnw && chmod +x mvnw; fi",
            "RUN mvn package -DskipTests || ./mvnw package -DskipTests",
            "",
            "FROM eclipse-temurin:17-jre-alpine",
            "WORKDIR /app",
            "",
            "COPY --from=builder /app/target/*.jar app.jar",
            "",
            "EXPOSE 8080",
            "",
            'ENTRYPOINT ["java", "-jar", "app.jar"]'
        ])

        return "\n".join(content)

    def generate_dockerignore(self, findings: Dict[str, Any]) -> str:
        """
        Generates a correct .dockerignore file for Java projects.
        We must NOT ignore the wrapper files if we need them.
        """
        return ".git\ntarget/\n*.class\n"

    def generate_cicd_workflow(self, findings: Dict[str, Any]) -> str:
        """
        Generates a Java-specific GitHub Actions workflow.
        """
        workdir = findings.get("path", ".")
        clean_workdir = workdir.strip("./")
        
        return f"""name: Java Spring Boot CI/CD

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Set up JDK 17
        uses: actions/setup-java@v3
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: maven

      - name: Build with Maven
        working-directory: ./{clean_workdir}
        run: |
          if [ -f "mvnw" ]; then
            chmod +x mvnw
            ./mvnw -B package --file pom.xml -DskipTests || mvn -B package --file pom.xml -DskipTests
          else
            mvn -B package --file pom.xml -DskipTests
          fi

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{{{ github.actor }}}}
          password: ${{{{ secrets.GITHUB_TOKEN }}}}

      - name: Lowercase repository name
        run: echo "IMAGE_ID=$(echo ${{{{ github.repository }}}} | tr '[:upper:]' '[:lower:]')" >> $GITHUB_ENV

      - name: Extract metadata (tags, labels) for Docker
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ghcr.io/${{{{ env.IMAGE_ID }}}}
          tags: |
            type=raw,value=latest,enable=${{{{ github.ref == 'refs/heads/main' }}}}
            type=sha,prefix=sha-,format=short

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: ./{clean_workdir}
          file: ./{clean_workdir}/Dockerfile
          push: true
          tags: ${{{{ steps.meta.outputs.tags }}}}
          labels: ${{{{ steps.meta.outputs.labels }}}}
          cache-from: type=gha
          cache-to: type=gha,mode=max
"""
