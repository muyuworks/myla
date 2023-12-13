npm run build

mkdir -p ../myla/webui/static/aify
cp build/static/js/*.js ../myla/webui/statics/aify/aify.js
cp build/static/css/*.css ../myla/webui/statics/aify/aify.css
