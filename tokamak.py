import argparse
import cubit
import yaml
import numpy as np

def parse_args():

	parser = argparse.ArgumentParser(description='Create a tokamak geometry based on a radial build.')
	parser.add_argument('radial_build', type=open, help='YAML file path describing tokamak radial build')
	parser.add_argument('major_radius', type=float, help='plasma major radius [cm]')
	parser.add_argument('minor_radius', type=float, help='plasma minor radius [cm]')
	parser.add_argument('export_path', nargs='?', default='tokamak', help='path to export .sat file')
	args = parser.parse_args()
	return args

def read_radial_build(file):
	
	radial_build = yaml.load(file, Loader=yaml.FullLoader)
	return radial_build


def build_torus(major_radius,minor_radius,radial_build):

	layers = list(radial_build.keys())
	thicknesses = list(radial_build.values())

	if np.sum(thicknesses) > major_radius:
		raise(ValueError, "material overlap at tokamak center.")
	
	cubit.init([''])

	cubit.torus(major_radius,minor_radius)
	
	radii = np.cumsum(thicknesses) + minor_radius
	for radius in radii:
		cubit.torus(major_radius,radius)

	cubit.cmd("group 'mat:Vacuum' add vol 1")
	vol_id = len(thicknesses) + 2
	for id, layer_name in zip(range(vol_id-1,1,-1), reversed(layers)):
		cubit.cmd("subtract volume "+str(id - 1)+" from volume "+str(id)+" keep_tool")
		cubit.cmd("group 'mat:"+ layer_name +"' add vol " + str(vol_id))
		vol_id += 1

	cubit.cmd("imprint volume all")
	cubit.cmd("merge volume all")


def save_geometry(export_path):

	cubit.cmd("set attribute on")
	cubit.cmd("export acis '"+export_path+".sat' overwrite")


def main():

	parameters = parse_args()
	radial_build = read_radial_build(parameters.radial_build)
	build_torus(parameters.major_radius, parameters.minor_radius, radial_build)
	save_geometry(parameters.export_path)
	print("Successfully created tokamak geometry.")


if __name__ == '__main__':
	main()