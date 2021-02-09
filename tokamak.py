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
	n = list(radial_build.keys())
	t = list(radial_build.values())
	return n, t


def build_torus(R,r,n,t):

	T = 0.0
	for i in t:
		T += i
	if T+r > R:
		print("Error: inboard thickness plus plasma minor radius is greater than plasma major radius.")
		exit()
	print(T)
	cubit.init([''])

	cubit.torus(R,r)
	a = r
	for j in t:
		a += j
		cubit.torus(R,a)

	k = len(t)+1
	while k > 1:
		cubit.cmd("subtract volume "+str(k-1)+" from volume "+str(k)+" keep_tool")
		k -= 1

	cubit.cmd("imprint volume all")
	cubit.cmd("merge volume all")

	cubit.cmd("group 'mat:Vaccum' add vol 1")
	m = 2*len(n)+1
	for l in n:
		cubit.cmd("group 'mat:"+str(l)+"' add vol "+str(m))
		m -= 1


def save_geometry(export_path):

	cubit.cmd("set attribute on")
	cubit.cmd("export acis '"+export_path+".sat' overwrite")


def main():

	parameters = parse_args()
	radial_build = read_radial_build(parameters.radial_build)
	build_torus(parameters.major_radius, parameters.minor_radius, radial_build[0], radial_build[1])
	save_geometry(parameters.export_path)
	print("Successfully created tokamak geometry.")


if __name__ == '__main__':
	main()