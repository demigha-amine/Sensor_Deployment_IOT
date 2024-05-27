import math
import turtle
import threading
import socket
from math import acos,sqrt,pow,pi
import pickle

#**************************Global**********************************


class Capteur(threading.Thread):
    def __init__(self,id,x,y,Rc,Rs,actif):
        super(Capteur, self).__init__()
        self.id = id
        self.X = x
        self.Y = y
        self.RC = int(Rc)
        self.RS = int(Rs)
        self.actif=actif
        self.voisins = []
        self.voisinsC = []

#--------------   CALCULATING --------------#

    def calculateDistance(self, sensorX, sensorY):
        myX = self.X
        myY = self.Y
        return sqrt(((myX - sensorX) ** 2) + ((myY - sensorY) ** 2))

#---------------   CHECKS  ---------------#

    def isInMyArea(self, sensorX, sensorY):
        distance = self.calculateDistance(sensorX, sensorY)
        if distance <= float(self.RS):
           return True

        return False

    def CanCommunicate(self,sensorX,sensorY):
        distance = self.calculateDistance(sensorX,sensorY)
        if distance <= self.RC:
           return True
        else:
           return False

#--------------------- Intersection de 2 capteurs --------------------------
    def get_intercetions(self, x0, y0, r0, x1, y1, r1):
        # circle 1: (x0, y0), radius r0
        # circle 2: (x1, y1), radius r1

        d = sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)

        # non intersecting
        if d > r0 + r1:
            return None
        # One circle within other
        if d < abs(r0 - r1):
            return None
        # coincident circles
        if d == 0 and r0 == r1:
            return None
        else:
            a = (r0 ** 2 - r1 ** 2 + d ** 2) / (2 * d)
            h = sqrt(r0 ** 2 - a ** 2)
            x2 = x0 + a * (x1 - x0) / d
            y2 = y0 + a * (y1 - y0) / d
            x3 = x2 + h * (y1 - y0) / d
            y3 = y2 - h * (x1 - x0) / d
            x4 = x2 - h * (y1 - y0) / d
            y4 = y2 + h * (x1 - x0) / d

            return (x3, y3, x4, y4)
#---------------------------------------------------------------------#

    def calculateD(self,X,Y,X2,Y2):
        return sqrt(((X - X2) ** 2) + ((Y - Y2) ** 2))

#-------------- Detection de Redandance ------------------------------#
    def Redandauncy(self, SensorList, listTest):

        radiuS = self.RS
        voisinsSuperpose = []
        pos = []
        if self.id not in listTest:
            superpos = False
            for j in SensorList:  
            # Pos permet dinscrir la pos dun pos traite pour detecter les capteurs redondants superpose et de garder qun seul
                id = j[0]
                X = j[1][0]
                Y = j[1][1]
                if self.isInMyArea(X, Y) and self.id != id and (self.X != X or self.Y != Y) and (X, Y) not in pos:
                    self.voisins.append(j)
                    pos.append((X, Y))
                if self.CanCommunicate(X, Y) and self.id != id:
                    self.voisinsC.append(j)

                if self.X == X and self.Y == Y and self.id != id:
                    superpos = True
                    listTest.append(id)  # ListTest contient les capteurs redondant
                    voisinsSuperpose.append(j)
            out = True

            for j in self.voisins:  # les voisins de i qui sont voisins
                for k in self.voisins:
                    if j != k and out:
                        intercetions = self.get_intercetions(j[1][0], j[1][1], radiuS, k[1][0], k[1][1], radiuS)

                        if intercetions != None:
                            compteur1 = 0  # concerne le nbr de capteur qui couvre le 1er pt dintercetion
                            compteur2 = 0  # 2em pt dintecection

                            for p in self.voisins:
                                s = Capteur(p[0],p[1][0],p[1][1],self.RC,self.RS)
                                if (s.isInMyArea(round(intercetions[0], 0),
                                                 round(intercetions[1], 0)) or s.isInMyArea(
                                        round(intercetions[0], 0) + 1,
                                        round(intercetions[1], 0) + 1) or s.isInMyArea(
                                        round(intercetions[0], 0) - 1, round(intercetions[1], 0) - 1)) and (
                                        self.isInMyArea(round(intercetions[0], 0),
                                                     round(intercetions[1], 0)) or self.isInMyArea(
                                        round(intercetions[0], 0) + 1,
                                        round(intercetions[1], 0) + 1) or self.isInMyArea(
                                        round(intercetions[0], 0) - 1, round(intercetions[1], 0) - 1)):
                                    compteur1 = compteur1 + 1

                                if (s.isInMyArea(round(intercetions[2], 0),
                                                 round(intercetions[3], 0)) or s.isInMyArea(
                                        round(intercetions[2], 0) + 1,
                                        round(intercetions[3], 0) + 1) or s.isInMyArea(
                                        round(intercetions[2], 0) - 1, round(intercetions[3], 0) - 1)) and (
                                        self.isInMyArea(round(intercetions[2], 0),
                                                     round(intercetions[3], 0)) or self.isInMyArea(
                                        round(intercetions[2], 0) + 1,
                                        round(intercetions[3], 0) + 1) or self.isInMyArea(
                                        round(intercetions[2], 0) - 1, round(intercetions[3], 0) - 1)):
                                    compteur2 = compteur2 + 1

                                if compteur1 >= 3 and compteur2 >= 3:
                                    break

                            if (compteur1 < 3 and (self.isInMyArea(round(intercetions[0], 0),
                                                                round(intercetions[1], 0)) or self.isInMyArea(
                                    round(intercetions[0], 0) + 1, round(intercetions[1], 0) + 1) or self.isInMyArea(
                                    round(intercetions[0], 0) - 1, round(intercetions[1], 0) - 1))) or (
                                    compteur2 < 3 and (self.isInMyArea(round(intercetions[2], 0),
                                                                    round(intercetions[3], 0)) or self.isInMyArea(
                                    round(intercetions[2], 0) + 1, round(intercetions[3], 0) + 1) or self.isInMyArea(
                                    round(intercetions[2], 0) - 1, round(intercetions[3], 0) - 1))):
                                out = False

            for j in self.voisins:
                intercetions = self.get_intercetions(self.X, self.Y, radiuS, j[1][0], j[1][1], radiuS)

                if intercetions != None:
                    compteur1 = 0
                    compteur2 = 0

                    for p in self.voisins:
                        s = Capteur(p[0],p[1][0],p[1][1],self.RC,self.RS)
                        if (s.isInMyArea(round(intercetions[0], 0), round(intercetions[1], 0)) or s.isInMyArea(
                                round(intercetions[0], 0) + 1, round(intercetions[1], 0) + 1) or s.isInMyArea(
                                round(intercetions[0], 0) - 1, round(intercetions[1], 0) - 1)) and (
                                self.isInMyArea(round(intercetions[0], 0), round(intercetions[1], 0)) or self.isInMyArea(
                                round(intercetions[0], 0) + 1, round(intercetions[1], 0) + 1) or self.isInMyArea(
                                round(intercetions[0], 0) - 1, round(intercetions[1], 0) - 1)):
                            compteur1 = compteur1 + 1

                        if (s.isInMyArea(round(intercetions[2], 0), round(intercetions[3], 0)) or s.isInMyArea(
                                round(intercetions[2], 0) + 1, round(intercetions[3], 0) + 1) or s.isInMyArea(
                                round(intercetions[2], 0) - 1, round(intercetions[3], 0) - 1)) and (
                                self.isInMyArea(round(intercetions[2], 0), round(intercetions[3], 0)) or self.isInMyArea(
                                round(intercetions[2], 0) + 1, round(intercetions[3], 0) + 1) or self.isInMyArea(
                                round(intercetions[2], 0) - 1, round(intercetions[3], 0) - 1)):
                            compteur2 = compteur2 + 1

                        if compteur1 >= 2 and compteur2 >= 2:
                            break

                    if (compteur1 < 2 and (
                            self.isInMyArea(round(intercetions[0], 0), round(intercetions[1], 0)) or self.isInMyArea(
                            round(intercetions[0], 0) + 1, round(intercetions[1], 0) + 1) or self.isInMyArea(
                            round(intercetions[0], 0) - 1, round(intercetions[1], 0) - 1))) or (compteur2 < 2 and (
                            self.isInMyArea(round(intercetions[2], 0), round(intercetions[3], 0)) or self.isInMyArea(
                            round(intercetions[2], 0) + 1, round(intercetions[3], 0) + 1) or self.isInMyArea(
                            round(intercetions[2], 0) - 1, round(intercetions[3], 0) - 1))):
                        out = False

            if out and len(self.voisins) > 2 and self.id not in listTest:
                listTest.append(self.id)

            voisinsSuperpose[:] = []
        else:
            for j in SensorList:
                id = j[0]
                X = j[1][0]
                Y = j[1][1]
                if self.CanCommunicate(X, Y) and self.id != id:
                    self.voisinsC.append(j)
 
#-----------------------------------------------------------------------------------------------------------#

#------------------------ Confirmer la redondance ----------------------------------------------------------#
    def confirmRedendancy(self, listTest, SensorList):
        listTemp = listTest
        SensorListTemp = SensorList
        for j in self.voisins:
            id = j[0]
            X = j[1][0]
            Y = j[1][1]
            if j in listTest:
                SensorListTemp.remove(j) # verifier si le i reste redondant meme sans lexistance du j
                self.Redandauncy(SensorListTemp, listTemp)
                if self.id not in listTemp and self.id in listTest and self.id > id: # veux dire que i nest plus redondant
                   listTest.remove(self.id) #enlver i de la list de capteurs redondant
                SensorListTemp.append(j)
#------------------------------------------------------------------------------------------------------------#

#------------------------ Detection de trous ----------------------------------------------------------------#
    def verifTrous(self, SensorList, listTrou):

        radiuS = self.RS
        Xs = 0
        Ys = 0
        voisins = []

        for k in SensorList:
            i = Capteur(k[0],k[1][0],k[1][1],self.RC,self.RS)
            if i.CanCommunicate(self.X, self.Y):
               voisins.append(k)

        # verefication des points dintercection s'il sont couvert par un 3eme capteurs autre que les 2 voisins qui forme lintercection
        for j in voisins:  

            intercetions = self.get_intercetions(self.X, self.Y, radiuS, j[1][0], j[1][1], radiuS)
            if intercetions != None:
                compteur1 = 0
                compteur2 = 0
                bcompteur1 = False
                bcompteur2 = False

                for p in voisins:
                    s = Capteur(p[0],p[1][0],p[1][1],self.RC,self.RS)
                    if s.isInMyArea(intercetions[0], intercetions[1]):
                        compteur1 = compteur1 + 1
                        if s.id != self.id and s.id != j[0]:  # il suffit de trouver le 3 eme capteur pour dire que ce point dintercetion n'est pas un trou
                           bcompteur1 = True  # c'est pas la peine de continuer le test sur ce point car il y a au moins 3 capteurs quil le couvre

                    if s.isInMyArea(intercetions[2], intercetions[3]):
                        compteur2 = compteur2 + 1
                        if s.id != self.id and s.id != j[0]:
                           bcompteur2 = True

                    if (compteur1 >= 3 and compteur2 >= 3) or (bcompteur1 and bcompteur2):
                        break


                if not bcompteur1  and (
                        intercetions[0] >= -300 and intercetions[0] <= 300) and (
                        intercetions[1] >= -300 and intercetions[1] <= 300) and (
                        intercetions[0], intercetions[1]) not in listTrou:  
                        # si bcompteur est a faux donc le point nest pas couvert par un 3eme capteur donc cest un trou

                    Xs = intercetions[0]
                    Ys = intercetions[1]

                    covered = False

                    # verification des 4 directions
                    # direction droite
                    for p in voisins:
                        s = Capteur(p[0],p[1][0],p[1][1],self.RC,self.RS)
                        if s.isInMyArea(intercetions[0] + 1, intercetions[1]):
                           covered = True
                           break
                    if covered == False:
                        Xs = intercetions[0] + radiuS - 2
                        if Xs > 300:
                            Xs = 300
                        Ys = intercetions[1]
                    else:
                        covered = False
                        # direction haut
                        for p in voisins:
                            s = Capteur(p[0],p[1][0],p[1][1],self.RC,self.RS)
                            if s.isInMyArea(intercetions[0], intercetions[1] + 1):
                                covered = True
                                break
                        if covered == False:
                            Xs = intercetions[0]
                            Ys = intercetions[1] + radiuS - 2
                            if Ys > 300:
                                Ys = 300
                        else:
                            covered = False
                            # direction gauche
                            for p in voisins:
                                s = Capteur(p[0],p[1][0],p[1][1],self.RC,self.RS)
                                if s.isInMyArea(intercetions[0] - 1, intercetions[1]):
                                    covered = True
                                    break
                            if covered == False:
                                Xs = intercetions[0] - radiuS + 2
                                if Xs < -300:
                                    Xs = -300
                                Ys = intercetions[1]
                            else:
                                covered = False
                                # direction bas
                                for p in voisins:
                                    s = Capteur(p[0],p[1][0],p[1][1],self.RC,self.RS)
                                    if s.isInMyArea(intercetions[0], intercetions[1] - 1):
                                        covered = True
                                        break
                                    if covered == False:
                                       Xs = intercetions[0]
                                       Ys = intercetions[1] - radiuS + 2
                                       if Ys < -300:
                                          Ys = -300
                                    else:
                                       Xs = intercetions[0]
                                       Ys = intercetions[1]
   
                    listTrou.append((Xs, Ys))


                # meme choses pour lautre point dintercection
                if not bcompteur2  and (
                        intercetions[2] >= -300 and intercetions[2] <= 300) and (
                        intercetions[3] >= -300 and intercetions[3] <= 300) and (
                        intercetions[2], intercetions[3]) not in listTrou:

                    if (not bcompteur1 and not s.isInMyArea(intercetions[2],
                                                            intercetions[3])) or bcompteur1:
                        Xs = intercetions[2]
                        Ys = intercetions[3]
                        covered = False

                        # direction droite
                        for p in voisins:
                            s = Capteur(p[0],p[1][0],p[1][1],self.RC,self.RS)
                            if s.isInMyArea(intercetions[2] + 1, intercetions[3]):
                                covered = True
                                break
                        if covered == False:
                            Xs = intercetions[2] + radiuS - 2
                            if Xs > 300:
                                Xs = 300
                            Ys = intercetions[3]
                        else:
                            covered = False
                            # direction haut
                            for p in voisins:
                                s = Capteur(p[0],p[1][0],p[1][1],self.RC,self.RS)
                                if s.isInMyArea(intercetions[2], intercetions[3] + 1):
                                    covered = True
                                    break
                            if covered == False:
                                Xs = intercetions[2]
                                Ys = intercetions[3] + radiuS - 2
                                if Ys > 300:
                                    Ys = 300
                            else:
                                covered = False
                                # direction gauche
                                for p in voisins:
                                    s = Capteur(p[0],p[1][0],p[1][1],self.RC,self.RS)
                                    if s.isInMyArea(intercetions[2] - 1, intercetions[3]):
                                        covered = True
                                        break
                                if covered == False:
                                    Xs = intercetions[2] - radiuS + 2
                                    if Xs < -300:
                                        Xs = -300
                                    Ys = intercetions[3]
                                else:
                                    covered = False
                                    # direction bas
                                    for p in voisins:
                                        s = Capteur(p[0],p[1][0],p[1][1],self.RC,self.RS)
                                        if s.isInMyArea(intercetions[2], intercetions[3] - 1):
                                            covered = True
                                            break
                                    if covered == False:
                                        Xs = intercetions[2]
                                        Ys = intercetions[3] - radiuS + 2
                                        if Ys < -300:
                                            Ys = -300
                                    else:
                                        Xs = intercetions[2]
                                        Ys = intercetions[3]
                      
                        listTrou.append((Xs, Ys))

        return (listTrou)
#-------------------------------------------------------------------

   