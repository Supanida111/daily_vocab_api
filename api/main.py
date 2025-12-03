# api/app/main.py
from typing import List, Dict, Any

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Word, PracticeSession
from app.utils import mock_ai_validation


app = FastAPI(title="Vocabulary Practice API")

# ------------ CORS ให้ frontend (localhost:3000) เรียกได้ -------------
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------- Pydantic Schemas ---------------------


class ValidateSentenceRequest(BaseModel):
    word_id: int
    sentence: str


class ValidateSentenceResponse(BaseModel):
    score: float
    level: str
    suggestion: str
    corrected_sentence: str


# --------------------- Basic endpoints ----------------------


@app.get("/")
def read_root() -> Dict[str, Any]:
    return {
        "message": "Vocabulary Practice API",
        "endpoints": {
            "word": "/api/word",
            "validate": "/api/validate-sentence",
            "summary": "/api/summary",
            "history": "/api/history",
            "health": "/health",
        },
    }


@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok"}


# --------------------- API: GET /api/word -------------------


@app.get("/api/word")
def get_random_word(db: Session = Depends(get_db)) -> Dict[str, Any]:
    words: List[Word] = db.query(Word).all()
    if not words:
        raise HTTPException(status_code=404, detail="No words in database")

    # random แบบง่าย ๆ ใช้ offset ด้วย COUNT()
    # (ถ้าอยาก random จริง ๆ ใช้ random.choice ใน Python ก็ได้)
    import random

    word = random.choice(words)

    return {
        "id": word.id,
        "word": word.word,
        "definition": word.definition,
        "difficulty_level": word.difficulty_level,
    }


# --------- API: POST /api/validate-sentence (โจทย์หลัก) ----


@app.post(
    "/api/validate-sentence",
    response_model=ValidateSentenceResponse,
)
def validate_sentence(
    request: ValidateSentenceRequest,
    db: Session = Depends(get_db),
):
    # 1) ดึงข้อมูลคำศัพท์จาก DB ด้วย word_id
    word: Word | None = db.query(Word).filter(Word.id == request.word_id).first()
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")

    # 2) เรียกใช้ logic mock AI
    result = mock_ai_validation(
        sentence=request.sentence,
        word=word.word,
        difficulty_level=word.difficulty_level,
    )

    # 3) บันทึกประวัติการฝึกลงตาราง practice_sessions
    practice = PracticeSession(
        word_id=word.id,
        user_sentence=request.sentence,
        score=result["score"],
        feedback=result["suggestion"],
        corrected_sentence=result["corrected_sentence"],
    )
    db.add(practice)
    db.commit()
    db.refresh(practice)

    # 4) ส่ง response JSON กลับไป
    return ValidateSentenceResponse(
        score=result["score"],
        level=result["level"],
        suggestion=result["suggestion"],
        corrected_sentence=result["corrected_sentence"],
    )


# --------------------- API: GET /api/summary ----------------


@app.get("/api/summary")
def get_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    total_practices = db.query(PracticeSession).count()

    if total_practices == 0:
        return {
            "total_practices": 0,
            "average_score": 0.0,
            "total_words_practiced": 0,
            "level_distribution": {
                "Beginner": 0,
                "Intermediate": 0,
                "Advanced": 0,
            },
        }

    avg_score = db.query(func.avg(PracticeSession.score)).scalar() or 0
    total_words_practiced = (
        db.query(PracticeSession.word_id).distinct().count()
    )

    level_rows = (
        db.query(Word.difficulty_level, func.count(PracticeSession.id))
        .join(Word, Word.id == PracticeSession.word_id)
        .group_by(Word.difficulty_level)
        .all()
    )

    level_distribution: Dict[str, int] = {
        level: count for level, count in level_rows
    }

    # ให้มี key ครบทุก level
    for level in ["Beginner", "Intermediate", "Advanced"]:
        level_distribution.setdefault(level, 0)

    return {
        "total_practices": total_practices,
        "average_score": float(avg_score),
        "total_words_practiced": total_words_practiced,
        "level_distribution": level_distribution,
    }


# --------------------- API: GET /api/history ----------------


@app.get("/api/history")
def get_history(
    limit: int = 20,
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    rows = (
        db.query(PracticeSession, Word)
        .join(Word, Word.id == PracticeSession.word_id)
        .order_by(PracticeSession.practiced_at.desc())
        .limit(limit)
        .all()
    )

    history: List[Dict[str, Any]] = []
    for practice, word in rows:
        history.append(
            {
                "id": practice.id,
                "word": word.word,
                "difficulty_level": word.difficulty_level,
                "sentence": practice.user_sentence,
                "score": float(practice.score),
                "feedback": practice.feedback,
                "corrected_sentence": practice.corrected_sentence,
                "practiced_at": practice.practiced_at.isoformat()
                if practice.practiced_at
                else None,
            }
        )

    return history
