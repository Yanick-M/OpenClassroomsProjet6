#! /usr/bin/env python3
# coding: utf-8

import os, shutil, stat, argparse, getpass

# Déclaration des variables
#CHEMIN_SOURCE = os.getcwd() + "/"
CHEMIN_TACHE = "/var/spool/cron/crontabs/"
NOM_TACHE = "root"
CHEMIN_SCRIPT = "/root/"
NOM_SCRIPT = "archivage_logs_netfilter.sh"
CHEMIN_CLE = "/root/.ssh/"
NOM_CLE = "id_rsa_archivage"
NOM_CLE2 = "id_rsa_archivage.pub"
NOM_CLE3 = "authorized_keys"
CHEMIN_DOCUMENTS = os.path.join(os.path.dirname(__file__), 'doc/')
NOM_DOCUMENT = "script_archivage.txt"

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

def mise_en_place_fichier(chemin_dst, nom, droits):

    # Essai de modification des droits sur le script
    # En cas d'erreur, levée d'une exception
    try:
        os.chmod(chemin_dst + nom, droits)
    except FileNotFoundError:
        raise FichierNonTrouve
    except PermissionError:
        raise EchecEcriture

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
        liste_archivage = lecture_fichier(CHEMIN_DOCUMENTS, NOM_DOCUMENT)
    except FichierNonTrouve:
        print("\033[31mVérifiez la présence du fichier {} dans le répertoire \"{}\".\033[0m".format(NOM_DOCUMENT, CHEMIN_DOCUMENTS))
        os._exit(0)
    except EchecLecture as exc:
        raise Erreur.privileges(IOError)

    # Ajout des variables manquantes, appelées avec le script, dans la liste
    liste_archivage.insert(2, "host={}".format(host))
    liste_archivage.insert(2, "user={}".format(user))

    # Création du script dans le répertoire de root
    try:
        ecrire_fichier(CHEMIN_SCRIPT, NOM_SCRIPT, liste_archivage)
    except EchecEcriture as exc:
        raise Erreur.ecriture_impossible(EchecEcriture, CHEMIN_SCRIPT, NOM_SCRIPT)
    
    # Modification des droits du script
    try:  
        mise_en_place_fichier(CHEMIN_SCRIPT, NOM_SCRIPT, stat.S_IRWXU)
    except EchecEcriture as exc:
        raise Erreur.privileges(IOError)

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
    except EchecLecture as exc:
        raise Erreur.privileges(IOError)

    print("\033[32mLa tâche permettant l'archivage des logs est configurée !\033[0m")

def archivage(user, host):

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
    except EchecLecture as exc:
        raise Erreur.privileges(IOError)

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
        
        # Déclaration des droits pour les fichiers concernant ssh appartenant à root
        droits_ssh = stat.S_IREAD|stat.S_IWRITE

        # Dans le cas où il manque le fichier .pub, tentative de suppression du fichier id_rsa_archivage au préalable
        os.system("rm \"{0}{1}\" > /dev/null 2>&1 | ssh-keygen -b 4096 -q -f \"{0}{1}\" -N \"\"".format(CHEMIN_CLE, NOM_CLE))
        
        # Essai de modification des droits des fichiers générés que seul le propriétaire peut lire ou modifier
        try:
            mise_en_place_fichier(CHEMIN_CLE, NOM_CLE, droits_ssh)
            mise_en_place_fichier(CHEMIN_CLE, NOM_CLE2, droits_ssh)
                # Si le fichier n'a pas été trouvé car le transfert de la clé à échouer, le script continue
        except FichierNonTrouve as exc:
            pass
        except EchecEcriture as exc:
            raise Erreur.privileges(IOError)

        # Transfert de la clé vers le serveur central
        result = os.system("sshpass -p \"{}\" ssh-copy-id -i \"{}{}\" {}@{} > /dev/null 2>&1".format(password, CHEMIN_CLE, NOM_CLE, user, host))
        # Si la connexion échoue, l'utilisateur est informé
        if result == 256:
            print("\033[31mLa copie de l'ID ssh vers {} n'a pas fonctionné, problème à étudier ! Le nom du server ou de la clé est peut-être incorrecte\033[0m".format(host))
        elif result == 1536:
            print("\033[31mLe nom d'utilisateur du serveur {} ou son mot de passe n'est pas correct !\033[0m".format(host))
        
        # Essai de modification des droits sur le fichier contenant les machines autorisées via ssh
        try:
            mise_en_place_fichier(CHEMIN_CLE, NOM_CLE3, droits_ssh)
        # Si le fichier n'a pas été trouvé car le transfert de la clé à échouer, le script continue
        except FichierNonTrouve as exc:
            pass
        except EchecEcriture as exc:
            raise Erreur.privileges(IOError)

    # Si la fonction est exécutée sans privilèges, l'utilisateur est informée et l'exécution du script se termine
    except EchecLecture as exc:
        raise Erreur.privileges(IOError)

    print("\033[32mLa clé est en place !\033[0m")


# Archiver quotidiennement les journaux Netfilter sur un serveur central
# L'objectif est d'ajouter une tâche crontab qui va exécuter un script bash et créer ce script
# Le script compresse les journaux logs puis les copie en ssh sur une autre machine
def main(user, host, password):

    # Tâche crontab
    crontab()
    # Tâche script
    archivage(user, host)
    # Tâche clé ssh
    cle_ssh(user, host, password)

if __name__ == '__main__':

    try:
        verif_privileges()
    except EchecEcriture:
        raise Erreur.privileges(EchecEcriture)

    # Traitement des arguments
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