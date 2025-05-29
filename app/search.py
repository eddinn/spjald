from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import Post

def search_posts(session: Session, search_term: str):
    """
    Search for posts by partial match on several client fields.
    
    Args:
        session (Session): SQLAlchemy session to use for the query.
        search_term (str): The term to search for in client fields.
        
    Returns:
        List[Post]: List of Post objects matching the search criteria.
    """
    search_pattern = f"%{search_term}%"
    fields_to_search = [
        Post.clientname,
        Post.clientss,
        Post.clientemail,
        Post.clientphone,
        Post.clientaddress,
    ]
    search_conditions = [field.ilike(search_pattern) for field in fields_to_search]
    return session.query(Post).filter(or_(*search_conditions)).all()