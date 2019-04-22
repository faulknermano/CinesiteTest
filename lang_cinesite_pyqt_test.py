#C:/Users/lernie/AppData/Local/Programs/Python/Python37/python.exe
#!/usr/bin/env python3

'''
lang_cinesite_pyqt_test.py

	Script to execute render a predefined scene using the Arnold renderer.

Modules

	This script requires:

		- ainodes.py (pre-generated node scene db data, included in repo)
		
Notes

	- Generates an arnold.log file in the same location as script
	- Renders an image called render_image.tif in the same location as script

'''

__author__      = "Lernwel Ang"
__copyright__   = "Copyright 2019, Lernwel Ang"
__credits__     = ["Lernwel Ang"]
__version__     = "0.0.1"
__email__       = "faulknermano@gmail.com"
__status__      = "Prototype"

import os
import sys

# include camera, options, and driver, and sphere geo
import ainodes

from arnold import *

from PyQt5.QtCore import (Qt, pyqtSignal, QObject )
from PyQt5.QtWidgets import (
	QMainWindow, QLabel, QGridLayout, QWidget,
	QPushButton, QApplication, QColorDialog, QPlainTextEdit
	)
from PyQt5.QtGui import  QPixmap, QColor

# ======================
# Conveninence functions
# ======================

def get_path(fn):
	s_fn = fn.replace('\\','/').split('/')
	path = '/'.join(s_fn[0:-1])
	return(path)



# ======================
# Custom classes
# ======================

class AiDistantLight():
	''' Encapsulation of certain Arnold distant light attributes, mainly for convenience of init values for instances'''
	def __init__(self, light_name):
		# attribs (dict) maps light attributes simply and is init'd with default values
		# attribs contains the matrix, too
		self.attribs = {
			'color': [1,1,1],
			'shadow_color': [1,1,1],
			'shadow_density': 1,
			'cast_shadows': 'on',
			'intensity': 1,
			'exposure': 0,
			'samples': 1,
			'normalize': 'on',
			'diffuse': 1,
			'specular': 1,
			'aov': '"default"',
			'angle': 0,
		}
		self.name = light_name

class ArnoldRender(QObject):
	''' Opens up Arnold, sets up scene, and renders
	Uses settings from ainodes.py
	'''
	is_render_done = pyqtSignal(int)

	def DoRender(self):
		
		AiBegin()
		AiMsgSetLogFileName(self.log_file)
		AiMsgSetLogFileFlags(AI_LOG_ALL)

		# Create options
		options = AiUniverseGetOptions()
		self.SetAiNode(False, options, '', ainodes.options)

		# Set camera
		self.SetAiNode(True, 'persp_camera', '',  ainodes.camera)

		# Filter and driver
		self.SetAiNode(True, 'gaussian_filter', '', ainodes.gaussian_filter)
		self.SetAiNode(True, 'driver_tiff', '', ainodes.driver_tiff)

		# Shader
		# Modify shader colour
		ainodes.standard_shader['Kd_color'] = self.prim_color
		self.SetAiNode(True, 'standard', '', ainodes.standard_shader)

		# Primitives
		for pr in ainodes.prims:
			for k,v in pr.items(): # k is the type, v is the attrib dict
				self.SetAiNode(True, k, '', v)

		# Create AiDistantLights 
		for name,matrix in ainodes.distant_lights_matrix.items(): 
			# create the light
			dl = AiDistantLight(name)

			# populate the matrix
			dl.attribs['matrix'] = matrix
			self.SetAiNode(True, 'distant_light', name, dl.attribs)

		res = AiRender()

		AiEnd()
		self.is_render_done.emit(res)

	def SetAiNode(self, create=False, node_type='', node_name='', attribs=None):
		if create == True:
			# Create a new node
			n = AiNode( node_type )
			if node_name != None:
				AiNodeSetStr( n, 'name', node_name )
		else:
			# Use existing node
			n = node_type 
		try:
			for k,v in attribs.items():
				if isinstance(v, AtMatrix):
					am = AiArrayAllocate(1, 1, AI_TYPE_MATRIX)
					AiArraySetMtx( am, 0, v )
					AiNodeSetArray( n, "matrix", am  )
				elif isinstance(v, list):
					# Concat the list to a string
					sv = ' '.join(map(str,v))
					AiNodeSetAttributes(n, '%s %s' % (k,sv))
				else:
					AiNodeSetAttributes(n, '%s %s' % (k,v))
		except AttributeError as err:
			print(err)
			print('Unable to set attributes on SetAiNode')

	def __init__(self, prim_color, log_file):
		QObject.__init__(self)
		self.log_file = log_file
		self.prim_color = prim_color # list

class FColorPickerButton(QPushButton):
	''' Custom picker button for bringing up Picker dialog
	and then to convert result to usable value for renderer (i.e. float RGB)'''
	
	# Signal gets passed a tuple of float RGB (i.e. colour picked)
	is_changed = pyqtSignal(list)
	def __init__(self, *args, **kwargs):
		super(FColorPickerButton, self).__init__(*args, **kwargs)
		self.color = None
		self.pressed.connect(self.OnColorPicker)
	
	def OnColorPicker(self, *_args):
		dialog = QColorDialog(self)

		# Set starting/default/previous value
		if self.color:
			dialog.setCurrentColor(QColor(self.color))

		# On ok
		if dialog.exec_():
			self.color = dialog.currentColor()
			rgbcolor = [
				self.color.redF(),
				self.color.greenF(),
				self.color.blueF()
			]
			self.is_changed.emit(rgbcolor)

# ======================
# GUI
# ======================

class RGui(QMainWindow):
	def OnColorPicked(self, new_color):
		self.current_color = new_color
		self.UpdateColorPickSwatch()

	def UpdateColorPickSwatch(self):
		pixmap = QPixmap(24,24)
		pixmap.fill(QColor(
			self.current_color[0]*255,
			self.current_color[1]*255,
			self.current_color[2]*255
			))
		
		self.color_pick_swatch.setPixmap(pixmap)

	def OnRenderButton(self):
		# Clear the log first
		self.text_log.clear()
		ar = ArnoldRender(self.current_color, self.log_file)
		ar.is_render_done.connect(self.OnRenderDone)
		ar.DoRender()

	def OnRenderDone(self, result):
		if result == AI_SUCCESS.value:
			self.UpdateRenderView()
			self.UpdateLog()

	def UpdateRenderView(self):
		# Default grey image
		pixmap = QPixmap(720,486)
		pixmap.fill(QColor(.2,.2,.2))
		if bool(self.rendered_image):
			if os.path.exists(self.rendered_image):
				pixmap = QPixmap(self.rendered_image)

		self.img_label.setPixmap(pixmap)

	def UpdateLog(self):
		with open(self.log_file) as f:
			self.text_log.insertPlainText(f.read())

	def InitUI(self):
		wi=0 # widget index for vertical spacing
		spacing = 24 # vertical spacing

		# Colour picker
		wi+=1
		button_pick_color = FColorPickerButton('Pick color', self)
		button_pick_color.is_changed.connect(self.OnColorPicked)

		# button_pick_color = QPushButton('Pick color', self)
		# button_pick_color.clicked.connect(self.OnColorPicker)

		
		button_pick_color.resize(button_pick_color.sizeHint())
		button_pick_color.move(1,spacing*wi)

		# Render button
		wi+=1
		button_render = QPushButton('Render', self)
		button_render.resize(button_render.sizeHint())
		button_render.move(1,spacing*wi)
		button_render.clicked.connect(self.OnRenderButton)

		self.text_log = QPlainTextEdit(self)
		self.text_log.setReadOnly(True)
		
		self.text_log.resize(400,400)

		self.cw = QWidget()
		
		self.setCentralWidget(self.cw)
		layout = QGridLayout(self.cw)
		color_layout = QGridLayout()

		# Image display
		self.img_label = QLabel(self)
		self.img_label.resize(720,486)
		layout.addWidget(self.img_label, 0,0, Qt.AlignHCenter)

		# Colour swatch
		self.color_pick_swatch = QLabel(self)
		self.color_pick_swatch.resize(24,24)
		self.color_pick_swatch.mousePressEvent = button_pick_color.OnColorPicker

		# Add button picker, swatch, and render button to color layout
		color_layout.addWidget(button_pick_color,0,1)
		color_layout.addWidget(self.color_pick_swatch,0,2)
		color_layout.addWidget(button_render,0,3)
		
		layout.addLayout(color_layout, 1, 0, Qt.AlignHCenter)
		layout.addWidget(self.text_log)
		
		# Init the render view
		self.UpdateRenderView()

		# Init the swatch
		self.UpdateColorPickSwatch()
		
		# self.setGeometry(300,300,300,200)
		self.setWindowTitle('Render view test (Arnold)')
		self.show()
	
	def __init__(self):
		super().__init__()
		spath = get_path(__file__)
		self.current_color = [1,1,1]
		self.img_label = None # control for the image display
		self.text_log = None # control for the text log
		self.color_pick_swatch = None
		self.log_file = '%s/%s' % (spath, 'arnold.log')
		
		# Modify the ainodes.driver_tiff with a fixed render output filename
		self.rendered_image = '%s/%s' % (spath, 'render_image.tif')
		ainodes.driver_tiff['filename'] = self.rendered_image
		self.InitUI()



if __name__ == '__main__':
	app = QApplication(sys.argv)
	rgui = RGui()

	sys.exit(app.exec_())
