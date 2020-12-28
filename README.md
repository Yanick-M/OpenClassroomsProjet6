![alt text](https://whiterivernow.com/wp-content/uploads/2018/12/Under-Construction-Sign.png)

# Archivage des journaux Netfilter

## Description: 
Ce projet, sous python 3.7, a pour but d’archiver les journaux issus du pare-feu Netfilter d’un serveur fonctionnant sur une distribution Debian-based. L’archivage est réalisé quotidiennement en compressant les différents fichiers contenant les logs de la veille et en les transférant vers une machine dédiée.

## Fonctionnement: 
   ### - Rendre les règles Netfilter persistantes (module persistent.py)
1. Sauvegarder les règles via IPtables  
Le premier objectif de ce module est de s’assurer que les règles du pare-feu sont sauvegardées :  
      * Vérifier la présence du fichier de sauvegarde,  
      * Si ce n’est pas le cas, télécharger une copie du fichier depuis la machine dédiée,  
      * Sinon, réaliser la sauvegarde des règles et transférer une copie sur la machine dédiée.
>La sauvegarde est effectuée avec la commande "iptables-save".  
>Elle est stockée en local dans le répertoire "/etc/init.d/".  
>Son nom est la combinaison du préfixe "sauvegarde_iptables_" et du nom de la machine ("hostname").
2. Mettre en place un daemon "Netfilter"  
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
   ### - Extraire les logs Netfilter et mettre en place une rotation des fichiers (module creation_journaux.py)
1. Configurer rsyslog  
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
2. Configurer logrotate  
Le second objectif du module est de s’assurer qu’un fichier conf pour logrotate existe pour les logs de Netfilter :  
      * Vérifier si le fichier existe,  
      * Créer le fichier à partir d'un template le cas échéant.
>Le fichier conf est stocké dans le répertoire "/etc/logrotate.d/".  
>Il se nomme "netfilter.conf".  
>Le fichier contenant le template se trouve dans "doc/rotation.txt".
   ### - Planifier et mettre en place un script d’archivage (module transfert_journaux.py)
1. Configurer cron  
Le premier objectif de ce module est de s'assurer que l'exécution du script est programmé à 07H00 tous les jours :
      * Vérifier si le fichier crontab de root existe,  
      * Vérifier si le nom du script d'archivage est présent dans le fichier,  
      * Créer le fichier ou la tâche le cas échéant.
>Le fichier est stocké dans le répertoire "/var/spool/cron/crontabs/".  
>Le fichier se nomme "root".  
>La tâche exécute le fichier "archivage_logs_netfilter.sh".
2. Générer le script d'archivage  
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
   ### - La communication avec la machine dédiée au stockage des archives  
   Les modules "persistent" et "transfert_journaux" utilisent le protocole SSH pour communiquer avec la machine dédiée à l'archivage des logs et des fichiers nécessaires au démon. Il est donc nécessaire de s'assurer que les clés id sont présentes :
   * Vérifier si les fichiers sont présents,  
   * Générer les fichiers, transférer la clé publique et définir la machine dédiée comme hôte connu le cas échéant.
>Les clés utilisent un chiffrement RSA de 4096 bits.  
>Elles sont stockés dans le répertoire "/root/.ssh/".  
>Elles se nomment "id_rsa_archivage" et "id_rsa_archivage.pub".  
>Les fichiers sont stockés sur la machine dédiée dans le répertoire "/Depot_netfilter/".  
>Chaque client dispose de son répertoire propre créé à partir de son nom ("hostname"), à l'intérieur du dépôt.

## Installation:  
Installation is the next section in an effective README. Tell other users how to install your project locally. Optionally, include a gif to make the process even more clear for other people.

## Utilisation:  
The next section is usage, in which you instruct other people on how to use your project after they’ve installed it. This would also be a good place to include screenshots of your project in action.

## Credits:  
Include a section for credits in order to highlight and link to the authors of your project.

## Version:  
1.0 (finale)

## License:  
Finally, include a section for the license of your project. For more information on choosing a license, check out GitHub’s licensing guide!
