#!/usr/bin/env python3
# coding: utf-8
 
import os, shutil, stat

# Vérifications des paramètres obligatoires

HOST = "SERVER_ANSIBLE"
USER = "aic"

# Déclaration des variables
CHEMIN_SOURCE = os.getcwd() + "/"
CHEMIN_TACHE = "/var/spool/cron/crontabs/"
NOM_TACHE = "root"
CHEMIN_SCRIPT = "/root/"
NOM_SCRIPT = "archivage_logs_netfilter.sh"
CHEMIN_CLE = "/root/.ssh/"
NOM_CLE = "id_rsa_archivage"
CHEMIN_DOCUMENTS = os.path.join(os.path.dirname(__file__), 'doc/')
NOM_DOCUMENT = "script_archivage.txt"

def lecture_fichier(chemin, nom):

    print("-----lecture du fichier {} dans {}-----".format(nom, chemin))
    # Essai de lecture du fichier correspondant au nom appelé
    try:
        mon_fichier = open(chemin + nom, "r")
        liste = [i[:-1] for i in mon_fichier]
        mon_fichier.close()
    # En cas de fichier inexistant, renvoie d'une chaîne vide
    except FileNotFoundError:
        liste=[]
    # En cas de droits insuffisants, l'utilisateur est informé du problème et l'exécution du script se termine
    except IOError:
        print("\033[31mLe script doit être lancé avec des priviléges pour réaliser cette action\033[0m")
        os._exit(0)

    return(liste)

def recherche(liste, valeur):
    
    # Recherche d'une valeur dans chaque ligne d'une liste (ex. : le nom du script dans la tâche cronatb active)
    # Si elle est trouvée, un "vrai" est renvoyé
    # Sinon un "faux"
    print("-----vérification de la liste-----")
    resultat = False
    for line in liste:
        if line.find(valeur) >= 0:
            resultat = True

    return(resultat)

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
        shutil.move(emplacement_src, emplacement_dst)
    except PermissionError:
        print("\033[31mLe script doit être lancé avec des priviléges pour réaliser cette action\033[0m")
        os._exit(0)
    
    # Modification des droits du script
    # Essai de modification des droits du fichier dans le réperoire de destination
    # En cas d'erreur, exécution de la commande bash correspondante avec privilèges
    try:
        os.chmod(emplacement_dst, stat.S_IRWXU)
    except:
        os.system('sudo chmod 100 "{}"'.format(emplacement_dst))

    print("\033[32m-----le fichier a été enregistré sur le disque-----\033[0m")

def creation_tache_crontab():
    
    print("-----planification d'une tâche-----")
    # Ajout de la tâche à l'aide d'une commande bash dans le fichier root du répertoire crontabs
    os.system("echo '0 1 * * *  \"{}./{}\" > /dev/null 2>&1' | sudo tee -a \"{}{}\" > /dev/null".format(CHEMIN_SCRIPT, NOM_SCRIPT, CHEMIN_TACHE, NOM_TACHE))
    # Activation de la tâche à l'aide d'une commande bash (le fichier sera ainsi lisible et modifiable par root ou le groupe crontab uniquement)
    os.system("sudo crontab \"{}{}\"".format(CHEMIN_TACHE, NOM_TACHE))

def creation_script():

    # Lecture du fichier contenant le script d'archivage dans une liste
    liste_archivage = lecture_fichier(CHEMIN_DOCUMENTS, NOM_DOCUMENT)
    
    # Ajout des variables manquantes appelées avec le script dans la liste
    liste_archivage.insert(2, "host={}".format(HOST))
    liste_archivage.insert(2, "user={}".format(USER))

    # Création du fichier conf dans le répertoire courant
    ecrire_fichier(CHEMIN_SOURCE, NOM_SCRIPT, liste_archivage)

    # Déplacement du fichier dans le répertoire root
    mise_en_place_fichier(CHEMIN_SOURCE, CHEMIN_SCRIPT, NOM_SCRIPT)

def crontab():

    print("\n\033[34mJ'analyse les tâches planifiées...\033[0m")
    
    # Ouverture du fichier /var/spool/cron/crontabs/root
    liste_tache = lecture_fichier(CHEMIN_TACHE, NOM_TACHE)
        # Vide ----> Ajout et validation tâche 
    if not liste_tache:
        creation_tache_crontab()
    else:
        # Sinon ----> Recherche nom du script dans le fichier
        resultat = recherche(liste_tache, NOM_SCRIPT)
            # Faux ----> Ajout et validation tâche
        if resultat is not True:
            creation_tache_crontab()
            # Vrai ----> Flag OK

    print("\033[32mLa tâche permettant l'archivage des logs est configurée !\033[0m")

def script():

    print("\n\033[34mJe cherche le script d'archivage des logs...\033[0m")
    
    # Ouverture du fichier /root/archivage_logs_netfilter.sh
    liste_script = lecture_fichier(CHEMIN_SCRIPT, NOM_SCRIPT)
        # Vide ----> création du script
    if not liste_script:
        creation_script()

    print("\033[32mLe script est en place !\033[0m")

def cle_ssh():

    print("\n\033[34mJe cherche la clé ssh permettant le transfert des archives...\033[0m")
    
    # Ouverture du fichier /root/.ssh/id_rsa_archivage
    liste_cle = lecture_fichier(CHEMIN_CLE, NOM_CLE)
        # Vide ----> Création
    if not liste_cle:
        print("-----génération d'une clé-----")
        os.system("sudo ssh-keygen -b 4096 -q -f \"{}{}\" -N \"\"".format(CHEMIN_CLE, NOM_CLE))

    print("\033[32mLa clé est en place !\033[0m")


# Archiver quotidiennement les journaux Netfilter sur un serveur central
# L'objectif est d'ajouter une tâche crontab qui va exécuter un script bash et créer ce script
# Le script compresse les journaux logs puis les copie en ssh sur une autre machine
def main():

    # Tâche crontab
    crontab()
    # Tâche script
    script()
    # Tâche clé ssh
    cle_ssh()

if __name__ == '__main__':
    #main()
    crontab()