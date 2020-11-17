#! /usr/bin/env python3
# coding: utf-8

import os, shutil

# Déclaration du fichier regles.txt et de son répertoire doc/
CHEMIN_DOCUMENTS = os.path.join(os.path.dirname(__file__), 'doc/')
NOM_REGLES = "regles.txt"
# Déclaration des répertoire source et de destination ainsi qu'n nom pour le fichier de configuration rsyslog
CHEMIN_SOURCE = os.getcwd() + "/"
CHEMIN_DESTINATION = "/etc/rsyslog.d/"
NOM_LOG = "10-iptables.conf"

def lire_fichier(chemin, nom):
    
    # Essai de lecture du fichier correspondant au nom appelé
    print("-----lecture du fichier {} dans {}-----".format(nom, chemin))
    try :
        mon_fichier = open(chemin + nom)
        liste = [i[:-1] for i in mon_fichier]
        mon_fichier.close()
        print("\033[32m-----le fichier a été trouvé et lu-----\033[0m")
    
    # Si l'essai ne fonctionne pas, levée d'une exception qui renvoie une liste vide
    except :
        liste=[]
    return(liste)

def recherche_regles_conf(liste_conf):
    
    # L'objectif est de savoir si tous les commentaires sont redirigés dans un fichier de log propre
    # Comparaison des listes pour voir si toutes les règles existent dans le fichier de config rsyslog en fonction du prefix inséré par netfilter
    # La liste des préfixes manquants sera renvoyé
    print("-----vérification des règles de commentaires dans la configuration actuelle-----")
    liste_regles = lire_fichier(CHEMIN_DOCUMENTS, NOM_REGLES)

    # Si la lecture du fichier renvoie une liste vide, l'utilisateur est informé du problème et l'exécution du script se termine
    if not liste_regles:
        
        print("\033[31mLe fichier {} dans \"{}\" est manquant ou vide !\033[0m".format(NOM_REGLES, CHEMIN_DOCUMENTS))
        os._exit(0)

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

    if not regles_a_definir:
        print("\033[32m-----les informations sont identiques-----\033[0m")

    return(regles_a_definir)

def creation_regles_manquantes(liste_finale, liste_regles):

    print("-----génération des informations manquantes-----")
    
    # Démarrage d'une boucle pour lire la liste des préfixes
    for line in liste_regles:
        # Génération d'une règle pour chaque préfixe manquant et ajout à la liste des règles déjà existantes
        liste_finale.append(":msg, contains, " + line + " -/var/log/" + line[1:-3] + ".log \n & ~")

    return(liste_finale)

def creation_fichier_conf(liste_conf):

    # Comparaison des règles actives aux règles souhaitées pour extraire la liste des préfixes générés par Netfilter
    # et qui ne sont pas encore isolés par rsyslog
    liste_a_definir = recherche_regles_conf(liste_conf)

    # Génération et ajout des règles correspondant aux préfixes manquants dans le fichier de configuration
    liste_finale = creation_regles_manquantes(liste_conf, liste_a_definir)

    # Création du fichier conf dans le répertoire courant
    ecrire_fichier(CHEMIN_SOURCE, NOM_LOG, liste_finale)
    
    # Déploiement du fichier dans le répertoire rsyslog.d
    mise_en_place_fichier(CHEMIN_SOURCE, CHEMIN_DESTINATION, NOM_LOG)

def ecrire_fichier(chemin, nom, donnees):
    
    print("-----sauvegarde de données dans un fichier-----")

    # Essai d'ouverture en écriture du fichier dans lequel écrire des données
    # Si l'ouverture réussi, l'écriture est effectuée    
    try:
        with open(chemin + nom, "w") as fichier:
            for line in donnees:
                fichier.write("{}\n".format(line))
    # Si l'ouverture échoue, l'utilisateur est informé et l'exécution du script se termine
    except IOError:
        print("\033[31mLe fichier {} n'a pas pu être créer à l'emplacement {} !\033[0m".format(nom, chemin))
        os._exit(0)

def mise_en_place_fichier(chemin_src, chemin_dst, nom):
    
    # Génération de l'emplacement source
    emplacement_src = chemin_src + nom
    
    # Génération de l'emplacement de destination
    emplacement_dst = chemin_dst + nom
    
    # Essai de copie du fichier de son emplacement actuel vers sa destination
    # En cas d'erreur, exécution de la commande bash correspondante avec privilège
    try:
        shutil.copyfile(emplacement_src, emplacement_dst)
    except PermissionError:
        os.system('sudo cp "{}" "{}"'.format(emplacement_src, emplacement_dst))
    
    # Modification du propriétaire du script
    user = 'root'
    group = 'root'
    # Essai de modification du propriétaire du fichier dans le réperoire de destination
    # En cas d'erreur, exécution de la commande bash correspondante avec privilège
    try:
        os.chown(emplacement_dst, user, group)
    except:
        os.system('sudo chown {}:{} "{}"'.format(user, group, emplacement_dst))

    print("\033[32m-----le fichier a enregistré sur le disque-----\033[0m")

def main():
    
    # Créer des journaux regroupant chaque événement que Netfilter aura commenté en fonction de son préfixe
    # L'objectif de ce module est de s'assurer qu'un fichier conf existe dans le répertoire rsyslog.d et qu'il contient
    # des règles correspondantes aux préfixes ajoutés par Netfilter
    objectif_atteint = False
    while objectif_atteint is not True:
    
        print("\n\033[34mJe cherche le fichier de config rsyslog...\033[0m")
        liste_conf = lire_fichier(CHEMIN_DESTINATION, NOM_LOG)
        while not liste_conf:

            print("\n\033[34mJe lance la création du fichier...\033[0m")
            creation_fichier_conf(liste_conf)

            # Je relance la lecture du fichier
            liste_conf = lire_fichier(CHEMIN_DESTINATION, NOM_LOG)

        print("\n\033[34mJe lance la vérification de la présence des règles de commentaires...\033[0m")
        resultat = recherche_regles_conf(liste_conf)

        if not resultat:
            print("\n\033[32mLe ficher de config rsyslog est en place et IPtables a ses propres logs !\033[0m")
            objectif_atteint = True
        else:
            print("\033[34mJe lance la création du fichier...\033[0m")
            creation_fichier_conf(liste_conf)
        
    print("\n\033[34mJe redémarre le service rsyslog...\033[0m")
    os.system ('sudo service rsyslog restart')

if __name__ == '__main__':
    main()