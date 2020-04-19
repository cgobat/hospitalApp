# Hospital App (InstaCare)
App to help users efficiently find and get to medical help

Will explain and add comments to uploaded files as we go : )

## iOS App

| <img src="Device-natives/iOS/screenshots/IMG-1087.PNG" width="200">       | <img src="Device-natives/iOS/screenshots/IMG-1090.PNG" width="200">         | <img src="Device-natives/iOS/screenshots/IMG-1091.PNG" width="200">  | <img src="Device-natives/iOS/screenshots/IMG-1088.PNG" width="200">  | <img src="Device-natives/iOS/screenshots/IMG-1089.PNG" width="200">  |
| :-------------: |:-------------:| :-----:|:-----:|:-----:|
| Landing Page      | Care Results | Care Details | COVID Testing Results | COVID Testing Map |







## Structure of HospitalStats Content:

Segment of Hospital Stats HTML we're interested in
![Example Hospital Result](infoStrcut.png)

## API Request Structure:
This is an example API Route Request from Clarendon Blvd to Glebe Rd, Arlington VA:

http://www.mapquestapi.com/directions/v2/route?key=KEY&from=ClarendonBlvd,Arlington,VA&to=2400+S+Glebe+Rd,+Arlington,+VA

Python's requets library makes sending API requests easy: 
![Example Hospital Result](apiRequest_python.png)

Notice how you must send an API key with the request - we're using the mapquest API (because it's free) so you can get a key from:
https://developer.mapquest.com/ Just make an account and you get 15k API requests for free.

## Output JSON structure:
This is the output of the jSonFile after we call the api request.
It gives us the optimal route as well as some attributes of the route.
IT also neatly braks down the route by steps in case we wanted to create a visual representation with our app.
![Example Output](jSonInfo.png)

# Action Items
 * ~~Baseline proof of concept~~
 * ~~Implement interface to test code flexibility~~
 * ~~Bolster (useful) information output~~
 * ~~Develop visual interface (app): iOS and Android | Pythonista (?)~~
 * ~~Obtain more immediate and accurate wait times~~
 * Prettify app interface (New Color scheme?)
