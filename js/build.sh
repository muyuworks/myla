npm run build

mkdir -p ../webui/static/aify
cp build/static/js/*.js ../webui/static/aify/aify.js
cp build/static/css/*.css ../webui/static/aify/aify.css
