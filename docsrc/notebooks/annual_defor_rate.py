#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
# author          :Ghislain Vieilledent
# email           :ghislain.vieilledent@cirad.fr, ghislainv@gmail.com
# web             :https://ecology.ghislainv.fr
# python_version  :>=3
# license         :GPLv3
# ==============================================================================

import os
import numpy as np
import matplotlib.pyplot as plt

os.chdir("/home/ghislain/Code/riskmapjnr/docsrc/notebooks")

# Notations
# A1: forest area at date 1
# A2: forest area at date 2
# D: deforestation between date 1 and 2
# T: time interval (in years) between date 1 and 2


# Functions for computing annual deforestation rate

# Cirad
def annual_defor_cirad(D, A1, T):
    d = 1 - (1 - D / A1) ** (1 / T)
    return d


# Clark University
# Not defined for A2 = 0
def annual_defor_clark(D, A1, T):
    A2 = A1 - D
    d = (A1 / A2) ** (1 / T) - 1
    return d


# FAO (annual rate of change)
def annual_change_fao(D, A1, T):
    A2 = A1 - D
    d = (A2 / A1) ** (1 / T) - 1
    return d


# Puyravaud
# Not defined for A2 = 0
def annual_defor_puyravaud(D, A1, T):
    A2 = A1 - D
    d = -((1 / T) * np.log(A2 / A1))
    return d


# D-perc relationship
# Data
D = np.arange(0, 100, step=10)
T = 5
p_cirad = annual_defor_cirad(D=D, A1=100, T=T)
p_clark = annual_defor_clark(D=D, A1=100, T=T)
p_fao = annual_change_fao(D=D, A1=100, T=T)
p_puyravaud = annual_defor_puyravaud(D=D, A1=100, T=T)
# Plot
fig, ax = plt.subplots(figsize=(8, 6), dpi=150)
ax.plot(D, p_cirad, label="Cirad")
ax.plot(D, p_clark, label="Clark U.")
ax.plot(D, p_fao, label="FAO")
ax.plot(D, p_puyravaud, label="Puyravaud")
ax.hlines(y=0, xmin=0, xmax=100, colors="black", linestyles="dashed")
ax.set_xlabel("A_T / A_0 (%)")
ax.set_ylabel("Annual deforestation rate (%/yr)\n"
              "(FAO: rate of change)")
ax.set_title("Comparing formulas for computing\n"
             "the annual deforestation rate")
ax.annotate("T = 5 years", xy=(0, 0.3))
ax.legend()
fig.savefig("outputs_test_annual_defor_rate/D-perc-relationship.png")

# D-T relationship
# Data
D = 50
T = np.arange(1, 11)
p_cirad = annual_defor_cirad(D=D, A1=100, T=T)
p_clark = annual_defor_clark(D=D, A1=100, T=T)
p_fao = annual_change_fao(D=D, A1=100, T=T)
p_puyravaud = annual_defor_puyravaud(D=D, A1=100, T=T)
# Plot
fig, ax = plt.subplots(figsize=(8, 6), dpi=150)
ax.plot(T, p_cirad, label="Cirad")
ax.plot(T, p_clark, label="Clark U.")
ax.plot(T, p_fao, label="FAO")
ax.plot(T, p_puyravaud, label="Puyravaud")
ax.hlines(y=0, xmin=1, xmax=10, colors="black", linestyles="dashed")
ax.set_xlabel("T (yr)")
ax.set_ylabel("Annual deforestation rate (%/yr)\n"
              "(FAO: rate of change)")
ax.set_title("Comparing formulas for computing\n"
             "the annual deforestation rate")
ax.annotate("A_T / A_0 = 50%", xy=(8, 0.3))
ax.legend()
fig.savefig("outputs_test_annual_defor_rate/D-T-relationship.png")

#
