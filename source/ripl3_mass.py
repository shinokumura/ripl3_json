import pandas as pd
from submodules.utilities.util import slices

from source.config import MASSFILE, AME2020

def read_mass_table():
    z = []
    a = []
    mselect = []
    with open(MASSFILE) as f:
        lines = f.readlines()
        if any(x in MASSFILE for x in ["mass-frdm95.dat", "mass-hfb14.dat"]):
            for line in lines[5:]:
                t_z, t_a, t_s, t_fl, t_mexp, t_dmexp, t_mth = slices(
                    line, 4, 4, 3, 2, 10, 10, 10
                )
                z.append(int(t_z))
                a.append(int(t_a))

                if not t_mexp.isspace():
                    mselect.append(float(t_mexp))
                elif t_mexp.isspace() and not t_mth.isspace():
                    mselect.append(float(t_mth))
                else:
                    mselect.append(0.0)

    df = pd.DataFrame({"Z": z, "A": a, "Mselect": mselect})

    ## check
    if df.empty:
        raise TypeError()

    return df



def read_amdc():
    """
    Atomic Mass Data Center Mass Evaluation AME 2020 https://www-nds.iaea.org/amdc/
    """
    z = []
    a = []
    mselect = []
    with open(AME2020) as f:
        lines = f.readlines()
        if "mass_1.mass20.txt" in MASSFILE:

            for line in lines[36:]:
                t_1, t_nz, t_n, t_z, t_a, t_el, t_0, t_mexcess = slices(
                    line, 1, 3, 5, 5, 5, 4, 5, 14
                )
                z.append(int(t_z))
                a.append(int(t_a))

                if not t_mexcess.isspace():
                    mselect.append(float(t_mexcess.replace("#", "")) / 1000)
                else:
                    mselect.append(0.0)

    df = pd.DataFrame({"Z": z, "A": a, "Mselect": mselect})

    ## check
    if df.empty:
        raise TypeError()

    return df


mass_table_df = read_mass_table()
print(mass_table_df)
