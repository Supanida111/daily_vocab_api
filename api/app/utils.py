# api/app/utils.py
from typing import Dict


def mock_ai_validation(sentence: str, word: str, difficulty_level: str) -> Dict:
    """
    ฟังก์ชันจำลองการตรวจสอบจาก AI
    - ให้คะแนนแบบง่าย ๆ จากความยาวประโยค + การมีคำ vocab
    - คืนค่าตามรูปแบบที่ assignment ต้องการ
    """
    clean_sentence = sentence.strip()
    word_in_sentence = word.lower() in clean_sentence.lower()

    # ให้คะแนนจากจำนวนคำ (สูงสุด 10)
    word_count = len(clean_sentence.split())
    base_score = min(10.0, max(0.0, word_count * 1.0))

    # ถ้ามีคำ vocab ให้โบนัส +2
    if word_in_sentence:
        base_score = min(10.0, base_score + 2.0)

    # สร้าง feedback ตามช่วงคะแนน
    if base_score >= 8.0:
        suggestion = "Great job! Your sentence looks very natural."
    elif base_score >= 6.0:
        suggestion = "Good! You can add more detail to make it better."
    else:
        suggestion = "Try again. Check grammar and make a clearer sentence."

    corrected = clean_sentence.capitalize()
    if corrected and not corrected.endswith("."):
        corrected += "."

    return {
        "score": round(base_score, 1),
        "level": difficulty_level,          # ส่ง level กลับไปด้วย
        "suggestion": suggestion,
        "corrected_sentence": corrected or "",
    }
