release: sh -c 'cd aparkapp && python manage.py migrate'
web: sh -c 'cd aparkapp && gunicorn aparkapp.wsgi --log-file -'