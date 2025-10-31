# General
- [x] Decide specialized travel app
    => ski trips
- [ ] Which special attributes might be needed for Skiing??
- [ ] Setup VS Code "shared coding"
- [ ] discuss with teachers how many points you could get with the features you plan to implement

    
# Mandatory functionality
- [ ] managing user accounts
    - [ ] users can create accounts
    - [ ] users can log into their accounts
    - [ ] users can logout
    - [ ] all controllers/views only accessible by authenticated users
        - [ ] exception is the landing page and ressources needed to create accounts and login
- [ ] displaying and editing user profiles
    - [ ] users can create accounts
    - [ ] users can edit a short description/bio of themselves
    - [ ] other users can read the bio
    - [ ] every ention to a user in the application must link to their profile view
- [ ] creating trip proposals
    - [ ] users can create new trip proposals => they become a participant of it and have editing permissions
        - [ ] maximum number of participants has to be set by creation
        - [ ] specify tentative information about trip (not everything has to be set immediately)
            - departure locations
            - destination
            - dates
            - budget
            - types of activities to be done
            - accomodation
            - trip duration
            etc
    - [ ] users can specify information (departure etc - what special information for skiing? maybe smth like skill level required, blue/red/black routes)
    - [ ] users can edit "not final" information (trip dates can be provided as a range of possible dates and durations e.g. from 6 to 9 days between June 1st and July 31st, blank destination or list of possible destinations)
    - [ ] users must specify a maximum number of participants at creation time - might be adjustable
- [ ] browsing, joining and leaving trip proposals
    - [ ] users can see list of trip proposals (from other users and still accepting new participants)
        - [ ] with current details and number of participants joined vs max participants allowed
    - [ ] users can join trips if possible => they become a participant of it
- [ ] displaying and editing trip proposal details
    - [ ] participants can see all details including the list of participants => central view of a trip proposal
    - [ ] particpants with editing permissions can edit details
    - [ ] editors can give editing permissions to other participants
    - [ ] editors can mark details as final => no longer open to discussion
        - [ ] so every single detail can be open for discussion if not final - maybe add an own small message board for each detail with a number of messages for this detail indicating how much was already written about it?
        - [ ] final marked details can not longer be edited
            - [ ] but can editors still change the mark of details from final to open?
- [ ] posting to message boards
    - [ ] participants can post and see other messages
        => when a user posts a message to the message board of a trip proposal, the form should include a hidden field with the identifier of the trip proposal
    - [ ] messages are shown from most recent to oldest
        - [ ] including name of author and timestamp
        - [ ] no threads or replies needed
- [ ] creating meetups
    - [ ] participants with editing skills can set up meetups
    - [ ] provide date, time and location
        - bars
        - social centers
    - [ ] participants are able to see the list of scheduled meetups for every trip they participate
- [ ] leave trips
    - [ ] participants can leave trips
    - [ ] no access anymore to details and message board
    - [ ] participants that is the only editor cannot leave a trip if its not finalized or cancelled
- [ ] closing trip proposals to new participants
    - [ ] other users cannot join anymore
- [ ] finalizing or cancelling trip proposals
    - [ ] editors can finalize or cancel trips
        - open
        - closed_to_new_participants
        - finalized
            - no edit/messaging anymore possible
            - see details still possible
        - cancelled
            - no edit/messaging anymore possible
            - see details still possible
    - [ ] only finalize if everything has been planned
    - [ ] trip becomes read only
        - [ ] no new messages, details not editable, no new participants can join, no longer discoverable by other users
    - [ ] participants can still access the details and the message board


# Models
- [ ] Users
    - [ ] email address
    - [ ] password (salted, encrypted)
    - [ ] bio/description about themselves
- [ ] Trip proposals
    - [ ] current information...
    - [ ] max number of participants
    - [ ] current status (open, closed etc)
        => use enumarated data types
            ```
            import enum

            (...)

            class ProposalStatus(enum.Enum):
                open = 1
                closed_to_new_participants = 2
                finalized = 3
                cancelled = 4

            # Use the enumerated type in the model
            class DateProposal(db.Model):
                (...)
                status: Mapped["ProposalStatus"]
                (...)
            The syntax to access these columns in your model objects is as follows:

            Copy code icon
            # Create a new instance of a date proposal
            proposal = model.TripProposal(
                (...)
                status=model.TripProposal.open,
                (...)
            )

            (...)

            # Check the status of a proposal
            if proposal.status == model.TripProposal.closed_to_new_participants:
                (...)

            {% if proposal.status == proposal.status.__class__.finalized %}
            ```
    - [ ] every detail (departure etc) has boolean field indicating whether its final or not
- [ ] Messages
    - [ ] text
    - [ ] timestamp
    - [ ] user who posted them (many to one relationship with users)
    - [ ] trip proposal they belong to (many to one relationship)
- [ ] Trip proposal participation (many to many relationship)
    - [ ] participants who have editing permissions or not (explicit entity for this relationship needed)
        - [ ] entity should contain
            - [ ] permissions (editing or not)
            - [ ] user that is participating and editor (many to one relationship)
            - [ ] trip proposal the editors are participating in (many to one relationship)
- [ ] Meetups
    - [ ] date
    - [ ] time
    - [ ] location
    - [ ] trip proposal they belong to (many to one relationship)
    - [ ] user that created it (many to one relationship)


# Additional functionality
- [ ] user can check a map where they had their trips - leaflet.js
- [ ] statistics of your trips
- [ ] follower
- [ ] "live" messages via async JS
- [ ] "brilliant" user interface
    - remarkable appearance at level of current standards for professional applications


# Requirements
- [x] developed in Python with Flask
- [ ] must work with infra from lab with assigned database
- [ ] views of application are clear and easy to use
- [ ] potential error situations are properly handled, giving users feedback when appropriate
- [ ] proper access controls
- [ ] secure application (no SQLI, no XSS)


# Statement about AI
- [ ] Whether they used generative artificial intelligence tools in the development of their project
- [ ] If they used them, the name of the generative artificial tool or tools they used, how they used them, for what purposes and *in which parts of the code.*
    e.g.
        You can ask it about fragments of code you don't understand.
        You can ask it to look for errors in pieces of code you wrote.
        You can use it as an auto-completion assistant in your development environment, in order to get quick suggestions of short code fragments as you type.
        You can ask it to produce a few lines of code to solve a specific problem.
