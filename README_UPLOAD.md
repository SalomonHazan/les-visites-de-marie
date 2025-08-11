# Système d'Upload d'Images - Les Visites de Marie

## Vue d'ensemble

Le système d'upload d'images permet aux administrateurs d'importer et de gérer des photos pour les visites et la page "À propos" directement depuis l'interface d'administration.

## Fonctionnalités

### ✅ Fonctionnalités implémentées

1. **Upload d'images pour les visites**
   - Formats supportés : PNG, JPG, JPEG, GIF, WEBP
   - Taille maximale : 10MB
   - Stockage sécurisé avec noms de fichiers uniques
   - Suppression automatique des anciennes images lors de la mise à jour

2. **Upload d'image pour la page "À propos"**
   - Même système de validation et de stockage
   - Prévisualisation de l'image actuelle
   - Remplacement sécurisé des images

3. **Sécurité**
   - Validation des types de fichiers
   - Noms de fichiers sécurisés
   - Limitation de la taille des fichiers
   - Suppression automatique des fichiers orphelins

4. **Interface utilisateur**
   - Champs de fichiers stylisés
   - Prévisualisation des images actuelles
   - Messages d'erreur informatifs
   - Support des URLs externes en alternative

## Structure des dossiers

```
static/
├── uploads/
│   ├── visites/     # Images des visites
│   ├── about/       # Images de la page "À propos"
│   └── temp/        # Fichiers temporaires (si nécessaire)
```

## Utilisation

### Pour les visites

1. **Créer une nouvelle visite**
   - Allez dans l'administration
   - Cliquez sur "Créer une nouvelle visite"
   - Utilisez le champ "Image de la visite" pour uploader une image
   - Ou utilisez le champ "URL de l'image" pour une URL externe

2. **Modifier une visite existante**
   - Allez dans l'administration
   - Cliquez sur "Modifier" pour une visite
   - L'image actuelle est affichée en prévisualisation
   - Uploadez une nouvelle image ou modifiez l'URL

### Pour la page "À propos"

1. **Modifier l'image de Marie**
   - Allez dans "Configuration du site"
   - Section "Configuration de la page 'À propos'"
   - Utilisez le champ "Image de Marie" pour uploader une image
   - L'image actuelle est affichée en prévisualisation

## Fonctions techniques

### Fonctions principales

- `allowed_file(filename)` : Vérifie si l'extension du fichier est autorisée
- `save_uploaded_file(file, folder)` : Sauvegarde un fichier uploadé
- `delete_file(file_path)` : Supprime un fichier du système
- `get_file_size_mb(file_path)` : Retourne la taille d'un fichier en MB

### Configuration

```python
# Formats autorisés
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Taille maximale (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

# Dossier d'upload
UPLOAD_FOLDER = 'static/uploads'
```

## Sécurité

### Mesures de sécurité implémentées

1. **Validation des types de fichiers**
   - Seuls les formats d'image sont acceptés
   - Vérification des extensions de fichiers

2. **Sécurisation des noms de fichiers**
   - Utilisation de `secure_filename()` de Werkzeug
   - Génération d'identifiants uniques pour éviter les conflits

3. **Limitation de la taille**
   - Taille maximale de 10MB par fichier
   - Configuration au niveau de Flask

4. **Nettoyage automatique**
   - Suppression des anciennes images lors de la mise à jour
   - Suppression des images lors de la suppression de visite

## Maintenance

### Nettoyage des fichiers

Les fichiers uploadés sont automatiquement gérés par le système :
- Suppression lors de la mise à jour d'image
- Suppression lors de la suppression de visite
- Pas de fichiers orphelins

### Sauvegarde

Les fichiers uploadés sont stockés dans `static/uploads/` et ne sont pas inclus dans le contrôle de version (voir `.gitignore`).

## Support

Pour toute question ou problème avec le système d'upload, consultez les logs de l'application ou contactez l'administrateur. 