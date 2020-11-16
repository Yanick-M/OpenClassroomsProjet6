import os, shutil, sys, socket

# Définition des variables constantes
NOM_SCRIPT = "pare-feu_" + socket.gethostname() + ".sh"
NOM_IPTABLES = "sauvegarde_iptables_" + socket.gethostname()
NOM_REGLES = "regles.txt"
NOM_DEFAUT = "script_defaut.txt"
CHEMIN_SOURCE = os.getcwd() + "/"
CHEMIN_DESTINATION = "/etc/init.d/"
CHEMIN_DOCUMENTS = os.path.join(os.path.dirname(__file__), 'doc/')
BLOC_A = "# Commentaires"
BLOC_B = "# Restauration iptables"

#1. Les fonctions de recherche
def recherche_regles_log(regles_configurees):
    # L'objectif est de savoir si tous les commentaires désirés sont définis dans le script ou la sauvegarde iptables
    # Comparaison des listes pour voir si toutes les règles existent dans le script ou dans la sauvegarde iptables
    # Si elles existent, renvoi du résultat 'vrai'
    # Si absentes ou incomplètes, renvoi du résultat 'faux'
    print("-----vérification des règles de commentaires dans la configuration actuelle-----")
    regles_a_tester = lire_fichier(CHEMIN_DOCUMENTS, NOM_REGLES)

    # Si la lecture du fichier renvoie une liste vide, j'informe l'utilisateur et je quitte le script
    if not regles_a_tester:
        print("\033[31mLe fichier {} dans \"{}\" est manquant ou vide !\033[0m".format(NOM_REGLES, CHEMIN_DOCUMENTS))
        os._exit(0)

    # Déclaration du nombre de fois qu'une règle a été trouvé dans Netfilter
    #compteur = 0
    regles_a_definir = []
    
    # Lecture dans une première boucle des règles qui devraient être présentes sur le système
    print("-----comparaison des informations-----")
    for regle in regles_a_tester:
        regle_trouvee = False
        # Lecture dans une seconde boucle des règles actives sur le système
        for line in regles_configurees:
            # Comparaison d'une règle par rapport à une ligne à la fois
            if regle == line or regle[9:] == line:
                regle_trouvee = True
                break
        if regle_trouvee is False:
            #regles_a_definir.append(regles_a_tester[compteur])
            regles_a_definir.append(regle)
        #compteur +=1

    return(regles_a_definir)

def recherche_bloc(liste, bloc):
    print("-----recherche du bloc {}-----".format(bloc))
    # Définition du point de départ de la recherche
    position = 0
    # Lancement de la recherche dans la liste appelée grâce à une boucle
    for lines in liste:
        # Comparaison de la chaîne en cours de lecture avec la chaîne appelée avec la fonction
        if lines == bloc:
            # Si les chaînes sont égales, sortie de la boucle pour renvoyer la position
            break
        # Sinon, la position est incrémentée et la boucle continue
        position += 1
    return(position)

#2. Les fonctions de lecture
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

#3. Les fonctions de création
def sauvegarde_iptables(chemin, nom):
    print("-----sauvegarde d'iptables-----")
    # Génération de la commande bash à éxécuter pour réaliser la sauvegarde à partir des paramètres appelées avec la fonction
    commande = "sudo iptables-save > \"{}{}\"".format(chemin, nom)
    # Exécution de la commande de sauvegarde
    os.system(commande)

def creation_script():
    print("-----création du script-----")
    # Lecture du fichier contenant le script par défaut
    script = lire_fichier(CHEMIN_DOCUMENTS, NOM_DEFAUT)

    # Si la lecture du fichier renvoie une liste vide, j'informe l'utilisateur et je quitte le script
    if not script:
        print("\033[31mLe fichier contenant les règles par défaut est manquant !\033[0m")
        os._exit(0)

    # Je lance la comparaison entre le script et les règles
    regles_a_definir = recherche_regles_log(script)

    # Je cherche à quelle position dans le script se trouve l'emplacement des règles de commentaires à ajouter que j'incrémente de 1 pour la ligne suivante
    positionA = recherche_bloc(script, BLOC_A) + 1
    # Je lance l'ajout des règles manquantes dans la liste représentant le script
    script_temporaire = ajout_donnees_manquantes(script, positionA, regles_a_definir)

    # Je génére la commande qui va permettre de restaurer la configuration IPtables sans écraser les règles du bloc précédent dans le script
    commande = ["iptables-restore -n < \"" + CHEMIN_DESTINATION + NOM_IPTABLES + "\""]
    # Je cherche à quelle position dans le script se trouve l'emplacement de restauration iptables que j'incrémente de 1 pour la ligne suivante
    positionB = recherche_bloc(script_temporaire, BLOC_B) + 1
    # Je lance l'ajout de la commande de restauration dans la liste représentant le script
    script_definitif = ajout_donnees_manquantes(script_temporaire, positionB, commande)

    # génération d'un fichier contenant le script à partir de la liste "défaut" dans le répertoire courant
    ecrire_fichier(CHEMIN_SOURCE, NOM_SCRIPT, script_definitif)

def ajout_donnees_manquantes(liste, position, donnees):
    print("-----ajout de données manquantes dans le bloc-----")
    
    # ajout des donnèes manquantes à partir de la position obtenue
    for donnee in reversed(donnees):
        # début à la ligne suivante de la position du bloc
        liste.insert(position, donnee)

    return(liste)

def ecrire_fichier(chemin, nom, donnees):
    print("-----sauvegarde de données dans un fichier-----")

    # Essai d'ouverture en écriture du fichier dans lequel écrire des données
    # Si l'ouverture réussi, l'écriture est effectuée    
    try:
        with open(chemin + nom, "w") as fichier:
            for line in donnees:
                #line = line + "\n"
                fichier.write("{}\n".format(line))
    # Si l'ouverture échoue, j'informe l'utilisateur et je quitte le script
    except IOError:
        print("\033[31mLe fichier {} n'a pas pu être créer à l'emplacement {} !\033[0m".format(nom, chemin))
        os._exit(0)

#4. Les fonctions de déploiement
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
    
    return(emplacement_dst)
    
def mise_en_place_script(chemin_src, chemin_dst, nom):
    
    # Le script nécessite des droits d'exécution , puis permet la création et le démarrage d'un daemon donc une fonction spécifique par rapport au fichier IPtables
    # Mise en place du fichier dans le répertoire de destination
    emplacement_dst = mise_en_place_fichier(chemin_src, chemin_dst, nom)

    # Essai d'ajout du mod +x (exécutable) au propriétaire et son groupe
    # En cas d'erreur, exécution de la commande bash correspondante avec privilège
    st = os.stat(emplacement_dst)
    try:
        os.chmod(emplacement_dst, st.st_mode | 0o110)
    except:
        os.system('sudo chmod +x "{}"'.format(emplacement_dst))
    
    # Transformation du script en daemon
    # Pour le démarrage du daemon, j'enlève les lettres de l'extension du fichier et je rajoute service pour obtenir le nom exact du service
    os.system('sudo update-rc.d "{}" defaults'.format(nom))
    os.system('sudo systemctl start {}service'.format(nom[:-2]))

#5. Les fonctions de communication
def upload_fichier():
    pass

def download_fichier():
    pass

def main():
    # Rendre le pare-feu persistent et ajouter des commentaires dans les logs :
    # L'objectif de ce script est de s'assurer que Netfilter affiche les commentaires définis par les règles présentes dans le fichier
    # "regles" du sous-dossier "doc"
    objectif_atteint = False
    while objectif_atteint is not True:
        
        print("\033[34mJe cherche la sauvegarde IPtables...\033[0m")
        regles_iptables = lire_fichier(CHEMIN_DESTINATION, NOM_IPTABLES)
        while not regles_iptables:
            print("\033[34mJe lance la sauvegarde de Netfilter...\033[0m")
            sauvegarde_iptables(CHEMIN_SOURCE, NOM_IPTABLES)
            # Je sauvegarde le fichier sur le serveur distant
            # Je déploie le fichier dans le répertoire init.d
            mise_en_place_fichier(CHEMIN_SOURCE, CHEMIN_DESTINATION, NOM_IPTABLES)
            
            # Je relance la lecture
            regles_iptables = lire_fichier(CHEMIN_DESTINATION, NOM_IPTABLES)

        print("\033[34mJe cherche le script...\033[0m")
        regles_script = lire_fichier(CHEMIN_DESTINATION, NOM_SCRIPT)
        while not regles_script:
            print("\033[34mJe lance la création du script...\033[0m")
            creation_script()
            # Je sauvegarde le fichier sur le serveur distant
            # Je déploie le fichier dans le répertoire init.d
            mise_en_place_script(CHEMIN_SOURCE, CHEMIN_DESTINATION, NOM_SCRIPT)
            
            # Je relance la lecture
            regles_script = lire_fichier(CHEMIN_DESTINATION, NOM_SCRIPT)
        
            # Pour faciliter la comparaison, je fusionne les deux listes
        regles = regles_script + regles_iptables

        print("\033[34mJe lance la vérification de la présence des règles de commentaires...\033[0m")
        resultat = recherche_regles_log(regles)

        if not resultat:
            print("\033[32mNetfilter est persistent et les règles de commentaires sont configurées !\033[0m")
            objectif_atteint = True
        else:
            position = recherche_bloc(regles_script, BLOC_B) - 1
            script_definitif = ajout_donnees_manquantes(regles_script, position, resultat)
            ecrire_fichier(CHEMIN_SOURCE, NOM_SCRIPT, script_definitif)
            mise_en_place_script(CHEMIN_SOURCE, CHEMIN_DESTINATION, NOM_SCRIPT)
            # upload_fichier

if __name__ == '__main__':
    main()