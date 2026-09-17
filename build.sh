set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

python manage.py migrate_schemas

# python manage.py migrate_schemas --shared 

# python manage.py migrate_schemas --tenant 

# python manage.py migrate Client
# python manage.py migrate CompteurApps
# python manage.py migrate Corrective
# python manage.py migrate Entreprise
# python manage.py migrate MatRoulant
# python manage.py migrate Parameters
# python manage.py migrate PreventApps
# python manage.py migrate Travaux


