# RentFlex - Car Rental System

[![api.png](https://i.postimg.cc/8kFVVqr5/api.png)](https://postimg.cc/G91fFgKw)


RentFlex is a modern car rental management system with a user-friendly interface. Customers can browse available vehicles, book cars, and manage their orders, while administrators can manage the vehicle inventory and handle booking requests.

---

## Features

- **User Authentication** (Login/Register)
- **Customer Features:**
  - Browse available vehicles
  - View vehicle details
  - Book vehicles
  - Manage personal bookings
- **Admin Features:**
  - Manage vehicle inventory
  - Approve or reject booking requests

---

## Showcase

**Admin - Booking Management**  
![admin-booking.png](https://i.postimg.cc/htLyB0rh/admin-booking.png)

**Admin - Vehicle Management**  
![admin-vehicle.png](https://i.postimg.cc/CKwvLfP7/admin-vehicle.png)

**User - My Bookings**  
![user-booking.png](https://i.postimg.cc/4d62JQZW/user-booking.png)

**User - Vehicle Details**  
![user-vehicle-detail-info.png](https://i.postimg.cc/MHzPXfpq/user-vehicle-detail-info.png)

**User - Browse Vehicles**  
![user-vehicles.png](https://i.postimg.cc/nzz0qftQ/user-vehicles.png)

### Default Accounts

The system automatically initializes the database with sample data including:

1. **Admin Account**
   - Email: admin@rentflex.com
   - Password: admin123!

2. **Customer Account**
   - Email: customer@example.com
   - Password: admin123!

3. **Sample Vehicles**
   - Various car models with different pricing and availability
   
4. **Sample Bookings**
   - Pre-existing bookings to demonstrate the system

The database initialization happens automatically when you first start the containers using the SQL script in `backend/init.sql`.

---

## System Requirements

- Docker & Docker Compose
- Node.js 18+ (if not using Docker)
- Python 3.12+ (if not using Docker)
- MySQL 8.0+ (if not using Docker)

---

## Installation & Setup

### Using Docker (Recommended)

1. **Clone the repository:**
    ```bash
    git clone https://github.com/osh1130/rentflex.git
    cd rentflex
    ```

2. **Build and start the containers:**
    ```bash
    docker-compose up --build
    ```

   > **Note**: All necessary environment configurations are already set up in the repository. The database credentials are pre-configured with username `rentflex` and password `vivizhao`.

3. **Access the application:**
    - Frontend: http://localhost:3000
    - Backend API: http://localhost:8000/api
    - API Documentation: http://localhost:8000/docs (Swagger UI with detailed API information)

### Testing with Different Database Environment

The system supports switching between development and test databases:

1. **Use the test database**:
   Edit `docker-compose.yml` to ensure the backend connects to the test database (this is the default configuration).

2. **Use the development database**:
   If you want to switch back to the development database, edit `docker-compose.yml` and change the backend service configuration:
   ```yaml
   backend:
     # ...
     depends_on:
       - mysql
     environment:
       DB_HOST: mysql
       DB_PORT: 3306
       DB_USER: rentflex
       DB_PASSWORD: vivizhao
       DB_NAME: rentflex
       ENV: dev
   ```

3. **Restart the backend service**:
   ```bash
   docker-compose stop backend
   docker-compose up -d backend
   ```

---

### Manual Setup (Without Docker)

#### Backend Setup

1. Install Python 3.12 and MySQL 8.0

2. Navigate to the backend directory:
    ```bash
    cd backend
    ```

3. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

4. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

5. Create the `.env.dev` file:
    ```
    DB_HOST=localhost
    DB_PORT=3306
    DB_USER=rentflex
    DB_PASSWORD=vivizhao
    DB_NAME=rentflex
    ENV=dev
    ```

6. Start the backend service:
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --env-file .env.dev
    ```

#### Frontend Setup

1. Install Node.js 18+

2. Navigate to the frontend directory:
    ```bash
    cd frontend
    ```

3. Install dependencies:
    ```bash
    npm install
    # or with pnpm
    pnpm install
    ```

4. Create a `.env` file:
    ```
    # Frontend API configuration - point to your running backend
    VITE_API_URL=http://localhost:8000/api
    ```

5. Start the frontend development server:
    ```bash
    npm run dev
    # or with pnpm
    pnpm dev
    ```

6. Access the frontend: http://localhost:3000

---

## Project Structure

### Root Directory

- `docker-compose.yml` - Docker Compose configuration
- `Dockerfile.backend` - Backend service Dockerfile
- `Dockerfile.frontend` - Frontend service Dockerfile
- `Dockerfile.mock` - (Optional) Mock service Dockerfile
- `package.json` - Node.js dependencies at root
- `.gitignore` - Git ignore rules
- `.dockerignore` - Docker ignore rules

### Backend (`/backend`)

- `/app` - Main application directory
  - `main.py` - FastAPI app entry point
  - `database.py` - Database connection config
  - `models.py` - SQLAlchemy model definitions
  - `deps.py` - Dependency injection
  - `utils.py` - Utility functions
  - `/routers` - API route handlers
  - `/schemas` - Pydantic models/data validation
  - `/services` - Business logic services
- `requirements.txt` - Python dependencies
- `wait-for-db.sh` - DB startup helper script
- `alembic.ini` - Alembic DB migration config
- `/alembic` - DB migration scripts
- `init.sql` - Database initialization script with sample data

### Frontend (`/frontend`)

- `/src` - Source code directory
  - `main.jsx` - React app entry point
  - `App.jsx` - Main app component and routes
  - `/pages` - Page components
    - `/auth` - Auth pages
    - `/customer` - Customer pages
    - `/admin` - Admin pages
  - `/components` - Reusable UI components
  - `/contexts` - React context (e.g., Auth)
  - `/utils` - Utility functions
  - `/api` - API client code
- `package.json` - Frontend dependencies
- `vite.config.js` - Vite build config
- `tailwind.config.js` - Tailwind CSS config
- `postcss.config.js` - PostCSS config
- `index.html` - HTML entry point

---

## Data Models

1. **User**
   - Role: customer or admin
   - Personal information
   - Booking history

2. **Vehicle**
   - Basic info (make, model, year, etc.)
   - Availability status
   - Rental conditions (min/max period)
   - Pricing

3. **Booking**
   - Customer info
   - Vehicle info
   - Date range
   - Status (pending, approved, rejected, cancelled)
   - Fee details

4. **Extra**
   - Name and description
   - Fee info

---

## Known Issues & Limitations

- MySQL port conflicts may occur between local and Docker MySQL (both use 3306 by default). Change the host port in `docker-compose.yml` (e.g., to 3307) if needed.
- On some systems, the `wait-for-db.sh` script may require execute permission (`chmod +x backend/wait-for-db.sh`).
- After login, the frontend does **not** auto-redirect to the homepage.
- No password reset function.
- Payment processing is not implemented.
- Admin interface lacks full data validation.
- If you need to use your own database credentials, edit the `docker-compose.yml` file and replace `vivizhao` with your preferred password.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Maintenance Plan

RentFlex follows a structured maintenance plan that outlines version control rules, upgrade strategies, and backward compatibility guarantees. For detailed information, please refer to the [Maintenance Plan](MAINTENANCE.md).

## Developer Information

**Xinyi Zhao**

- GitHub: [github.com/osh1130](https://github.com/osh1130)
- Email: vivizhao401@gmail.com

## Contribution

Contributions through issues and pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Acknowledgments

Thanks to all developers and testers who contributed to this project.

