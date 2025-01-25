Before start you need to have:

1. .env-frontend
2. .env-app
3. .env-bd-credentials

And apply commands to create:

1. kubectk create secret generic secret-frontend --from-env-file=.env-frontend
2. kubectk create secret generic secret-app --from-env-file=.env-app
3. kubectk create secret generic secret-db-credentials --from-env-file=.env-db-credentials