# Hack the Burgh - Hackathon  (Edinburgh, 19-20th Mar 2016)

## This is the backend part of the app BlockParty

### See [BlockParty on Devpost](http://devpost.com/software/block-party) - A multiplayer game for iOS where you create images out of shapes.

![BlockParty screenshot](https://github.com/Dalimil/Hack-the-Burgh-2016/blob/master/screenshot.jpg)


### API
```
Client clicks join button:
	- call /join
	- subscribe to the channel-id returned in the 'payload'

Client receives 'game-started' event with 'payload' in their personal channel:
	{'payload':{"shapes":[]} }
	- use this to initialize the game

Client updates the game:
	- call POST /update with changes and uid
	- constantly listen to 'game-updated' event which is called whenever one of the team members updates the game

Client finishes the game:
	- call POST /finish with uid 
	- team members receive 'game-finished' event in their channel
	- now just wait for the 'game-products' event with 'payload' in their personal channel
	- you can start rating games now...

Client assigns a rating to a game:
	- call POST /rate with score and teamid - you have this from the previous 'game-products' message
	- wait for the 'game-results' event with 'payload' in their channel (when all scores have been collected for all players)

Client closes the game/app or leaves the queue:
	- unsubscribe from the personal channel
```