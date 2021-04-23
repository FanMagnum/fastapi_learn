gunicorn app.main:app -b 0.0.0.0:10000 -w 4 -k uvicorn.workers.UvicornH11Worker --access-logfile ./app/logs/server.log --error-logfile ./app/logs/server_error.log --daemon

