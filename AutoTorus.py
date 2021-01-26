import cubit
cubit.init([''])

print("\n")

R = int(input("What is the plasma major radius [cm]? "))
r = int(input("What is the plasma minor radius [cm]? "))
names_input = input("Please name the material regions (in series, excluding plasma, separated by comma and space)? ")
t_input = input("What are the respective thicknesses of those material regions (in series, separated by comma and space) [cm]? ")

names = names_input.split(", ")
t = t_input.split(", ")

print("\n")

print("Materials array:",names)
print("Respective thicknesses:",t)

print("\n")

if len(names) != len(t):
	print("Error: the materials array is not the same length as the thicknesses array.")
	exit()

T = 0
for i in t:
	T += int(i)
print("Inboard is", T,"cm thick.")

print("\n")

if T+r > R:
	print("Error: inboard thickness plus plasma minor radius is greater than plasma major radius.")
	exit()

cubit.cmd("create torus major radius "+str(R)+" minor radius "+str(r))
#cubit.torus(R,r)
#print("Created torus 1 :\nMajor radius =",R,"\nMinor radius =",r,"\n")
a = r
for j in range(len(t)):
	a += int(t[j])
	cubit.cmd("create torus major radius "+str(R)+" minor radius "+str(a))
	#cubit.torus(R,a)
	#print("Created torus",j+2,":\nMajor radius =",R,"\nMinor radius =",a,"\n")

print("\n")

k = len(t)+1
while k > 1:
	#print("subtract volume",k-1,"from volume",k,"keep_tool")
	cubit.cmd("subtract volume "+str(k-1)+" from volume "+str(k)+" keep_tool")
	k -= 1

print("\n")

#print("imprint volume all")
#print("merge volume all")
cubit.cmd("imprint volume all")
cubit.cmd("merge volume all")

print("\n")

#print("group 'mat:Vaccum' add vol 1")
cubit.cmd("group 'mat:Vaccum' add vol 1")
n = 2*len(names)+1
for l in names:
	#print("group 'mat:{}' add vol {}".format(l,n))
	cubit.cmd("group 'mat:"+str(l)+"' add vol "+str(n))
	n -= 1

print("\n")

filename = input("Please name the geometry file: ")
path = input("To what path would you like to export the geometry file? ")

cubit.cmd("set attribute on")
cubit.cmd("export acis '"+path+filename+".sat' overwrite")

print("Successfully created geometry.")
print("Geometry exported to ",path,filename)