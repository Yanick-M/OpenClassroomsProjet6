#! /usr/bin/env python3
# coding: utf-8

'''
Scénario : Tout juste embauché comme stagiaire au sein de l'entreprise "Project Six", le responsable du service production me 
demande de mettre de l'ordre dans les pare-feux des routeurs et serveurs linux au sein de l'infrastructure. Les différents
pare-feux netfilter ont été configurés avec la commande iptables mais ces règles ne sont pas persistentes.

Solution : Ce script doit permettre de rendre les pare-feux persistents, d'y intégrer des commentaires dans les logs avec 
des règles définies par le RSSI et d'enregistrer les logs dans des fichiers spécifiques (et non dans syslog). Il doit permettre
de sauvegarder les journaux sur le serveur central tous les jours, ainsi que le script du pare-feu et le fichier contenant la tâche
de sauvegarde lors de leurs créations. Chaque machine doit avoir un répertoire de sauvegarde propre sur le serveur central.

Une fois le script terminé, il sera intéressant d'en faire un module ansible pour rendre la tâche moins contraignante.
'''
import os, argparse, getpass, subprocess
try:
    from libnetfilterlocal import persistent, creation_journaux, transfert_journaux
except:
    import sys
    chemin = os.getcwd() + "/"
    sys.path.insert(0, chemin)
    from libnetfilterlocal import persistent

# traitement des arguments
parser = argparse.ArgumentParser ()
parser.add_argument ( "-U", "--user", help = "indiquez un nom d'utilisateur pour la connexion SSH" )
parser.add_argument ( "-H", "--host", help = "Indiquez un nom de la machine à contacter pour la connexion SSH" )
args = parser.parse_args ()

def logo_acceuil():
    
    logo = [
        "                                     __________          __   __                   ",
        "                                     \______   \___ __ _/  |_|  |__   ____   ____  ",
        "                                      |     ___<   |  |\   __\  |  \ /  _ \ /    \ ",
        "                                      |    |    \___  | |  | |   Y  (  <_> )   |  \ ",
        "                                      |____|    / ____| |__| |___|  /\____/|___|  /",
        "                                                \/                \/            \/"
    ]

    for line in logo:
        print(line)

def verif_privileges():
    # Vérification que le script a été exécuté avec des privilèges
    if os.geteuid() != 0:
        print("\033[31mLe script nécessite des privilèges pour fonctionner !\033[0m")
        os._exit(0)

def verif_paquet(*args):
    # Vérification que les packages utilisés dans le script sont bien présents sur le système
    verif = True
    for line in args:
        result = os.system("man {} > /dev/null 2>&1".format(line))
        if result == 4096:
            print("Attention ! Le package {} n'est pas installé.".format(line))
            verif = False
    if verif is False:
        print("Il est nécessaire d'installer le(s) paquet(s) manquant(s) pour que le script fonctionne correctement !\033[0m")

def main():
    
    verif_privileges()
    
    verif_paquet("iptables", "rsyslogd", "ssh", "rsync", "tar")

    logo_acceuil()

    choix = "n"
    # Boucle de choix:
    while choix != "q":
        print(
            "\n \033[34m1\033[0m : Rendre le pare-feu persistent,\n",
            "\033[34m2\033[0m : Rediriger les logs netfilter,\n",
            "\033[34m3\033[0m : Planifier la sauvegarde des logs,\n",
            "\033[34m4\033[0m : Déployer un script mis à jour,\n",
            "\033[31mLes choix 1, 3 et 4 nécessitent d'avoir appelé les informations nécessaires à l'établissement de la connexion ssh,\033[0m\n",
            "\033[34mQ\033[0m : Quitter,"
        )
        choix = input("Quel est votre choix ? ")
        choix = choix.lower()
        if choix == "1":
            print("\nJe rends le pare-feu persistent.\n")
            persistent.main()
        elif choix == "2":
            print("\nJ'extrais les logs dans des fichiers spécifiques.\n")
            creation_journaux.main()    
        elif choix == "3":
            print("\nJe transfére les logs ailleurs.\n")
            if not args.user or not args.host :
                print("Les arguments user et host n'ont pas été appelés. Ajoutez -h pour obtenir de l'aide.")
                os._exit(0)
            else:
                # Demande sécurisée du mot de passe de l'utilisateur pour la connexion ssh
                try: 
                    password = getpass.getpass(prompt="Quel est le mot de passe de l'utilisateur pour la connexion ssh ?") 
                except: 
                    print("Problème détecté avec la saisie du mot de passe")
                    os._exit(0)
                transfert_journaux.main(args.user, args.host, password)
        elif choix == "4":
            print("\nJe downloade le script corrigé.\n")
            #transfert_mise_a_jour.main()
        elif choix == "q":
            print("\nJe quitte as soon as possible.\n")
        else:
            print("\nJe n'ai pas compris !!!\n")

main()