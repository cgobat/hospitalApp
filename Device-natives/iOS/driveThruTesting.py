from bs4 import BeautifulSoup as bs
import location as loc1
#import test2 as main
from PIL import Image
from io import BytesIO
from mapview import *
#import geopy
import ui, io, random, json, requests, copy

view = None
resultBox = None
scrollObj = None
markerColors = ['blue', 'green', 'red', 'yellow', 'purple', 'gray']
resultsCount = 5
mapObj = None

_tAddresses, _tPhones, _tNames = ([] for i in range(3))


def getTestingSites(state):
	global _tAddress, _tPhones, _tNames
	url = 'https://my.castlighthealth.com/corona-virus-testing-sites/data/result.php?county=All&state='+state+'&v=03042020813'
	request = requests.get(url)
	page = bs(request.content, 'html.parser')
	headings = page.findAll('h2')
	for idx, master in enumerate(page.findAll('div', class_='dont-break-out')):
		name = headings[idx].get_text()
		ps = master.findAll('p')
		address = ps[0].get_text()
		phone = ps[1].get_text()
		address = address.replace('\n', '').replace('  ', '').replace('Address:', '')
		phone = phone.replace('\n', '').replace('  ', '').replace('Phone:', '')
		print(name)
		_tNames.append(name)
		_tAddresses.append(address)
		_tPhones.append(phone)
		#print(address + str(idx))
		
	updateLanding()
	#print(_tNames)
	#print(_tAddresses)
	#print(_tPhones)
	
def updateLanding():
	print('size of results: ' + str(len(_tPhones)))
	for idx in range(resultsCount):
		box = scrollObj.subviews[idx]
		box['label_r'].text = _tNames[idx]
		
def setLanding():
	global scrollObj
	global resultBox
	car = view['content']['car_r']
	car.image = ui.Image.named('assets/car.png')
	phone = view['content']['phone_r']
	horiz_r = view['content']['horizontal_r']
	vert_r = view['content']['vertical_r']
	case_r = view['content']['case_r']
	marker_r = view['content']['siteMarker']
	scrollObj = view['content']['innerScroll']
	label_r = view['content']['label_r']
	
	view['content']['copyright'].image = ui.Image.named('assets/copyright.png')
	
	phoneBounds = phone.frame
	marker_r.tint_color = 'blue'
	scrollObj.add_subview(case_r)
	
	scrollObj.content_size = (375, 900)
	
	#scrollObj.content_mode = ui.CONTENT_TOP_LEFT
	markerPos = (marker_r.x, marker_r.y)
	case_r.add_subview(phone)
	case_r.x = 14
	case_r.y = 20
	
	marker_r.x = 20
	marker_r.y = 40
	
	vert_r.x = 90
	vert_r.y = 12
	
	horiz_r.x = 100
	horiz_r.y = 80
	
	label_r.x = 110
	label_r.y = 10
	
	phone.x = 150
	phone.y = 90
	
	car.x = 220
	car.y = 90
	#case_r.frame = scrollObj.bounds
	phone.bring_to_front()
	case_r.add_subview(marker_r)
	case_r.add_subview(car)
	case_r.add_subview(horiz_r)
	case_r.add_subview(label_r)
	case_r.add_subview(vert_r)
	vert_r.bring_to_front()
	
	resultBox = case_r
	boxSave = ui.dump_view(case_r)
	for idx in range(4):
		_idx = idx + 1
		box = ui.load_view_str(boxSave)
		box.x = 14
		box.y = 180 + (180 * idx)
		box['siteMarker'].tint_color = markerColors[_idx]
		scrollObj.add_subview(box)
		
	showMap([38.926640,-77.006981], None)
	
	#view.add_subview(resultBox)
	#scrollObj.add_subview(case_r)
def showMap(center, pois):
	global mapObj
	v = MapView(frame=(20, 570, 325, 270))
	v.scroll_action = scroll_action
	v.name = 'map'
	view.add_subview(v)
	v.set_region(center[0],center[1], 0.1, 0.1, animated=True)
	mapObj = v
	
def updateMap(center, pois):
	global mapObj
	v = mapObj
	v.set_region(center[0], center[1], 0.1, 0.1, animated=True)
	for idx, poi in enumerate(pois):
		v.add_pin(poi[0], poi[1], markerColors[idx], 'a')
		
		
def getLoc():
	return loc1.get_location()
	
def revGeo(loc):
	return loc1.reverse_geocode(loc)
	
def geo(loc):
	return loc1.geocode(loc)
	
def locAuthorized():
	return loc1.is_authorized()
	
def startLoc():
	loc1.start_updates()
	
def stopLoc():
	loc1.stop_updates()

def locObj():
	return loc1
	
def testingOnMap(numShow):
	#locator = geocoder.geocodefarm(_tAddresses[1])
	#print(locator.json)
	#locator = #geo.Nominatim(user_agent='myGeocoder')
	showList = ''
	siteCoords = []
	agLat, agLng = 0, 0
	for idx in range(numShow):
		thisAddr = _tAddresses[random.randint(0, len(_tAddresses) -1)]
		print(thisAddr)
		address_dict = {'Street': 'Infinite Loop', 'City': 'Cupertino', 'Country': 'USA'}
		splitStr = thisAddr.split(',')
		if len(splitStr) > 3:
			splitStr[0] += (splitStr[1])
			del splitStr[1]
			
		splitStr[2] = 'USA'
		_address_dict = {'Street': splitStr[0], 'City': splitStr[1], 'Country': splitStr[2]}
		#location = geocoder.geocodefarm(thisAddr).json
		print(_address_dict)
		print(location.get_location())
		obscure = location.geocode(_address_dict)
		#lat, lng = location['raw']['COORDINATES']['latitude'], location['raw']['COORDINATES']['longitude']
		print(obscure)
		print('hi')
		#colors = ['blue', 'green', 'red', 'yellow', 'purple']
		lat, lng = obscure[0]['latitude'], obscure[0]['longitude']
		thisList = (str(lat)+ ',' +str(lng)+'|marker-'+markerColors[idx]+'||')
		print(thisList)
		showList += thisList
		agLat += lat
		agLng += lng
		siteCoords.append((lat,lng))
	mapCenter = (agLat/float(numShow), agLng/float(numShow))
	updateMap(mapCenter, siteCoords)
	showList = showList[:-2]
	print(showList)
	#response = requests.get('https://www.mapquestapi.com/staticmap/v5/map?key=diLpeRXgA56YLQTiN8iZ4tK3G9wvTGSY&locations='+showList+'&size=@2x&defaultMarker=marker-sm-22407F-3B5998&size=375,240@2x#')
	#img = Image.open(BytesIO(response.content))
	#img.show()
	
	#mapView = view['localView']
	#with io.BytesIO() as bIO:
		#img.save(bIO, img.format)
		#mapView.image = ui.Image.from_data(bIO.getvalue())
		

def initScene():
	global view
	view = ui.ScrollView()
	_view = ui.load_view('testing.pyui')
	_view.name = 'content'
	view.content_inset = (-50, 0, 0, 0)
	view.content_size = (_view.width*.9, _view.height*.85)
	view.add_subview(_view)
	setLanding()
	getTestingSites('DC')
	testingOnMap(5)
	
#initScene()
#currView = ui.NavigationView(view, navigation_bar_hidden=False)
#currView.objc_instance.navigationController().navigationBar().hidden = True
#view.present('fullscreen', hide_title_bar=True)

