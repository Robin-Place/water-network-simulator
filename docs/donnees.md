# Données et unités

Le réseau original comprend `connec2.txt`, `noeuds2.txt`, `debit2.txt` et `Diam2.txt`. Ils doivent rester ensemble dans le dossier donné à `--data-dir`.

- `connec2.txt` : deux lignes d'en-tête, puis deux indices de nœuds par canalisation, séparés par des espaces. Les indices commencent à 1 dans le fichier et sont convertis en indices commençant à 0.
- `noeuds2.txt` : deux lignes d'en-tête, puis `x`, `y`, `z` séparés par des tabulations. Les coordonnées sont utilisées en kilomètres dans la représentation interne ; les longueurs sont converties en mètres pour les calculs.
- `debit2.txt` : une ligne d'en-tête, puis un débit de consommation entier par nœud, en litres par seconde. Le débit de la source est recalculé.
- `Diam2.txt` : une ligne d'en-tête, puis un diamètre par canalisation, en centimètres. La lecture convertit ces valeurs en mètres.

L'ordre des diamètres correspond à celui des canalisations ; l'ordre des débits correspond à celui des nœuds. Le premier nœud est la source de charge imposée.

## Exemple autonome

Les fichiers de `data/demo/` utilisent le format historique suffixé `0` : coordonnées séparées par des espaces et exprimées en mètres ; diamètres déjà exprimés en mètres. Les conversions à la lecture diffèrent donc du format suffixé `2`.

Le réseau synthétique contient quatre nœuds, cinq canalisations et une consommation totale de 30 L/s. Il a été créé pour rendre le dépôt directement essayable. Il ne doit pas être présenté comme le réseau original du projet ou comme un résultat expérimental.

## Données originales

Les données originales ont été ajoutées au dépôt par Robin PLACE. La source initiale et les éventuelles conditions de redistribution restent à documenter.

