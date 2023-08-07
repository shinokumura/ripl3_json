MASS_RANGE_FILE = "A_min_max.txt"

# ------------------------------------------------------------------------------
# Mass
# ------------------------------------------------------------------------------
def read_mass_range():
    mass_range = {}
    with open(MASS_RANGE_FILE) as f:
        for z in f.readlines():
            if z.startswith("#"):
                continue
            z_mass = z.split(",")
            mass_range[z_mass[0]] = {"min": z_mass[1].strip(), "max": z_mass[2].strip()}
    return mass_range
