"""Writes the testbed sample apps under testbed/apps/.
Each app is a few lines; expect.json records what the analyzer should detect."""
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apps")

JAVA_APP = (
    "import com.sun.net.httpserver.HttpServer;\n"
    "import java.net.InetSocketAddress;\n\n"
    "public class App {\n"
    "    public static void main(String[] args) throws Exception {\n"
    "        HttpServer s = HttpServer.create(new InetSocketAddress(8080), 0);\n"
    "        s.createContext(\"/\", ex -> {\n"
    "            byte[] b = \"ok\".getBytes();\n"
    "            ex.sendResponseHeaders(200, b.length);\n"
    "            ex.getResponseBody().write(b);\n"
    "            ex.close();\n"
    "        });\n"
    "        s.start();\n"
    "    }\n"
    "}\n"
)

EXPRESS_PKG = {"name": "node-express", "version": "1.0.0",
               "scripts": {"start": "node server.js"},
               "dependencies": {"express": "^4.19.2"}}
EXPRESS_SRV = (
    "const express = require('express');\n"
    "const app = express();\n"
    "app.get('/', (req, res) => res.send('ok'));\n"
    "app.listen(3000, '0.0.0.0');\n"
)


def js(obj):
    return json.dumps(obj, indent=2) + "\n"


APPS = {
    "python-flask": ({"language": "Python", "framework": "Flask"}, {
        "app.py": "from flask import Flask\napp = Flask(__name__)\n\n@app.route('/')\ndef index():\n    return 'ok'\n\nif __name__ == '__main__':\n    app.run(host='0.0.0.0', port=5000)\n",
        "requirements.txt": "flask\n"}),
    "python-fastapi": ({"language": "Python", "framework": "FastAPI"}, {
        "main.py": "from fastapi import FastAPI\napp = FastAPI()\n\n@app.get('/')\ndef index():\n    return {'status': 'ok'}\n",
        "requirements.txt": "fastapi\nuvicorn\n"}),
    "python-django": ({"language": "Python", "framework": "Django"}, {
        "manage.py": "import os\nimport sys\n\nif __name__ == '__main__':\n    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')\n    from django.core.management import execute_from_command_line\n    execute_from_command_line(sys.argv)\n",
        "mysite/__init__.py": "",
        "mysite/settings.py": "SECRET_KEY = 'testbed'\nDEBUG = False\nALLOWED_HOSTS = ['*']\nROOT_URLCONF = 'mysite.urls'\nINSTALLED_APPS = []\nMIDDLEWARE = []\nUSE_TZ = True\n",
        "mysite/urls.py": "from django.http import HttpResponse\nfrom django.urls import path\n\nurlpatterns = [path('', lambda r: HttpResponse('ok'))]\n",
        "mysite/wsgi.py": "import os\nfrom django.core.wsgi import get_wsgi_application\n\nos.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')\napplication = get_wsgi_application()\n",
        "requirements.txt": "django>=4.2,<5.0\ngunicorn\n"}),
    "python-stdlib": ({"language": "Python", "framework": "Python (Generic)"}, {
        "app.py": "import os\nfrom http.server import BaseHTTPRequestHandler, HTTPServer\n\n\nclass H(BaseHTTPRequestHandler):\n    def do_GET(self):\n        self.send_response(200)\n        self.end_headers()\n        self.wfile.write(b'ok')\n\n\nHTTPServer(('0.0.0.0', int(os.environ.get('PORT', 8000))), H).serve_forever()\n",
        "requirements.txt": "# no third-party dependencies\n"}),
    "node-express": ({"language": "JavaScript/TypeScript", "framework": "Express"}, {
        "package.json": js(EXPRESS_PKG),
        "server.js": EXPRESS_SRV}),
    "node-port-env": ({"language": "JavaScript/TypeScript", "framework": "Node.js (Generic)"}, {
        "package.json": js({"name": "node-port-env", "version": "1.0.0", "scripts": {"start": "node index.js"}}),
        "index.js": "const http = require('http');\nconst port = process.env.PORT || 5000;\nhttp.createServer((req, res) => res.end('ok')).listen(port, '0.0.0.0');\n"}),
    "node-vite-react": ({"language": "JavaScript/TypeScript", "framework": "React"}, {
        "package.json": js({"name": "node-vite-react", "private": True, "version": "1.0.0",
                            "scripts": {"dev": "vite", "build": "vite build", "preview": "vite preview"},
                            "dependencies": {"react": "^18.3.1", "react-dom": "^18.3.1"},
                            "devDependencies": {"@vitejs/plugin-react": "^4.3.1", "vite": "^5.4.0"}}),
        "vite.config.js": "import { defineConfig } from 'vite';\nimport react from '@vitejs/plugin-react';\n\nexport default defineConfig({ plugins: [react()] });\n",
        "index.html": "<!doctype html>\n<html><body><div id=\"root\"></div><script type=\"module\" src=\"/src/main.jsx\"></script></body></html>\n",
        "src/main.jsx": "import React from 'react';\nimport { createRoot } from 'react-dom/client';\n\ncreateRoot(document.getElementById('root')).render(<h1>ok</h1>);\n"}),
    "node-nextjs": ({"language": "JavaScript/TypeScript", "framework": "Next.js"}, {
        "package.json": js({"name": "node-nextjs", "version": "1.0.0",
                            "scripts": {"dev": "next dev", "build": "next build", "start": "next start"},
                            "dependencies": {"next": "^14.2.5", "react": "^18.3.1", "react-dom": "^18.3.1"}}),
        "pages/index.js": "export default function Home() {\n  return <h1>ok</h1>;\n}\n"}),
    "go-http": ({"language": "Go", "framework": "Go (Modules)"}, {
        "go.mod": "module example.com/app\n\ngo 1.22\n",
        "main.go": "package main\n\nimport (\n\t\"fmt\"\n\t\"net/http\"\n)\n\nfunc main() {\n\thttp.HandleFunc(\"/\", func(w http.ResponseWriter, r *http.Request) { fmt.Fprint(w, \"ok\") })\n\thttp.ListenAndServe(\":8080\", nil)\n}\n"}),
    "rust-std": ({"language": "Rust", "framework": "Unknown"}, {
        "Cargo.toml": "[package]\nname = \"app\"\nversion = \"0.1.0\"\nedition = \"2021\"\n\n[dependencies]\n",
        "src/main.rs": "use std::io::{Read, Write};\nuse std::net::TcpListener;\n\nfn main() {\n    let port = std::env::var(\"PORT\").unwrap_or_else(|_| \"8080\".to_string());\n    let listener = TcpListener::bind(format!(\"0.0.0.0:{}\", port)).unwrap();\n    for stream in listener.incoming() {\n        let mut s = stream.unwrap();\n        let mut buf = [0u8; 1024];\n        let _ = s.read(&mut buf);\n        let _ = s.write_all(b\"HTTP/1.1 200 OK\\r\\nContent-Length: 2\\r\\nConnection: close\\r\\n\\r\\nok\");\n    }\n}\n"}),
    "java-maven": ({"language": "Java", "framework": "Maven / Spring Boot"}, {
        "pom.xml": "<project xmlns=\"http://maven.apache.org/POM/4.0.0\">\n  <modelVersion>4.0.0</modelVersion>\n  <groupId>example</groupId>\n  <artifactId>app</artifactId>\n  <version>1.0</version>\n  <properties>\n    <maven.compiler.source>17</maven.compiler.source>\n    <maven.compiler.target>17</maven.compiler.target>\n  </properties>\n  <build>\n    <plugins>\n      <plugin>\n        <groupId>org.apache.maven.plugins</groupId>\n        <artifactId>maven-jar-plugin</artifactId>\n        <version>3.3.0</version>\n        <configuration>\n          <archive><manifest><mainClass>App</mainClass></manifest></archive>\n        </configuration>\n      </plugin>\n    </plugins>\n  </build>\n</project>\n",
        "src/main/java/App.java": JAVA_APP}),
    "java-gradle": ({"language": "Java", "framework": "Gradle"}, {
        "build.gradle": "plugins { id 'java' }\n\nrepositories { mavenCentral() }\n\njar { manifest { attributes 'Main-Class': 'App' } }\n",
        "settings.gradle": "rootProject.name = 'app'\n",
        "src/main/java/App.java": JAVA_APP}),
    "php-plain": ({"language": "PHP", "framework": "Unknown"}, {
        "index.php": "<?php echo 'ok';\n"}),
    "ruby-sinatra": ({"language": "Ruby", "framework": "Ruby (Bundler)"}, {
        "Gemfile": "source 'https://rubygems.org'\ngem 'sinatra'\ngem 'rackup'\ngem 'puma'\n",
        "config.ru": "require './app'\nrun Sinatra::Application\n",
        "app.rb": "require 'sinatra'\n\nget '/' do\n  'ok'\nend\n"}),
    "static-html": ({"language": "HTML/Static", "framework": "Static Website"}, {
        "index.html": "<!doctype html>\n<html><body><h1>ok</h1></body></html>\n"}),
    "trap-node-stray-files": ({"language": "JavaScript/TypeScript", "framework": "Express"}, {
        "package.json": js(dict(EXPRESS_PKG, name="trap-node")),
        "server.js": EXPRESS_SRV,
        "scripts/seed.rb": "puts 'seed'\n",
        "tests/main.py": "print('test helper')\n",
        "src/index.js": "module.exports = {};\n"}),
}

for name, (expect, files) in APPS.items():
    expect = dict(expect, services=1, path="/")
    base = os.path.join(ROOT, name)
    for rel, content in files.items():
        p = os.path.join(base, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", newline="\n") as f:
            f.write(content)
    with open(os.path.join(base, "expect.json"), "w", newline="\n") as f:
        json.dump(expect, f, indent=2)
        f.write("\n")
print(len(APPS), "apps written")
