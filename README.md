# UC3M - Web-App-Project
## Starting the app
To start the project with local docker setup use the `start.sh`.
To start the project with the remote database from the telematics lab use the `start_virtlab.sh`.
Both need and use `python3 -m venv`.

## Information
### Author names
- Adrian Junge | XXXXXX
- Liam van Doorn | 100575986
- Sam Parkin | 100577769

### Additional functionality to get evaluated
- **UI/UX design**
There's a base main view containing the most frequent functionality of the application, such as handling, searching and seeing active trips. 
Other less frequently used functionality is shown in the navbar such as user info etc.

- **Trip map**
The dashboard contains a leaflet map that gets populated for each authorized trip the user can view. 
The leaflet map contains icons that can be hovered to show the trips associated to it. 

- **Async update of trip user roles**
By using the JS fetch API user roles can be updated without a page reload.

- **Reply to messages**
It is possible to reply to messages in the trip dashboard, showing the original message above the response.

### Testing
The `init_db.py` file adds some predefined users and trips to the application.
Example users:
- username: a@a | password: a
- username: mary@mary | password: a

### Declaration of use of AI
**Github copilot:**
Used for auto completion. 

**ChatGPT:**
Used for debugging and error interpertation. 
