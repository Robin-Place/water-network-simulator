# Données et unités

Le réseau original comprend `connec2.txt`, `noeuds2.txt`, `debit2.txt` et `Diam2.txt`. Ils doivent rester ensemble dans le dossier donné à `--data-dir`.

- `connec2.txt` : deux lignes d'en-tête, puis deux indices de nœuds par canalisation, séparés par des espaces. Les indices commencent à 1 dans le fichier et sont convertis en indices commençant à 0.
- `noeuds2.txt` : deux lignes d'en-tête, puis `x`, `y`, `z` séparés par des tabulations. Les coordonnées sont utilisées en kilomètres dans la représentation interne ; les longueurs sont converties en mètres pour les calculs.
- `debit2.txt` : une ligne d'en-tête, puis un débit de consommation entier par nœud, en litres par seconde. Le débit de la source est recalculé.
- `Diam2.txt` : une ligne d'en-tête, puis un diamètre par canalisation, en centimètres. La lecture convertit ces valeurs en mètres.

L'ordre des diamètres correspond à celui des canalisations ; l'ordre des débits correspond à celui des nœuds. Le premier nœud est la source de charge imposée.

## Réseau de démonstration du projet

Les fichiers de `data/demo/` utilisent le format historique suffixé `0` : coordonnées séparées par des espaces et exprimées en mètres ; diamètres déjà exprimés en mètres. Les conversions à la lecture diffèrent donc du format suffixé `2`.

Les quatre fichiers sont ceux transmis par Robin PLACE pour le réseau de démonstration du projet. Ils contiennent six nœuds et sept canalisations, avec une consommation totale de **780 L/s** sur les cinq nœuds consommateurs.

Les fichiers fournis sont conservés sans modification. La première ligne numérique de `debit0.txt` indique un débit de source de −900 L/s ; ce débit est recalculé lors de la résolution à partir des consommations, soit −780 L/s à l'équilibre.

## Données originales

Le sujet et les données du projet ont été fournis par **Florent Prunier** dans le cadre du P2I à l'INSA Lyon. Robin PLACE a fourni les fichiers intégrés au dépôt. Les données conservent leurs conditions d'utilisation propres et sont exclues du périmètre MIT du code.

