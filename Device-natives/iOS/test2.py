import ui, requests, json, random, math, webbrowser, clipboard
from scene import *
#import location as loc
from hospitalTraversal import *
import driveThruTesting as testScene
from objc_util import *
from functools import partial
from bs4 import BeautifulSoup as bs

testScene.startLoc()
user_address = ''
HospView = None
_hospView = None
homeV = None
resultsV = None
hospIdx = -1
pages = [homeV, resultsV]
HospTimes, HospNames, HospStates, HospNamesL, HospAddresses, HospNum, HospIDs, HospPhones = ([] for i in range(8))

_tAddresses, _tPhones, _tNames = ([] for i in range(3))

loadedHospitals = {}
hospitalTable = None

backC = ''
page = 0

print('location access: ' + str(testScene.locAuthorized()))

def geoLoc(_loc):
	return loc.geocode(_loc)

def cellTapped(sender):
	global page
	global resultsV
	global hospIdx
	global HospView
	global _hospView
	global homeV
	if HospView is not None:
		HospView.wait_modal()
	currView = None
	if hospIdx is -1:
		_hospView = ui.load_view('hospital-details.pyui')
		hospIdx = getIdxOfName(sender.items[0])
		initHospResults()
		updateHospResults()
	else:
		#resultsV.navigation_view.pop_view()
		#hospView.wait_modal()
		#print('sheet already being presented')
		_controller = ui.NavigationView(HospView, navigation_bar_hidden=False)
		#_controller.objc_instance.navigationController().dismis()
		#ehospView.close()
		
	#resultsV.navigation_view.push_view(hospView)
	currView = ui.NavigationView(HospView, navigation_bar_hidden=False)
	currView.objc_instance.navigationController().navigationBar().hidden = True
	HospView.present('sheet', hide_title_bar=False)
	print(HospView.wait_modal())
	page = 2
	
	#presentResultsPage(hospIdx)
	
	print(HospNamesL[hospIdx] + ' Tapped')
	
def openMaps(sender):
	LSApplicationWorkspace = ObjCClass('LSApplicationWorkspace').alloc()
	BundleID = 'com.apple.Maps'
	dest = HospAddresses[hospIdx]
	dest = dest.replace(' ', '+')
	mapsURL = 'http://maps.apple.com/?daddr=' + dest + '&dirflg=d&t=h'
	print(mapsURL)
	#webbrowser.open('http://maps.apple.com/?daddr=San+Francisco&dirflg=d&t=h')
	webbrowser.open(mapsURL)
	#LSApplicationWorkspace.openApplicationWithBundleID(BundleID)
	
def openLyft(sender):
	LSApplicationWorkspace = ObjCClass('LSApplicationWorkspace').alloc()
	BundleID = 'com.zimride.instant'
	#webbrowser.open('https://lyft.com/ride?id=lyft&pickup[latitude]=37.764728&pickup[longitude]=-122.422999&partner=ncx7I-E7jM-g&destination[latitude]=37.7763592&destination[longitude]=-122.4242038')
	
	#uiApplication = ObjCClass('UIApplication').alloc()
	#uiApplication.openURL('lyft://')
	LSApplicationWorkspace.openApplicationWithBundleID(BundleID)
	
def callSite(sender):
	num = HospPhones[hospIdx]
	area,num = num.split('-', 1)
	area = area.replace('(', '')
	num = num.replace('-', '')
	num ='tel:+1-' + area + '-' + num
	print(num)
	webbrowser.open(num)
	
def openUber(sender):
	LSApplicationWorkspace = ObjCClass('LSApplicationWorkspace').alloc()
	BundleID = 'com.ubercab.UberClient'
	LSApplicationWorkspace.openApplicationWithBundleID(BundleID)
	
def initHospResults():
	global HospView
	global _hospView
	window = ui.get_screen_size()
	
	container = ui.ScrollView()
	container.background_color = 'white'
	container.alpha = 1
	container.content_size = (window.x, window.y * .9)
	container.name = 'Results-Container'
	
	_hospView.tint_color = 'gray'
	lyft = _hospView['lyft']
	uber = _hospView['uber']
	maps = _hospView['maps']
	
	lyft.name = 'lyft'
	uber.name = 'uber'
	maps.name = 'maps'
	
	uber.image = ui.Image.named('assets/uber-1.png').with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
	maps.image = ui.Image.named('assets/maps-1.png').with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
	lyft.image = ui.Image.named('assets/lyft-1.png').with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
	container.add_subview(_hospView)
	HospView = container
	#hospView.present('sheet', hide_title_bar=True)
	#hospView.wait_modal()
	
def updateHospResults():
	global _hospView
	_hospView['siteName'].text = HospNames[hospIdx]
	_hospView['siteAddress'].text = HospAddresses[hospIdx]
	_hospView['hospNum'].text = HospPhones[hospIdx]
	
	_hospView['insurance1'].image = ui.Image.named('assets/aetna.png').with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
	_hospView['insurance2'].image = ui.Image.named('assets/medicaid.png').with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
	_hospView['insurance3'].image = ui.Image.named('assets/blue.png').with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
	
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
		_tNames.append(name)
		_tAddresses.append(address)
		_tPhones.append(phone)
		#print(address + str(idx))
		
	#print(_tNames)
	#print(_tAddresses)
	#print(_tPhones)
	
	
def testingOnMap(numShow):
	#locator = geocoder.geocodefarm(_tAddresses[1])
	#print(locator.json)
	locator = geo.Nominatim(user_agent='myGeocoder')
	showList = ''
	for idx in range(numShow):
		thisAddr = _tAddresses[random.randint(0, len(_tAddresses) -1)]
		print(thisAddr)
		location = geocoder.geocodefarm(thisAddr).json
		lat, lng = location['raw']['COORDINATES']['latitude'], location['raw']['COORDINATES']['longitude']
		thisList = (str(lat)+ ',' +str(lng)+'|marker-green||')
		print(thisList)
		showList += thisList
	showList = showList[:-2]
	print(showList)
	#location = locator.geocode(_tAddresses[1])
	#lat, lng = location.latitude, location.longitude
	#print('Latitude = {}, Longitude = {}'.format(location.latitude, location.longitude))
	#print(g.latlng)
	response = requests.get('https://www.mapquestapi.com/staticmap/v5/map?key=diLpeRXgA56YLQTiN8iZ4tK3G9wvTGSY&locations='+showList+'&size=@2x&defaultMarker=marker-sm-22407F-3B5998&size=600,400@2x#')
	img = Image.open(BytesIO(response.content))
	img.show()
	
	
def presentResultsPage(hospIdx):
	v = ui.View()
	window = ui.get_screen_size()
	v.background_color = '#f0ede6'
	v.alpha = 0.95
	v.name = 'Results'
	v.width, v.height = window.x, window.y * .9
	
	hospName = HospNamesL[hospIdx]
	if '-' in hospName:
		name1, name2 = hospName.split('-')
		name1 = name1[:-1]
		name2 = name2[1:]
		hospName = name1 + '\n' + name2
		
	hospTitle = ui.Label('Hospital Title')
	hospTitle.number_of_lines = 3
	hospTitle.alignment = ui.ALIGN_CENTER
	
	hospTitle.text = (hospName)
	hospTitle.font = ('<system-bold>', 18)
	hospTitle.text_color = '#3d3da1'
	hospTitle.scales_font = True
	#hospTitle.center = (v.width/2, v.height/10)
	#hospTitle.width, hospTitle.height = 150, 50
	hospTitle.frame = (v.width/6, v.height/20, 250, 50)
	
	v.add_subview(hospTitle)
	v.present('sheet', hide_title_bar=True)
	
class Data (ui.ListDataSource):
	def __init(self, items):
		print(type(self))
		
	def tableview_number_of_rows(self, tableview, s):
		return 2
		
	def tableview_cell_for_row(self, tableview, section, row):
	
		if row is 0:
			cell = ui.TableViewCell('subtitle')
			cell.text_label.text = str(self.items[0])
			#cell.detail_text_label.text = ('Time to service: ' + str(self.items[4]) + ' minutes')
			cell.detail_text_label.text = (str(self.items[1]))
			cell.text_label.alignment = ui.ALIGN_LEFT
			cell.text_label.number_of_lines = 0
			cell.text_label.font= ('<system-bold>', 20)
			cell.accessory_type = 'disclosure_indicator'
			cell.selectable = True
		else:
			cell = ui.TableViewCell('subtitle')
			cell.text_label.text = (str(self.items[4] + ' Minutes to service'))
			cell.text_label.alignment = ui.ALIGN_CENTER
			cell.text_label.font= ('<system-bold>', 14)
			
			cell.detail_text_label.text = ('Drive Time: ' + str(self.items[3])
			+ ' minute | Wait Time: ' + str(self.items[2]) + ' minutes')
			cell.detail_text_label.alignment = ui.ALIGN_CENTER
			cell.detail_text_label.font= ('<system>', 10)
			
			
		cell.selectable = False
		cell.text_label.number_of_lines = 0
		
		return cell
		
def resolveAddress():
	global user_address
	
	if testScene.locAuthorized():
		_ad = testScene.revGeo(testScene.getLoc())
		_street = _ad[0]['Street'].split()
		_city = _ad[0]['City']
		_state = _ad[0]['State']
		_zip = _ad[0]['ZIP']
		
		_streetNo = _street[0]
		user_address = 'hello'
		if '–' in _streetNo:
			_streetNo = _streetNo.split('–')[0]
			_street[0] = _streetNo
			_streetAd = ''
			for idx, elem in enumerate(_street):
				addage = ' '
				if idx is (len(_street) - 1):
					addage = ''
				_streetAd += elem + addage
			user_address = (_streetAd + ', ' + _city + ", " + _state + ' ' + _zip)
		print(user_address)
		return True
	else:
		user_address = currentAddy()
	return False
	
def getIdxOfName(name):
	return HospNames.index(name)
	
def getHospPhone(idx):
	hosp = loadedHospitals[idx]
	hospPhone = hName = hosp['Site']['Phone']
	hospPhone = hospPhone.replace(') ', '-')
	hospPhone = hospPhone.replace('(', '')
	hospHone = hospPhone[1:]
	return hospPhone
	
def getHospPhones():
	global HospPhones
	hospPhones = []
	for idx in loadedHospitals:
		phone = getHospPhone(idx)
		hospPhones.append(phone)
	HospPhones = hospPhones
	return hospPhones
	
def getHospName(idx):
	hosp = loadedHospitals[idx]
	hNameL = hName = hosp['Site']['Name']
	cutStr1 = 'Health Urgent Care'
	cutStr2 = 'Urgent Care'
	if cutStr2 in hName:
		hName = hName.replace(cutStr2, '')
	if cutStr1 in hName:
		hName = hName.replace(cutStr1, '')
	if '  ' in hName:
		hName = hName.replace('  ', ' ')
	return (hName, hNameL)
	
def getHospNames():
	global HospNames
	global HospNamesL
	hospNames, hospNamesL = [],[]
	for idx in loadedHospitals:
		hName = getHospName(idx)
		hospNames.append(hName[0])
		hospNamesL.append(hName[1])
	HospNames = hospNames
	HospNamesL = hospNamesL
	return hospNames
	
def getHospTime(idx):
	hosp = loadedHospitals[idx]
	hTraf = int(hosp['route']['Traffic'])
	hWait = int(hosp['route']['Wait'] / 100)
	hAg = int(hTraf + hWait)
	return (hWait, hTraf, hAg)
	
def getHospTimes():
	global HospTimes
	hospTimes = []
	for idx in loadedHospitals:
		hTime = getHospTime(idx)
		hospTimes.append(hTime)
	HospTimes = hospTimes
	return hospTimes
	
def getHospAddress(idx):
	hosp = loadedHospitals[idx]
	hStreet = hosp['Site']['Street']
	hArea = hosp['Site']['Area']
	hAdd = hStreet + ' ' + hArea
	return (hAdd)
	
def getHospAddresses():
	global HospAddresses
	hospAddresses = []
	for idx in loadedHospitals:
		address = getHospAddress(idx)
		hospAddresses.append(address)
	HospAddresses = hospAddresses
	return hospAddresses
	
def getHospID(idx):
	hosp = loadedHospitals[idx]
	hID = hosp['route']['Wait']
	return (hID)
	
def getHospIDs():
	global HospIDs
	hospIDs = []
	for idx in loadedHospitals:
		hID = getHospID(idx)
		hospIDs.append(hID)
	HospIDs = hospIDs
	return hospIDs
	
def getHospState(idx):
	hosp = loadedHospitals[idx]
	hState = hosp['Site']['Area']
	hState = hState.split(',')[0]
	return hState
	
def getHospStates():
	global HospStates
	hospStates = []
	for idx in loadedHospitals:
		hState = getHospState(idx)
		hospStates.append(hState)
	HospStates = hospStates
	return hospStates
	#print(_street)
	
@ui.in_background
def getResults():
	global loadedHospitals
	global HospTimes
	global exResults
	
	window = ui.get_screen_size()
	#loadedHospitals = proximityHospitals()
	loadedHospitals = exResults
	hospNames = getHospNames()
	hospTimes = getHospTimes()
	hospStates = getHospStates()
	getHospAddresses()
	getHospPhones()
	getHospIDs()
	#print(loadedHospitals)
	#updatehospNames(getHospNames())
	
	titleBox = ui.Label('Results Title')
	titleBox.text = 'Treatment Near You'
	titleBox.scales_font = True
	titleBox.font = ('Avenir_Black', 24)
	titleBox.text_color = '#797c65'
	titleBox.frame = (window.x / 4, window.y /18, 200, 50)
	titleBox.alignment = ui.ALIGN_CENTER
	
	resultsV.add_subview(titleBox)
	resultBoxes(hospNames, hospStates, hospTimes)
	#print(getHospNames())
	
def updatehospNames(hospitalNames):
	global hospitalTable
	hospitalTable.data_source = Data(hospitalNames)
	hospitalTable.reload()
	print(hospitalTable.data_source)
	
def showResults(v, objList):
	getResults()
	#v.add_subview(viewBox(0))
	#for obj in objList:
		#v.add_subview(obj)
		
		
def prepareResultsView():
	global resultsV
	global page
	global backC
	global hospitalTable
	
	window = ui.get_screen_size()
	_v = ui.ScrollView()
	#_v = SceneView()
	_v.background_color = '#f0ede6'
	_v.content_size = (window.x, window.y * 3)
	_v.frame = (0, 0, window.x, window.y)
	_v.alpha = 1
	_v.name = 'Results'
	
	
	
	backB = ui.Button(title='Go back!')
	backB.center = (_v.width * .5, _v.height * .8)
	backB.flex = 'LRTB'
	
	getResults()
	#_v.add_subview(backB)
	#ui.delay(partial(showResults, _v, [backB, tv]), .5)
	resultsV = _v
	homeV.navigation_view.push_view(resultsV)
	page = 1
	
def viewBox(indexInCall):
	v = ui.View()
	v.background_color ='white'
	v.alpha = 1.0
	v.frame = (20, 100 + (indexInCall * 250 + 50), 335, 200)
	v.corner_radius = 4
	
	cRef = ObjCInstance(v)
	cRef.layer().setMasksToBounds_(False)
	cRef.layer().setShadowRadius_(7)
	#cRef.layer().setShadowOffset_(CGSize(0,0))
	cRef.layer().setShadowOpacity_(0.15)
	return v
	
def tableToView(v, name, state, hTime):
	tv = ui.TableView()
	_v = ui.View()
	x, y = v.width, v.height
	tv.center = (x * .2, y * .3)
	tv.row_height = 90
	tv.width, tv.height = x * .9, y * .9
	tv.allows_multiple_selection = False
	ds = Data([str(name), str(state), str(hTime[0]), str(hTime[1]), str(hTime[2])])
	ds.delete_enables = False
	ds.action = cellTapped
	tv.data_source = tv.delegate = ds
	tv.add_subview(_v)
	v.add_subview(tv)
	
def resultBoxes(objects1, objects2, objects3):
	global resultsV
	for idx, name in enumerate(objects1):
		#print(name)
		hTime = objects3[idx]
		state = objects2[idx]
		_v = viewBox(idx)
		tableToView(_v, name, state, hTime)
		resultsV.add_subview(_v)
	print('done adding boxes')
	
	
def refreshInRad():
	print('call rad function')
	

def resolve_landing():
	#homeV['get-started'].center = (homeV.width * 0.5, homeV.height * 0.9)
	homeV['covidLogo'].image = ui.Image.named('assets/covid.png').with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
	homeV['careLogo'].image = ui.Image.named('assets/care.png').with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
	backC = homeV.background_color
	#print(backC)
	
@ui.in_background
def get_started(sender):
	global homeV
	global page
	locServices = resolveAddress()
	print('Utilizing precise location: ' + str(locServices))
	print(user_address)
	#homeV['get-started'].title = 'Hi'
	prepareResultsView()
	
@ui.in_background
def get_testing(sender):
	testScene.initScene()
	_view = testScene.view
	homeV.navigation_view.push_view(_view)
	
def presentMode():
	global page
	modes = ['fullscreen', 'sheet', 'sheet']
	return modes[page]
	
v = ui.View()
#v = SceneView()
if homeV is None:
	homeV = v = ui.load_view()
	resolve_landing()
currView = ui.NavigationView(v, navigation_bar_hidden=False)
currView.objc_instance.navigationController().navigationBar().hidden = True
#button = ui.Button(title='button1')
#v.add_subview(button)
currView.present('fullscreen', hide_title_bar=True)

exResults ={
    '1': {
        'Site': {
            "Name": "MedStar Health Urgent Care - Adams Morgan",
            "Street": "1805 Columbia Rd. NW",
            "Area": "DC, 20009",
            "Phone": "(202) 797-4950"
        },
        'route': {
            'Distance': 2.135,
            'Wait': 1276,
            'Traffic': 6,
            'Aggregate': 1282
        }
    },
    '2': {
        'Site': {
            "Name": "Metro Immediate and Primary Care - Capitol Hill/Noma",
            "Street": "220 L St NE ",
            "Area": "DC, 20002",
            "Phone": "(202) 797-4950"
        },
        'route': {
            'Distance': 1.469,
            'Wait': 332,
            'Traffic': 4,
            'Aggregate': 336
        }
    },
    '3': {
        'Site': {
            "Name": "MedStar Health Urgent Care - Capitol Hill",
            "Street": "228 7th St. SE",
            "Area": "DC, 20003",
            "Phone": "(202) 698-0795"
        },
        'route': {
            'Distance': 2.802,
            'Wait': 1278,
            'Traffic': 8,
            'Aggregate': 1286
        }
    },
    '4': {
        'Site': {
            "Name": "Metro Immediate and Primary Care - Cleveland Park",
            "Street": "2902 Porter Street, NW",
            "Area": "DC, 20008",
            "Phone": "(202) 525-5287"
        },
        'route': {
            'Distance': 3.732,
            'Wait': 331,
            'Traffic': 10,
            'Aggregate': 341
        }
    },
    '5': {
        'Site': {
            "Name": "Inova Urgent Care  - North Arlington",
            "Street": "4600 Lee Highway, Suite C",
            "Area": "VA, 22207",
            "Phone": "(571) 492-3080"
        },
        'route': {
            'Distance': 6.659,
            'Wait': 1114,
            'Traffic': 15,
            'Aggregate': 1129
        }
    },
    '6': {
        'Site': {
            "Name": "Inova Urgent Care - South Arlington",
            "Street": "3263 Columbia Pike",
            "Area": "VA, 22204",
            "Phone": "(703) 746-0111"
        },
        'route': {
            'Distance': 7.063,
            'Wait': 1074,
            'Traffic': 13,
            'Aggregate': 1087
        }
    },
    '7': {
        'Site': {
            "Name": "MedStar Health Urgent Care - Alexandria",
            "Street": "3610 King St.",
            "Area": "VA, 22302",
            "Phone": "(571) 492-3080"
        },
        'route': {
            'Distance': 9.365,
            'Wait': 1277,
            'Traffic': 14,
            'Aggregate': 1291
        }
    },
    '8': {
        'Site': {
            "Name": "Immediate Care by PMA Health",
            "Street": "510 W. Annandale Rd. Suite 100",
            "Area": "VA, 22046",
            "Phone": "(703) 236-7133"
        },
        'route': {
            'Distance': 10.807,
            'Wait': 2798,
            'Traffic': 19,
            'Aggregate': 2817
        }
    },
    '9': {
        'Site': {
            "Name": "Inova Urgent Care - Dunn Loring",
            "Street": "2671 Avenir Pl.",
            "Area": "VA, 22180",
            "Phone": "(703) 207-8600"
        },
        'route': {
            'Distance': 14.82,
            'Wait': 837,
            'Traffic': 24,
            'Aggregate': 861
        }
    },
    '10': {
        'Site': {
            "Name": "Inova Urgent Care - Vienna",
            "Street": "180 Maple Ave West",
            "Area": "VA, 22180",
            "Phone": "(703) 938-5300"
        },
        'route': {
            'Distance': 17.91,
            'Wait': 1112,
            'Traffic': 27,
            'Aggregate': 1139
        }
    },
    '11': {
        'Site': {
            "Name": "Inova Urgent Care - Tysons",
            "Street": "8357-E Leesburg Pike",
            "Area": "VA, 22182",
            "Phone": "(571) 665-6440"
        },
        'route': {
            'Distance': 15.074,
            'Wait': 1073,
            'Traffic': 24,
            'Aggregate': 1097
        }
    },
    '12': {
        'Site': {
            "Name": "Inova Urgent Care - West Springfield",
            "Street": "6230 Rolling Road, Suite J",
            "Area": "VA, 22152",
            "Phone": "(571) 665-6460"
        },
        'route': {
            'Distance': 17.974,
            'Wait': 1115,
            'Traffic': 25,
            'Aggregate': 1140
        }
    },
    '13': {
        'Site': {
            "Name": "Inova Urgent Care - Reston",
            "Street": "1488 Northpoint Village Ctr",
            "Area": "VA, 20194",
            "Phone": "(571) 525-5850"
        },
        'route': {
            'Distance': 24.273,
            'Wait': 3363,
            'Traffic': 35,
            'Aggregate': 3398
        }
    },
    '14': {
        'Site': {
            "Name": "Fairfax Family Practice",
            "Street": "3650 Joseph Siewick Drive",
            "Area": "VA, 22033",
            "Phone": "(571) 525-5850"
        },
        'route': {
            'Distance': 23.727,
            'Wait': 2673,
            'Traffic': 34,
            'Aggregate': 2707
        }
    },
    '15': {
        'Site': {
            "Name": "Sentara Northern Virginia Employee Health",
            "Street": "2296 Opitz Blvd, Suite 310",
            "Area": "VA, 22191",
            "Phone": "(703) 523-1390"
        },
        'route': {
            'Distance': 27.717,
            'Wait': 2179,
            'Traffic': 35,
            'Aggregate': 2214
        }
    },
    '16': {
        'Site': {
            "Name": "Velocity Urgent Care - Port Potomac",
            "Street": "16433 Navigation Dr. ",
            "Area": "VA, 22191",
            "Phone": "(571) 297-1437"
        },
        'route': {
            'Distance': 30.623,
            'Wait': 3307,
            'Traffic': 38,
            'Aggregate': 3345
        }
    },
    '17': {
        'Site': {
            "Name": "Inova Urgent Care  - Centreville",
            "Street": "6201 Centreville Road, Suite 200",
            "Area": "VA, 20121",
            "Phone": "(703) 830-5600"
        },
        'route': {
            'Distance': 27.328,
            'Wait': 1113,
            'Traffic': 36,
            'Aggregate': 1149
        }
    },
    '18': {
        'Site': {
            "Name": "MedStar Health Urgent Care - Hyattsville",
            "Street": "6401 America Blvd., Suite 200",
            "Area": "MD, 20782",
            "Phone": "(301) 276-8800"
        },
        'route': {
            'Distance': 6.762,
            'Wait': 1280,
            'Traffic': 15,
            'Aggregate': 1295
        }
    },
    '19': {
        'Site': {
            "Name": "MMG at Hyattsville",
            "Street": "6401 America Boulevard",
            "Area": "MD, 20782",
            "Phone": "(301) 209-5480"
        },
        'route': {
            'Distance': 6.762,
            'Wait': 1885,
            'Traffic': 15,
            'Aggregate': 1900
        }
    },
    '20': {
        'Site': {
            "Name": "MedStar Health Urgent Care - Chevy Chase",
            "Street": "5454 Wisconsin Ave.",
            "Area": "MD, 20815",
            "Phone": "(301) 215-9440"
        },
        'route': {
            'Distance': 7.544,
            'Wait': 1279,
            'Traffic': 18,
            'Aggregate': 1297
        }
    },
    '21': {
        'Site': {
            "Name": "MedStar Health Center at Chevy Chase",
            "Street": "5454 Wisconsin Avenue",
            "Area": "MD, 20815",
            "Phone": "(301) 215-9440"
        },
        'route': {
            'Distance': 7.544,
            'Wait': 1884,
            'Traffic': 18,
            'Aggregate': 1902
        }
    },
    '22': {
        'Site': {
            "Name": "GW Immediate and Primary Care - Silver Spring",
            "Street": "8484 Georgia Ave Ste 100",
            "Area": "MD, 20910",
            "Phone": "(202) 525-5287"
        },
        'route': {
            'Distance': 6.065,
            'Wait': 333,
            'Traffic': 14,
            'Aggregate': 347
        }
    },
    '23': {
        'Site': {
            "Name": "MMG Family Practice at Camp Springs",
            "Street": "5801 Allentown Rd.",
            "Area": "MD, 20746",
            "Phone": "(301) 899-0020"
        },
        'route': {
            'Distance': 12.597,
            'Wait': 1886,
            'Traffic': 21,
            'Aggregate': 1907
        }
    },
    '24': {
        'Site': {
            "Name": "MedStar Health Urgent Care - Wheaton",
            "Street": "11915 Georgia Ave.",
            "Area": "MD, 20902",
            "Phone": "(301) 942-4505"
        },
        'route': {
            'Distance': 10.328,
            'Wait': 1281,
            'Traffic': 23,
            'Aggregate': 1304
        }
    },
    '25': {
        'Site': {
            "Name": "MMG at Silver Spring",
            "Street": "10301 Georgia Avenue",
            "Area": "MD, 20902",
            "Phone": "(301) 754-1950"
        },
        'route': {
            'Distance': 8.346,
            'Wait': 1882,
            'Traffic': 19,
            'Aggregate': 1901
        }
    },
    '26': {
        'Site': {
            "Name": "MMG at Bethesda",
            "Street": "6410 Rockledge Dr",
            "Area": "MD, 20817",
            "Phone": "(301) 897-5001"
        },
        'route': {
            'Distance': 14.099,
            'Wait': 1883,
            'Traffic': 25,
            'Aggregate': 1908
        }
    },
    '27': {
        'Site': {
            "Name": "ExpressCare - Largo",
            "Street": "10416 Campus Way South",
            "Area": "MD, 20774",
            "Phone": "301-316-9620"
        },
        'route': {
            'Distance': 15.993,
            'Wait': 695,
            'Traffic': 23,
            'Aggregate': 718
        }
    },
    '28': {
        'Site': {
            "Name": "Physicians Now",
            "Street": "15215 Shady Grove Road",
            "Area": "MD, 20850",
            "Phone": "202-797-4950"
        },
        'route': {
            'Distance': 20.215,
            'Wait': 267,
            'Traffic': 33,
            'Aggregate': 300
        }
    },
    '29': {
        'Site': {
            "Name": "ExpressCare - Bowie",
            "Street": "6000 Laurel Bowie Road",
            "Area": "MD, 20715",
            "Phone": "301-383-0330"
        },
        'route': {
            'Distance': 16.846,
            'Wait': 140,
            'Traffic': 25,
            'Aggregate': 165
        }
    },
    '30': {
        'Site': {
            "Name": "MedStar Health Urgent Care - Gaithersburg",
            "Street": "12111 Darnestown Rd.",
            "Area": "MD, 20878",
            "Phone": "202-797-4950"
        },
        'route': {
            'Distance': 23.421,
            'Wait': 1565,
            'Traffic': 38,
            'Aggregate': 1603
        }
    },
    '31': {
        'Site': {
            "Name": "MedStar Health Urgent Care - Waldorf",
            "Street": "3064 Waldorf Market Pl.",
            "Area": "MD, 20603",
            "Phone": "301-932-5960"
        },
        'route': {
            'Distance': 27.493,
            'Wait': 1567,
            'Traffic': 37,
            'Aggregate': 1604
        }
    },
    '32': {
        'Site': {
            "Name": "COVID UNI Urgent Care Center Clarksville",
            "Street": "12272 Clarksville Pike",
            "Area": "MD, 21029",
            "Phone": "202-797-4950"
        },
        'route': {
            'Distance': 26.503,
            'Wait': 4850,
            'Traffic': 40,
            'Aggregate': 4890
        }
    },
    '33': {
        'Site': {
            "Name": "Premier Health Express Urgent Care",
            "Street": "9710 Patuxent Woods Dr.  Ste 200 ",
            "Area": "MD, 21046",
            "Phone": "443-899-9525"
        },
        'route': {
            'Distance': 28.005,
            'Wait': 3405,
            'Traffic': 36,
            'Aggregate': 3441
        }
    },
    '34': {
        'Site': {
            "Name": "ChoiceOne Dunkirk",
            "Street": "10845 Town Center Blvd",
            "Area": "MD, 20754",
            "Phone": "410-650-4346"
        },
        'route': {
            'Distance': 28.754,
            'Wait': 3630,
            'Traffic': 39,
            'Aggregate': 3669
        }
    },
    '35': {
        'Site': {
            "Name": "Dunkirk",
            "Street": "10845 Town Center Blvd",
            "Area": "MD, 20754",
            "Phone": "202-797-4950"
        },
        'route': {
            'Distance': 28.754,
            'Wait': 4564,
            'Traffic': 39,
            'Aggregate': 4603
        }
    },
    '36': {
        'Site': {
            "Name": "ExpressCare - Wilkens",
            "Street": "3815 Wilkens Avenue ",
            "Area": "MD, 21229",
            "Phone": "667-212-5920"
        },
        'route': {
            'Distance': 34.892,
            'Wait': 129,
            'Traffic': 45,
            'Aggregate': 174
        }
    },
    '37': {
        'Site': {
            "Name": "MedStar NRH Rehab Network - Wilkens Avenue",
            "Street": "3455 Wilkens Avenue",
            "Area": "MD, 21229",
            "Phone": "410-737-8418"
        },
        'route': {
            'Distance': 35.189,
            'Wait': 1881,
            'Traffic': 46,
            'Aggregate': 1927
        }
    }
}

