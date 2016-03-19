# Hack the Burgh - Hackathon  (Edinburgh, 19-20th Mar 2016)

### This is the backend part of the app


### Installation

#### Install required packages
```sh
pip install -r requirements.txt
```

#### Start the server (localhost:8080):
```sh
python main.py
```

### API
```
Client clicks join button:
	- call /join
	- subscribe to the channel-id returned in the 'payload'

Client receives 'game-started' event with 'payload' in their personal channel:
	{'payload':{"shapes":[]} }

Client updates the game:
	- call /update - or can trigger a pusher event???

Client closes the game/app or leaves the queue:
	- unsubscribe from the personal channel

