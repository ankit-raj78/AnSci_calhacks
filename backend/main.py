from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
from pathlib import Path
import traceback
import logging
from ansci.workflow import create_animation

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create an output directory for animations
output_dir = Path("output")
output_dir.mkdir(parents=True, exist_ok=True)

# Mount the output directory to serve static files (the generated videos)
app.mount("/videos", StaticFiles(directory=output_dir), name="videos")

@app.post("/api/create-animation")
async def create_animation_endpoint(
    file: UploadFile = File(...), 
    scope: str = Form(...)
):
    """
    API endpoint to generate an animation from a PDF file.
    
    Args:
        file: The uploaded PDF file.
        scope: The animation scope (e.g., "High-Level Summary", "Core Concepts").
    """
    logger.info(f"Received request for animation generation. Scope: {scope}, File: {file.filename}")

    if not file.filename.lower().endswith('.pdf'):
        logger.error("Uploaded file is not a PDF.")
        raise HTTPException(status_code=400, detail="File must be a PDF.")

    try:
        # Read the uploaded file into a BytesIO object
        paper_bytes = BytesIO(await file.read())
        
        # Use the scope as the prompt for animation generation
        prompt = scope
        
        logger.info("Starting animation generation workflow...")
        # The create_animation function expects an output path as a string
        video_paths = create_animation(paper_bytes, str(output_dir), prompt)
        
        if video_paths:
            logger.info(f"Successfully generated {len(video_paths)} videos.")
            # Create web-accessible URLs for the videos
            video_urls = [f"/videos/{Path(p).name}" for p in video_paths]
            return JSONResponse(
                content={
                    "message": "Animation generated successfully!",
                    "video_urls": video_urls,
                }
            )
        else:
            logger.error("Animation generation failed, no video paths returned.")
            raise HTTPException(status_code=500, detail="Failed to generate animations.")

    except Exception as e:
        logger.error(f"An error occurred during animation generation: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "AnSci Backend is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
