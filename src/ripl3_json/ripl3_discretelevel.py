####################################################################
#
# This file is part of exfor-parser.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Disclaimer: The code is still under developments and not ready
#             to use. It has been made public to share the progress
#             among collaborators.
# Contact:    nds.contact-point@iaea.org
#
# Read discrete levels from RIPL-3 data
#
####################################################################


import json
import os
import re

from submodules.utilities.util import slices
from submodules.utilities.elem import ztoelem


def read_identification_record(line):
    #   SYMB    A     Z     Nol    Nog    Nmax    Nc     Sn[MeV]     Sp[MeV]
    #   22Mg    22    12    17     18      9      4     19.382000    5.497000
    # The corresponding FORTRAN format is (a5,6i5,2f12.6)
    # SYMB   : mass number with symbol of the element
    # A      : mass number
    # Z      : atomic number
    # Nol    : number of levels in the decay scheme
    # Nog    : number of gamma rays in the decay scheme
    # Nmax   : maximum number of levels up to which the level scheme is
    #          complete
    # Nc     : number of a level up to which spins and parities are unique
    # Sn     : neutron separation energy in MeV
    # Sp     : proton separation energy in MeV

    return slices(line, 5, 5, 5, 5, 5, 5, 5, 12, 12)


def read_level_record(line):
    #     N1  Elv[MeV]  s   p   T1/2    Ng  J  unc  spins   nd  m  percent  mode      m   percent   mode    /.../ shift     band
    # 1  0.000000  0.0  1  3.86E+00  0           0+      2  =  8.2000E+01 %IT     =  1.8000E+01 %B-     /.../ 0.031100  2
    # 2  1.246300  2.0  1  2.10E12   1           2+      0
    # (i3,1x,f10.6,1x,f5.1,i3,1x,(e10.3),i3,1x,a1,1x,a4,1x,a18,i3,10(1x,a2,1x,e10.4,1x,a7),f10.6,1x,3(2i))
    # Nl    :  sequential number of a level
    # Elv   :  energy of the level in MeV
    # s     :  level spin (unique). Whenever possible unknown spins up to
    # p     :  parity (unique). If the parity of the level was unknown, positive or
    # T1/2  :  half-life of the level (if known). All known half-lives or level widths
    # Ng    :  number of gamma rays de-exciting the level.
    # J     :  flag for spin estimation method (see below the list of possible flags).
    # unc   :  flag for an uncertain level energy. When impossible to determine, the
    # spins :  original spins from the ENSDF file.
    # nd    :  number of decay modes of the level (if known). Values from 0 through 10
    # m     :  decay percentage modifier; informs a user about major uncertainties.
    # percent: percentage decay of different decay modes. As a general rule  the
    # mode   : short indication of decay modes of a level (see Table below).
    # shift  : value assigned to the unknown "X", in MeV.
    # band   : integer assigned to band(s) to which the level is part
    # (i3,1x,f10.6,1x,f5.1,i3,1x,(e10.3),i3,1x,a1,1x,a4,1x,a18,i3,10(1x,a2,1x,e10.4,1x,a7),f10.6,1x,3(2i))
    return slices(line, 3, 11, 6, 3, 11, 3, 8, 18, 3)


def read_gamma_record(line):
    #     Two examples of the gamma records are given below:
    #   Nf    Eg[MeV]       Pg          Pe          ICC
    #   3      0.055     2.790E-01   2.870E-01    5.130E-03
    #   1      0.113     5.330E-01   5.330E-01    0.000E+00
    # The corresponding FORTRAN format is (39x,i4,1x,f10.4,3(1x,e10.3))
    # Nf    : sequential number of the final state
    # Eg    : gamma-ray energy in MeV
    # Pg    : Probability that the level decays through photon (gamma ray) emission.
    #         If no branching ratio is given in the ENSDF file, Pg=0.
    # Pe    : Probability of the electromagnetic transition (photon, conversion electron, pair creation).
    #         The sum of the Pe gives the IT (electromagnetic transition) branching ratio of the level.
    #         This is 1 unless other decay modes are listed in the level record (see example below).
    # ICC   : Internal conversion coefficient of the transition.
    #  (39x,i4,1x,f10.4,3(1x,e10.3))
    return slices(line, 39, 4, 11, 11, 11, 11)


def read_levels(charge):

    levels_file = "data/levels/z" + str(charge).zfill(3) + ".dat"

    with open(levels_file) as f:
        lines = f.read().splitlines()

    level_dict = {}
    i = 0
    while i < len(lines):
        symb, a, z, nol, nog, nmax, nc, sn, sp = read_identification_record(lines[i])

        ## level scheme array
        levels = []

        if int(nol) + int(nog) > 0:
            lev = i + 1
            lev_lines = lev + int(nol) + int(nog)

            while lev < lev_lines:
                nl, elv, s, p, thalf, ng, _, spins, nd = read_level_record(lines[lev])

                ## level layes array
                gammas = []
                if int(ng) > 0:
                    for gl in range(lev + 1, lev + 1 + int(ng)):
                        ## reading gamma lines
                        _, nf, eg, pg, pe, icc = read_gamma_record(lines[gl])
                    gammas.append(
                        {
                            "final_state": int(nf),
                            "gamma_energy": "%10.4e" % float(eg),
                            "probability_gamma": "%10.4e" % float(pg),
                            "probability_electmag": "%10.4e" % float(pe),
                            "internal_conversion": "%10.4e" % float(icc),
                        }
                    )

                levels.append(
                    {
                        "level_number": int(nl),
                        "level_energy": "%10.4e" % float(elv),
                        "spin": float(s.strip()),
                        "parity": int(p.strip()),
                        "half_life": "%10.4e" % float(thalf.strip())
                        if thalf.strip() != ""
                        else None,
                        "spin_notation": spins.strip(),
                        "gamma_record": gammas,
                    }
                )

                if lev > i + int(nol) + int(nog):
                    break

                lev += 1 + int(ng)

        if i == len(lines):
            break

        i += 1 + int(nol) + int(nog)

        level_dict[symb.strip()] = {
            "A": int(a.strip()),
            "Z": int(z.strip()),
            "nlevels": int(nol.strip()),
            "Sn": "%10.4e" % float(sn),
            "Sp": "%10.4e" % float(sp),
            "levels": [l["level_energy"] for l in levels],
            "level_record": levels,
        }

    return level_dict


def write_json(nuclide, dic):

    elem = re.sub(r"[^A-Za-z]{1,2}", "", nuclide)
    file_dir = os.path.join("levels_json", elem)

    print(elem)

    if os.path.exists(file_dir):
        pass

    else:
        os.mkdir(file_dir)

    file = os.path.join(file_dir, nuclide + ".json")

    with open(file, "wt") as json_file:
        json.dump(dic, json_file, indent=2)


def main():
    for charge in range(1, 119):
        level_dict = read_levels(charge)

        for key, item in level_dict.items():

            # write json file
            write_json(key, dict({"nuclide": key, "level_info": item}, indent=1))

            # post data to mongoDb
            # post_one_mongodb("ripl3_levels", dict({"nuclide": key, "level_info": item}))
            # replace_one_mongodb("ripl3_levels", dict({"nuclide": key}),  dict({"nuclide": key, "level_info": item}))


###################################################################
###
###   For exfor_parser
###
###################################################################
class RIPL_Level:
    def __init__(self, charge, mass, e_lvl):

        self.charge = int(charge)
        self.mass = int(mass)
        self.e_lvl = float(e_lvl)

        self.lelevs_info = self.ripl_levels_info_by_nuclide()
        self.levels = self.ripl_levels_by_nuclide()


    def ripl_levels_by_charge(self):
        return read_levels(self.charge)


    def ripl_levels_info_by_nuclide(self):
        elem = ztoelem(self.charge)
        file = os.path.join(
            "levels_json", elem, str(self.mass) + elem + ".json"
        )
        if os.path.exists(file):
            with open(file) as f:
                json_content = f.read()
            return json.loads(json_content)
        
        else:
            return None


    def ripl_levels_by_nuclide(self):
        if self.lelevs_info:
            return self.lelevs_info["level_info"]["levels"]
        
        else:
            return []


    def ripl_find_level_num(self):
        if self.e_lvl == 0.0:
            return int(0)
        else:
            for l in range(len(self.levels)):
                if self.e_lvl * 0.95 < float(self.levels[l]) < self.e_lvl * 1.05:
                    return int(l)
            return None
        

    def get_all_ripl_levels(self):
        all = {}
        for charge in range(1, 119):
            level_dict = read_levels(charge)

            for key, item in level_dict.items():
                # write json file
                all = {"nuclide": key, "level_info": item}

        return read_levels(self.charge)


if __name__ == "__main__":
    main()
