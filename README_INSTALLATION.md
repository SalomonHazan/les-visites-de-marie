# 📋 Guide d'Installation et d'Utilisation - Les Visites de Marie

## 🎯 Prérequis Système

### **1. Système d'exploitation :**
- ✅ **macOS** (recommandé)
- ✅ **Windows 10/11** 
- ✅ **Linux** (Ubuntu, etc.)

### **2. Logiciels requis :**
- ✅ **Python 3.11** ou plus récent
- ✅ **Git** (pour télécharger le projet)

---

## 🚀 Étapes d'Installation

### **Étape 1 : Télécharger Python**

#### **Sur macOS :**
1. Aller sur [python.org](https://www.python.org/downloads/)
2. Cliquer sur "Download Python 3.11.x"
3. Installer en suivant les instructions
4. Vérifier l'installation : ouvrir Terminal et taper `python3 --version`

#### **Sur Windows :**
1. Aller sur [python.org](https://www.python.org/downloads/)
2. Cliquer sur "Download Python 3.11.x"
3. **IMPORTANT** : Cocher "Add Python to PATH" pendant l'installation
4. Installer en suivant les instructions
5. Vérifier l'installation : ouvrir Command Prompt et taper `python --version`

### **Étape 2 : Télécharger Git**

#### **Sur macOS :**
- Git est généralement déjà installé
- Sinon, télécharger depuis [git-scm.com](https://git-scm.com/)

#### **Sur Windows :**
1. Aller sur [git-scm.com](https://git-scm.com/)
2. Télécharger et installer Git pour Windows

### **Étape 3 : Télécharger le Projet**

#### **Option A : Via Git (recommandé)**
```bash
# Ouvrir Terminal/Command Prompt
git clone [URL_DU_REPO]
cd les-visites-de-marie
```

#### **Option B : Via Archive ZIP**
1. Télécharger l'archive ZIP du projet
2. Extraire dans un dossier (ex: `les-visites-de-marie`)
3. Ouvrir Terminal/Command Prompt dans ce dossier

### **Étape 4 : Installer les Dépendances**

```bash
# Dans le dossier du projet
pip3 install flask
pip3 install werkzeug
pip3 install pillow
```

**Note :** Si `pip3` ne fonctionne pas, essayer `pip`

### **Étape 5 : Lancer l'Application**

```bash
# Dans le dossier du projet
python3 app.py
```

**Note :** Si `python3` ne fonctionne pas, essayer `python`

---

## 🌐 Utilisation de l'Application

### **1. Accès à l'Application**
- Ouvrir un navigateur web (Chrome, Firefox, Safari)
- Aller à l'adresse : `http://localhost:8000`

### **2. Navigation Publique**
- **Page d'accueil** : Affichage des ballades
- **Menu "Carnets de ballades"** : Toutes les promenades
- **Menu "Carnets de cultures"** : Sélection par catégorie
- **Menu "Carnets de santé naturelle"** : Sélection par catégorie
- **Menu "Carnets de jardin"** : Sélection par catégorie
- **Menu "Carnets d'organisation"** : Sélection par catégorie

### **3. Mode Administrateur**
- **Option 1 :** Cliquer sur le lien "Administration du site" en bas de page
- **Option 2 :** Une fois connecté, utiliser le menu "⚙️ Admin" dans la navigation
- **Identifiants :**
  - **Nom d'utilisateur :** `Marie`
  - **Mot de passe :** `Jousselin`

---

## ✏️ Fonctionnalités d'Administration

### **1. Tableau de bord Admin avec Onglets**

#### **Onglet "Général" :**
- **Titre du Site** : Modifier le titre principal
- **Sous-titre du Site** : Modifier le sous-titre
- **Email de l'administrateur** : Définir l'email de contact
- **Guide d'utilisation** : Instructions détaillées
- **Informations de configuration** : Statut et version

#### **Onglet "Menus" :**
- **Configuration des menus existants** : Titre, description, statut
- **Ajout de nouveaux menus** : Créer de nouvelles sections
- **Gestion des pages** : Titres et descriptions des pages de menu

#### **Onglet "Pied de page" :**
- **Texte "À propos"** : Personnaliser le lien du footer
- **Texte de contact** : Modifier le texte du lien de contact
- **Email de contact** : Définir l'email de contact

#### **Onglet "À propos" :**
- **Texte de la page** : Rédiger la présentation
- **Image de la page** : Uploader une photo de profil

### **2. Gestion du Contenu**

#### **Ballades :**
- **Ajouter une ballade** : Bouton "➕ Ajouter une balade"
- **Modifier une ballade** : Clic sur ✏️ sur la carte
- **Supprimer une ballade** : Clic sur 🗑️ sur la carte

#### **Carnets :**
- **Ajouter une page** : Bouton "➕ Ajouter une page" dans chaque catégorie
- **Modifier une page** : Clic sur ✏️ sur la carte
- **Supprimer une page** : Clic sur 🗑️ sur la carte

#### **Catégories :**
- **Ajouter une catégorie** : Bouton "➕ Ajouter une catégorie"
- **Modifier une catégorie** : Clic sur ✏️ sur la carte de catégorie
- **Supprimer une catégorie** : Clic sur 🗑️ sur la carte de catégorie

---

## 📁 Structure des Fichiers

```
les-visites-de-marie/
├── app.py                    # Application principale
├── data/                     # Données du site
│   ├── visites.json         # Ballades
│   ├── config.json          # Configuration du site
│   ├── carnets_culture.json # Carnets de culture
│   └── categories.json      # Catégories des menus
├── static/                   # Fichiers statiques
│   └── uploads/             # Images uploadées
├── templates/               # Pages du site
└── README.md               # Ce guide
```

---

## 🔧 Dépannage

### **Problème : "python3 not found"**
**Solution :**
```bash
# Essayer
python app.py
```

### **Problème : "pip3 not found"**
**Solution :**
```bash
# Essayer
pip install flask
```

### **Problème : "Port already in use"**
**Solution :**
```bash
# Arrêter l'application (Ctrl+C)
# Relancer
python3 app.py
```

### **Problème : "Module not found"**
**Solution :**
```bash
# Réinstaller les dépendances
pip3 install flask werkzeug pillow
```

---

## 📝 Guide d'Utilisation Rapide

### **Pour Ajouter une Ballade :**
1. Se connecter en mode admin
2. Aller sur "Carnets de ballades"
3. Cliquer sur "➕ Ajouter une balade"
4. Remplir le formulaire
5. Cliquer sur "Créer la ballade"

### **Pour Ajouter une Page de Culture :**
1. Se connecter en mode admin
2. Aller sur "Carnets de cultures"
3. Choisir une catégorie (ex: "Musées & Expositions")
4. Cliquer sur "➕ Ajouter une page"
5. Remplir le formulaire
6. Cliquer sur "Créer le carnet"

### **Pour Modifier le Titre du Site :**
1. Se connecter en mode admin
2. Aller dans le "Tableau de bord Admin"
3. Onglet "Général"
4. Modifier le "Titre du Site"
5. Cliquer sur "💾 Sauvegarder la configuration"

---

## ⌨️ Commandes Utiles

### **Démarrer l'application :**
```bash
python3 app.py
```

### **Arrêter l'application :**
```bash
# Dans le terminal, appuyer sur Ctrl+C
```

### **Redémarrer l'application :**
```bash
# Arrêter (Ctrl+C) puis relancer
python3 app.py
```

---

## 📞 Support

### **En cas de problème :**
1. Vérifier que Python est installé : `python3 --version`
2. Vérifier que les dépendances sont installées
3. Redémarrer l'application
4. Vérifier que le port 8000 n'est pas utilisé

### **Logs d'erreur :**
- Les erreurs s'affichent dans le terminal
- Noter le message d'erreur pour le support

---

## ✅ Checklist d'Installation

- [ ] Python 3.11+ installé
- [ ] Git installé (ou archive ZIP téléchargée)
- [ ] Projet téléchargé et extrait
- [ ] Dépendances installées (`pip3 install flask werkzeug pillow`)
- [ ] Application lancée (`python3 app.py`)
- [ ] Site accessible sur `http://localhost:8000`
- [ ] Connexion admin réussie (Marie / Jousselin)

---

## 🎉 Nouvelles Fonctionnalités

### **Interface d'Administration Améliorée :**
- **Système d'onglets** : Organisation claire des fonctionnalités
- **Configuration centralisée** : Tout dans le tableau de bord admin
- **Interface simplifiée** : Plus d'icônes de modification dispersées
- **Guide intégré** : Instructions d'utilisation directement dans l'admin
- **Menu Admin** : Accès direct via le menu de navigation (visible uniquement en mode admin)

### **Gestion Simplifiée :**
- **Titre et sous-titre** : Modifiables directement dans l'onglet "Général"
- **Configuration des menus** : Tout dans l'onglet "Menus"
- **Pied de page** : Personnalisation dans l'onglet dédié
- **Page "À propos"** : Gestion complète dans l'onglet dédié

---

**🎊 Félicitations ! Le site "Les Visites de Marie" est maintenant opérationnel avec une interface d'administration moderne et intuitive !**

Vous pouvez maintenant ajouter du contenu, modifier les ballades et les carnets, et personnaliser le site selon vos besoins grâce à l'interface d'administration organisée en onglets. 