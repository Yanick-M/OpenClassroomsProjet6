import os, shutil, sys, socket

# Définition des variables constantes
NOM_SCRIPT = "pare-feu_" + socket.gethostname() + ".sh"
NOM_IPTABLES = "sauvegarde_iptables_" + socket.gethostname()
NOM_REGLES = "regles.txt"
CHEMIN_SOURCE = os.getcwd() + "/"
CHEMIN_DESTINATION = "/etc.init.d/"
CHEMIN_REGLES = CHEMIN_SOURCE + "doc/"

#1. Les fonctions de recherche
def recherche_fichier(chemin, nom):
    # Pour vérifier la présence d'un fichier, tentative d'ouverture en lecture
    # S'il s'ouvre, c'est qu'il est présent, renvoi du résultat 'vrai'
    # Si la tentative de lecture retourne une erreur, c'est qu'il n'existe pas, renvoi du résultat 'faux'
    print("-----recherche d'un fichier-----")
    fichier = chemin + nom
    try:
        with open(fichier, "r"):
            resultat = True
    except IOError:
        resultat = False
    return(resultat)

def recherche_regles_log(regles_configurees):
    # L'objectif est de savoir si tous les commentaires désirés sont définis dans le script ou la sauvegarde iptables
    # Comparaison des listes pour voir si toutes les règles existent dans le script ou dans la sauvegarde iptables
    # Si elles existent, renvoi du résultat 'vrai'
    # Si absentes ou incomplètes, renvoi du résultat 'faux'
    print("-----vérification des règles de commentaires dans la configuration actuelle-----")
    resultat = lire_fichier(CHEMIN_REGLES, NOM_REGLES)
    regles_a_tester = resultat[1]

    # Déclaration du nombre de fois qu'une règle a été trouvé dans Netfilter
    compteur = 0
    regles_a_definir = []
    
    # Lecture dans une première boucle des règles qui doivent être présentes sur le système
    for regle in regles_a_tester:
        regle_trouvee = False
        # Lecture dans une seconde boucle des règles actives sur le système
        for line in regles_configurees:
            # Comparaison d'une règle par rapport à une ligne à la fois
            if regle == line or regle[9:] == line:
                regle_trouvee = True
                break
        if regle_trouvee is False:
            regles_a_definir.append(regles_a_tester[compteur])
        compteur +=1

    return(regles_a_definir)

#2. Les fonctions de lecture
def lire_fichier(chemin, nom):
    return()

#3. Les fonctions de création
def sauvegarde_iptables():
    pass

def creation_script():
    pass

def ajout_regles_manquantes(regles_manquantes):
    pass

#4. Les fonctions de déploiement
def mise_en_place_fichier(chemin_src, chemin_dst, nom):
    # Génération de l'emplacement source
    emplacement_src = chemin_src + nom
    # Génération de l'emplacement de destination
    emplacement_dst = chemin_dst + nom
    # Copie du fichier de son emplacement actuel vers sa destination
    try:
        shutil.copyfile(emplacement_src, emplacement_dst)
    except PermissionError:
        os.system('sudo cp "{}" "{}"'.format(emplacement_src, emplacement_dst))
    # Modification du propriétaire du script
    user = 'root'
    group = 'root'
    try:
        os.chown(emplacement_dst, user, group)
    except:
        os.system('sudo chown {}:{} "{}"'.format(user, group, emplacement_dst))
    return(emplacement_dst)
    
def mise_en_place_script(chemin_src, chemin_dst, nom):
    emplacement_dst = mise_en_place_fichier(chemin_src, chemin_dst, nom)
    # Ajout du mod +x (exécutable) au propriétaire et son groupe
    st = os.stat(emplacement_dst)
    try:
        os.chmod(emplacement_dst, st.st_mode | 0o110)
    except:
        os.system('sudo chmod +x "{}"'.format(emplacement_dst))
    # Transformation du script en daemon
    os.system('sudo update-rc.d "{}" defaults'.format(nom))

#5. Les fonctions de communication

def upload_fichier():
    pass

def download_fichier():
    pass



                            # Rendre le pare-feu persistent et ajouter des commentaires dans les logs :
# L'objectif de ce script est de s'assurer que Netfilter affiche les commentaires définis par les règles présentes dans le fichier regles dans le dossier doc
objectif_atteint = False
while objectif_atteint is not True:
    
    regles_script = lire_fichier(CHEMIN_DESTINATION, NOM_SCRIPT)
    while regles_script[0] is not True:
        print("Je lance la création du script...")
        creation_script()
        # Je sauvegarde le fichier sur le serveur distant
        # Je déploie le fichier dans le répertoire init.d
        mise_en_place_script(CHEMIN_SOURCE, CHEMIN_DESTINATION, NOM_SCRIPT)
        
        # Je relance la lecture
        regles_script = lire_fichier(CHEMIN_DESTINATION, NOM_SCRIPT)
    
    regles_iptables = lire_fichier(CHEMIN_DESTINATION, NOM_IPTABLES)
    while regles_iptables[0] is not True:
        print("Je lance la sauvegarde de Netfilter...")
        sauvegarde_iptables()
        # Je sauvegarde le fichier sur le serveur distant
        # Je déploie le fichier dans le répertoire init.d
        mise_en_place_fichier(CHEMIN_SOURCE, CHEMIN_DESTINATION, NOM_IPTABLES)
        
        # Je relance la lecture
        regles_iptables = lire_fichier(CHEMIN_DESTINATION, NOM_IPTABLES)
    
    # Pour faciliter la comparaison, je fusionne les deux listes
    regles = regles_script[1], regles_iptables[1]

    print("Je lance la vérification de la présence des règles de commentaires...")
    resultat = recherche_regles_log(regles)

    if not resultat:
        print("Les règles de commentaires sont configurées !")
        objectif_atteint = True
    else:
        ajout_regles_manquantes(resultat)