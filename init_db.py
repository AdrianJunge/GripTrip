#!/usr/bin/env python3
from server import create_app, db, model
from server.model import Message, Proposal, ProposalParticipant, ProposalParticipantRole, User, Country
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

        countries = [
        ("ALB", "Albania"),
        ("AUT", "Austria"),
        ("BEL", "Belgium"),
        ("BIH", "Bosnia and Herzegovina"),
        ("BGR", "Bulgaria"),
        ("HRV", "Croatia"),
        ("CYP", "Cyprus"),
        ("CZE", "Czechia"),
        ("DNK", "Denmark"),
        ("EST", "Estonia"),
        ("FIN", "Finland"),
        ("FRA", "France"),
        ("DEU", "Germany"),
        ("GRC", "Greece"),
        ("HUN", "Hungary"),
        ("ISL", "Iceland"),
        ("IRL", "Ireland"),
        ("ITA", "Italy"),
        ("LVA", "Latvia"),
        ("LIE", "Liechtenstein"),
        ("LTU", "Lithuania"),
        ("LUX", "Luxembourg"),
        ("MLT", "Malta"),
        ("MDA", "Moldova"),
        ("MCO", "Monaco"),
        ("MNE", "Montenegro"),
        ("NLD", "Netherlands"),
        ("MKD", "North Macedonia"),
        ("NOR", "Norway"),
        ("POL", "Poland"),
        ("PRT", "Portugal"),
        ("ROU", "Romania"),
        ("RUS", "Russia"),
        ("SMR", "San Marino"),
        ("SRB", "Serbia"),
        ("SVK", "Slovakia"),
        ("SVN", "Slovenia"),
        ("ESP", "Spain"),
        ("SWE", "Sweden"),
        ("CHE", "Switzerland"),
        ("TUR", "Turkey"),
        ("UKR", "Ukraine"),
        ("GBR", "United Kingdom"),
        ("VAT", "Vatican City"),
        ]

        for code, name in countries:
            if not Country.query.get(code):
                db.session.add(Country(code=code, name=name))
        db.session.commit()
        print("Populated countries table.")

        
        testuser = User(
            email="a@a",
            username="testuser",
            password=generate_password_hash("a")
        )
        mary = User(
            email="mary@mary",
            username="mary",
            password=generate_password_hash("a")
        )
        testuser_trip = Proposal(
            user=testuser,
            title="Test Trip",
            max_participants=5,
        )

        testuser_participant = ProposalParticipant(
            user=testuser,
            proposal=testuser_trip,
            permission=ProposalParticipantRole.ADMIN
        )
        mary_participant = ProposalParticipant(
            user=mary,
            proposal=testuser_trip,
            permission=ProposalParticipantRole.EDITOR
        )
        testuser_trip.participants.extend([testuser_participant, mary_participant])

        message = Message(
            proposal=testuser_trip,
            user=testuser,
            content="Welcome to the test trip!"
        )
        message2 = Message(
            proposal=testuser_trip,
            user=mary,
            content="This is a reply to the first message.",
            response_to=message
        )
        message3 = Message(
            proposal=testuser_trip,
            user=mary,
            content="This is another message.",
        )
        message4 = Message(
            proposal=testuser_trip,
            user=testuser,
            content="Replying to Mary's message.",
            response_to=message2
        )
        message5 = Message(
            proposal=testuser_trip,
            user=testuser,
            content="Another reply to the first message but this time its very very long to test how the UI handles long messages. " * 5,
            response_to=message
        )
        message6 = Message(
            proposal=testuser_trip,
            user=mary,
            content="Continuing the discussion here.",
        )
        message7 = Message(
            proposal=testuser_trip,
            user=mary,
            content="Adding more to the conversation.",
            response_to=message5,
        )
        
        db.session.add(testuser)
        db.session.add(mary)
        db.session.add(testuser_participant)
        db.session.add(mary_participant)
        db.session.add(testuser_trip)
        db.session.add(message)
        db.session.add(message2)
        db.session.add(message3)
        db.session.add(message4)
        db.session.add(message5)
        db.session.add(message6)
        db.session.add(message7)
        db.session.commit()

        print(f"Prepared database with initial data.")

if __name__ == "__main__":
    init_database()
