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
>La commande utilisée pour lancer le démon au démarrage est "update-rc.d" et son options "defaults".
### - Extraire les logs Netfilter et mettre en place une rotation des fichiers (module creation_journaux.py)
1. Configurer rsyslog  
Le premier objectif de ce module est de s’assurer qu’un fichier conf pour rsyslog existe pour les logs de Netfilter :
      * S’il existe, seules les règles manquantes seront ajoutées. Le contenu du fichier sera comparé à la liste des règles de logs à définir,
      * S’il n’existe pas, il sera créé à partir de la liste.
>Le fichier conf est stocké dans le répertoire "/etc/rsyslog.d/".
>Il se nomme "10-iptables.conf".
>Les logs du pare-feu seront stocké dans le répertoire "/var/log/netfilter".
>Chaque règle de logs aura son propre fichier dont le nom est le préfixe défini.
>Le service "rsyslog" est redémarré en cas de création ou de modification du fichier conf.
2. Configurer logrotate  
Le second objectif du module est de s’assurer qu’un fichier conf pour logrotate existe pour les logs de Netfilter.  
Dans le cas où le fichier est absent, il est créé à partir d’un template.
>Le fichier conf est stocké dans le répertoire "/etc/logrotate.d/".  
>Il se nomme "netfilter.conf"
### - Planifier et mettre en place un script d’archivage (module transfert_journaux.py)
1. Configurer cron  
2. Générer le script d'archivage  
### - La communication avec la machine dédiée au stockage des archives

•	Installation: Installation is the next section in an effective README. Tell other users how to install your project locally. Optionally, include a gif to make the process even more clear for other people.
•	Utilisation: The next section is usage, in which you instruct other people on how to use your project after they’ve installed it. This would also be a good place to include screenshots of your project in action.
•	Credits: Include a section for credits in order to highlight and link to the authors of your project.
•	License: Finally, include a section for the license of your project. For more information on choosing a license, check out GitHub’s licensing guide!
