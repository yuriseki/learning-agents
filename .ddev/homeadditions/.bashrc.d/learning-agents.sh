# Activate the shared framework venv in interactive shells (ddev ssh).
# AG2 has its own: `source /var/www/html/.ddev/.venv-ag2/bin/activate`
if [ -f /var/www/html/.ddev/.venv/bin/activate ]; then
  . /var/www/html/.ddev/.venv/bin/activate
fi
