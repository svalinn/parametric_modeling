import openmc
from math import pi

# Define materials
# Tungsten armor, assuming 8.7% void
Armor = openmc.Material()
Armor.add_element('W', 1.0)
Armor.set_density('g/cm3', 19.35*0.913)

# Reduced Activation Ferritic Martensitic steel (based on the EUROFER97 alloy)
RAFM = openmc.Material()
RAFM.add_element('Fe', 0.9, 'wo')
RAFM.add_element('Cr', 0.09, 'wo')
RAFM.add_element('W', 0.01, 'wo')
RAFM.set_density('g/cm3', 7.8)

# Pressurized helium coolant (8 MPa, 673 K)
He = openmc.Material()
He.add_element('He', 1.0)
He.set_density('g/cm3', 5.723e-3)

# Define first wall material
First_Wall = openmc.Material.mix_materials([Armor, RAFM, He], [0.05, 0.323, 0.627], 'vo', 'first_wall')

# Lead-lithium eutectic breeder/multiplier
PbLi = openmc.Material()
PbLi.add_element('Pb', 0.84, 'ao')
PbLi.add_element('Li', 0.16, 'ao', 90.0, enrichment_target='Li6', enrichment_type='ao')
PbLi.set_density('g/cm3', 10.5)

# Silicon carbide flow channel insert
SiC = openmc.Material()
SiC.add_element('Si', 0.5, 'ao')
SiC.add_element('C', 0.5, 'ao')
SiC.set_density('g/cm3', 3.21)

# Define breeder material
Breeder = openmc.Material.mix_materials([RAFM, He, PbLi, SiC], [0.075, 0.149, 0.737, 0.039], 'vo', 'breeder')

# Define back wall material
Back_Wall = openmc.Material.mix_materials([RAFM, He], [0.8, 0.2], 'vo', 'back_wall')

# Compile materials
mat = openmc.Materials([First_Wall, Breeder, Back_Wall])
mat.export_to_xml()

# Define run settings
settings = openmc.Settings()
settings.dagmc = True
settings.run_mode = 'fixed source'
settings.particles = 10000
settings.batches = 10

# Define source
source = openmc.Source()
r = openmc.stats.Discrete([480.0], [1.0])
phi = openmc.stats.Uniform(0.0, 2*pi)
z = openmc.stats.Discrete([0.0], [1.0])
source.space = openmc.stats.CylindricalIndependent(r, phi, z)
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([14.1e6], [1.0])

# Compile settings
settings.source = source
settings.export_to_xml()

# Define tallies
# Tally TBR in breeder
Breeder_ID = 6
Breeder_Cell_Filter = openmc.CellFilter(Breeder_ID)
TBR = openmc.Tally(name='TBR')
TBR.filters = [Breeder_Cell_Filter]
TBR.scores = ['H3-production']

# Compile tallies
tallies = openmc.Tallies([TBR])
tallies.export_to_xml()

# Run simulation
openmc.run()
