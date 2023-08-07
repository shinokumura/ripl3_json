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
####################################################################
import os

if os.path.exists("data"):
    data_path = "./data"
else:
    from importlib.resources import files
    data_path = files("ripl3_json").joinpath("data")

print(data_path)

out_path = "./data"

MASSFILE_FRDM = os.path.join(data_path, "mass-frdm95.dat")
MASSFILE_HFB = os.path.join(data_path, "mass-hfb14.dat")
MASSFILE = MASSFILE_FRDM
AME2020 = os.path.join(data_path, "mass_1.mass20.txt")


