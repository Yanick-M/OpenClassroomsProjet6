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
try:
    from libnetfilterlocal import persistent, creation_journaux, transfert_journaux
except:
    import sys, os
    chemin = os.getcwd() + "/"
    sys.path.insert(0, chemin)
    from libnetfilterlocal import persistent

# Besoin d'intégrer trois paramètres appelés avec le script : le nom d'hôte du serveur centrale (ou son IP) et les identifiants de
# l'utilisateur pour la connexion ssh ????

def logo_acceuil():
    
    logo = [
        "              __________          __   __                   ",
        "              \______   \___ __ _/  |_|  |__   ____   ____  ",
        "               |     ___<   |  |\   __\  |  \ /  _ \ /    \ ",
        "               |    |    \___  | |  | |   Y  (  <_> )   |  \ ",
        "               |____|    / ____| |__| |___|  /\____/|___|  /",
        "                         \/                \/            \/"
    ]

    for line in logo:
        print(line)

def main():
    
    logo_acceuil()
    choix = "n"
    # Boucle de choix:
    while choix != "q":
        print("\n \033[34m1\033[0m : Rendre le pare-feu persistent,\n", "\033[34m2\033[0m : Rediriger les logs netfilter,\n", "\033[34m3\033[0m : Planifier la sauvegarde des logs \033[31m(nécessite d'être root ou sudoers)\033[0m,\n", "\033[34m4\033[0m : Déployer un script mis à jour,\n", "\033[34mQ\033[0m : Quitter,")
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
            transfert_journaux.main()
        elif choix == "4":
            print("\nJe downloade le script corrigé.\n")
            #transfert_mise_a_jour.main()
        elif choix == "q":
            print("\nJe quitte as soon as possible.\n")
        else:
            print("\nJe n'ai pas compris !!!\n")

main()