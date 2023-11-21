                                                                                
                                                                                
                                                                                
                                                                                
                                                 #&%,                           
                                                 &  &       .&@.                
                                    .% ,%        &  &      %* %*                
                                      &* %(      & ,&     %  &                  
                                       .& ,# /&&%(((#%%%*%#%#       ,&&.        
                             &. #&/      (&               ,&*    %&  *&*        
                               /%(  ,& %/                    ##% ,&(            
                               (%%%%%%&                        &                
                           ##            #&                     &               
                         &*                .%                   #,%&&&&%&&%     
              .%&%%&%&%.&                    &                  %.#%&&&&&%&     
          %%                                 ,%                ,%               
        %                                    *%%&/.*#&%#      *%,%              
      #/                                                 *%.,%..&*  (&(         
     /#                                                    .&      ,%% *%       
     %.                                                      %                  
     %,                                                      %(%                
      #                                                      %, &               
       %.                                                  .%                   
         %*                                               %,                    
            #&(.                                      *%%   --  STATION-MÉTÉO
# Documentation du Projet

## Introduction

Bienvenue dans la documentation du projet station-meteo. Cette documentation fournit des informations sur la structure du projet, les fonctionnalités principales, les dépendances, et les instructions pour l'installation et la configuration.

## Structure du Projet

Le projet Django station-meteo suit une structure conventionnelle recommandée pour les projets Django. Voici une vue d'ensemble des principaux répertoires et fichiers :

- api
  - admin.py
  - api.py
  - apps.py
  - __init__.py
  - migrations
    - __init__.py
  - models.py
  - script.py
  - tests.py
  - views.py
- app
  - admin.py
  - apps.py
  - forms.py
  - __init__.py
  - migrations
    - 0001_initial.py
    - 0002_remove_user_creation_date_remove_user_password_and_more.py
    - __init__.py
  - models.py
  - templates
    - base.html
    - history.html
    - home.html
  - tests.py
  - views.py
- db.sqlite3
- manage.py
- station_meteo
  - asgi.py
  - __init__.py
  - settings.py
  - urls.py
  - wsgi.py

- **api**: Contient les appels vers le web-sevice et l'auto-insertion des données en base de données.
- **app**: Contient la partie logique de l'application. L'affichage des graphique et des tables.
- **manage.py**: Script de gestion de Django pour diverses tâches.

## Installation

1. Clonez le dépôt depuis GitHub :

   ```bash
   git clone https://github.com/barthelemy-lebel/station-meteo.git
2. Installez les dépendances requises :
    ```bash
    pip install -r requirements.txt
3. Appliquez les migrations de la base de données :
    ```bash
    python manage.py migrate

## Conventions de Codage PEP 8

Le code Python suit les directives de style PEP 8. Assurez-vous de respecter ces conventions pour garantir une cohérence dans le code.
Docstrings

Chaque module, classe, et fonction doit être documenté à l'aide de docstrings conformes aux directives de PEP 257.
Nommage

- Utilisez des noms significatifs pour les variables, fonctions, classes, etc.
- Suivez la convention snake_case pour les noms de variables et de fonctions.
- Suivez la convention CamelCase pour les noms de classes.
- Ajoutez des commentaires explicatifs lorsque nécessaire pour expliquer des sections complexes ou des décisions de conception.

### Contributions
Les contributions sont les bienvenues! Veuillez consulter le fichier CONTRIBUTING.md pour plus d'informations sur la manière de contribuer au projet.
