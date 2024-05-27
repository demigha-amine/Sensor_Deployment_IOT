import math
import threading
from turtle import *
from Capteur import *
import random
import pickle
import time
from math import *
import turtle

t=turtle.Turtle()
t.pensize(2)
t.color("blue")
#******************Global


class Robot(threading.Thread):

    def __init__(self,id,X,Y,Sx,Sy,Rc,Rs, chargeActuel,chargeMax,val):
        super(Robot, self).__init__()
        self.id=id
        self.X=X
        self.Y=Y
        self.SX=int(int(Sx)/2)
        self.SY=int(int(Sy)/2)
        self.RC=int(Rc)
        self.RS=int(Rs)
        self.chargeActuel=chargeActuel
        self.chargeMax=chargeMax
        self.chargeR = []
        self.nbrMessage = 0
        self.nbpas = 0
        self.Pixel=[]
        if val==0 : self.CovredArea=81440   #312
        if val==1 : self.CovredArea=119829  #400
        if val==2 : self.CovredArea=234072  #612
        if val==3 : self.CovredArea=462826  #864
        if val==4 : self.CovredArea=739401  #1080
        if val==5: self.CovredArea =3032640  # 2160
        if val==6: self.CovredArea = 6823440 # 3240
        if val==7: self.CovredArea = 12130560  # 4320
        if val==8: self.CovredArea = 18954000  # 5400
        link = "robot.gif"
        register_shape(link)
        t.shape(link)
        t.up()
        t.goto(X,Y)
        t.down()
# -------------------------------------------------------------------------------------------

    def div_grille(self, longG, largG, listRed, listTrou):
        grille = longG * largG
        nbr_gx = (self.Sx*2) // largG
        nbr_gy = (self.Sy*2) // longG
        listR = []
        listT = []
        listGT = []
        listGR = []
        listTT = []
        listRR = []

        for p in listTrou :
            if p[0] > -self.Sx and p[0] < self.Sx and p[1] < self.Sx and p[1] > -self.Sx :
               x = int((p[0] + self.Sx) // nbr_gx)
               y = int(abs(p[1] - self.Sx) / nbr_gy)
               listT.append([(x,y),(p[0],p[1])]) 
               listGT.append((x,y))

        for p in listRed :
            if p[1][0] > -self.Sx and p[1][0] < self.Sx and p[1][1] < self.Sx and p[1][1] > -self.Sx :
               x = int((p[1][0] + self.Sx) // nbr_gx)
               y = int(abs(p[1][1] - self.Sx) / nbr_gy)
               listR.append([(x,y),(p[1][0],p[1][1])])
               listGR.append((x,y))

        listGT = set (listGT)
        for p in listGT :
            cpt = 0 
            listP = []
            for s in listT :
                if p[0] == s[0][0] and p[1] == s[0][1] :
                   listP.append((s[1][0],s[1][1]))
                   cpt = cpt + 1   
            listTT.append([(p[0],p[1]),cpt,listP])

        listGR = set (listGR)
        for p in listGR :
            cpt = 0 
            listP = []
            for s in listR :
                if p[0] == s[0][0] and p[1] == s[0][1] :
                   listP.append((s[1][0],s[1][1]))
                   cpt = cpt + 1   
            listRR.append([(p[0],p[1]),cpt,listP])




#-----------Calcule du taux de couverture----------------
    def TauxDeCouverture(self,listCap , temps_perdu,val):
        print("################# Taux couverture ###############")
        debut = time.time()
        cpt = 0
        covered = 0
        if val==1:
            for i in range(-self.SX,self.SY):
                for j in range(-self.SX,self.SY):
                    cpt = cpt + 1
                    for p in listCap:
                        if p.actif == 1 and p.isInMyArea(i, j):
                            covered = covered + 1
                            break
        taux = float(float(covered) / float(cpt))
        taux = 100.0 * taux
        fin = time.time()
        temps_perdu = temps_perdu + fin - debut
        self.CovredArea=covered
        print("Taux de couverture : ",taux,'% , Pixel covred : ',self.CovredArea)

        return covered,temps_perdu

#---------------   CHECKS  ---------------#
    def calculateDistance(self, X,Y, sensorX, sensorY):
        myX = X
        myY = Y
        return math.sqrt(((myX - sensorX) ** 2) + ((myY - sensorY) ** 2))

#---------------   CHECKS  ---------------#

    def CanCommunicate(self,X,Y,sensorX,sensorY):
        distance = self.calculateDistance(X,Y,sensorX,sensorY)
        if distance <= self.RC:
           return True
        else:
           return False


    def voisinage(self, X, Y, listCapteur):
        voisin =0
        D = sqrt(3) * self.RS
        for l in listCapteur:
            if l.actif==1 and l.calculateD(X, Y, l.X, l.Y) <= D+1:
                voisin=voisin+1

        return voisin

    def getPixel(self,voisin,X,Y):
        surface=self.SX
        
        if voisin==0 :
            return self.RS*math.sqrt(3)
        if voisin==1 :
            return 537
        if voisin==2 :
            if surface-2 <= X <= surface or -surface <= X <= -surface+2 or surface-2 <= Y <= surface or -surface <= Y <= -surface+2:
                return 466
            else : return 904
        if voisin==3 :
            if surface - 2 <= X <= surface or -surface <= X <= -surface + 2 or surface - 2 <= Y <= surface or -surface <= Y <= -surface + 2:
                return 426
            else : return 837
        if voisin==4 :
            if surface - 2 <= X <= surface or -surface <= X <= -surface + 2 or surface - 2 <= Y <= surface or -surface <= Y <= -surface + 2:
                return 374
            else : return 777
        if voisin==5 :
            return 732
        if voisin>=6 :
            return 677

# -----------------Verification de redondance------------------------------------

    def verifRedondance(self, monX, monY, listCapteur, listRed, temps_perdu):

        for p in listCapteur:
            if self.CanCommunicate(monX, monY,p.X,p.Y):
               for g in listRed :
                   if(p.X,p.Y) == (g[1][0],g[1][1]) and self.chargeActuel < self.chargeMax:
                   #Les voisins de ce capteur v on minformer quil est redondant
                    self.nbrMessage = self.nbrMessage + len(p.voisinsC)
                    self.chargeActuel = self.chargeActuel + 1
                    self.chargeR.append(p)
                    if p in listCapteur : listCapteur.remove(p)
                    listRed.remove(g)
                    t.up()
                    t.goto(p.X,p.Y)

                    debut = time.time()
                    self.drow1(p.X,p.Y)
                    fin = time.time()
                    temps_perdu = temps_perdu + fin - debut
                    t.goto(monX,monY)
                    t.down()
                    #print ("Red a la pos = (",p[1][0]," , ",p[1][1],")")
                    #print ("chargeActuel = ",self.chargeActuel)
        return (self.chargeActuel,temps_perdu)

# ------------------------Reparation des trous----------------------------
    def verifTrous(self, monX, monY, listCapteur, listTrou, Trou_regle, temps_perdu,taux_actuel):
        
        for g in listTrou :
            for u in g[2] :
                if self.CanCommunicate(monX, monY,u[0], u[1]) and len(self.chargeR) > 0 and (u[0], u[1]) not in Trou_regle:            
                    X = u[0]
                    Y = u[1]
                    #je recupere le nombre de voisin pour ce capteur
                    voisin = self.voisinage(X, Y, listCapteur)

                    listCapteur.append(Capteur(self.chargeR[0], X, Y, self.RC, self.RS, 1))
                    self.chargeR.remove(self.chargeR[0])
                    Trou_regle.append((X,Y))
                    self.chargeActuel = self.chargeActuel - 1
                    t.up()
                    t.goto(X,Y)
                    debut = time.time()
                    #le nombre de Pixel ajoute lorsque j'nstalle ce capteur a la position X,Y
                    self.CovredArea=self.CovredArea + self.getPixel(voisin,X,Y)
                    self.drow2(X,Y)
                    taux_actuel=(self.CovredArea/pow(self.SX*2,2))*100
                    print("taux de couverture actuel = ", taux_actuel)
                    fin = time.time()
                    temps_perdu = temps_perdu + fin - debut
                    t.goto(monX,monY)
                    t.down()
                    #print ("Trou regle a la pos = (",X," , ",Y,")")                    
                    #print ("chargeActuel = ",self.chargeActuel)

        return (self.chargeActuel,Trou_regle,taux_actuel,temps_perdu)

# -------------------------------------------------------------------------------------------
    def drow1(self,X,Y):
        (monX,monY)=pos()
        up()
        goto(X, Y)
        dot('yellow')
        up()
        goto(X, Y - self.RS)
        down()
        color('yellow')
        circle(self.RS)
        up()

    def drow2(self,X,Y):
        up()
        goto(X, Y)
        dot('red')
        up()
        goto(X, Y - self.RS)
        down()
        color('red')
        circle(self.RS)
        up()
#-------------------------------------------------------------------------





#--------------------------Marche-------------------------------------------
    def marche(self, listCapteur, listRed, listTrou, initial_angle, temps_perdu):

        t.color('blue')
        (monX, monY) = (self.X, self.Y)
        t.up()
        t.goto(monX,monY)
        t.down()

        #Rs = 20 / math.sqrt(2)
        #delta = Rs * math.sqrt(2)

        Rs = self.RS
        delta = self.RS * 2

        # ----------Tirer la proba-----------------
        proba = random.random()
        p1 = 1 / (1 + tan(math.radians(initial_angle)))
        p2 = tan(math.radians(initial_angle)) / (1 + tan(math.radians(initial_angle)))

        if proba <= p1:
            t.setheading(0)
            dir = 0
        else:
            t.setheading(90)
            dir = 90
        # ----------------------------------------------
        nbTire=1
        From = "b"
        vers = "d"
        (initialX, initialY) = (self.X, self.Y)
        angle = initial_angle
        Trou_regle = []
        taux_actuel = 0
        while (1) :
            
            c = 0
            (self.chargeActuel,temps_perdu) = self.verifRedondance(monX,monY,listCapteur,listRed,temps_perdu)
            (self.chargeActuel,Trou_regle,taux_actuel,temps_perdu) = self.verifTrous(monX,monY,listCapteur,listTrou,Trou_regle,temps_perdu,taux_actuel)
            self.nbrMessage = self.nbrMessage + 1
            self.nbpas = self.nbpas + 1

            if (taux_actuel >= 98) :
                print("Fin")
                break
            
            if dir == 0:
                (ancienX, ancienY) = (monX, monY)
                (monX, monY) = (monX + delta, monY)
                c = delta

            elif dir == 90:
                (ancienX, ancienY) = (monX, monY)
                (monX, monY) = (monX, monY + delta)
                c = delta


            elif dir == 180:
                (ancienX, ancienY) = (monX, monY)
                (monX, monY) = (monX - delta, monY)
                c = delta


            elif dir == 270:
                (ancienX, ancienY) = (monX, monY)
                (monX, monY) = (monX, monY - delta)
                c = delta


            if -self.SX <= monX <= self.SX and -self.SX <= monY <= self.SY :

                t.goto(monX, monY)
                t.dot(5, "black")

            else :
                debut=time.time()
                #t.up()
                t.goto(monX, monY)
                #t.down()
                fin=time.time()
                temps_perdu=temps_perdu+(fin-debut)

            if monX+1 >= self.SX and monY != self.SY and monY != -self.SY:  # Bordure droite

                #(monX, monY) = (self.SX, monY)
                #print('nbTire',nbTire)

                if initialY < monY:
                    vers = "h"
                    # ----------Tirer la proba-----------------
                    proba = random.random()
                    p1 = 1 / (1 + tan(math.radians(angle)))
                    p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                    nbTire=nbTire+1
                    if proba <= p1:
                        dir = 180
                    else:
                        dir = 90
                    # ----------------------------------------------

                else:
                    vers = "b"
                    nbTire = nbTire + 1
                    # ----------Tirer la proba-----------------
                    proba = random.random()
                    p1 = 1 / (1 + tan(math.radians(angle)))
                    p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                    if proba <= p1:
                        dir = 180
                    else:
                        dir = 270
                    # ----------------------------------------------

                From = "d"
                (initialX, initialY) = (monX, monY)

            elif monX-1 <= -self.SX and monY != self.SY and monY != -self.SY:  # Bordure gauche

                #(monX, monY) = (-self.SX, monY)
                print('nbTire',nbTire)
                From = "g"

                if initialY < monY:
                    vers = "h"
                    # ----------Tirer la proba-----------------
                    proba = random.random()
                    p1 = 1 / (1 + tan(math.radians(angle)))
                    p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                    nbTire = nbTire + 1
                    if proba <= p1:
                        dir = 0
                    else:
                        dir = 90
                    # ----------------------------------------------

                else:
                    vers = "b"
                    # ----------Tirer la proba-----------------
                    proba = random.random()
                    p1 = 1 / (1 + tan(math.radians(angle)))
                    p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                    nbTire = nbTire + 1
                    if proba <= p1:
                        dir = 0
                    else:
                        dir = 270
                    # ----------------------------------------------

                (initialX, initialY) = (monX, monY)

            elif monY + 1 >= self.SY:  # Bordure haut

                #(monX, monY) = (monX, self.SY)
                print("nbTire",nbTire)

                From = "h"

                if initialX < monX:
                    vers = "d"
                    # ----------Tirer la proba-----------------
                    proba = random.random()
                    p1 = 1 / (1 + tan(math.radians(angle)))
                    p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                    nbTire = nbTire + 1
                    if proba <= p1 and monX != self.SX and monX != -self.SX:
                        dir = 0
                    else:
                        dir = 270
                    # ----------------------------------------------

                else:
                    vers = "g"
                    # ----------Tirer la proba-----------------
                    proba = random.random()
                    p1 = 1 / (1 + tan(math.radians(angle)))
                    p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                    nbTire = nbTire + 1
                    if proba <= p1 and monX != -self.SX and monX != self.SX:
                        dir = 180
                    else:
                        dir = 270
                    # ----------------------------------------------

                (initialX, initialY) = (monX, monY)

            elif monY -1  <= -self.SY:  # Bordure bas
                #(monX, monY) = (monX, -self.SY)
                print('nbTire',nbTire)

                From = "b"

                if initialX < monX:
                    vers = "d"
                    # ----------Tirer la proba-----------------
                    proba = random.random()
                    p1 = 1 / (1 + tan(math.radians(angle)))
                    p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                    nbTire = nbTire + 1
                    if proba <= p1 and monX != self.SX and monX != -self.SX:
                        dir = 0
                    else:
                        dir = 90
                    # ----------------------------------------------

                else:
                    vers = "g"
                    # ----------Tirer la proba-----------------
                    proba = random.random()
                    p1 = 1 / (1 + tan(math.radians(angle)))
                    p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                    nbTire = nbTire + 1
                    if proba <= p1 and monX != -self.SX and monX != self.SX:
                        dir = 180
                    else:
                        dir = 90
                    # ----------------------------------------------

                (initialX, initialY) = (monX, monY)

            if c == delta:

                if From == "b":

                    
                    if vers == "d":
                        # ----------Tirer la proba-----------------
                        proba = random.random()
                        p1 = 1 / (1 + tan(math.radians(angle)))
                        p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                        nbTire = nbTire + 1
                        if proba <= p1 and monX != self.SX and monX != -self.SX:
                            dir = 0
                        else:
                            dir = 90
                        # ----------------------------------------------
                    else:
                        # ----------Tirer la proba-----------------
                        proba = random.random()
                        p1 = 1 / (1 + tan(math.radians(angle)))
                        p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                        nbTire = nbTire + 1
                        if proba <= p1 and monX != -self.SX and monX != self.SX:
                            dir = 180
                        else:
                            dir = 90
                        # ----------------------------------------------

                elif From == "d":

                    

                    if vers == "b":
                        # ----------Tirer la proba-----------------
                        proba = random.random()
                        p1 = 1 / (1 + tan(math.radians(angle)))
                        p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                        nbTire = nbTire + 1
                        if proba <= p1:
                            dir = 180
                        else:
                            dir = 270
                        # ----------------------------------------------
                    else:
                        # ----------Tirer la proba-----------------
                        proba = random.random()
                        p1 = 1 / (1 + tan(math.radians(angle)))
                        p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                        nbTire = nbTire + 1
                        if proba <= p1:
                            dir = 180
                        else:
                            dir = 90
                        # ----------------------------------------------

                elif From == "g":

                    

                    if vers == "b":
                        # ----------Tirer la proba-----------------
                        proba = random.random()
                        p1 = 1 / (1 + tan(math.radians(angle)))
                        p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                        nbTire = nbTire + 1
                        if proba <= p1:
                            dir = 0
                        else:
                            dir = 270
                        # ----------------------------------------------
                    else:
                        # ----------Tirer la proba-----------------
                        proba = random.random()
                        p1 = 1 / (1 + tan(math.radians(angle)))
                        p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                        nbTire = nbTire + 1
                        if proba <= p1:
                            dir = 0
                        else:
                            dir = 90
                        # ----------------------------------------------

                elif From == "h":

                    

                    if vers == "d":
                        # ----------Tirer la proba-----------------
                        proba = random.random()
                        p1 = 1 / (1 + tan(math.radians(angle)))
                        p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                        nbTire = nbTire + 1
                        if proba <= p1 and monX != self.SX and monX != -self.SX:
                            dir = 0
                        else:
                            dir = 270
                        # ----------------------------------------------
                    else:
                        # ----------Tirer la proba-----------------
                        proba = random.random()
                        p1 = 1 / (1 + tan(math.radians(angle)))
                        p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                        nbTire = nbTire + 1
                        if proba <= p1 and monX != self.SX and monX != -self.SX:
                            dir = 180
                        else:
                            dir = 270
                        # ----------------------------------------------



        return (self.nbrMessage, self.nbpas, temps_perdu)
    #---------------------------------------------------------------------------

#-------------------------------------------------------------------------



#--------------------------LRV-------------------------------------------
    def LRV(self, listCapteur, listRed, listTrou, initial_angle, temps_perdu):

        item=[]
        listPixel=[]
        item=[]
        for i in range(-self.SX, self.SX+1):
            for j in range(-self.SY, self.SY+1):
               listPixel.append([i, j, 0, 0, 0, 0])

        (monX, monY) = (self.X, self.Y)



        Rs = self.RS
        delta = self.RS * 2


        # ----------Choisir la Direction-----------------
        direction = random.randint(1, 2)
        
        if direction == 1:  
           t.setheading(0)  # Droite
           dir = 0
           vers = "d"
           for g in listTrou :
            for u in g[2] :
                if self.CanCommunicate(monX, monY,u[0], u[1])== False:
                   for index, p in enumerate(listPixel):
                       if (p[0],p[1]) == (monX, monY):
                          item = p
                          item[2] = p[2] + 1
                          listPixel[index] = item    
                          break
        else :  
           t.setheading(90) # Haut
           dir = 90
           vers = "h"
           for g in listTrou :
            for u in g[2] :
                if self.CanCommunicate(monX, monY,u[0], u[1])== False:
                   for index, p in enumerate(listPixel):
                       if (p[0],p[1]) == (monX, monY):
                          item = p
                          item[4] = p[4] + 1
                          listPixel[index] = item    
                          break
        # ----------------------------------------------

        From = "b"
        Trou_regle = []
        taux_actuel = 0

        while (1) :
            c = 0
            
            (self.chargeActuel,temps_perdu) = self.verifRedondance(monX,monY,listCapteur, listRed,temps_perdu)
            (self.chargeActuel,Trou_regle,taux_actuel,temps_perdu) = self.verifTrous(monX,monY,listCapteur,listTrou,Trou_regle,temps_perdu,taux_actuel) 
            self.nbrMessage = self.nbrMessage + 1
            self.nbpas = self.nbpas + 1
            

            if (taux_actuel >= 98) :
                print("Fin")
                break

            if dir == 0:
                    (monX, monY) = (monX + delta, monY)
                    c = delta

            elif dir == 90:
                    (monX, monY) = (monX, monY + delta)
                    c = delta

            elif dir == 180:
                    (monX, monY) = (monX - delta, monY)
                    c = delta

            elif dir == 270:
                    (monX, monY) = (monX, monY - delta)
                    c = delta

            t.goto(monX, monY)
            t.dot(5, "black")
            #print(monX, monY)
            if monX >= self.SX:  # Bordure droite

                From = "d"
                if monX == self.SX and -self.SY<monY<self.SY:
                   # ----------Choisir la Direction-----------------
                    for index, p in enumerate(listPixel):
                        
                        if (p[0],p[1]) == (round(monX), round(monY)):
                           item = p

                           if p[3]==p[4]==p[5] : 
                              direction = random.randint(2, 4)
                              cas = 2
                           else : 
                              direction = min(p[3],p[4],p[5])
                              cas = 1

                           if (direction == p[3] and cas == 1) or (direction == 2 and cas == 2):
                              vers = "g"
                              t.setheading(180) # gauche
                              dir = 180
                           elif (direction == p[4] and cas == 1) or (direction == 3 and cas == 2):  
                              vers = "h"
                              t.setheading(90)  # haut
                              dir = 90
                           else:
                              vers = "b"
                              t.setheading(270) # bas
                              dir = 270

                           for g in listTrou :
                              for u in g[2] :
                                if self.CanCommunicate(monX, monY,u[0], u[1])== False:
                                    if  vers == "g" : item[3]= p[3] + 1
                                    if  vers == "h" : item[4]= p[4] + 1
                                    if  vers == "b" : item[5]= p[5] + 1
                                    listPixel[index] = item 
                                    break
                           break
                    # ------------------------------------------------

                else :
                    vers = "g"
                    t.setheading(180)  # gauche
                    dir = 180

                    # ----------en dehors du surface-----------------
                    for g in listTrou :
                      for u in g[2] :
                        if self.CanCommunicate(monX, monY,u[0], u[1])== False:
                           for index, p in enumerate(listPixel):
                               if (p[0],p[1]) == (round(monX), round(monY)):
                                  item = p
                                  item[3]= p[3] + 1
                                  listPixel[index] = item    
                                  break


            elif monX <= -self.SX:  # Bordure gauche

                From = "g"
                if monX == -self.SX and -self.SY<monY<self.SY:
                   # ----------Choisir la Direction-----------------
                    for index, p in enumerate(listPixel):
                        
                        if (p[0],p[1]) == (round(monX), round(monY)):
                           item = p

                           if p[2]==p[4]==p[5] : 
                              direction = random.randint(1, 3)
                              cas = 2
                           else : 
                              direction = min(p[2],p[4],p[5])
                              cas = 1

                           if (direction == p[2] and cas == 1) or (direction == 1 and cas == 2):
                              vers = "d"
                              t.setheading(0) # droit
                              dir = 0
                           elif (direction == p[4] and cas == 1) or (direction == 2 and cas == 2):  
                              vers = "h"
                              t.setheading(90)  # haut
                              dir = 90
                           else:
                              vers = "b"
                              t.setheading(270) # bas
                              dir = 270

                           for g in listTrou :
                              for u in g[2] :
                                if self.CanCommunicate(monX, monY,u[0], u[1])== False:
                                    if  vers == "d" : item[2]= p[2] + 1
                                    if  vers == "h" : item[4]= p[4] + 1
                                    if  vers == "b" : item[5]= p[5] + 1
                                    listPixel[index] = item 
                                    break
                           break
                    # ------------------------------------------------

                else :
                    vers = "d"
                    t.setheading(0)  # droit
                    dir = 0

                    # ----------en dehors du surface-----------------
                    for g in listTrou :
                      for u in g[2] :
                        if self.CanCommunicate(monX, monY,u[0], u[1])== False:
                           for index, p in enumerate(listPixel):
                               if (p[0],p[1]) == (round(monX), round(monY)):
                                  item = p
                                  item[2]= p[2] + 1
                                  listPixel[index] = item    
                                  break


            elif monY >= self.SY:  # Bordure haut

                From = "h"
                if monY == self.SY and -self.SX<monX<self.SX:
                   # ----------Choisir la Direction-----------------
                    for index, p in enumerate(listPixel):
                        
                        if (p[0],p[1]) == (round(monX), round(monY)):
                           item = p

                           if p[2]==p[3]==p[5] : 
                              direction = random.randint(1, 3)
                              cas = 2
                           else : 
                              direction = min(p[2],p[3],p[5])
                              cas = 1

                           if (direction == p[2] and cas == 1) or (direction == 1 and cas == 2):
                              vers = "d"
                              t.setheading(0) # droit
                              dir = 0
                           if (direction == p[3] and cas == 1) or (direction == 2 and cas == 2):
                              vers = "g"
                              t.setheading(180) # gauche
                              dir = 180
                           else:
                              vers = "b"
                              t.setheading(270) # bas
                              dir = 270

                           for g in listTrou :
                              for u in g[2] :
                                if self.CanCommunicate(monX, monY,u[0], u[1])== False:
                                    if  vers == "d" : item[2]= p[2] + 1
                                    if  vers == "g" : item[3]= p[3] + 1
                                    if  vers == "b" : item[5]= p[5] + 1
                                    listPixel[index] = item 
                                    break
                           break
                    # ------------------------------------------------

                else :
                    vers = "b"
                    t.setheading(270)  # bas
                    dir = 270

                    # ----------en dehors du surface-----------------
                    for g in listTrou :
                      for u in g[2] :
                        if self.CanCommunicate(monX, monY,u[0], u[1])== False:
                           for index, p in enumerate(listPixel):
                               if (p[0],p[1]) == (round(monX), round(monY)):
                                  item = p
                                  item[5]= p[5] + 1
                                  listPixel[index] = item    
                                  break


            elif monY <= -self.SY:  # Bordure bas

                From = "b"
                if monY == -self.SY and -self.SX<monX<self.SX:
                   # ----------Choisir la Direction-----------------
                    for index, p in enumerate(listPixel):
                        
                        if (p[0],p[1]) == (round(monX), round(monY)):
                           item = p

                           if p[2]==p[3]==p[4] : 
                              direction = random.randint(1, 3)
                              cas = 2
                           else : 
                              direction = min(p[2],p[3],p[4])
                              cas = 1

                           if (direction == p[2] and cas == 1) or (direction == 1 and cas == 2):
                              vers = "d"
                              t.setheading(0) # droit
                              dir = 0
                           if (direction == p[3] and cas == 1) or (direction == 2 and cas == 2):
                              vers = "g"
                              t.setheading(180) # gauche
                              dir = 180
                           else:
                              vers = "h"
                              t.setheading(90) # haut
                              dir = 90

                           for g in listTrou :
                              for u in g[2] :
                                if self.CanCommunicate(monX, monY,u[0], u[1])== False:
                                    if  vers == "d" : item[2]= p[2] + 1
                                    if  vers == "g" : item[3]= p[3] + 1
                                    if  vers == "h" : item[4]= p[4] + 1
                                    listPixel[index] = item 
                                    break
                           break
                    # ------------------------------------------------

                else :
                    vers = "h"
                    t.setheading(90)  # haut
                    dir = 90

                    # ----------en dehors du surface-----------------
                    for g in listTrou :
                      for u in g[2] :
                        if self.CanCommunicate(monX, monY,u[0], u[1])== False:
                           for index, p in enumerate(listPixel):
                               if (p[0],p[1]) == (round(monX), round(monY)):
                                  item = p
                                  item[4]= p[4] + 1
                                  listPixel[index] = item    
                                  break



            if c == delta and -self.SX<monX<self.SX and -self.SY<monY<self.SY:

                if vers == "b" or vers == "h" or vers == "d" or vers == "g":

                    # ----------Choisir la Direction-----------------
                    for index, p in enumerate(listPixel):
                        
                        if (p[0],p[1]) == (round(monX), round(monY)):
                           item = p
                           if p[2]==p[3]==p[4]==p[5] : 
                              direction = random.randint(1, 4)
                              cas = 2
                           else : 
                              direction = min(p[2],p[3],p[4],p[5])
                              cas = 1

                           if (direction == p[2] and cas == 1) or (direction == 1 and cas == 2):  
                              vers = "d"
                              t.setheading(0)  # droit
                              dir = 0
                           elif (direction == p[3] and cas == 1) or (direction == 2 and cas == 2):
                              vers = "g"
                              t.setheading(180) # gauche
                              dir = 180
                           elif (direction == p[4] and cas == 1) or (direction == 3 and cas == 2):  
                              vers = "h"
                              t.setheading(90)  # haut
                              dir = 90
                           else:
                              vers = "b"
                              t.setheading(270) # bas
                              dir = 270


                           for g in listTrou :
                              for u in g[2] :
                                if self.CanCommunicate(monX, monY,u[0], u[1])== False:
                                    if  vers == "d" : item[2]= p[2] + 1
                                    if  vers == "g" : item[3]= p[3] + 1
                                    if  vers == "h" : item[4]= p[4] + 1
                                    if  vers == "b" : item[5]= p[5] + 1
                                    listPixel[index] = item 
                                    break
                           break
                    # ------------------------------------------------
        

        return (self.nbrMessage, self.nbpas, temps_perdu)
#---------------------------------------------------------------------------

#-------------------------------------------------------------------------





#-------------------------- REFLEXION -------------------------------------------
    def Reflexion(self, listCapteur, listRed, listTrou, initial_angle, temps_perdu):


        (monX, monY) = (self.X, self.Y)

        #Rs = 20 / math.sqrt(2)
        #delta = Rs * math.sqrt(2)

        Rs = self.RS
        delta = self.RS * 2



        # ---------Angle de depart-----------------
        t.setheading(initial_angle)

        From = "b"
        vers = "d"
        (initialX, initialY) = (monX, monY)
        angle = initial_angle

        # ----------------------------------------------


        Trou_regle = []
        taux_actuel = 0

        while (1) :
            c = 0

            (self.chargeActuel,temps_perdu) = self.verifRedondance(monX,monY,listCapteur, listRed,temps_perdu)
            (self.chargeActuel,Trou_regle,taux_actuel,temps_perdu) = self.verifTrous(monX,monY,listCapteur,listTrou,Trou_regle,temps_perdu,taux_actuel)
            self.nbrMessage = self.nbrMessage + 1
            self.nbpas = self.nbpas + 1



            if (taux_actuel >= 98) :
                print("Fin")
                break


            (ancienX, ancienY) = (monX, monY)
            t.forward(delta)
            (monX, monY) = t.pos()

            if -self.SX <= monX <= self.SX and -self.SX <= monY <= self.SY:

                goto(monX, monY)
                down()
                dot(5, "black")
                up()


            if round(monX+1) >= self.SX and -self.SY <= monY <= self.SY and From != "d":  # Bordure droite

                #(monX, monY) = (self.SX, monY)
                From = "d"


                if initialY < monY:
                    # ---------------------------
                    angle = angle - (180 + 2*initial_angle)
                    t.setheading(angle)
                    # ----------------------------------------------
                else:
                    # ---------------------------
                    angle = angle - (180 - 2 * initial_angle)
                    t.setheading(angle)
                    # ----------------------------------------------

                (initialX, initialY) = (monX, monY)

            elif monX-1 <= -self.SX and -self.SY <= monY <= self.SY and From != "g":  # Bordure gauche

                #(monX, monY) = (-self.SX, monY)
                From = "g"

                if initialY < monY:
                    # ---------------------------
                    angle = angle + (180 + 2 * initial_angle)
                    t.setheading(angle)
                    # ----------------------------------------------

                else:
                    # ---------------------------
                    angle = angle + (180 - 2 * initial_angle)
                    t.setheading(angle)
                    # ----------------------------------------------

                (initialX, initialY) = (monX, monY)

            elif monY+1 >= self.SY and -self.SX <= monX <= self.SX and From != "h":  # Bordure haut


                #(monX, monY) = (monX, self.SY)
                From = "h"

                if initialX < monX:
                    # ---------------------------
                    angle = angle + (180+(180-(2*initial_angle)))
                    t.setheading(angle)
                    # ----------------------------------------------

                else:
                    # ---------------------------
                    angle = angle + (180 - (180 - (2 * initial_angle)))
                    t.setheading(angle)
                    # ----------------------------------------------

                (initialX, initialY) = (monX, monY)

            elif monY-1 <= -self.SY and -self.SX <= monX <= self.SX and From != "b":  # Bordure bas

                #(monX, monY) = (monX, -self.SY)
                From = "b"

                if initialX < monX:
                    # ---------------------------
                    angle = angle - (180 + (180 - (2 * initial_angle)))
                    t.setheading(angle)
                    # ----------------------------------------------

                else:
                    # ----------Tirer la proba-----------------
                    angle = angle - (180 - (180 - (2 * initial_angle)))
                    t.setheading(angle)
                    # ----------------------------------------------

                (initialX, initialY) = (monX, monY)




        return (self.nbrMessage, self.nbpas, temps_perdu)

        
    #---------------------------------------------------------------------------



    #--------------------Division Angle-----------------------------------------

    def div_angle(self,initial_angle):
        (monX, monY) = (self.X, self.Y)
        t.color('black')
        Rs = self.RS
        #delta = self.RC
        delta = 1

        # ---------Angle de depart-----------------
        t.setheading(initial_angle)

        From = "b"
        vers = "d"
        (initialX, initialY) = (monX, monY)
        angle = initial_angle

        # ----------------------------------------------

        Trou_regle = []
        dist = []
        taux_actuel = 0

        while (1):
            c = 0

            (ancienX, ancienY) = (monX, monY)
            t.forward(delta)
            (monX, monY) = t.pos()
            #monX, monY = round(monX), round(monY)
            #print(monX,monY)


            if monX >= self.SX and -self.SY < monY< self.SY:  # Bordure droite

                # (monX, monY) = (self.SX, monY)
                dist.append((monX, monY))
                #print(monX,monY)
                From = "d"

                if initialY < monY:
                    # ---------------------------
                    angle = angle - (180 + 2 * initial_angle)
                    t.setheading(angle)
                    # ----------------------------------------------
                else:
                    # ---------------------------
                    angle = angle - (180 - 2 * initial_angle)
                    t.setheading(angle)
                    # ----------------------------------------------

                (initialX, initialY) = (monX, monY)

            elif monX <= -self.SX and -self.SY < monY< self.SY :  # Bordure gauche

                # (monX, monY) = (-self.SX, monY)
                From = "g"

                if initialY < monY:
                    # ---------------------------
                    angle = angle + (180 + 2 * initial_angle)
                    t.setheading(angle)
                    # ----------------------------------------------

                else:
                    # ---------------------------
                    angle = angle + (180 - 2 * initial_angle)
                    t.setheading(angle)
                    # ----------------------------------------------

                (initialX, initialY) = (monX, monY)

            elif monY >= self.SY and -self.SX < monX < self.SX:  # Bordure haut

                # (monX, monY) = (monX, self.SY)

                From = "h"

                if initialX < monX:
                    # ---------------------------
                    angle = angle + (180 + (180 - (2 * initial_angle)))
                    t.setheading(angle)
                    # ----------------------------------------------

                else:
                    # ---------------------------
                    angle = angle + (180 - (180 - (2 * initial_angle)))
                    t.setheading(angle)
                    # ----------------------------------------------

                (initialX, initialY) = (monX, monY)

            elif monY <= -self.SY and -self.SX < monX < self.SX:  # Bordure bas


                From = "b"

                if initialX < monX :
                    # ---------------------------
                    angle = angle - (180 + (180 - (2 * initial_angle)))
                    t.setheading(angle)
                    # ----------------------------------------------

                else:
                    # ---------------------------
                    angle = angle - (180 - (180 - (2 * initial_angle)))
                    t.setheading(angle)
                    # ----------------------------------------------

                (initialX, initialY) = (monX, monY)

            elif (round(monY) == self.SY or round(monY) == -self.SY) and (round(monX) == -self.SX or  round(monX) == self.SX ) :
                break
        












#--------------------------Obstacle-------------------------------------------
    def marche_obs(self, listCapteur, listRed, listTrou, initial_angle, temps_perdu):

        Rs = self.RS
        delta = self.RS * 2
        
        nbr_delta = (self.SX*2) / delta
        nbr_del   = int(nbr_delta / 2)
        nbr_delta = int(nbr_delta / 4)
        t.fillcolor('black')
        
        t.pencolor('black')
        t.pensize(5)
        #Rectangle 1
        t.up()
        X1 = -self.SX + nbr_delta*delta
        Y1 = -self.SY + nbr_delta*delta

        X2 =  X1 + (3*delta)
        Y2 =  Y1 + delta
        t.begin_fill()
        t.goto(X1,Y1)
        t.down()
        t.goto(X2,Y1)
        t.goto(X2,Y2)
        t.goto(X1,Y2)
        t.goto(X1,Y1)
        t.end_fill()
        
        #Rectangle 2
        t.up()
        X3 =  self.SX - nbr_delta*delta
        Y3 =  self.SY - nbr_delta*delta

        X4 = X3 - (3*delta)
        Y4 = Y3 + delta 

        t.fillcolor('black')
        t.begin_fill()
        t.goto(X3,Y3)
        t.down()
        t.goto(X4,Y3)
        t.goto(X4,Y4)
        t.goto(X3,Y4)
        t.goto(X3,Y3)
        t.end_fill()
        
        t.color('blue')
        t.pensize(2)
        (monX, monY) = (self.X, self.Y)
        t.up()
        t.goto(monX,monY)
        t.down()
        
        
        

        # ----------Tirer la proba-----------------
        proba = random.random()
        p1 = 1 / (1 + tan(math.radians(initial_angle)))
        p2 = tan(math.radians(initial_angle)) / (1 + tan(math.radians(initial_angle)))

        if proba <= p1:
            t.setheading(0)
            dir = 0
        else:
            t.setheading(90)
            dir = 90
        # ----------------------------------------------

        From = "b"
        vers = "d"
        (initialX, initialY) = (self.X, self.Y)
        angle = initial_angle
        Trou_regle = []
        taux_actuel = 0
        obs_gd = False
        obs_hb = False
        For = 'n'

        while (1) :
            
            c = 0

            if (obs_gd == False) and (obs_hb == False) and (For != "o") : 
               (self.chargeActuel,temps_perdu) = self.verifRedondance(monX,monY,listCapteur,listRed,temps_perdu)
               (self.chargeActuel,Trou_regle,taux_actuel,temps_perdu) = self.verifTrous(monX,monY,listCapteur,listTrou,Trou_regle,temps_perdu,taux_actuel)
               self.nbrMessage = self.nbrMessage + 1
               self.nbpas = self.nbpas + 1

            if (taux_actuel >= 98) :
                print("Fin")
                break

            obs_gd = False
            obs_hb = False

            if dir == 0:
                (ancienX, ancienY) = (monX, monY)
                if (Y1<= monY <= Y2 and monX < X1 and monX + delta >= X1) or (
                    Y3<= monY <= Y4 and monX < X4 and monX + delta >= X4) and For != "o":
                    obs_gd = True 
                else: c = delta
                (monX, monY) = (monX + delta, monY)
                

            elif dir == 90:
                (ancienX, ancienY) = (monX, monY)
                if (X1<= monX <= X2 and monY < Y1 and monY + delta >= Y1) or (
                    X4<= monX <= X3 and monY < Y3 and monY + delta >= Y3) and For != "o":
                    obs_hb = True 
                else: c = delta
                (monX, monY) = (monX, monY + delta)


            elif dir == 180:
                (ancienX, ancienY) = (monX, monY)
                if (Y1<= monY <= Y2 and monX > X2 and monX - delta <= X2) or (
                    Y3<= monY <= Y4 and monX > X3 and monX - delta <= X3) and For != "o":
                    obs_gd = True
                else: c = delta
                (monX, monY) = (monX - delta, monY)


            elif dir == 270:
                (ancienX, ancienY) = (monX, monY)
                if (X1<= monX <= X2 and monY > Y2 and monY - delta <= Y2) or (
                    X4<= monX <= X3 and monY > Y4 and monY - delta <= Y4) and For != "o":
                    obs_hb = True 
                else: c = delta
                (monX, monY) = (monX, monY - delta)


            if -self.SX <= monX <= self.SX and -self.SX <= monY <= self.SY :

                t.goto(monX, monY)
                t.dot(5, "black")

            else :
                debut=time.time()
                #t.up()
                t.goto(monX, monY)
                #t.down()
                fin=time.time()
                temps_perdu=temps_perdu+(fin-debut)
            
            #if (obs_gd == True) or (obs_hb == True):
               #time.sleep(5)
           
            For = 'n'

            if obs_gd == True:  # Obstacle droit / gauche

              For = "o"

              if (From == "b" and vers == "d") or (From == "g" and vers == "h") or (
                  From == "h" and vers == "d") or (From == "g" and vers == "b"):
                From = "d"
                if initialY < monY:
                    vers = "h"
                    # ----------Tirer la proba-----------------
                    proba = random.random()
                    p1 = 1 / (1 + tan(math.radians(angle)))
                    p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                    if proba <= p1:
                        dir = 180
                    else:
                        dir = 90
                    # ----------------------------------------------

                else:
                    vers = "b"
                    # ----------Tirer la proba-----------------
                    proba = random.random()
                    p1 = 1 / (1 + tan(math.radians(angle)))
                    p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                    if proba <= p1:
                        dir = 180
                    else:
                        dir = 270
                    # ----------------------------------------------
                (initialX, initialY) = (monX, monY)

              elif (From == "b" and vers == "g") or (From == "d" and vers == "h") or (
                    From == "h" and vers == "g") or (From == "d" and vers == "b"):
                From = "g"
                if initialY < monY:
                    vers = "h"
                    # ----------Tirer la proba-----------------
                    proba = random.random()
                    p1 = 1 / (1 + tan(math.radians(angle)))
                    p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                    if proba <= p1:
                        dir = 0
                    else:
                        dir = 90
                    # ----------------------------------------------

                else:
                    vers = "b"
                    # ----------Tirer la proba-----------------
                    proba = random.random()
                    p1 = 1 / (1 + tan(math.radians(angle)))
                    p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                    if proba <= p1:
                        dir = 0
                    else:
                        dir = 270
                    # ----------------------------------------------
                (initialX, initialY) = (monX, monY)

 # ----------------------------------------------
            if obs_hb == True:  # Obstacle haut / bas

              For = "o"

              if (From == "b" and vers == "d") or (From == "g" and vers == "h") or (
                  From == "d" and vers == "h") or (From == "b" and vers == "g"):
                From = "h"

                if initialX < monX:
                    vers = "d"
                    # ----------Tirer la proba-----------------
                    proba = random.random()
                    p1 = 1 / (1 + tan(math.radians(angle)))
                    p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                    if proba <= p1:
                        dir = 0
                    else:
                        dir = 270
                    # ----------------------------------------------

                else :
                    vers = "g"
                    # ----------Tirer la proba-----------------
                    proba = random.random()
                    p1 = 1 / (1 + tan(math.radians(angle)))
                    p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                    if proba <= p1 and monX != -self.SX:
                        dir = 180
                    else:
                        dir = 270
                    # ----------------------------------------------

                (initialX, initialY) = (monX, monY)

              elif (From == "h" and vers == "g") or (From == "d" and vers == "b") or (
                    From == "h" and vers == "d") or (From == "g" and vers == "b"):

                From = "b"

                if initialX < monX:
                    vers = "d"
                    # ----------Tirer la proba-----------------
                    proba = random.random()
                    p1 = 1 / (1 + tan(math.radians(angle)))
                    p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                    if proba <= p1 and monX != self.SX:
                        dir = 0
                    else:
                        dir = 90
                    # ----------------------------------------------

                else :
                    vers = "g"
                    # ----------Tirer la proba-----------------
                    proba = random.random()
                    p1 = 1 / (1 + tan(math.radians(angle)))
                    p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                    if proba <= p1:
                        dir = 180
                    else:
                        dir = 90
                    # ----------------------------------------------
                (initialX, initialY) = (monX, monY)



            if monX+1 >= self.SX and monY != self.SY and monY != -self.SY:  # Bordure droite

                #(monX, monY) = (self.SX, monY) 
                
                #time.sleep(5)
                if initialY < monY:
                    vers = "h"
                    # ----------Tirer la proba-----------------
                    proba = random.random()
                    p1 = 1 / (1 + tan(math.radians(angle)))
                    p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                    if proba <= p1:
                        dir = 180
                    else:
                        dir = 90
                    # ----------------------------------------------

                else:
                    vers = "b"
                    # ----------Tirer la proba-----------------
                    proba = random.random()
                    p1 = 1 / (1 + tan(math.radians(angle)))
                    p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                    if proba <= p1:
                        dir = 180
                    else:
                        dir = 270
                    # ----------------------------------------------

                From = "d"
                (initialX, initialY) = (monX, monY)

            elif monX-1 <= -self.SX and monY != self.SY and monY != -self.SY:  # Bordure gauche

                #(monX, monY) = (-self.SX, monY)
                #time.sleep(5)
                From = "g"

                if initialY < monY:
                    vers = "h"
                    # ----------Tirer la proba-----------------
                    proba = random.random()
                    p1 = 1 / (1 + tan(math.radians(angle)))
                    p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                    if proba <= p1:
                        dir = 0
                    else:
                        dir = 90
                    # ----------------------------------------------

                else:
                    vers = "b"
                    # ----------Tirer la proba-----------------
                    proba = random.random()
                    p1 = 1 / (1 + tan(math.radians(angle)))
                    p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                    if proba <= p1:
                        dir = 0
                    else:
                        dir = 270
                    # ----------------------------------------------

                (initialX, initialY) = (monX, monY)

            elif monY + 1 >= self.SY or monY == self.SY:  # Bordure haut
                #time.sleep(5)
                #(monX, monY) = (monX, self.SY)

                From = "h"

                if initialX < monX:
                    vers = "d"
                    # ----------Tirer la proba-----------------
                    proba = random.random()
                    p1 = 1 / (1 + tan(math.radians(angle)))
                    p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                    if proba <= p1 and monX != self.SX and monX != -self.SX:
                        dir = 0
                    else:
                        dir = 270
                    # ----------------------------------------------

                else :
                    vers = "g"
                    # ----------Tirer la proba-----------------
                    proba = random.random()
                    p1 = 1 / (1 + tan(math.radians(angle)))
                    p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                    if proba <= p1 and monX != -self.SX and monX != self.SX:
                        dir = 180
                    else:
                        dir = 270
                    # ----------------------------------------------

                (initialX, initialY) = (monX, monY)

            elif monY -1  <= -self.SY or monY == -self.SY:  # Bordure bas
                #(monX, monY) = (monX, -self.SY)
                #time.sleep(5)
                From = "b"

                if initialX < monX:
                    vers = "d"
                    # ----------Tirer la proba-----------------
                    proba = random.random()
                    p1 = 1 / (1 + tan(math.radians(angle)))
                    p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                    if proba <= p1 and monX != -self.SX and monX != self.SX:
                        dir = 0
                    else:
                        dir = 90
                    # ----------------------------------------------

                else :
                    vers = "g"
                    # ----------Tirer la proba-----------------
                    proba = random.random()
                    p1 = 1 / (1 + tan(math.radians(angle)))
                    p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                    if proba <= p1 and monX != -self.SX and monX != self.SX:
                        dir = 180
                    else:
                        dir = 90
                    # ----------------------------------------------
                (initialX, initialY) = (monX, monY)

            if c == delta:

                if From == "b":

                    
                    if vers == "d":
                        # ----------Tirer la proba-----------------
                        proba = random.random()
                        p1 = 1 / (1 + tan(math.radians(angle)))
                        p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                        if proba <= p1 and monX != -self.SX and monX != self.SX:
                            dir = 0
                        else:
                            dir = 90
                        # ----------------------------------------------
                    else:
                        # ----------Tirer la proba-----------------
                        proba = random.random()
                        p1 = 1 / (1 + tan(math.radians(angle)))
                        p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                        if proba <= p1 and monX != -self.SX and monX != self.SX:
                            dir = 180
                        else:
                            dir = 90
                        # ----------------------------------------------

                elif From == "d":

                    
                    if vers == "b":
                        # ----------Tirer la proba-----------------
                        proba = random.random()
                        p1 = 1 / (1 + tan(math.radians(angle)))
                        p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                        if proba <= p1:
                            dir = 180
                        else:
                            dir = 270
                        # ----------------------------------------------
                    else:
                        # ----------Tirer la proba-----------------
                        proba = random.random()
                        p1 = 1 / (1 + tan(math.radians(angle)))
                        p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                        if proba <= p1:
                            dir = 180
                        else:
                            dir = 90
                        # ----------------------------------------------

                elif From == "g":


                    if vers == "b":
                        # ----------Tirer la proba-----------------
                        proba = random.random()
                        p1 = 1 / (1 + tan(math.radians(angle)))
                        p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                        if proba <= p1:
                            dir = 0
                        else:
                            dir = 270
                        # ----------------------------------------------
                    else:
                        # ----------Tirer la proba-----------------
                        proba = random.random()
                        p1 = 1 / (1 + tan(math.radians(angle)))
                        p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                        if proba <= p1:
                            dir = 0
                        else:
                            dir = 90
                        # ----------------------------------------------

                elif From == "h":

                    

                    if vers == "d":
                        # ----------Tirer la proba-----------------
                        proba = random.random()
                        p1 = 1 / (1 + tan(math.radians(angle)))
                        p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                        if proba <= p1 and monX != -self.SX and monX != self.SX:
                            dir = 0
                        else:
                            dir = 270
                        # ----------------------------------------------
                    else:
                        # ----------Tirer la proba-----------------
                        proba = random.random()
                        p1 = 1 / (1 + tan(math.radians(angle)))
                        p2 = tan(math.radians(angle)) / (1 + tan(math.radians(angle)))
                        if proba <= p1 and monX != -self.SX and monX != self.SX:
                            dir = 180
                        else:
                            dir = 270
                        # ----------------------------------------------

        

        return (self.nbrMessage, self.nbpas, temps_perdu)
    #---------------------------------------------------------------------------
