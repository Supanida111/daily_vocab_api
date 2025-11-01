from fastapi import FastAPI, HTTPException
from app.schemas import WordResponse
from app.routers import words

# Initialize FastAPI app
app = FastAPI(
    title="Vocabulary Practice API",
    version="1.0.0",
    description="API for vocabulary practice and learning"
)

app.include_router(words.router, prefix="/api", tags=["words"])

@app.get("/api/word", response_model=WordResponse)
def get_random_word():
    """Get a random word"""
    # TODO Write logic here....
    """
    return {
        "word": "example",
        "definition": "a representative form or pattern",
        "difficulty_level": "Beginner",

    }
    
    return WordResponse(
        id=2,
        word= "book",
        definition= "Reading material",
        difficulty_level= "Beginner"
     )
     """
    words= []
    if len(words) == 0:
        raise HTTPException(
            status_code=404,
            detail="No word available in database"
        )


@app.get("/")
def read_root():
    return {
        "message": "Vocabulary Practice API",
        "version": "1.0.0",
        "endpoints": {
            "random_word": "/api/word",
            "validate": "/api/validate-sentence",
            "summary": "/api/summary",
            "history": "/api/history"
        }
    }