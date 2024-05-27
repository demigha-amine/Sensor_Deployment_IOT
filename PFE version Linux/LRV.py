import random
import sys
from Tkinter import *
from Robot import *
from Capteur import *
from random import *
from turtle import *
import time
import pickle
import signal
from math import *

global listCapteur
listCapteur = []

global listRedondant
listRedondant = []

global listTrou
listTrou = []

global temps_perdu
temps_perdu = 0.0
global x, y, D, R, T, Rc, Rs, val, charg
x = y = val = 0
D = R = T = " "


# -------------------------------------------------------------------------------------------
def do1(x, y, D, R, T, val):
    x = 360
    y = 360
    D = "Deploiement1"
    R = "Redondants_1.txt"
    T = "Trous_1.txt"
    val = 0
    return (x, y, D, R, T, val)


def do2(x, y, D, R, T, val):
    x = 432
    y = 432
    D = "Deploiement2"
    R = "Redondants_2.txt"
    T = "Trous_2.txt"
    val = 1
    return (x, y, D, R, T, val)


def do3(x, y, D, R, T, val):
    x = 612
    y = 612
    D = "Deploiement3"
    R = "Redondants_3.txt"
    T = "Trous_3.txt"
    val = 2
    return (x, y, D, R, T, val)


def do4(x, y, D, R, T, val):
    x = 864
    y = 864
    D = "Deploiement4"
    R = "Redondants_4.txt"
    T = "Trous_4.txt"
    val = 3
    screensize(900,900)
    return (x, y, D, R, T, val)


def do5(x, y, D, R, T, val):
    x = 1080
    y = 1080
    D = "Deploiement5"
    R = "Redondants_5.txt"
    T = "Trous_5.txt"
    val = 4
    screensize(1200, 1200)
    return (x, y, D, R, T, val)


def do6(x, y, D, R, T, val):
    x = 2160
    y = 2160
    D = "Deploiement6"
    R = "Redondants_6.txt"
    T = "Trous_6.txt"
    val = 5
    screensize(2500, 2500)
    return (x, y, D, R, T, val)

def do7(x, y, D, R, T, val):
    x = 3240
    y = 3240
    D = "Deploiement9"
    R = "Redondants_9.txt"
    T = "Trous_9.txt"
    val = 6
    screensize(3300, 3300)
    return (x, y, D, R, T, val)

def do8(x, y, D, R, T, val):
    x = 4320
    y = 4320
    D = "Deploiement7"
    R = "Redondants_7.txt"
    T = "Trous_7.txt"
    val = 7
    screensize(4500, 4500)
    return (x, y, D, R, T, val)

def do9(x, y, D, R, T, val):
    x = 5400
    y = 5400
    D = "Deploiement8"
    R = "Redondants_8.txt"
    T = "Trous_8.txt"
    val = 8
    screensize(5500, 5500)
    return (x, y, D, R, T, val)
def do10(x, y, D, R, T, val):
    x = 6480
    y = 6480
    D = "Deploiement10"
    R = "Redondants_10.txt"
    T = "Trous_10.txt"
    val = 9
    screensize(6500, 6500)
    return (x, y, D, R, T, val)


Rs = 18
Rc = 36
initial_angle = 35
charg = 8
# -------------------------------------------------------------------------------------------
print("Parametres de simulation :")
print("*****************************")
print("Angle de depart = ",initial_angle)
print("Charge de robot = ",charg)
print("RS = ",Rs)
print("RC = ",Rc)
print('*****************************')
print('Scenarios :')
print('Scenario 1 :  360*360')
print('Scenario 2 :  432*432')
print('Scenario 3 :  612*612')
print('Scenario 4 :  864*864')
print('Scenario 5 :  1080*1080')
print('Scenario 6 :  2160*2160')
print('Scenario 7 :  3240*3240')
print('Scenario 8 :  4320*4320')
print('Scenario 9 :  5400*5400')
print('Scenario 10:  6480*6480')
print('*****************************\n')
print('Merci d\'indiquer votre choix')



s = int(input("Num de Scenario : "))
if s == 1: (x, y, D, R, T, val) = do1(x, y, D, R, T, val)
if s == 2: (x, y, D, R, T, val) = do2(x, y, D, R, T, val)
if s == 3: (x, y, D, R, T, val) = do3(x, y, D, R, T, val)
if s == 4: (x, y, D, R, T, val) = do4(x, y, D, R, T, val)
if s == 5: (x, y, D, R, T, val) = do5(x, y, D, R, T, val)
if s == 6: (x, y, D, R, T, val) = do6(x, y, D, R, T, val)
if s == 7: (x, y, D, R, T, val) = do7(x, y, D, R, T, val)
if s == 8: (x, y, D, R, T, val) = do8(x, y, D, R, T, val)
if s == 9: (x, y, D, R, T, val) = do9(x, y, D, R, T, val)
if s ==10: (x, y, D, R, T, val) = do10(x, y, D, R, T, val)


# ---------------------Fichier Contient les position des capteurs-------------------------
fichier = eval(open(D, "r").read())
# ---------------------Fichier Contient les position des Capteur Redondant----------------
fichierRedondant = eval(open(R, "r").read())
# ---------------------Fichier Contient les position des Trou-----------------------------
fichierTrou = eval(open(T, "r").read())

# ------------------------------List Capteurs --------------------------------------------
for i in fichier:
    t = 0
    X = i[1][0]
    Y = i[1][1]
    for j in fichierRedondant:
        if (X, Y) == j[1]: t = 1
    if t == 1:
        listCapteur.append(Capteur(i[0], X, Y, Rc, Rs, 0))
    else:
        listCapteur.append(Capteur(i[0], X, Y, Rc, Rs, 1))

# ------------------------------List des Trou------------------------------
for i in fichierTrou:
    listTrou.append(i)

# ------------------------------List des Redondant------------------------------
for j in fichierRedondant:
    listRedondant.append(j)


def DrowSurface():
    up()
    goto(-x / 2, -y / 2)
    down()
    c = 2
    u = x / 2
    for k in range(4):
        forward(c * u)
        left(90)


def fxn(x, y):
    goto(x, y)
    write(str(x) + "," + str(y))
    print("[1,(" + str(x) + "," + str(y) + ")],")


def PositionCapteur(fich):
    speed(5000)
    cpt = 0

    for i in fichier:
        X = i[1][0]
        Y = i[1][1]
        up()
        goto(X, Y)
        dot('black')
        up()
        goto(X, Y - Rs)
        down()
        circle(Rs)
        up()


# -----------------------------------------------------------------------------------------------------------------------#

#dessiner la ROI
DrowSurface()

#Deploiement des capteurs
PositionCapteur(listCapteur)

robot = Robot(1, -x / 2, -y / 2, x, y, Rc, Rs, 0, charg, val)


#""""""""""""""""""""""""""""""""""""""""""""Start""""""""""""""""""""""""""""

debut = time.time()
(nbrMessage, nbrpas, temps_perdu) = robot.LRV(listCapteur, listRedondant, listTrou, initial_angle, temps_perdu)


print("*****************************")
print("Nbr de message ", nbrMessage)
print("Nbr de pas ", nbrpas)
print("temp perdu ", temps_perdu)
temps_exec = (time.time() - debut - temps_perdu)
print("temps d execution ", temps_exec)
print("*****************************")

