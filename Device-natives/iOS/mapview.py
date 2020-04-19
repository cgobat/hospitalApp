# coding: utf-8
'''
NOTE: This requires Pythonista 3
Demo of a custom ui.View subclass that embeds a native map view using MapKit (via objc_util). Tap and hold the map to drop a pin.
The MapView class is designed to be reusable, but it doesn't implement *everything* you might need. I hope that the existing methods give you a basic idea of how to add new capabilities though. For reference, here's Apple's documentation about the underlying MKMapView class: http://developer.apple.com/library/ios/documentation/MapKit/reference/MKMapView_Class/index.html
adapted from original code by omz
'''

from objc_util import *
import ctypes
import ui
import location
import time
import weakref

# _map_delegate_cache is used to get a reference to the MapView from the (Objective-C) delegate callback. The keys are memory addresses of `OMMapViewDelegate` (Obj-C) objects, the values are `ObjCInstance` (Python) objects. This mapping is necessary because `ObjCInstance` doesn't guarantee that you get the same object every time when you instantiate it with a pointer (this may change in future betas). MapView stores a weak reference to itself in the specific `ObjCInstance` that it creates for its delegate.
_map_delegate_cache = weakref.WeakValueDictionary()
MKAnnotationView = ObjCClass('MKAnnotationView')

# Create a new Objective-C class to act as the MKMapView's delegate...

def mapView_regionDidChangeAnimated_(self, cmd, mk_mapview, animated):
		# Resolve weak reference from delegate to mapview:
		map_view = _map_delegate_cache[self].map_view_ref()
		if map_view:
			map_view._notify_region_changed()
images=['plc:Character_Boy','plc:Tree_Short']
def mapView_viewForAnnotation_(self, cmd, mapview, annotation):	
	av=	ObjCInstance(mapview).dequeueReusableAnnotationViewWithIdentifier('MyAnnotation')
	if not av:	
		av=MKAnnotationView.alloc().initWithAnnotation_reuseIdentifier_(ObjCInstance(annotation),'MyAnnotation')

	#if title is an image name, set image
	img=ui.Image.named('assets/ionf-'+ str(ObjCInstance(annotation).title()) + '.PNG')
	if img:
			av.setImage_(img.objc_instance)
			return av.ptr
	else:	 #None defaults to pin
		return None

#new simplified class creation using protocols	
OMMapViewDelegate=create_objc_class('OMMapViewDelegate', 
					methods=[mapView_regionDidChangeAnimated_, mapView_viewForAnnotation_],
					protocols=['MKMapViewDelegate'])

class CLLocationCoordinate2D (Structure):
	_fields_ = [('latitude', c_double), ('longitude', c_double)]
class MKCoordinateSpan (Structure):
	_fields_ = [('d_lat', c_double), ('d_lon', c_double)]
class MKCoordinateRegion (Structure):
	_fields_ = [('center', CLLocationCoordinate2D), ('span', MKCoordinateSpan)]

class MapView (ui.View):
	@on_main_thread
	def __init__(self, *args, **kwargs):
		ui.View.__init__(self, *args, **kwargs)
		MKMapView = ObjCClass('MKMapView')
		frame = CGRect(CGPoint(0, 0), CGSize(self.width, self.height))
		self.mk_map_view = MKMapView.alloc().initWithFrame_(frame)
		flex_width, flex_height = (1<<1), (1<<4)
		self.mk_map_view.setAutoresizingMask_(flex_width|flex_height)
		self_objc = ObjCInstance(self)
		self_objc.addSubview_(self.mk_map_view)
		self.mk_map_view.release()
		self.long_press_action = None
		self.scroll_action = None
		#NOTE: The button is only used as a convenient action target for the gesture recognizer. While this isn't documented, the underlying UIButton object has an `-invokeAction:` method that takes care of calling the associated Python action.
		self.gesture_recognizer_target = ui.Button()
		self.gesture_recognizer_target.action = self.long_press
		UILongPressGestureRecognizer = ObjCClass('UILongPressGestureRecognizer')
		self.recognizer = UILongPressGestureRecognizer.alloc().initWithTarget_action_(self.gesture_recognizer_target, sel('invokeAction:')).autorelease()
		self.mk_map_view.addGestureRecognizer_(self.recognizer)
		self.long_press_location = ui.Point(0, 0)
		self.map_delegate = OMMapViewDelegate.alloc().init()#.autorelease()
		self.mk_map_view.setDelegate_(self.map_delegate)
		self.map_delegate.map_view_ref = weakref.ref(self)
		_map_delegate_cache[self.map_delegate.ptr] = self.map_delegate

	def long_press(self, sender):
		#NOTE: The `sender` argument will always be the dummy ui.Button that's used as the gesture recognizer's target, just ignore it...
		gesture_state = self.recognizer.state()
		if gesture_state == 1 and callable(self.long_press_action):
			loc = self.recognizer.locationInView_(self.mk_map_view)
			self.long_press_location = ui.Point(loc.x, loc.y)
			self.long_press_action(self)

	@on_main_thread
	def add_pin(self, lat, lon, title, subtitle=None, select=False):
		'''Add a pin annotation to the map'''
		MKPointAnnotation = ObjCClass('MKPointAnnotation')
		coord = CLLocationCoordinate2D(lat, lon)
		annotation = MKPointAnnotation.alloc().init()
		annotation.setTitle_(title)
		if subtitle:
			annotation.setSubtitle_(subtitle)
		annotation.setCoordinate_(coord, restype=None, argtypes=[CLLocationCoordinate2D])
		self.mk_map_view.addAnnotation_(annotation)
		if select:
			self.mk_map_view.selectAnnotation_animated_(annotation, True)



	@on_main_thread
	def remove_all_pins(self):
		'''Remove all annotations (pins) from the map'''
		self.mk_map_view.removeAnnotations_(self.mk_map_view.annotations())

	@on_main_thread
	def set_region(self, lat, lon, d_lat, d_lon, animated=False):
		'''Set latitude/longitude of the view's center and the zoom level (specified implicitly as a latitude/longitude delta)'''
		region = MKCoordinateRegion(CLLocationCoordinate2D(lat, lon), MKCoordinateSpan(d_lat, d_lon))
		self.mk_map_view.setRegion_animated_(region, animated, restype=None, argtypes=[MKCoordinateRegion, c_bool])

	@on_main_thread
	def set_center_coordinate(self, lat, lon, animated=False):
		'''Set latitude/longitude without changing the zoom level'''
		coordinate = CLLocationCoordinate2D(lat, lon)
		self.mk_map_view.setCenterCoordinate_animated_(coordinate, animated, restype=None, argtypes=[CLLocationCoordinate2D, c_bool])

	@on_main_thread
	def get_center_coordinate(self):
		'''Return the current center coordinate as a (latitude, longitude) tuple'''
		coordinate = self.mk_map_view.centerCoordinate(restype=CLLocationCoordinate2D, argtypes=[])
		return coordinate.latitude, coordinate.longitude

	@on_main_thread
	def point_to_coordinate(self, point):
		'''Convert from a point in the view (e.g. touch location) to a latitude/longitude'''
		coordinate = self.mk_map_view.convertPoint_toCoordinateFromView_(CGPoint(*point), self._objc_ptr, restype=CLLocationCoordinate2D, argtypes=[CGPoint, c_void_p])
		return coordinate.latitude, coordinate.longitude

	def _notify_region_changed(self):
		if callable(self.scroll_action):
			self.scroll_action(self)


# --------------------------------------
# DEMO:

def long_press_action(sender):
	# Add a pin when the MapView recognizes a long-press
	c = sender.point_to_coordinate(sender.long_press_location)
	sender.remove_all_pins()
	sender.add_pin(c[0], c[1], 'Dropped Pin', str(c), select=True)
	sender.set_center_coordinate(c[0], c[1], animated=True)

def scroll_action(sender):
	# Show the current center coordinate in the title bar after the map is scrolled/zoomed:
	sender.name = 'lat/long: %.2f, %.2f' % sender.get_center_coordinate()

if __name__ == '__main__':
	# Create and present a MapView:
	v = MapView(frame=(0, 0, 500, 500))
	v.long_press_action = long_press_action
	v.scroll_action = scroll_action
	v.present('sheet')
	# Add a pin with the current location (if available), and zoom to that location:
	import location
	location.start_updates()
	time.sleep(1)
	loc = location.get_location()
	location.stop_updates()
	if loc:
		lat, lon = loc['latitude'], loc['longitude']
		v.set_region(lat, lon, 0.05, 0.05, animated=True)
		v.add_pin(lat, lon, 'Current Location', str((lat, lon)))
		v.add_pin(lat+.01, lon, 'red','a')
		v.add_pin(lat-.011, lon+.01, 'gray','b')
		v.add_pin(lat+.003, lon+.005, 'blue','a')
