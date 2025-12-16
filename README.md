# Social Marketing Agency Managed By AI Agents

This project is an AI-powered platform for managing social marketing campaigns, analytics, and customer engagement. It leverages FastAPI, MongoDB, and integrations with Facebook and AI services to automate and optimize social media marketing for agencies.

---

## Features

- **AI-Driven Campaign Management:** Automate ad and post creation, competitor analysis, and customer insights using OpenAI and HuggingFace models.
- **Analytics Dashboard:** Visualize campaign performance and customer engagement in real-time.
- **Facebook Integration:** Manage Facebook ads and posts directly from the platform.
- **Modular Architecture:** Easily extend models and routes for new social platforms or analytics.

---

## Project Structure

```
SRS.pdf
dashboard/
  index.html
  script.js
  style.css
docker/
  docker-compose.yml
src/
  main.py
  requirments.txt
  controller/
  models/
    __init__.py
    AdModel.py
    BaseModel.py
    CompetitorModel.py
    CustomerModel.py
    PostModel.py
  routes/
    __init__.py
    analytics.py
    base.py
    facebook.py
    responses.py
  stores/
```

- **dashboard/**: Frontend dashboard for analytics and management.
- **docker/**: Docker configuration for deployment.
- **src/**: Main backend source code.
  - **models/**: Database models for Ads, Posts, Customers, Competitors.
  - **routes/**: FastAPI route handlers for analytics, Facebook, and base endpoints.
  - **controller/** and **stores/**: (Reserved for business logic and data access layers.)

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js (for dashboard, if needed)
- Docker (optional, for containerized deployment)

### Installation

1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd Social-Marketing-Agency-Manged-By-AI-Agents
   ```

2. **Install Python dependencies:**
   ```sh
   pip install -r src/requirements.txt
   ```

3. **Run the application:**
   ```sh
   uvicorn src.main:app --reload
   ```

4. **Open the dashboard:**
   - The app will run at `http://localhost:8000`
   - It will automatically redirect to the login page.
   - You can also optionally run with Docker:
     ```sh
     docker-compose up
     ```

---

## Configuration

- Environment variables can be managed using `.env` files (see `python-dotenv` in requirements).
- MongoDB connection and API keys for OpenAI, Facebook, etc., should be set in your environment.

---

## Dependencies

See [`src/requirments.txt`](src/requirments.txt) for the full list, including:
- `fastapi`, `uvicorn`, `motor`, `pydantic-mongo`
- `openai`, `huggingface-hub`
- `facebook-business`, `requests`, `python-jose`

---

## License

This project is for educational and demonstration purposes.

---

## Documentation

- See [SRS.pdf](SRS.pdf) for the full Software Requirements Specification.
- Backend code is organized for easy extension and maintenance.

---

## Contributing

Pull requests and issues are welcome!

---

## Contact

For questions or support, please open an issue on GitHub.


<!-- uvicorn src.main:app --reload -->