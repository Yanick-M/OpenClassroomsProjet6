#! /usr/bin/env python3
# coding: utf-8

import os, shutil

# Déclaration du fichier regles.txt et de son répertoire doc/
CHEMIN_DOCUMENTS = os.path.join(os.path.dirname(__file__), 'doc/')
NOM_REGLES = "regles.txt"
# Déclaration des répertoire source et de destination ainsi qu'n nom pour le fichier de configuration rsyslog
#CHEMIN_SOURCE = os.getcwd() + "/"
CHEMIN_DESTINATION = "/etc/rsyslog.d/"
NOM_LOG = "10-iptables.conf"

# Déclaration de classes pour gérer les exceptions
class Erreur(Exception):
    # Classe de gestion des erreurs personnalisées
    pass
    # Si l'utilisateur n'a pas de privilège, il est informé du problème et l'exécution du script se termine 
    def privileges(self):
        print("\033[31mLe script doit être exécuté avec des privilèges !\033[0m")
        os._exit(0)
    # En cas de fichier absent et obligatoire, l'utilisateur est informé du problème et l'exécution du script se termine
    def fichier_absent(self, chemin, nom):
        print("\033[31mLe fichier {} dans \"{}\" est manquant ou vide !\033[0m".format(chemin, nom))
        os._exit(0)
    # En cas d'échec de création ou de modification de fichier, l'utilisateur est informé du problème et l'exécution du script se termine
    def ecriture_impossible(self, chemin, nom):
        print("\033[31mImpossible d'écrire dans le fichier {} dans \"{}\" ! Privilèges ?\033[0m".format(chemin, nom))
        os._exit(0)
    # En cas de problème inconnue, l'utilisateur est informé du problème et l'exécution du script se termine
    def erreurfatale(self):
        print("\033[31mUne erreur fatale est survenue, le script doit être débuggé :(\033[0m")
        os._exit(0)

class FichierNonTrouve(Erreur):
    # Définition d'une exception personnalisée si un fichier n'a pas pu être lu
    pass
class EchecLecture(Erreur):
    # Définition d'une exception personnalisée si un fichier n'a pas pu être créé ou modifié
    pass
class EchecEcriture(Erreur):
    # Définition d'une exception personnalisée si un fichier n'a pas pu être créé ou modifié
    pass
class RechercheVide(Erreur):
    # Définition d'une exception personnalisée si une comparaison est identique
    pass

def verif_privileges():
    # Vérification que le script a été exécuté avec des privilèges
    if os.geteuid() != 0:
        raise EchecEcriture

def annulation_modification():

    # En cas d'erreur en cours d'exécution ou à la demande de l'utilisateur, suppression du fichier créé
    try:
        lecture_fichier(CHEMIN_DESTINATION, NOM_LOG)
        try:
            os.remove(CHEMIN_DESTINATION + NOM_LOG)
            print("\033[32m-----le fichier a été supprimé-----\033[0m")
        except IOError:
            raise Erreur.privileges(EchecLecture)
    except FichierNonTrouve as exc:
        print("\033[32m-----le fichier a déjà été supprimé-----\033[0m")
    except EchecLecture as exc:
        raise Erreur.privileges(EchecLecture)

def lecture_fichier(chemin, nom):

    print("-----lecture du fichier {} dans {}-----".format(nom, chemin))
    # Essai de lecture du fichier correspondant au nom appelé
    try:
        mon_fichier = open(chemin + nom, "r")
        liste = [i[:-1] for i in mon_fichier]
        mon_fichier.close()
        print("\033[32m-----le fichier a été trouvé et lu-----\033[0m")
    # En cas de fichier inexistant, renvoie d'une exception pour traitement
    except FileNotFoundError:
        raise FichierNonTrouve
    # En cas de droits insuffisants, l'utilisateur est informé du problème et l'exécution du script se termine
    except IOError:
        raise EchecLecture
    
    return(liste)

def recherche_regles_conf(liste_conf):
    
    # L'objectif est de savoir si tous les commentaires sont redirigés dans un fichier de log propre
    # Comparaison des listes pour voir si toutes les règles existent dans le fichier de config rsyslog en fonction du prefix inséré par netfilter
    # La liste des préfixes manquants sera renvoyé
    print("-----vérification des règles de commentaires dans la configuration actuelle-----")
    try:
        liste_regles = lecture_fichier(CHEMIN_DOCUMENTS, NOM_REGLES)
    except FichierNonTrouve as exc:
        # Si la lecture du fichier renvoie une liste vide, l'utilisateur est informé du problème et l'exécution du script se termine
        raise Erreur.fichier_absent(FichierNonTrouve, CHEMIN_DOCUMENTS, NOM_REGLES)

    # Déclaration d'une liste qui contiendra les noms des commentaires à ajouter dans le fichier conf
    regles_a_definir = []

    # Lecture dans une première boucle des règles qui devraient être présentes sur le système
    print("-----comparaison des informations-----")
    for regle in liste_regles:
        
        regle_trouvee = False

        # Vérification si la liste appelée est vide au quel cas tous les préfixes sont ajoutés à la liste à définir
        if not liste_conf:
            regles_a_definir.append(regle[regle.find("\""):regle.rfind("\"") + 1])
        else:
            # Lecture dans une seconde boucle des règles actives sur le système                                                                             
            for line in liste_conf:
                # Comparaison du préfixe d'une règle par rapport au préfixe d'une ligne du fichier conf
                if regle[regle.find("\""):regle.rfind("\"") + 1] == line[line.find("\""):line.rfind("\"") + 1]:
                    regle_trouvee = True
                    break
            # Si le préfixe n'a pas été trouvée lors de la comparaison, ajout du préfixe dans la liste à définir
            if regle_trouvee is False:
                regles_a_definir.append(regle[regle.find("\""):regle.rfind("\"") + 1])

    # Si la comparaison est identique, renvoie d'une exception personnalisée
    if not regles_a_definir:
        raise RechercheVide        

    return regles_a_definir

def creation_regles_manquantes(liste_finale, liste_regles):

    print("-----génération des informations manquantes-----")
    
    # Démarrage d'une boucle pour lire la liste des règles manquantes et compléter la liste finale
    for line in liste_regles:
        # Génération d'une règle pour chaque préfixe manquant et ajout à la liste des règles déjà existantes
        liste_finale.append(":msg, contains, " + line + " -/var/log/netfilter/" + line[1:-3] + ".log \n & ~")

    return(liste_finale)

def ecrire_fichier(chemin, nom, donnees):
    
    print("-----sauvegarde de données dans un fichier-----")

    # Essai d'ouverture en écriture du fichier dans lequel écrire des données
    # Si l'ouverture réussi, l'écriture est effectuée    
    try:
        with open(chemin + nom, "w") as fichier:
            for line in donnees:
                fichier.write("{}\n".format(line))
        print("\033[32m-----le fichier a enregistré sur le disque-----\033[0m")
    # Si l'ouverture échoue, l'utilisateur est informé et l'exécution du script se termine
    except IOError:
        raise EchecEcriture

def creation_fichier_conf(liste_conf):

    # Comparaison des règles actives aux règles souhaitées pour extraire la liste des préfixes générés par Netfilter
    # et qui ne sont pas encore isolés par rsyslog
    try:
        liste_a_definir = recherche_regles_conf(liste_conf)
    # Si la comparaison est identique, levée d'une erreur fatale car ce n'est pas possible
    except RechercheVide:
        raise Erreur.erreurfatale(RechercheVide)

    # Génération et ajout des règles correspondant aux préfixes manquants dans le fichier de configuration
    liste_finale = creation_regles_manquantes(liste_conf, liste_a_definir)

    # Création du fichier conf dans le répertoire courant
    try:
        ecrire_fichier(CHEMIN_DESTINATION, NOM_LOG, liste_finale)
    except EchecEcriture:
        raise Erreur.ecriture_impossible(EchecEcriture, CHEMIN_DESTINATION, NOM_LOG)

    # L'ajout du fichier 10-iptables.conf nécessite le redémarrage du service pour être pris en compte
    print("\n\033[34mJe redémarre le service rsyslog...\033[0m")
    os.system ('service rsyslog restart')

def main():
    
    # Créer des journaux regroupant chaque événement que Netfilter aura commenté en fonction de son préfixe
    # L'objectif de ce module est de s'assurer qu'un fichier conf existe dans le répertoire rsyslog.d et qu'il contient
    # des règles correspondantes aux préfixes ajoutés par Netfilter
    
    print("\n\033[36mJe cherche le fichier de config rsyslog...\033[0m")
    # Essai de lecture du fichier 10-iptables.conf
    try :
        liste_conf = lecture_fichier(CHEMIN_DESTINATION, NOM_LOG)
        print("\n\033[36mJe lance la vérification de la présence des règles de commentaires...\033[0m")
        # Si il existe, comparaison des règles présentes avec les règles à appliquer
        try:
            recherche_regles_conf(liste_conf)
            print("\n\033[36mJe lance la création du fichier...\033[0m")
            creation_fichier_conf(liste_conf)
        # Si les règles sont différentes, recréation du fichier 10-iptables.conf
        except RechercheVide:
            print("\033[32m-----les informations sont identiques-----\033[0m")
    # Si il n'exite pas, création du fichier 10-iptables.conf à partir d'une liste vide
    except FichierNonTrouve:
        print("\n\033[36mJe lance la création du fichier...\033[0m")
        liste_conf = []
        creation_fichier_conf(liste_conf)
    except EchecLecture as esc:
        raise Erreur.privileges

    print("\n\033[32mLe ficher de config rsyslog est en place et IPtables a ses propres logs !\033[0m\n")

if __name__ == '__main__':
    
    # Vérification si le script est exécutée avec des privilèges
    try:
        verif_privileges()
    except EchecEcriture:
        raise Erreur.privileges(EchecEcriture)
    
    choix = "n"
    # Boucle de choix:
    while choix != "q":
        print(
            "\n \033[36m1\033[0m : Rendre le pare-feu persistent,\n",
            "\033[36m2\033[0m : Annuler les modifications,\n",
            "\033[36mQ\033[0m : Quitter,"
        )   
        choix = input("Quel est votre choix ? ")
        choix = choix.lower()
        if choix == "1":
            print("\nJe rends le pare-feu persistent.\n")
            main()
        elif choix == "2":
            print("\nJ'annule les modifications.\n")
            annulation_modification()
        elif choix == "q":
            print("\nJe quitte as soon as possible.\n")
        else:
            print("\nJe n'ai pas compris !!!\n")