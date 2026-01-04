import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime
import anthropic

from .database import get_db
from .enums import FactCategory
from .models import Fact, AppState
from .schemas import FactResponse

router = APIRouter(prefix="/api/v1")

current_fact_category_index = 0

async def _generate_fact(db: Session) -> Fact:
    """Generate a random fact using AI"""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # Get current index from database with row locking
    state = db.query(AppState).filter(AppState.key == "fact_category_index").with_for_update().first()
    
    if not state:
        # Initialize if doesn't exist
        print("init state")
        state = AppState(key="fact_category_index", value=0)
        db.add(state)
        db.flush()
    
    category = list(FactCategory)[state.value]
    
    # Update index for next time
    state.value = (state.value + 1) % len(FactCategory)
    db.commit()

    # Get previous facts with the same category to filter LLM response
    prev_facts = await _get_facts_by_category(db, category, 10)
    prev_facts_contents = " ".join(fact.content for fact in prev_facts)
    print(prev_facts_contents)


    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=256,
            temperature=0.9,
            messages=[
                {
                    "role": "user",
                    "content": f"""Generate one interesting, accurate fact about {category.value}. Just the fact, no preamble or formating symbols.
                    
                    Do *not* generate any, or similar, facts like these: {prev_facts_contents}""",
                }
            ],
        )
        fact_content = message.content[0].text

        fact = Fact(content=fact_content, category=category)
        return fact

    except Exception as e:
        print(f"Error generating fact: {e}")
        raise HTTPException(500, "Failed to generate fact")

async def _save_fact(db: Session, fact: Fact) -> None:
    """Save a fact to the database"""
    try:
        db.add(fact)
        db.commit()
        db.refresh(fact)

    except Exception as e:
        db.rollback()
        print(f"Error saving fact to database: {e}")
        raise HTTPException(500, "Failed to generate fact, database error")

async def _get_facts_by_category(db: Session, category: FactCategory, limit: int | None = None):
    """Get all facts for a specific category"""
    query = db.query(Fact).filter(Fact.category == category).order_by(Fact.created_at.desc())
    
    if limit:
        query = query.limit(limit)
    
    return query.all()

@router.get("/facts/today", response_model=FactResponse)
async def get_todays_fact(db: Session = Depends(get_db)):
    """Get todays new fact"""
    today = date.today()

    # Get the latest fact
    fact = (
        db.query(Fact)
        .filter(
            Fact.created_at >= datetime.combine(today, datetime.min.time()),
            Fact.created_at < datetime.combine(today, datetime.max.time()),
        )
        .first()
    )

    if not fact:
        # Generate a new fact
        fact = await _generate_fact(db)
        await _save_fact(db, fact)

    return fact

@router.get("/facts/history", response_model=list[FactResponse])
def get_fact_history(limit: int = 30, db: Session = Depends(get_db)):
    """Get previous facts"""
    facts = db.query(Fact).order_by(Fact.created_at.desc()).limit(limit).all()
    return facts
