# Simple Travel Application

## Overview

The Simple Travel Application is a comprehensive solution designed to provide users with detailed travel listings through a responsive web interface and a robust backend. The frontend is built with **Next.js**, offering a seamless and interactive user experience, while the backend leverages **Django** to handle data processing, API endpoints, and integrations with external services.

## Features

### Frontend
- **Next.js Framework:** Utilizes server-side rendering and static site generation for optimal performance.
- **Responsive Design:** Ensures compatibility across various devices and screen sizes.
- **API Integration:** Communicates with the Django backend to fetch and display travel data.
- **Optimized Performance:** Implements automatic code splitting and image optimization.

### Backend
- **Django Framework:** Provides a scalable and secure backend infrastructure.
- **API Endpoints:** Offers RESTful APIs for data retrieval and manipulation.
- **Embedchain Integration:** Facilitates advanced data embedding and retrieval.
- **Environment Management:** Uses Conda for managing Python dependencies and environments.
- **CORS Support:** Configured with `django-cors-headers` to handle Cross-Origin Resource Sharing.

## Prerequisites

Ensure the following are installed on your machine:

- **Environment Management Tool:** [Conda](https://docs.conda.io/en/latest/) or a similar tool.
- **Python:** Version 3.10 or higher.
- **Node.js:** Version 14.x or higher.
- **npm or Yarn:** Package managers for JavaScript.
- **Git:** For cloning repositories.
- **Docker:** (Optional) For containerized deployment.

## Project Structure

```
simple-travel-application/
├── backend/
│   ├── config/                 # Django project settings
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── listings/               # Django app
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── services.py         # Contains Embedchain logic
│   │   ├── utils.py            # Contains helper functions
│   │   └── views.py
│   ├── manage.py
│   ├── chat_config.py          # Embedchain configuration
│   ├── requirements.txt
│   └── Dockerfile              # Docker configuration for backend
├── frontend/
│   ├── components/             # Reusable React components
│   ├── pages/                  # Next.js pages
│   │   ├── api/                # API routes (if any)
│   │   ├── hotels.js           # Example page for hotels
│   │   └── index.js            # Home page
│   ├── public/                 # Static assets
│   ├── styles/                 # CSS and styling
│   ├── .env.local              # Environment variables
│   ├── package.json
│   ├── README.md               # Frontend-specific README
│   └── Dockerfile              # Docker configuration for frontend
├── clean/                      # Directory for existing datasets and raw data
├── .gitignore
└── README.md                   # Combined project README
```

## Setup Instructions

Follow the steps below to set up both the backend and frontend components of the application.

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/simple-travel-application.git
cd simple-travel-application
```

### 2. Backend Setup

#### 2.1. Create and Activate Conda Environment

Create a new Conda environment with Python 3.11 and activate it.

```bash
conda create -n backend-env python=3.11 -y
conda activate backend-env
```

#### 2.2. Install Dependencies

Navigate to the backend directory and install the required Python packages.

```bash
cd backend
pip install -r requirements.txt
```

#### 2.3. Set Up Environment Variables

Create a `.env` file in the `backend` directory and add the necessary environment variables.

```bash
echo "OPENAI_API_KEY=\"<YOUR_OPENAI_API_KEY>\"" > .env
echo "GROQ_API_KEY=\"<YOUR_GROQ_API_KEY>\"" >> .env
echo "CHROMA_BOOKS_COLLECTION=\"finbooks\"" >> .env
echo "CHROMA_DB_PATH=\"chromadb\"" >> .env
```

*Replace `<YOUR_OPENAI_API_KEY>` and `<YOUR_GROQ_API_KEY>` with your actual API keys.*

#### 2.4. Apply Migrations

Set up the database by applying Django migrations.

```bash
python manage.py migrate
```

#### 2.5. Run the Backend Application

Start the Django development server.

```bash
python manage.py runserver 0.0.0.0:8001
```

*Alternatively, use Gunicorn for production environments:*

```bash
gunicorn -w 2 -b 0.0.0.0:8001 config.wsgi:application
```

### 3. Frontend Setup

#### 3.1. Navigate to Frontend Directory

Open a new terminal window and navigate to the frontend directory.

```bash
cd ../frontend
```

#### 3.2. Install Dependencies

Use your preferred package manager to install the necessary packages.

##### Using npm:

```bash
npm install
```

##### Using Yarn:

```bash
yarn install
```

#### 3.3. Configure Environment Variables

Create a `.env.local` file in the `frontend` directory and add any necessary environment variables, such as API endpoints if required.

```bash
echo "NEXT_PUBLIC_API_URL=http://localhost:8001/api" > .env.local
```

#### 3.4. Run the Frontend Application

Start the Next.js development server.

##### Using npm:

```bash
npm run dev
```

##### Using Yarn:

```bash
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser to view the application.

*For production builds:*

```bash
npm run build
npm run start
```

### 4. Dockerized Deployment (Optional)

If you prefer containerized deployment, Dockerfiles are provided for both backend and frontend.

#### 4.1. Backend Docker Setup

Navigate to the backend directory and build the Docker image.

```bash
cd ../backend
docker build -t simple-travel-backend .
```

Run the Docker container.

```bash
docker run --rm \
    -v $(pwd)/chroma.sqlite3:/app/chromadb/chroma.sqlite3 \
    -v $(pwd)/.env:/app/.env \
    -p 8001:8001 \
    simple-travel-backend
```

#### 4.2. Frontend Docker Setup

Open a new terminal window, navigate to the frontend directory, and build the Docker image.

```bash
cd ../frontend
docker build -t simple-travel-frontend .
```

Run the Docker container.

```bash
docker run --rm \
    -v $(pwd)/public:/app/public \
    -v $(pwd)/.env.local:/app/.env.local \
    -p 3000:3000 \
    simple-travel-frontend
```

Access the frontend at [http://localhost:3000/hotels](http://localhost:3000/hotels).

## Usage

Once both backend and frontend applications are running, navigate to the frontend URL to interact with the application. The frontend communicates with the backend APIs to fetch and display travel listings based on user queries.

### Example Interaction

1. **Access the Hotels Page:**
   Open [http://localhost:3000/hotels](http://localhost:3000/hotels) in your browser to view available hotel listings.

2. **Search Functionality:**
   Use the search bar to input queries, such as "Find hotels near Central Park," and view the filtered results.

## API Endpoints

The backend provides several API endpoints to facilitate data retrieval and interaction.

### Chat Endpoint

- **URL:** `/api/chat/`
- **Method:** `POST`
- **Description:** Handles chat queries and returns filtered travel listings based on user input.
- **Request Body:**

  ```json
  {
      "query": "Find hotels near Central Park."
  }
  ```

- **Response:**

  ```json
  {
      "filters": ["price", "location"],
      "listings": [
          {
              "idStr": "12345",
              "name": "Hotel Sunshine",
              "description": "A lovely place to stay...",
              "url": "http://example.com/hotel-sunshine",
              "image_url": "http://example.com/images/hotel-sunshine.jpg",
              "price": 150,
              "stars": 4.5,
              "review_count": 200,
              "Accuracy": 4.7,
              "Communication": 4.8,
              "Cleanliness": 4.9,
              "Location": 4.6,
              "CheckIn": 4.5,
              "Value": 4.7
          }
          // More listings...
      ]
  }
  ```

### Test Data Endpoint

- **URL:** `/api/test/`
- **Method:** `GET`
- **Description:** Returns a confirmation message to verify that the backend is operational.
- **Response:**

  ```json
  {
      "message": "Backend is running smoothly!"
  }
  ```

## Testing

Ensure that both frontend and backend components function correctly by performing the following tests.

### Backend Testing

Navigate to the backend directory and run Django tests.

```bash
cd backend
python manage.py test
```

### Frontend Testing

Navigate to the frontend directory and run tests using your package manager.

##### Using npm:

```bash
npm run test
```

##### Using Yarn:

```bash
yarn test
```

## Contributing

Contributions are welcome to enhance the functionality and features of the Simple Travel Application. Follow the guidelines below to contribute effectively.

### How to Contribute

1. **Fork the Repository**

   Click the "Fork" button at the top right of the repository page to create your own fork.

2. **Clone Your Fork**

   ```bash
   git clone https://github.com/yourusername/simple-travel-application.git
   cd simple-travel-application
   ```

3. **Create a Feature Branch**

   ```bash
   git checkout -b feature/YourFeature
   ```

4. **Commit Your Changes**

   ```bash
   git commit -m "Add Your Feature"
   ```

5. **Push to Your Fork**

   ```bash
   git push origin feature/YourFeature
   ```

6. **Open a Pull Request**

   Navigate to the original repository and click the "Compare & pull request" button to submit your changes.

### Coding Standards

- Follow [PEP 8](https://pep8.org/) style guidelines for Python code.
- Adhere to best practices for JavaScript and React in the frontend.
- Write clear and concise commit messages.
- Include tests for new features or bug fixes.
- Update documentation as necessary.

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

For any questions, suggestions, or support, please reach out to:

- **Qavi Inan** - [qaviinan@gmail.com](mailto:qaviinan@gmail.com)

```
