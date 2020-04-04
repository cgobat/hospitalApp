from wkwebview import *
from objc_util import *
import webbrowser
import ui
import clipboard

def openMaps(sender):
	LSApplicationWorkspace = ObjCClass('LSApplicationWorkspace').alloc()
	BundleID = 'com.apple.Maps'
	webbrowser.open('http://maps.apple.com/?daddr=San+Francisco&dirflg=d&t=h')
	#LSApplicationWorkspace.openApplicationWithBundleID(BundleID)
	
def openLyft(sender):
	LSApplicationWorkspace = ObjCClass('LSApplicationWorkspace').alloc()
	BundleID = 'com.zimride.instant'
	#webbrowser.open('https://lyft.com/ride?id=lyft&pickup[latitude]=37.764728&pickup[longitude]=-122.422999&partner=ncx7I-E7jM-g&destination[latitude]=37.7763592&destination[longitude]=-122.4242038')
	
	uiApplication = ObjCClass('UIApplication').alloc()
	uiApplication.openURL('lyft://')
	#LSApplicationWorkspace.openApplicationWithBundleID(BundleID)	

def openUber(sender):
	LSApplicationWorkspace = ObjCClass('LSApplicationWorkspace').alloc()
	BundleID = 'com.ubercab.UberClient'
	LSApplicationWorkspace.openApplicationWithBundleID(BundleID)

def assignOptions():
	global View
	View.tint_color = 'gray'
	lyft = View['lyft']
	uber = View['uber']
	maps = View['maps']
	
	lyft.name = 'lyft'
	uber.name = 'uber'
	maps.name = 'maps'
	
	uber.image = ui.Image.named('assets/uber-1.png').with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
	maps.image = ui.Image.named('assets/maps-1.png').with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
	lyft.image = ui.Image.named('assets/lyft-1.png').with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
	
	View.add_subview(uber)
	View.add_subview(lyft)
	View.add_subview(maps)
	
View = ui.load_view('hospital-details.pyui')

currView = ui.NavigationView(View, navigation_bar_hidden=False)
View.tint_color = None
currView.objc_instance.navigationController().navigationBar().hidden = True
currView.present(style='fullscreen', hide_title_bar=True)
assignOptions()

