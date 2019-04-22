''' Pre-determined scene db data '''
from arnold import *

# A list of pre-defined distant light matrices to be used in the scene
distant_lights_matrix = {
	'top_light': AtMatrix(
		1, 0, 0, 0,
		0, 2.22044605, -1, 0,
		0, 1, 2.22044605, 0,
		0, 0, 0, 1
	),
	'key_light': AtMatrix(
		0.707106769, -5.55111512, -0.707106769, 0,
		-0.5, 0.707106769, -0.5, 0,
		0.5, 0.707106769, 0.5, 0,
		0, 0, 0, 1
	),
	'rim_light': AtMatrix(
		-0.707106769,0,0.707106769,0,
		-0.241844758,0.939692616,-0.241844758,0,
		-0.664463043,-0.342020154,-0.664463043,0,
 		0, 0, 0, 1
	)
}

# Fixed camera matrix
cam_matrix = AtMatrix(
		1, 0, 0, 0,
		0, 1, 0, 0,
		0, 0, 1, 0,
		0, 0, 6, 1
	)


options = {
		'AA_samples': 3,
		'outputs': '"RGBA RGBA gfilter tiffdriver"',
		'xres':720,
		'yres':486
		}
camera = {
		'name':'main_camera',
		'fov':45.0,
		'matrix':cam_matrix
	}

driver_tiff = {
	'name':'tiffdriver',
	'filename':'"image.tif"',
}

gaussian_filter = {
	'name':'gfilter',
	'width':2.0
}

standard_shader = {
	'name':'stdshader',
	'Kd': 1.0,
	'Kd_color': [1, 1, 1],
	'Ks': 1.0,
	'Ks_color': [1,1,1],
	'specular_roughness' : 0.7
}

prims = [
	{
		'sphere':
		{
			'center': [0,0,0],
			'radius': 1,
			'shader': 'stdshader'
		}
	}
]


