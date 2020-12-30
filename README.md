# Archivage des journaux Netfilter

## Description: 
Ce projet, sous python 3.7, a pour but d’archiver les journaux issus du pare-feu Netfilter d’un serveur fonctionnant sur une distribution Debian-based. L’archivage est réalisé quotidiennement en compressant les différents fichiers contenant les logs de la veille et en les transférant vers une machine dédiée.

## Table des matières:  
  - [Fonctionnement:](#fonctionnement)
      - [- Rendre les règles Netfilter persistantes (module persistent.py)](#--rendre-les-règles-netfilter-persistantes-module-persistentpy)
      - [- Extraire les logs Netfilter et mettre en place une rotation des fichiers (module creation_journaux.py)](#--extraire-les-logs-netfilter-et-mettre-en-place-une-rotation-des-fichiers-module-creation_journauxpy)
      - [- Planifier et mettre en place un script d’archivage (module transfert_journaux.py)](#--planifier-et-mettre-en-place-un-script-darchivage-module-transfert_journauxpy)
      - [- La communication avec la machine dédiée au stockage des archives](#--la-communication-avec-la-machine-dédiée-au-stockage-des-archives)
  - [Installation](#installation)
  - [Utilisation](#utilisation)
  - [Prérequis](#prérequis)
  - [Version](#version)
  - [License](#license)

## Fonctionnement: 
   #### - Rendre les règles Netfilter persistantes (module persistent.py)
1. ***Sauvegarder les règles via IPtables:***  
Le premier objectif de ce module est de s’assurer que les règles du pare-feu sont sauvegardées :  
      * Vérifier la présence du fichier de sauvegarde,  
      * Si ce n’est pas le cas, télécharger une copie du fichier depuis la machine dédiée,  
      * Sinon, réaliser la sauvegarde des règles et transférer une copie sur la machine dédiée.
>La sauvegarde est effectuée avec la commande "iptables-save".  
>Elle est stockée en local dans le répertoire "/etc/init.d/".  
>Son nom est la combinaison du préfixe "sauvegarde_iptables_" et du nom de la machine ("hostname").
2. ***Mettre en place un daemon "Netfilter":***  
Le second objectif est de s’assurer qu’un démon s’exécute au démarrage et qu’il contient la liste des règles de logs à mettre en place :
      * Vérifier la présence du script ou téléchargement depuis la machine dédiée si besoin,
      * Comparer les règles existantes dans le script avec celles à mettre en place ; Mise à jour du script en cas de différence,
      * Dans le cas où le script ou la copie n’existent pas, créer le fichier à partir d’un template dans lequel sera ajouté la liste des règles à mettre en place ainsi que la commande restaurant les règles précédemment sauvegardées.
>Le script est stocké dans le répertoire "/etc/init.d/".  
>Son nom est la combinaison du préfixe "pare-feu_" et du nom de la machine ("hostname").  
>La liste des règles à mettre en place est insérée sous la ligne "# Commentaires" du template.  
>La commande de restauration des règles est insérée sous la ligne "# Restauration iptables" du template.  
>Elle est de la forme "iptables-restore < sauvegarde_iptables_$hostname".  
>La commande utilisée pour lancer le démon au démarrage est "update-rc.d" et son option "defaults".  
>Le fichier contenant le template du démon se trouve dans "doc/script_defaut.txt".  
>Le fichier contenant la liste des règles à définir se trouve dans "doc/regles.txt".
   #### - Extraire les logs Netfilter et mettre en place une rotation des fichiers (module creation_journaux.py)
1. ***Configurer rsyslog:***  
Le premier objectif de ce module est de s’assurer qu’un fichier conf pour rsyslog existe pour les logs de Netfilter :
      * Vérifier si le fichier existe,
      * Vérifier si les règles à définir sont déjà configurées,
      * Créer le fichier ou le mettre à jour le cas échéant.
>Le fichier conf est stocké dans le répertoire "/etc/rsyslog.d/".  
>Il se nomme "10-iptables.conf".  
>Les logs du pare-feu seront stocké dans le répertoire "/var/log/netfilter/".  
>Chaque règle de logs aura son propre fichier dont le nom est le préfixe défini.  
>Le service "rsyslog" est redémarré en cas de création ou de modification du fichier conf.  
>Le fichier contenant la liste des règles à définir se trouve dans "doc/regles.txt".
2. ***Configurer logrotate:***  
Le second objectif du module est de s’assurer qu’un fichier conf pour logrotate existe pour les logs de Netfilter :  
      * Vérifier si le fichier existe,  
      * Créer le fichier à partir d'un template le cas échéant.
>Le fichier conf est stocké dans le répertoire "/etc/logrotate.d/".  
>Il se nomme "netfilter.conf".  
>Le fichier contenant le template se trouve dans "doc/rotation.txt".
   #### - Planifier et mettre en place un script d’archivage (module transfert_journaux.py)
1. ***Configurer cron:***  
Le premier objectif de ce module est de s'assurer que l'exécution du script est programmé à 07H00 tous les jours :
      * Vérifier si le fichier crontab de root existe,  
      * Vérifier si le nom du script d'archivage est présent dans le fichier,  
      * Créer le fichier ou la tâche le cas échéant.
>Le fichier est stocké dans le répertoire "/var/spool/cron/crontabs/".  
>Le fichier se nomme "root".  
>La tâche exécute le fichier "archivage_logs_netfilter.sh".
2. ***Générer le script d'archivage:***  
Le second objectif est de s'assurer que le script d'archivage est présent :
      * Vérifier si le fichier existe,  
      * Vérifier si les informations de connexion à la machine dédiée sont correctes,  
      * Créer ou mettre à jour le fichier le cas échéant.
>Le fichier est stocké dans le répertoire "/root/".  
>Le fichier se nomme "archivage_logs_netfilter.sh".  
>Le script compresse tous les fichiers avec l'extension "*.1" dans le répertoire "/var/log/netfilter/".  
>Le nom de l'archive est de la forme "archive_$hostname-$date.tar.gz".  
>Le script déplace l'archive vers la machine dédiée dans un réperoire propre et un sous-répertoire composé du mois et de l'année en cours (exemple : "décembre2020/").  
>Le fichier contenant le template se trouve dans "doc/script_archivage.txt".
   #### - La communication avec la machine dédiée au stockage des archives
Les modules "persistent" et "transfert_journaux" utilisent le protocole SSH pour communiquer avec la machine dédiée à l'archivage des logs et des fichiers nécessaires au démon. Il est donc nécessaire de s'assurer que les clés id sont présentes :
   * Vérifier si les fichiers sont présents,  
   * Générer les fichiers, transférer la clé publique et définir la machine dédiée comme hôte connu le cas échéant.
>Les clés utilisent un chiffrement RSA de 4096 bits.  
>Elles sont stockés dans le répertoire "/root/.ssh/".  
>Elles se nomment "id_rsa_archivage" et "id_rsa_archivage.pub".  
>Les fichiers sont stockés sur la machine dédiée dans le répertoire "/Depot_netfilter/".  
>Chaque client dispose de son répertoire propre créé à partir de son nom ("hostname"), à l'intérieur du dépôt.

## Installation:  
1. ***Fichier zip:***  
Télécharger le projet sous la forme d'une archive .zip en cliquant [ici](https://github.com/Yanick-M/OpenClassroomsProjet6/archive/main.zip).  
Décompresser l'archive dans votre espace de travail.
2. ***Clonage du projet:***  
La deuxième option d'installation est de cloner le projet grâce à "git".  
Placer vous dans votre espace de travail au préalable ou dans le répertoire temporaire.  
```cd /tmp/
git clone https://github.com/Yanick-M/OpenClassroomsProjet6.git  
```
3. ***Déclaration de la librairie:***  
Il n'est pas nécessaire d'effectuer des modifications au niveau du système pour que python puisse accéder aux différents modules (que ce soit la variable "PYTHONPATH" ou dans "sys.path").  
Le script principal dispose d'une action qui insére le chemin complet dans "sys.path" si la librairie n'est pas accessible :  
```  
import os, argparse, getpass, subprocess  
try:  
    from libnetfilterlocal import persistent, creation_journaux, transfert_journaux  
except:  
    import sys  
    chemin = os.getcwd() + "/"  
    sys.path.insert(0, chemin)  
    from libnetfilterlocal import persistent  
```  
## Utilisation:  
1. ***Informations importantes:***  
Pour que cet outil fonctionne correctement, il ne faut pas modifier la structure des répertoires que ce soit en les déplaçant ou en les renommant.  
Il ne faut pas non plus renommé ou changer les extensions des différents fichiers.  
Si vous décidez d'effectuer des modifications, il faudra modifier le code en conséquence.
2. ***Effectuer vos réglages:***  
Le but de cet outil étant d'archiver le trafic spécifique d'une machine en fonction des services qu'elle héberge, il est donc obligatoire de modifier le fichier [regles.txt](https://github.com/Yanick-M/OpenClassroomsProjet6/tree/main/libnetfilterlocal/doc/regles.txt) dans le dossier "libnetfilterlocal/doc/". Le lien montre des exemples de règles pouvant être configurées. Pour pouvoir fonctionner correctement, une seule expression doit contenir des guillemets doubles ("double quote").  
Il est également possible de modifier le [template](https://github.com/Yanick-M/OpenClassroomsProjet6/blob/main/libnetfilterlocal/doc/script_defaut.txt) du démon mais il ne faut pas enlever ou modifier les lignes "# Commentaires" et "# Restauration iptables".  
Le [template]() de rotation des logs peut aussi être affiner. Par contre, l'archivage se fait uniquement sur l'ensemble des fichiers "iptables*.1" dans le répertoire "/var/log/netfilter/".
3. ***L'outil:***  

Affichage de l'aide :  
```  
./Netfilter_local.py -h  
```

Lancement de l'outil par défaut pour visualiser le menu ou "annuler des modifications" :  
```  
sudo ./Netfilter_local.py  
```

Exemple de lancement de l'outil pour exécuter des actions de déploiement :  
```  
sudo ./Netfilter_local.py --user yanick --host ServerCentral  
sudo ./Netfilter_local.py -U root -H 10.0.0.1  
```

Apparence du menu :

![alt text](https://github.com/Yanick-M/OpenClassroomsProjet6/blob/main/menu.png)

## Prérequis:  
* Créer le répertoire "/Depot_netfilter/" à la racine de la machine dédiée,
* Modifier le propriétaire de ce répertoire pour l'utilisateur servant à la connexion ssh,
* Le package "iptables" doit être installé et configuré sur le client,  
* Le package "rsyslogd" doit être installé sur le client,  
* Le package "tar" doit être installé sur le client,  
* Les packages "openssh-client" et "sshpass" doivent être installés sur le client,  
* Le package "openssh-server" doit être installé et configuré sur la machine dédiée,  
* Le package "rsync" doit être installé sur le client et la machine dédiée.

## Version:  
1.0 (finale)

## License:  
#### Copyright (c) 2020 [Yanick-M]
#### GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
