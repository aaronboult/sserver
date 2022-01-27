# Set working directory to src/ folder and start server
cd ./src/
uwsgi --http :80 --wsgi-file server.py
