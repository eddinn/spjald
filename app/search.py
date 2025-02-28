from flask import current_app
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import Post


def search_posts(session: Session, search_term: str):
    search_pattern = f"%{search_term.lower()}%"
    results = session.query(Post).filter(
        or_(
            Post.title.ilike(search_pattern),
            Post.body.ilike(search_pattern),
            # Add other fields here as needed
        )
    ).all()
    return results
