# General
- [x] Ask Josue how you are supposed to do the statement if you use e.g. github copilot
    - memorize/write down every single line/part of the code that was completed by copilot?
- [x] Decide specialized travel app
    => ski trips
- [x] Setup VS Code "shared coding"

# Mandatory functionality
- [x] managing user accounts
    - [x] users can create accounts
    - [x] users can log into their accounts
    - [x] users can logout
    - [x] all controllers/views only accessible by authenticated users (test this one in the very end)
        - [x] exception is the landing page and ressources needed to create accounts and login
- [x] displaying and editing user profiles
    - [x] users can edit a short description/bio of themselves
    - [x] other users can read the bio
- [x] creating trip proposals
    - [x] users can create new trip proposals => they become a participant of it and have editing permissions
        - [x] maximum number of participants has to be set by creation
        - [x] specify tentative information about trip (not everything has to be set immediately)
    - [x] users can specify information (departure etc - what special information for skiing? maybe smth like skill level required, blue/red/black routes)
    - [x] users must specify a maximum number of participants at creation time - might be adjustable
    - [x] users can edit "not final" information (trip dates can be provided as a range of possible dates and durations e.g. from 6 to 9 days between June 1st and July 31st, blank destination or list of possible destinations)
    - [x] view trip alle details anzeigen inklusive "final" vs "not final"
    - [x] check validity of given attributes
        - e.g. end-date > start-date, budget is float etc
- [x] browsing, joining and leaving trip proposals
    - [x] users can see list of trip proposals (from other users and still accepting new participants)
        - [x] with current details and number of participants joined vs max participants allowed
    - [x] users can join trips if possible => they become a participant of it
        - [x] add explicit "join" button
        - [x] don't make whole card clickable
    - [x] creator name has to link to profile
    - [x] still list trips you are a participant in? Maybe different color better
    - [x] List participating trips in user profil

# Rest of mandatory functionality
- [x] displaying and editing trip proposal details
    - [x] participants can see all details including the list of participants => central view of a trip proposal
    - [x] particpants with editing permissions can edit details
    - [x] editors can give editing permissions to other participants
    - [x] editors can mark details as final => no longer open to discussion
        - [x] so every single detail can be open for discussion if not final - maybe add an own small message board for each detail with a number of messages for this detail indicating how much was already written about it?
        - [x] final marked details can not longer be edited
            - [x] but can editors still change the mark of details from final to open?
- [x] posting to message boards
    - [x] participants can post and see other messages
        => when a user posts a message to the message board of a trip proposal, the form should include a hidden field with the identifier of the trip proposal
    - [x] messages are shown from most recent to oldest
        - [x] including name of author and timestamp
        - [x] no threads or replies needed
    - [x] Replies like in WhatsApp
        - [x] Clickable so it scrolls automatically to the original message
- [x] leave trips
    - [x] participants can leave trips
    - [x] no access anymore to details and message board
    - [x] participants that is the only editor cannot leave a trip if its not finalized or cancelled
- [x] closing trip proposals to new participants
    - [x] other users cannot join anymore
- [x] finalizing or cancelling trip proposals
    - [x] editors can finalize or cancel trips
        - open
        - closed_to_new_participants
        - finalized
            - no edit/messaging anymore possible
            - see details still possible
        - cancelled
            - no edit/messaging anymore possible
            - see details still possible
    - [x] only finalize if everything has been planned
    - [x] trip becomes read only
        - [x] no new messages
        - [x] details not editable
        - [x] no new participants can join
        - [x] no longer discoverable by other users
        - [x] only editors can unfinalize the trip
    - [x] participants can still access the details and the message board
- [x] creating meetups
    - [x] participants with editing skills can set up meetups
    - [x] provide date, time and location
        - bars
        - social centers
    - [x] participants are able to see the list of scheduled meetups for every trip they participate
- [x] every mention to a user in the application must link to their profile view
    - search for ".username" in the application code

# Models
- [x] Users
    - [x] email address
    - [x] password (salted, encrypted)
    - [x] bio/description about themselves
- [x] Trip proposals
    - [x] current information...
            - departure locations
            - destination
            - dates
            - budget
            - types of activities to be done
            - accomodation
            - trip duration
    - [x] max number of participants
    - [x] current status (open, closed etc)
    - [x] every detail (departure etc) has boolean field indicating whether its final or not
- [x] Messages
    - [x] text
    - [x] timestamp
    - [x] user who posted them (many to one relationship with users)
    - [x] trip proposal they belong to (many to one relationship)
- [x] Trip proposal participation (many to many relationship)
    - [x] participants who have editing permissions or not (explicit entity for this relationship needed)
        - [x] entity should contain
            - [x] permissions (editing or not)
            - [x] user that is participating and editor (many to one relationship)
            - [x] trip proposal the editors are participating in (many to one relationship)
- [x] Meetups
    - [x] date
    - [x] time
    - [x] location
    - [x] trip proposal they belong to (many to one relationship)
    - [x] user that created it (many to one relationship)


# Additional functionality
- [x] user can check a map where they had their trips - leaflet.js
- [x] "brilliant" user interface
    - remarkable appearance at level of current standards for professional applications

# More
- [ ] Fix search term hiding/showing markers on map
- [ ] Finalize `README.md`
- [ ] Climbing related field (remove activities field)
    - [ ] Level of difficulty
    - [ ] Climbing gear needed
    - [ ] Specific climbing location (e.g. mountain or gym)

# Requirements
- [x] developed in Python with Flask
- [x] must work with infra from lab with assigned database
- [x] views of application are clear and easy to use
- [x] potential error situations are properly handled, giving users feedback when appropriate
- [x] proper access controls
- [x] secure application (no SQLI, no XSS)
