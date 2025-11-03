#!/usr/bin/env python3
from server import create_app, db
from server.model import User
from sqlalchemy import text
from werkzeug.security import generate_password_hash

def init_database():
    app = create_app()
    
    with app.app_context():
        with db.engine.connect() as connection:
            connection.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            connection.commit()
        
        db.drop_all()
        print("Dropped existing tables.")
        
        with db.engine.connect() as connection:
            connection.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            connection.commit()
        
        db.create_all()
        print("Created tables successfully!")
        
        mary = User(
            email="a@a",
            username="testuser",
            password=generate_password_hash("a")
        )
        
        db.session.add(mary)
        db.session.commit()

        print(f"Prepared database with initial data.")

if __name__ == "__main__":
    init_database()
