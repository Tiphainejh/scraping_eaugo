# Infos générales

Il faut veiller à ne pas modifier les fichiers présents dans le dossier!!
Le fichier contenant les produits doit s'appeler suivi.xlsx.

## Lancer le programme :

Cliquer sur le fichier "comparer.exe".
Le résultat est dans le fichier "comparaison_***.xlsx".

## Ajouter des produits

Ajouter le code GTIN et le code google shopping du produit dans le fichier code_shopping.xlsx.
Mettre le code google_shopping entre doubles quotes "".

## Ajouter un concurrent

Ajouter le nom exacte du vendeur qui apparait dans google shopping au fichier vendeurs.xlsx

## Si le programme ne se lance pas

Il est possible que ce soit du au fichier chromedriver.exe, s'il y a eu un mise à jour chrome.
Il faut télécharger la version correspondante au navigateur ici : https://chromedriver.chromium.org/downloads
et extraire le fichier chromedriver.exe pour remplacer celui du dossier.

# Infos développeurs

## Créer le fichier .exe
```python setup.py build```
