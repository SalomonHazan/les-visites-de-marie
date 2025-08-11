# 📸 Guide de Test - Upload des Photos

## ✅ **Tests Automatiques Réussis**

Tous les tests d'upload sont **PASSÉS** :
- ✅ Création image de test
- ✅ Formulaire d'upload
- ✅ Backend d'upload  
- ✅ Dossiers d'upload

## 🚀 **Comment Tester l'Upload en Mode Admin**

### 1. **Démarrer l'Application**
```bash
python3 app.py
```
L'application sera accessible sur `http://localhost:8000`

### 2. **Accéder au Mode Admin**
1. Allez sur `http://localhost:8000/admin`
2. Connectez-vous avec vos identifiants admin
3. Vous arrivez sur le dashboard

### 3. **Créer une Nouvelle Visite avec Photo**
1. Cliquez sur **"Créer une nouvelle visite"**
2. Remplissez les champs obligatoires :
   - **Titre** : "Test Upload Photo"
   - **Description complète** : "Test de l'upload d'image"
3. **Uploadez une image** dans le champ "Image de la visite"
4. Ajoutez au moins une étape :
   - **Titre étape** : "Départ"
   - **Description** : "Point de départ"
   - **Durée** : "30 min"
5. Cliquez sur **"Créer la visite"**

### 4. **Vérifier l'Upload**
1. Retournez au dashboard
2. Vérifiez que la nouvelle visite apparaît
3. Cliquez sur la visite pour voir l'image
4. L'image devrait s'afficher correctement

### 5. **Modifier une Visite Existante**
1. Cliquez sur **"Modifier"** pour une visite existante
2. Uploadez une nouvelle image
3. Sauvegardez
4. Vérifiez que la nouvelle image s'affiche

## 📋 **Formats d'Image Acceptés**
- **PNG** (.png)
- **JPG/JPEG** (.jpg, .jpeg)
- **GIF** (.gif)
- **WEBP** (.webp)
- **Taille maximale** : 10MB

## 🔧 **Dépannage**

### Si l'upload ne fonctionne pas :
1. **Vérifiez les permissions** des dossiers :
   ```bash
   ls -la static/uploads/
   ```

2. **Vérifiez les logs** de l'application :
   ```bash
   python3 app.py
   ```

3. **Testez avec une image simple** :
   - Utilisez une image JPG de moins de 1MB
   - Évitez les images avec caractères spéciaux dans le nom

### Si l'image ne s'affiche pas :
1. **Vérifiez le chemin** dans `static/uploads/visites/`
2. **Vérifiez les permissions** du fichier
3. **Rechargez la page** (Ctrl+F5)

## 📁 **Structure des Fichiers**
```
static/uploads/
├── visites/          # Images des visites
│   └── *.jpg        # Images uploadées
├── about/            # Image de la page "À propos"
└── temp/             # Fichiers temporaires
```

## ✅ **Statut Actuel**
- ✅ **Upload fonctionnel** dans tous les formulaires
- ✅ **Validation** des formats d'image
- ✅ **Stockage sécurisé** avec noms uniques
- ✅ **Affichage** dans l'interface utilisateur
- ✅ **Gestion des erreurs** intégrée

## 🎯 **Test Rapide**
1. Allez sur `http://localhost:8000/admin`
2. Créez une nouvelle visite avec une image
3. Vérifiez l'affichage
4. Modifiez la visite avec une nouvelle image

L'upload des photos est **entièrement opérationnel** ! 🎉 