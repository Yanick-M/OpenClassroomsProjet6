#! /usr/bin/env python3
# coding: utf-8

import os, shutil, stat, argparse, getpass

# Déclaration des variables
CHEMIN_SOURCE = os.getcwd() + "/"
CHEMIN_TACHE = "/var/spool/cron/crontabs/"
NOM_TACHE = "root"
CHEMIN_SCRIPT = "/root/"
NOM_SCRIPT = "archivage_logs_netfilter.sh"
CHEMIN_CLE = "/root/.ssh/"
NOM_CLE = "id_rsa_archivage"
NOM_CLE2 = "id_rsa_archivage.pub"
CHEMIN_DOCUMENTS = os.path.join(os.path.dirname(__file__), 'doc/')
NOM_DOCUMENT = "script_archivage.txt"

class Error(Exception):
    """ classe de gestion des erreurs personnalisées"""
    pass
class FichierNonTrouve(Error):
    """ définition d'une erreur perso """
    pass
class DroitsInsuffissants(Error):
    """ définition d'une erreur perso """
    pass
class RechercheVide(Error):
    """ définition d'une erreur perso """
    pass
class EchecEcriture(Error):
    """ définition d'une erreur perso """
    pass

def lecture_fichier(chemin, nom):

    print("-----lecture du fichier {} dans {}-----".format(nom, chemin))
    # Essai de lecture du fichier correspondant au nom appelé
    try:
        mon_fichier = open(chemin + nom, "r")
        liste = [i[:-1] for i in mon_fichier]
        mon_fichier.close()
    # En cas de fichier inexistant, renvoie d'une chaîne vide
    except FileNotFoundError:
        raise FichierNonTrouve
    # En cas de droits insuffisants, l'utilisateur est informé du problème et l'exécution du script se termine
    except IOError:
        raise DroitsInsuffissants

    return(liste)

def recherche(liste, valeur):
    
    # Recherche d'une valeur dans chaque ligne d'une liste (ex. : le nom du script dans la tâche cronatb active)
    # Si la valeur n'est pas trouvée, une exception est levée
    print("-----vérification de la liste-----")
    resultat = False
    for line in liste:
        if line.find(valeur) >= 0:
            resultat = True
    if resultat is False:
        raise RechercheVide

def ecrire_fichier(chemin, nom, donnees):
    
    print("-----sauvegarde de données dans un fichier-----")

    # Essai d'ouverture en écriture du fichier dans lequel écrire des données
    # Si l'ouverture réussi, l'écriture est effectuée    
    try:
        with open(chemin + nom, "w") as fichier:
            for line in donnees:
                fichier.write("{}\n".format(line))
    # Si l'ouverture échoue, l'utilisateur est informé et l'exécution du script se termine
    except:
        raise EchecEcriture

def mise_en_place_fichier(chemin_src, chemin_dst, nom):
    
    # Génération de l'emplacement source
    emplacement_src = chemin_src + nom
    
    # Génération de l'emplacement de destination
    emplacement_dst = chemin_dst + nom
    
    # Essai de copie du fichier de son emplacement actuel vers sa destination
    # En cas d'erreur, exécution de la commande bash correspondante avec privilège
    try:
        shutil.move(emplacement_src, emplacement_dst)
        os.chmod(emplacement_dst, stat.S_IRWXU)
    except PermissionError:
        raise DroitsInsuffissants

    print("\033[32m-----le fichier a été enregistré sur le disque-----\033[0m")

def creation_tache_crontab():
    
    print("-----planification d'une tâche-----")
    # Ajout de la tâche à l'aide d'une commande bash dans le fichier root du répertoire crontabs
    os.system("echo '0 1 * * *  \"{}./{}\" > /dev/null 2>&1' | sudo tee -a \"{}{}\" > /dev/null".format(CHEMIN_SCRIPT, NOM_SCRIPT, CHEMIN_TACHE, NOM_TACHE))
    # Activation de la tâche à l'aide d'une commande bash (le fichier sera ainsi lisible et modifiable par root ou le groupe crontab uniquement)
    os.system("sudo crontab \"{}{}\"".format(CHEMIN_TACHE, NOM_TACHE))

def creation_script(user, host):

    # Lecture du fichier contenant le script d'archivage dans une liste
    try:
        liste_archivage = lecture_fichier("/home/yanick/Documents/P6/NetFilterLocal/OpenClassroomsProjet6/libnetfilterlocal/doc/", NOM_DOCUMENT)
    except FichierNonTrouve:
        print("\033[31mVérifiez la présence du fichier {} dans le répertoire \"{}\".\033[0m".format(NOM_DOCUMENT, CHEMIN_DOCUMENTS))
        os._exit(0)
    except DroitsInsuffissants as exc:
        print("\033[31mLe script doit être lancé avec des priviléges pour réaliser cette action !\033[0m")
        os._exit(0)

    # Ajout des variables manquantes appelées avec le script dans la liste
    liste_archivage.insert(2, "host={}".format(host))
    liste_archivage.insert(2, "user={}".format(user))

    # Création du fichier conf dans le répertoire courant
    try:
        ecrire_fichier(CHEMIN_SOURCE, NOM_SCRIPT, liste_archivage)
    except EchecEcriture as exc:
        print("\033[31mLe fichier {} n'a pas pu être créer à l'emplacement {} !\033[0m".format(NOM_SCRIPT, CHEMIN_SOURCE))
        os._exit(0)
    
    # Déplacement du fichier dans le répertoire root
    try:    
        mise_en_place_fichier(CHEMIN_SOURCE, CHEMIN_SCRIPT, NOM_SCRIPT)
    except DroitsInsuffissants as exc:
        print("\033[31mLe script doit être lancé avec des priviléges pour réaliser cette action !\033[0m")

def crontab():

    print("\n\033[34mJ'analyse les tâches planifiées...\033[0m")
    
    # Ouverture du fichier /var/spool/cron/crontabs/root
    try:
        liste_taches = lecture_fichier(CHEMIN_TACHE, NOM_TACHE)
        # Vérification de la présence de l'exécution du script d'archivage dans la liste des tâches crontab
        try:
            recherche(liste_taches, NOM_SCRIPT)
        # Si la recherche est infructueuse, ajout de la tâche crontab
        except RechercheVide as exc:
            creation_tache_crontab()
    # Si le fichier n'existe pas, ajout de la tâche crontab
    except FichierNonTrouve as exc:
        creation_tache_crontab()
    # Si l'utilisateur n'a pas le droit d'accéder au fichier, il est informé et l'exécution du script est stoppé
    except DroitsInsuffissants as exc:
        print("\033[31mLe script doit être lancé avec des priviléges pour réaliser cette action !\033[0m")
        os._exit(0)

    print("\033[32mLa tâche permettant l'archivage des logs est configurée !\033[0m")

def script(user, host):

    print("\n\033[34mJe cherche le script d'archivage des logs...\033[0m")
    
    # Ouverture du fichier /root/archivage_logs_netfilter.sh
    try:
        liste_script = lecture_fichier(CHEMIN_SCRIPT, NOM_SCRIPT)
        # Vérification que l'utilisateur et le serveur sont les bons
        try:
            recherche(liste_script, user)
            recherche(liste_script, host)
        # Si un des deux est différent, le script est recréé
        except RechercheVide as exc:
            creation_script(user, host)
    # Si le fichier n'existe pas, création du script
    except FichierNonTrouve as exc:
        creation_script(user, host)
    # Si l'utilisateur n'a pas le droit d'accéder au fichier, il est informé et l'exécution du script est stoppé
    except DroitsInsuffissants as exc:
        print("\033[31mLe script doit être lancé avec des priviléges pour réaliser cette action\033[0m")
        os._exit(0)

    print("\033[32mLe script est en place !\033[0m")

def cle_ssh(user, host, password):

    print("\n\033[34mJe cherche la clé ssh permettant le transfert des archives...\033[0m")
    
    # Essai de lecture des fichiers /root/.ssh/id_rsa_archivage*
    try:
        lecture_fichier(CHEMIN_CLE, NOM_CLE)
        lecture_fichier(CHEMIN_CLE, NOM_CLE2)
    # Si un des fichiers n'est pas trouvé, création de la clé
    except FichierNonTrouve:
        print("-----génération d'une clé-----")
        # Dans le cas où il manque le fichier .pub, tentative de suppression du fichier id_rsa_archivage au préalable
        os.system("rm \"{0}{1}\" > /dev/null 2>&1 | ssh-keygen -b 4096 -q -f \"{0}{1}\" -N \"\"".format(CHEMIN_CLE, NOM_CLE))
        os.system("sshpass -p \"{}\" ssh-copy-id -i /home/yanick/.ssh/id_rsa_test {}@{} > /dev/null 2>&1".format(password, user, host))
    except DroitsInsuffissants as exc:
        print("\033[31mLe script doit être lancé avec des priviléges pour réaliser cette action !\033[0m")
        os._exit(0)

    print("\033[32mLa clé est en place !\033[0m")


# Archiver quotidiennement les journaux Netfilter sur un serveur central
# L'objectif est d'ajouter une tâche crontab qui va exécuter un script bash et créer ce script
# Le script compresse les journaux logs puis les copie en ssh sur une autre machine
def main(user, host, password):

    # Tâche crontab
    crontab()
    # Tâche script
    script(user, host)
    # Tâche clé ssh
    cle_ssh(user, host, password)

if __name__ == '__main__':

    # traitement des arguments
    parser = argparse.ArgumentParser ()
    parser.add_argument ( "-U", "--user", help = "indiquez un nom d'utilisateur pour la connexion SSH" )
    parser.add_argument ( "-H", "--host", help = "Indiquez un nom de la machine à contacter pour la connexion SSH" )
    args = parser.parse_args ()
    if not args.user or not args.host :
        print("Les arguments user et host n'ont pas été appelés. Ajoutez -h pour obtenir de l'aide.")
        os._exit(0)
    
    # Demande sécurisée du mot de passe de l'utilisateur pour la connexion ssh
    try: 
        password = getpass.getpass(prompt="Quel est le mot de passe de l'utilisateur pour la connexion ssh ?") 
    except: 
        print("Problème détecté avec la saisie du mot de passe")
        os._exit(0)
    main(args.user, args.host, password)