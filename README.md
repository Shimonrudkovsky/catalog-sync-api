# Catalog Sync API

Catalog Sync API is an application designed to manage a parts catalog. It consists of the following services:

- **External API**: A FastAPI-based service for interacting with the catalog (makers, categories, models, parts) and triggering scraper operations.
- **Scraper Service**: A service responsible for scraping data and populating the catalog.

---

## How to Launch the Application

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Shimonrudkovsky/catalog-sync-api
   cd catalog-sync-api
   ```

2. **Run the Application**:
   Use `docker-compose` to build and start the services:
   ```bash
   docker-compose up -d
   ```

3. **Access the Services**:
   - **External API**: [http://localhost:8081](http://localhost:8081)
   - **Swagger UI**: [http://localhost:8081/docs](http://localhost:8081/docs)

---

## Services and Ports

- **External API**:
  - Runs on port `8081` (default).
  - Provides endpoints for managing the catalog and triggering scraper operations.

- **Scraper Service**:
  - Runs on port `8080` (default).
  - Handles long-running scraping tasks.

- **Database**:
  - Runs on port `5432` (default).
  - Stores catalog data.

---

## Endpoints Overview

### External API
- **Parts**: `/parts`
- **Makers**: `/manufacturers`
- **Categories**: `/categories`
- **Models**: `/models`
- **Scans**: `/scans`
- **Run Scraper**: `/scraper/run`

### Scraper Service
- **Run Scraper**: `/run`

---

## Notes

- Ensure Docker and Docker Compose are installed on your system.
- You can modify the `.env` file to customize ports and other configurations.
