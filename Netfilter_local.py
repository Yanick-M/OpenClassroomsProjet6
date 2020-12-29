#! /usr/bin/env python3
# coding: utf-8

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
    
    # Vérification si le script est exécutée avec des privilèges
    verif_privileges()
    
    # Vérification si les paquets utilisés dans le script sont installés, l'utilisateur est informé si ce n'est pas le cas
    verif_paquet("iptables", "rsyslogd", "ssh", "rsync", "tar")

    # Affichage d'un logo au démarrage du script
    logo_acceuil()

    choix = "n"
    # Boucle de choix pour l'affichage du menu principal
    while choix != "q":
        print(
            "\n \033[36m1\033[0m : Rendre le pare-feu persistent,\n",
            "\033[36m2\033[0m : Rediriger les logs netfilter,\n",
            "\033[36m3\033[0m : Planifier l'archivage des logs,\n",
            "\033[36m4\033[0m : Déployer un script mis à jour,\n",
            "\033[36m5\033[0m : Annuler des modifications,\n",
            "\033[31mLes choix 1, 3 et 4 nécessitent d'avoir appelé les informations nécessaires à l'établissement de la connexion ssh,\033[0m\n",
            "\033[36mQ\033[0m : Quitter,"
        )
        choix = input("Quel est votre choix ? ")
        choix = choix.lower()
        if choix == "1":
            print("\nJe rends le pare-feu persistent.\n")
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
            persistent.main(args.user, args.host, password)
        elif choix == "2":
            print("\nJ'extrais les logs dans des fichiers spécifiques.\n")
            creation_journaux.main()    
        elif choix == "3":
            print("\nJ'archive les logs ailleurs.\n")
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
            persistent.download_fichier(args.user, args.host, password)
        elif choix == "5":
            choix2 = "n"
            # Boucle de choix pour l'affichage du menu secondaire
            while choix2 != "q":
                print(
                "\n \033[36m1\033[0m : Annuler la mise en place du pare-feu persistent,\n",
                "\033[36m2\033[0m : Annuler la redirection des logs netfilter,\n",
                "\033[36m3\033[0m : Annuler la planification de l'archivage des logs,\n",
                "\033[36mT\033[0m : Annuler toutes les modifications,\n",
                "\033[36mQ\033[0m : Revenir au menu principal,"
                )
                choix2 = input("Quel est votre choix ? ")
                choix2 = choix2.lower()
                if choix2 == "1":
                    print("\nJ'efface le daemon et la sauvegarde IPtables.\n")
                    persistent.annulation_modification()
                elif choix2 == "2":
                    print("\nJe supprime le fichier de config de rsyslog.\n")
                    creation_journaux.annulation_modification()    
                elif choix2 == "3":
                    print("\nJe déplanifie la tâche et j'efface le script.\n")
                    transfert_journaux.annulation_modification()
                elif choix2 =="t":
                    print("\nJ'écrase tout.\n")
                    persistent.annulation_modification()
                    creation_journaux.annulation_modification() 
                    transfert_journaux.annulation_modification()
                elif choix2 == "q":
                    break
                else:
                    print("\nJe n'ai pas compris votre choix!!!\n")
        elif choix == "q":
            print("\nJe quitte as soon as possible.\n")
        else:
            print("\nJe n'ai pas compris votre choix!!!\n")

main()
