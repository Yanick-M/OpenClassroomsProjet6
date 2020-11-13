# OpenClassroomsProjet6

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

![alt text](https://whiterivernow.com/wp-content/uploads/2018/12/Under-Construction-Sign.png)
