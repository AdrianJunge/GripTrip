#!/usr/bin/env python3
import datetime
from server import create_app, db, model
from server.model import Message, Proposal, ProposalParticipant, ProposalParticipantRole, User
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

        testuser = User(
            email="a@a",
            username="testuser",
            password=generate_password_hash("a"),
        )
        mary = User(
            email="mary@mary",
            username="mary",
            password=generate_password_hash("a"),
        )
        testuser_trip = Proposal(
            user=testuser,
            title="Test Trip",
            max_participants=5,
            destinations=["New York", "Los Angeles", "Chicago"],
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


        another_trip = Proposal(
            user=mary,
            title="Mary's Trip",
            max_participants=3,
            destinations=["Paris", "London", "Berlin"],
        )
        mary_participant_another_trip = ProposalParticipant(
            user=mary,
            proposal=another_trip,
            permission=ProposalParticipantRole.EDITOR
        )
        another_trip.participants.extend([mary_participant_another_trip])

        message = Message(
            proposal=testuser_trip,
            user=testuser,
            content="Welcome to the test trip!",
            timestamp_raw=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)
        )
        message2 = Message(
            proposal=testuser_trip,
            user=mary,
            content="This is a reply to the first message.",
            timestamp_raw=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1, hours=-1),
            response_to=message
        )
        message3 = Message(
            proposal=testuser_trip,
            user=mary,
            content="This is another message.",
            timestamp_raw=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1, hours=-2),
        )
        message4 = Message(
            proposal=testuser_trip,
            user=testuser,
            content="Replying to Mary's message.",
            timestamp_raw=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1, hours=-3),
            response_to=message2
        )
        message5 = Message(
            proposal=testuser_trip,
            user=testuser,
            content="Another reply to the first message but this time its very very long to test how the UI handles long messages. " * 5,
            timestamp_raw=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1, hours=-4),            
            response_to=message
        )
        message6 = Message(
            proposal=testuser_trip,
            user=mary,
            content="Continuing the discussion here.",
            timestamp_raw=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1, hours=-5),
        )
        message7 = Message(
            proposal=testuser_trip,
            user=mary,
            content="Adding more to the conversation.",
            timestamp_raw=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1, hours=-6),
            response_to=message5,
        )
        
        db.session.add(testuser)
        db.session.add(mary)
        db.session.add(testuser_participant)
        db.session.add(mary_participant)
        db.session.add(mary_participant_another_trip)
        db.session.add(testuser_trip)
        db.session.add(another_trip)
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
