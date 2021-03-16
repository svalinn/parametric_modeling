"""
This script generates a circular tokamak geometry in Coreform Cubit/Trelis based on a
given radial build. This radial build may differentiate between inboard and outboard, or
it may be symmetric between the two regions.

This script requires a YAML file describing the desired radial build, plasma major
radius, and plasma minor radius as inputs. The user may provide an optional export path
as well, though if none is provided, the output file is exported to the present working
directory under the name 'tokamak.sat'.

This script requires that argparse, PyYAML, and NumPy be installed within the working
Python environment. The script requires that Coreform Cubit/Trelis be installed on the
working system as well.

This script can also be imported as a module and contains the following functions:

    * arg_parser - parses and returns the input arguments
    * read_radial_build - returns the radial build of the input YAML file as a dictionary
    * contor - generates concentric torii according to the given radial build
    * build_torus - generates the completed tokamak geometry
    * save_geometry - exports the geometry from Cubit/Trelis
    * main - the main function of the script
"""

import argparse
import cubit
import yaml
import numpy as np

def arg_parser():
    parser = argparse.ArgumentParser(description='Create a tokamak geometry based on a radial build.')
    parser.add_argument('radial_build', type=open, help='YAML file path describing tokamak radial build')
    parser.add_argument('major_radius', type=float, help='plasma major radius [cm]')
    parser.add_argument('minor_radius', type=float, help='plasma minor radius [cm]')
    parser.add_argument('export_path', nargs='?', default='tokamak', help='path to export .sat file')
    parser.add_argument('-d', '--dagmc', action='store_true', default='False', help='export a dagmc.h5m file as well as .sat')
    parser.add_argument('-g', '--graveyard', action='store_true', default='False', help='include graveyard in geometry')
    args = parser.parse_args()
    return args

def read_radial_build(file_):
    """
    Loads the radial build YAML file as a Python dictionary

    Parameters
    ----------
    file_ : str
        The radial build file path

    Returns
    -------
    radial_build : list
        A Python dictionary storing the tokamak radial build data
    """
    radial_build = yaml.load(file_, Loader=yaml.FullLoader)
    return radial_build

def contor(major_radius, minor_radius, radial_build):
    """
    A function used by the function build_torus that generatres concentric torii in
    Cubit/Trelis corresponding to the portion of the radial build (inboard, outboard, or
    all) passed to the function.

    Parameters
    ----------
    major_radius : float
        The plasma major radius
    minor_radius : float
        The plasma minor radius
    radial_build : list
        The portion of the radial build being passed to the
        function
    """
    radii = np.cumsum(radial_build) + minor_radius
    for radius in radii:
        cubit.torus(major_radius,radius)

def build_torus(major_radius, minor_radius, radial_build, graveyard):
    """
    Generates a circular tokamak geometry in Cubit/Trelis according to a radial build of
    homogeneous material layers.

    Parameters
    ----------
    major_radius : float
        The plasma major radius
    minor_radius : float
        The plasma minor radius
    radial_build : dict
        A Python dictionary storing the tokamak radial build data
    graveyard : bool, optional
        A flag used to determine whether a graveyard volume is to be added to the geometry
    """
    if 'Inboard' in radial_build:
        inboard_layers = list(radial_build['Inboard'].keys())
        inboard_thicknesses = list(radial_build['Inboard'].values())
        outboard_layers = list(radial_build['Outboard'].keys())
        outboard_thicknesses = list(radial_build['Outboard'].values())

        cubit.init([''])

        cubit.cylinder(4*major_radius, major_radius, major_radius, major_radius)
        cubit.torus(major_radius, minor_radius)
        cubit.cmd("group 'mat:Vacuum' add vol 2")

        contor(major_radius, minor_radius, inboard_thicknesses)

        # volume id for inboard layers = number of elements in inboard layers array + 2
        # from the 2 volumes created previously + 1 for subtraction operation + 1 for
        # intersection operation
        inboard_id = len(inboard_layers) + 4
        for id, layer_name in zip(range(inboard_id - 2, 2, -1), reversed(inboard_layers)):
            cubit.cmd("subtract volume " + str(id - 1) + " from volume " + str(id) + " keep_tool")
            cubit.cmd("intersect vol 1 " + str(inboard_id - 1) + " keep")
            cubit.cmd("delete vol " + str(inboard_id - 1))
            cubit.cmd("group 'mat:" + layer_name + "' add vol " + str(inboard_id))
            # increase id number by 2, 1 for subtraction operation + 1 for intersection
            # operation
            inboard_id += 2

        contor(major_radius, minor_radius, outboard_thicknesses)
        
        # volume id for outboard layers = number of elements in outboard layers array
        # + id number left off on in inboard loop - 2 to undo +2 at end of loop + 1 for
        # subtraction operation
        outboard_id = len(outboard_layers) + inboard_id - 1
        for id, layer_name in zip(range(outboard_id - 1, inboard_id - 1, -1), reversed(outboard_layers)):
            cubit.cmd("subtract volume " + str(id - 1) + " from volume " + str(id) + " keep_tool")
            cubit.cmd("subtract vol 1 from vol " + str(outboard_id) + " keep_tool")
            cubit.cmd("group 'mat:" + layer_name + "' add vol " + str(outboard_id))
            # increase if number by 1 for subtraction operation
            outboard_id += 1

        cubit.cmd("subtract volume 2 from volume " + str(inboard_id - 1) + " keep_tool")
        cubit.cmd("subtract vol 1 from vol " + str(outboard_id) + " keep_tool")
        cubit.cmd("group 'mat:" + outboard_layers[0] + "' add vol " + str(outboard_id))
        
        cubit.cmd("delete vol 1")

        if graveyard == True:
            length = 4*major_radius
            cubit.cmd("brick x " + str(length) + " y " + str(length) + " z " + str(length))
            cubit.cmd("brick x " + str(length*1.25) + " y " + str(length*1.25) + " z " + str(length*1.25))
            cubit.cmd("subtract vol " + str(outboard_id + 1) + " from vol " + str(outboard_id + 2))
            cubit.cmd("group 'mat:Graveyard' add vol " + str(outboard_id + 3))

        cubit.cmd("imprint volume all")
        cubit.cmd("merge volume all")

    else:
        layers = list(radial_build.keys())
        thicknesses = list(radial_build.values())

        cubit.init([''])

        cubit.torus(major_radius,minor_radius)
        cubit.cmd("group 'mat:Vacuum' add vol 1")

        contor(major_radius, minor_radius, thicknesses)

        vol_id = len(thicknesses) + 2
        for id, layer_name in zip(range(vol_id - 1, 1, -1), reversed(layers)):
            cubit.cmd("subtract volume " + str(id - 1) + " from volume " + str(id) + " keep_tool")
            cubit.cmd("group 'mat:" + layer_name + "' add vol " + str(vol_id))
            vol_id += 1

        if graveyard == True:
            length = 4*major_radius
            cubit.cmd("brick x " + str(length) + " y " + str(length) + " z " + str(length))
            cubit.cmd("brick x " + str(length*1.25) + " y " + str(length*1.25) + " z " + str(length*1.25))
            cubit.cmd("subtract vol " + str(vol_id) + " from vol " + str(vol_id + 1))
            cubit.cmd("group 'mat:Graveyard' add vol " + str(vol_id + 2))

        cubit.cmd("imprint volume all")
        cubit.cmd("merge volume all")

def save_geometry(export_path, dagmc):
    """
    Exports the tokamak geometry from Cubit/Trelis to the specified path.

    Parameters
    ----------
    export_path : str
        The file path to which the .sat file will be exported
    dagmc : bool, optional
        A flag used to determine whether the geometry is exported as a dagmc.h5m geometry
        as well as a .sat file (uses default make_watertight parameters)
    """
    cubit.cmd("set attribute on")
    cubit.cmd("export acis '" + export_path + ".sat' overwrite")
    if dagmc == True:
        print("Creating DAGMC geometry...")
        cubit.cmd("export dagmc 'dagmc.h5m' make_watertight")

def main():
    parameters = arg_parser()
    radial_build = read_radial_build(parameters.radial_build)
    build_torus(parameters.major_radius, parameters.minor_radius, radial_build, parameters.graveyard)
    save_geometry(parameters.export_path, parameters.dagmc)
    print("Successfully created tokamak geometry.")

if __name__ == '__main__':
    main()
