#!/bin/bash

echo "📁 Creating templates structure..."
mkdir -p templates/home
mkdir -p templates/includes
mkdir -p templates/layouts

echo "📁 Creating static structure..."
mkdir -p static/css
mkdir -p static/js
mkdir -p static/img
mkdir -p static/audio/listening

echo "📄 Creating base templates..."
touch templates/layouts/base.html
touch templates/includes/navbar.html
touch templates/includes/footer.html

echo "📄 Creating home page template..."
touch templates/home/index.html

echo "📄 Creating static files..."
touch static/css/main.css
touch static/js/main.js

echo "✅ Frontend structure initialized successfully!"
