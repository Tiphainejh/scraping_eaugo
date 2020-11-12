# Infos générales

Il faut veiller à ne pas modifier les fichiers présents dans le dossier!!

## Lancer le programme :

Cliquer sur le fichier "comparer.exe"
Le résultat est dans le fichier "comparaison_***.xlsx"

## Ajouter un produit

Modifier le fichier json : Sur le site https://jsoneditoronline.org/, mettre copier le fichier dans la section "code" puis cliquer sur la section "tree" pour voir l'arborescence.

## Ajouter un concurrent

Les fonctions à modifier sont les fonctions ```get_uniform_price()``` et ```get_price()```. Il faut aussi penser à modifier la clé ```nb_stores``` dans le dictionnaire  ```category```.

# Infos développeurs

Créer le fichier .exe :
```python setup.py build```