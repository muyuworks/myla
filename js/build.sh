npm run build

mkdir -p ../myla/webui/static/aify
cp build/static/js/*.js ../myla/webui/static/aify/aify.js
cp build/static/css/*.css ../myla/webui/static/aify/aify.css
