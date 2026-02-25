
import os
import pickle
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, Depends, HTTPException, status, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# --- Configuration & Setup ---

PROJECT_NAME = "Portfolio Website with Blog"

# CORS configuration
CORS_ALLOWED_ORIGINS = ["*"] # Allow all origins as per requirement

# AI configuration
AI_ENABLED = True # Based on BACKEND_PLAN: ai.enabled: true
MODEL_PATH = "model.pkl" # Not actually loaded, just for illustrative purposes
PREPROCESSOR_PATH = "preprocessor.pkl" # Not actually loaded, just for illustrative purposes

# Admin Authentication Configuration
FAKE_ADMIN_TOKEN = "supersecretadmintoken" # In a real app, this would be a secure token/JWT

# --- FastAPI App Initialization ---
app = FastAPI(
    title=PROJECT_NAME,
    description="A comprehensive backend for a personal portfolio and blog website.",
    version="0.1.0",
)

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- AI Model Loading (Stubbed) ---

class MockModel:
    """A mock machine learning model for demonstration purposes."""
    def predict(self, data: List[Dict[str, Any]]) -> List[float]:
        """
        Mocks a prediction. In a real scenario, this would use the loaded model.
        Returns a list of dummy scores based on input data.
        """
        print(f"MockModel received data for prediction: {data}")
        # Example: return average of numeric values, or a fixed score
        predictions = []
        for item in data:
            if isinstance(item, dict):
                numeric_values = [v for v in item.values() if isinstance(v, (int, float))]
                if numeric_values:
                    predictions.append(sum(numeric_values) / len(numeric_values))
                else:
                    predictions.append(0.5) # Default score if no numeric values
            else:
                predictions.append(0.5)
        return predictions

class MockPreprocessor:
    """A mock data preprocessor for demonstration purposes."""
    def preprocess(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Mocks data preprocessing. In a real scenario, this would apply transformations.
        Returns the data with a simple modification.
        """
        print(f"MockPreprocessor received data for preprocessing: {data}")
        processed_data = []
        for item in data:
            if isinstance(item, dict):
                processed_item = {f"processed_{k}": v * 10 if isinstance(v, (int, float)) else v for k, v in item.items()}
                processed_data.append(processed_item)
            else:
                processed_data.append(item)
        return processed_data

# Global variables for AI models
ml_model: Optional[MockModel] = None
preprocessor: Optional[MockPreprocessor] = None

if AI_ENABLED:
    try:
        # In a real application, these files would be loaded from disk:
        # with open(MODEL_PATH, "rb") as f:
        #     ml_model = pickle.load(f)
        # with open(PREPROCESSOR_PATH, "rb") as f:
        #     preprocessor = pickle.load(f)

        # For this stub, we instantiate our mock objects
        ml_model = MockModel()
        preprocessor = MockPreprocessor()
        print(f"AI models (mocked) '{MODEL_PATH}' and '{PREPROCESSOR_PATH}' initialized successfully.")
    except (FileNotFoundError, EOFError, pickle.UnpicklingError) as e:
        print(f"Warning: Could not load AI models. Reason: {e}. AI prediction will be unavailable.")
        AI_ENABLED = False # Disable AI if loading fails
    except Exception as e:
        print(f"An unexpected error occurred while initializing AI models: {e}. AI prediction will be unavailable.")
        AI_ENABLED = False

# --- Pydantic Models ---

class PredictionInput(BaseModel):
    """Input schema for the AI prediction endpoint."""
    data: List[Dict[str, Any]] = Field(
        ...,
        example=[{"feature1": 10, "feature2": 20}, {"feature1": 5, "feature2": 15}],
        description="A list of dictionaries, where each dictionary represents a data point for prediction."
    )

class PredictionOutput(BaseModel):
    """Output schema for the AI prediction endpoint."""
    predictions: List[float] = Field(
        ...,
        example=[0.75, 0.62],
        description="A list of prediction scores corresponding to the input data points."
    )
    status: str = "success"

class HealthCheckResponse(BaseModel):
    """Response model for the health check endpoint."""
    status: str = Field(..., example="healthy")
    timestamp: str = Field(..., example="2023-10-27T10:00:00Z")
    service: str = Field(..., example=PROJECT_NAME)


# --- Authentication Dependency ---

def authenticate_admin(token: str = Depends(lambda x: x.headers.get("X-Admin-Token"))) -> bool:
    """
    Dependency to authenticate admin users.
    Checks for a specific header `X-Admin-Token` with `FAKE_ADMIN_TOKEN`.
    """
    if not token or token != FAKE_ADMIN_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: Invalid or missing admin token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True

# --- Public Routes ---

@app.get("/", summary="Home Page")
async def read_home():
    """Returns data for the home page."""
    return {"message": "Welcome to my Portfolio!", "page": "Home"}

@app.get("/about", summary="About Page")
async def read_about():
    """Returns data for the about page."""
    return {"message": "Learn more about me here.", "page": "About"}

@app.get("/portfolio", summary="Portfolio Page")
async def read_portfolio():
    """Returns a list of portfolio projects."""
    return {"message": "Here are my projects.", "page": "Portfolio", "projects": ["Project A", "Project B", "Project C"]}

@app.get("/portfolio/{slug}", summary="Portfolio Project Detail Page")
async def read_portfolio_item(slug: str = Path(..., title="The slug of the portfolio project")):
    """Returns details for a specific portfolio project."""
    return {"message": f"Details for project: {slug}", "page": "Portfolio Detail", "project_slug": slug}

@app.get("/blog", summary="Blog Page")
async def read_blog():
    """Returns a list of blog posts."""
    return {"message": "Welcome to my blog!", "page": "Blog", "posts": ["Post 1", "Post 2", "Post 3"]}

@app.get("/blog/{slug}", summary="Blog Post Detail Page")
async def read_blog_post(slug: str = Path(..., title="The slug of the blog post")):
    """Returns details for a specific blog post."""
    return {"message": f"Details for blog post: {slug}", "page": "Blog Post Detail", "post_slug": slug}

@app.get("/contact", summary="Contact Page")
async def read_contact():
    """Returns information for the contact page."""
    return {"message": "Get in touch with me!", "page": "Contact", "email": "contact@example.com"}

# --- Admin Routes ---

@app.get("/admin/login", summary="Admin Login Page")
async def admin_login_page():
    """Returns a message for the admin login page (no authentication required for the page itself)."""
    return {"message": "Admin login portal. Please provide credentials.", "page": "Admin Login"}

@app.get("/admin/dashboard", summary="Admin Dashboard", dependencies=[Depends(authenticate_admin)])
async def admin_dashboard():
    """Returns data for the admin dashboard (requires authentication)."""
    return {"message": "Welcome to the Admin Dashboard!", "page": "Admin Dashboard", "status": "authenticated"}

@app.get("/admin/posts", summary="Admin Post Management Page", dependencies=[Depends(authenticate_admin)])
async def admin_posts():
    """Returns a list of posts for admin management (requires authentication)."""
    return {"message": "Manage your blog posts here.", "page": "Admin Posts", "posts_count": 5}

@app.get("/admin/posts/edit/{post_id}", summary="Admin Post Editor Page", dependencies=[Depends(authenticate_admin)])
async def admin_edit_post(post_id: int = Path(..., title="The ID of the post to edit")):
    """Returns data for editing a specific post (requires authentication)."""
    return {"message": f"Editing post with ID: {post_id}", "page": "Admin Post Editor", "post_id": post_id}

# --- Utility Routes ---

@app.get("/health", response_model=HealthCheckResponse, summary="Health Check Endpoint")
async def health_check():
    """
    Checks the health status of the application.
    Returns a simple JSON response indicating the service is healthy.
    """
    import datetime
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds") + "Z",
        service=PROJECT_NAME
    )

# --- AI Routes (Conditional) ---

if AI_ENABLED:
    @app.post("/predict", response_model=PredictionOutput, summary="AI Inference Endpoint")
    async def predict(input_data: PredictionInput):
        """
        Performs AI inference using the loaded model.
        Expects a list of dictionaries as input and returns predictions.
        """
        if ml_model is None or preprocessor is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI models are not loaded or available."
            )

        try:
            # 1. Preprocess the input data
            processed_input = preprocessor.preprocess(input_data.data)
            # 2. Make predictions using the model
            predictions = ml_model.predict(processed_input)
            return PredictionOutput(predictions=predictions, status="success")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred during AI prediction: {e}"
            )
else:
    print("AI features are disabled as per configuration or due to loading errors.")
    @app.post("/predict", summary="AI Inference Endpoint (Disabled)")
    async def predict_disabled():
        """
        This AI prediction endpoint is disabled.
        """
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AI features are disabled for this service."
        )


