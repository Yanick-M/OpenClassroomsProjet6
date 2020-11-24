import os, shutil, sys, socket, stat, argparse, getpass

# Définition des variables constantes
NOM_SCRIPT = "pare-feu_" + socket.gethostname() + ".sh"
NOM_IPTABLES = "sauvegarde_iptables_" + socket.gethostname()
NOM_REGLES = "regles.txt"
NOM_DEFAUT = "script_defaut.txt"
CHEMIN_DESTINATION = "/etc/init.d/"
CHEMIN_DOCUMENTS = os.path.join(os.path.dirname(__file__), 'doc/')
BLOC_A = "# Commentaires"
BLOC_B = "# Restauration iptables"

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

def recherche_regles_log(regles_configurees):
    
    # L'objectif est de savoir si tous les commentaires désirés sont définis dans le script ou la sauvegarde iptables
    # Comparaison des listes pour voir si toutes les règles existent dans le script ou dans la sauvegarde iptables
    # Si elles existent, renvoi du résultat 'vrai'
    # Si absentes ou incomplètes, renvoi du résultat 'faux'
    print("-----vérification des règles de commentaires dans la configuration actuelle-----")
    
    try:    
        regles_a_tester = lecture_fichier(CHEMIN_DOCUMENTS, NOM_REGLES)
    except FichierNonTrouve as exc:
    # Si la lecture du fichier renvoie une liste vide, j'informe l'utilisateur et je quitte le script
        raise Erreur.fichier_absent(FichierNonTrouve, CHEMIN_DOCUMENTS, NOM_REGLES)
    except EchecLecture:
        raise Erreur.privileges(EchecLecture)

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
    
    if not regles_a_definir:
        raise RechercheVide

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

def ecriture_fichier(chemin, nom, donnees):
    
    print("-----sauvegarde de données dans un fichier-----")

    # Essai d'ouverture en écriture du fichier dans lequel écrire des données
    # Si l'ouverture réussi, l'écriture est effectuée    
    try:
        with open(chemin + nom, "w") as fichier:
            for line in donnees:
                fichier.write("{}\n".format(line))
    # Si l'ouverture échoue, l'utilisateur est informé et l'exécution du script se termine
    except IOError:
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

def mise_en_place_script(chemin_dst, nom):
    
    # Le script nécessite des droits d'exécution , puis permet la création et le démarrage d'un daemon donc une fonction spécifique par rapport au fichier IPtables
    # Mise en place du fichier dans le répertoire de destination
    droits = stat.S_IRUSR|stat.S_IXUSR
    mise_en_place_fichier(chemin_dst, nom, droits)

    # Transformation du script en daemon
    # Pour le démarrage du daemon, j'enlève les lettres de l'extension du fichier et je rajoute service pour obtenir le nom exact du service
    os.system('sudo update-rc.d "{}" defaults'.format(nom))
    os.system('sudo systemctl start {}service'.format(nom[:-2]))

def sauvegarde_iptables(chemin, nom):
    print("-----sauvegarde d'iptables-----")
    # Exécution de la commande pour réaliser la sauvegarde à partir des paramètres appelées avec la fonction
    os.system("/usr/sbin/iptables-save > \"{}{}\"".format(chemin, nom))

def ajout_donnees_manquantes(liste, position, donnees):
    print("-----ajout de données manquantes dans le bloc-----")
    
    # ajout des donnèes manquantes à partir de la position obtenue
    for donnee in reversed(donnees):
        # début à la ligne suivante de la position du bloc
        liste.insert(position, donnee)

    return(liste)

def creation_script():
    
    print("-----création du script-----")
    
    # Essai de lecture du fichier contenant le script par défaut
    try:
        script = lecture_fichier(CHEMIN_DOCUMENTS, NOM_DEFAUT)
    except FichierNonTrouve as exc:
        raise Erreur.fichier_absent(FichierNonTrouve, CHEMIN_DOCUMENTS, NOM_DEFAUT)
    except EchecLecture as exc:
        raise Erreur.privileges(EchecLecture)

    # Comparaison entre les règles existantes et les règles souhaitées pour obtenir les règles manquantes à définir
    regles_a_definir = recherche_regles_log(script)

    # Recherche de la position dans le script où se trouve l'emplacement des règles de commentaires à ajouter et incrémentation pour la ligne suivante
    positionA = recherche_bloc(script, BLOC_A) + 1
    # Ajout des règles manquantes dans la liste représentant le script
    script_temporaire = ajout_donnees_manquantes(script, positionA, regles_a_definir)

    # Génération de la commande qui va permettre de restaurer la configuration IPtables sans écraser les règles du bloc précédent dans le script
    commande = "iptables-restore -n < \"" + CHEMIN_DESTINATION + NOM_IPTABLES + "\""
    # Recherche de la position dans le script se trouve l'emplacement de restauration iptables et incrémentation pour la ligne suivante
    positionB = recherche_bloc(script_temporaire, BLOC_B) + 1
    # Ajout de la commande de restauration dans la liste représentant le script
    script_definitif = ajout_donnees_manquantes(script_temporaire, positionB, commande)

    # Création d'un fichier contenant le script à partir de la liste "défaut" dans le répertoire courant
    try:
        ecriture_fichier(CHEMIN_DESTINATION, NOM_SCRIPT, script_definitif)
    except EchecEcriture as exc:
        raise Erreur.ecriture_impossible(EchecEcriture,CHEMIN_DESTINATION, NOM_SCRIPT)

def upload_fichier():
    pass

def download_fichier():
    pass

def iptables():

    # Essai de lecture du ficher contenant la sauvegarde dans le répertoire init.d/
    try:
        regles_iptables = lecture_fichier(CHEMIN_DESTINATION, NOM_IPTABLES)
        return(regles_iptables)
    # S'il n'existe pas, lancement de la sauvegarde des règles
    except FichierNonTrouve:
        sauvegarde_iptables(CHEMIN_DESTINATION, NOM_IPTABLES)
    # S'il n'est pas accessible, l'utilisateur est informé et l'exécution du script se termine 
    except EchecLecture:
        raise Erreur.privileges(EchecLecture)


def daemon():

    # Essai de lecture du script qui génére le daemon dans init.d/
    try:
        regles_script = lecture_fichier(CHEMIN_DESTINATION, NOM_SCRIPT)
        try:
            regles_iptables = lecture_fichier(CHEMIN_DESTINATION, NOM_IPTABLES)
            regles = regles_script + regles_iptables   
            try:
                resultat = recherche_regles_log(regles)
                position = recherche_bloc(regles_script, BLOC_B) - 1
                script_definitif = ajout_donnees_manquantes(regles_script, position, resultat)
                ecriture_fichier(CHEMIN_DESTINATION, NOM_SCRIPT, script_definitif)
                mise_en_place_script(CHEMIN_DESTINATION, NOM_SCRIPT)
                # upload_fichier
            except RechercheVide:
                pass
        except FichierNonTrouve as exc:
            raise Erreur.erreurfatale(FichierNonTrouve)
        except EchecLecture as exc:
            raise Erreur.privileges(EchecLecture)
    except FichierNonTrouve as exc:
        creation_script()
        mise_en_place_script(CHEMIN_DESTINATION, NOM_SCRIPT)
        # upload_fichier
    except EchecLecture as exc:
        raise Erreur.privileges(EchecLecture)

def main():
    # Rendre le pare-feu persistent et ajouter des commentaires dans les logs :
    # L'objectif de ce script est de s'assurer que Netfilter affiche les commentaires définis par les règles présentes dans le fichier
    # "regles" du sous-dossier "doc"
    
    # Lancement de la tâche de sauvegarde des règles du pare-feu
    iptables()
    # Lancement de la tâche de génération du script permettant la mise en place du daemon
    daemon()

if __name__ == '__main__':
    
    try:
        verif_privileges()
    except EchecEcriture:
        raise Erreur.privileges(EchecEcriture)

    # # Traitement des arguments
    # parser = argparse.ArgumentParser ()
    # parser.add_argument ( "-U", "--user", help = "indiquez un nom d'utilisateur pour la connexion SSH" )
    # parser.add_argument ( "-H", "--host", help = "Indiquez un nom de la machine à contacter pour la connexion SSH" )
    # args = parser.parse_args ()
    # if not args.user or not args.host :
    #     print("Les arguments user et host n'ont pas été appelés. Ajoutez -h pour obtenir de l'aide.")
    #     os._exit(0)
    
    # # Demande sécurisée du mot de passe de l'utilisateur pour la connexion ssh
    # try: 
    #     password = getpass.getpass(prompt="Quel est le mot de passe de l'utilisateur pour la connexion ssh ?") 
    # except: 
    #     print("Problème détecté avec la saisie du mot de passe")
    #     os._exit(0)
    # main(args.user, args.host, password)