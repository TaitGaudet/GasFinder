# GasFinder — West Point

## Run the App

```bash
docker-compose up --build
```

## Seed the Database

Open a second terminal and run:

```bash
docker exec -it gasfinder-backend-1 python seed.py
```

## Open the App

```
http://localhost
```

## Stop the App

```bash
docker-compose down
```

> If you used `docker-compose down -v`, re-run the seed command after starting back up.
