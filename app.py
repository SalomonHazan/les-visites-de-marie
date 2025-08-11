from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import json
import os
from datetime import datetime
import uuid
import re
from functools import wraps
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import mimetypes

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_ici'

# Configuration pour l'upload de fichiers
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Configuration
VISITES_FILE = 'data/visites.json'
CONFIG_FILE = 'data/config.json'
CARNETS_CULTURE_FILE = 'data/carnets_culture.json'
CATEGORIES_FILE = 'data/categories.json'
CATEGORIES_ORGANISATION_FILE = 'data/categories_organisation.json'
CARNETS_ORGANISATION_FILE = 'data/carnets_organisation.json'
BULLET_JOURNAL_PAGES_FILE = 'data/bullet_journal_pages.json'

os.makedirs('data', exist_ok=True)

if not os.path.exists(VISITES_FILE):
    with open(VISITES_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=2)

if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            'site_title': 'Les Visites de Marie',
            'site_subtitle': 'Découvrez Paris à travers mes promenades aquarelles',
            'admin_email': 'marie@lesvisites.com',
            'last_updated': datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)

def load_visites():
    try:
        with open(VISITES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_visites(visites):
    with open(VISITES_FILE, 'w', encoding='utf-8') as f:
        json.dump(visites, f, ensure_ascii=False, indent=2)

def load_config():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            'site_title': 'Les Visites de Marie',
            'site_subtitle': 'Découvrez Paris à travers mes promenades aquarelles',
            'admin_email': 'marie@lesvisites.com',
            'last_updated': datetime.now().isoformat()
        }

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def load_carnets_culture():
    try:
        with open(CARNETS_CULTURE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "musees_expositions": [],
            "theatre_spectacles": [],
            "litterature": []
        }

def save_carnets_culture(carnets_culture):
    with open(CARNETS_CULTURE_FILE, 'w', encoding='utf-8') as f:
        json.dump(carnets_culture, f, ensure_ascii=False, indent=2)

def load_categories():
    try:
        with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_categories(categories):
    with open(CATEGORIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)

def load_categories_organisation():
    try:
        with open(CATEGORIES_ORGANISATION_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_categories_organisation(categories_organisation):
    with open(CATEGORIES_ORGANISATION_FILE, 'w', encoding='utf-8') as f:
        json.dump(categories_organisation, f, ensure_ascii=False, indent=2)

def load_carnets_organisation():
    try:
        with open(CARNETS_ORGANISATION_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "bullet_journal": [],
            "listes_generalistes": [],
            "listes_precises": [],
            "listes_thematiques": [],
            "listes_temporelles": [],
            "listes_quotidiennes": [],
            "todo_list": [],
            "post_it_virtuels": []
        }

def save_carnets_organisation(carnets_organisation):
    with open(CARNETS_ORGANISATION_FILE, 'w', encoding='utf-8') as f:
        json.dump(carnets_organisation, f, ensure_ascii=False, indent=2)

def load_bullet_journal_pages():
    try:
        with open(BULLET_JOURNAL_PAGES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "pages": {},
            "templates": {
                "blank": {"name": "Page blanche", "description": "Page vierge pour dessin libre", "background": "white"},
                "lined": {"name": "Page lignée", "description": "Page avec lignes pour l'écriture", "background": "white", "pattern": "lined"},
                "grid": {"name": "Page quadrillée", "description": "Page avec grille pour l'organisation", "background": "white", "pattern": "grid"},
                "dots": {"name": "Page à points", "description": "Page avec points pour bullet journal", "background": "white", "pattern": "dots"}
            },
            "media_library": {"stickers": [], "user_images": []}
        }

def save_bullet_journal_pages(bullet_journal_data):
    with open(BULLET_JOURNAL_PAGES_FILE, 'w', encoding='utf-8') as f:
        json.dump(bullet_journal_data, f, ensure_ascii=False, indent=2)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, folder):
    """Sauvegarde un fichier uploadé dans le dossier spécifié"""
    if file and file.filename:
        # Sécuriser le nom du fichier
        filename = secure_filename(file.filename)
        
        # Générer un nom unique pour éviter les conflits
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
        
        # Créer le chemin complet
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], folder)
        os.makedirs(upload_path, exist_ok=True)
        
        file_path = os.path.join(upload_path, unique_filename)
        
        # Sauvegarder le fichier
        file.save(file_path)
        
        # Retourner le chemin relatif pour l'affichage
        return f"uploads/{folder}/{unique_filename}"
    
    return None

def delete_file(file_path):
    """Supprime un fichier du système"""
    if file_path and not file_path.startswith('http'):
        full_path = os.path.join('static', file_path)
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
    return False

def get_file_size_mb(file_path):
    """Retourne la taille d'un fichier en MB"""
    if os.path.exists(file_path):
        size_bytes = os.path.getsize(file_path)
        return round(size_bytes / (1024 * 1024), 2)
    return 0

def slugify(text):
    text = text.lower()
    # Remplacer les caractères spéciaux par des espaces
    text = re.sub(r'[^a-z0-9\s-]', ' ', text)
    # Remplacer les espaces multiples par des tirets
    text = re.sub(r'\s+', '-', text)
    # Supprimer les tirets en début et fin
    text = text.strip('-')
    # Si le slug est vide, utiliser un slug par défaut
    if not text:
        text = 'visite-' + str(uuid.uuid4())[:8]
    return text

@app.route('/')
def index():
    # Rediriger vers le menu des ballades par défaut
    return redirect(url_for('menu_page', menu_id='ballades'))

@app.route('/menu/<menu_id>')
def menu_page(menu_id):
    visites = load_visites()
    config = load_config()
    categories = load_categories()
    
    # Filtrer les visites par catégorie si nécessaire
    if menu_id == 'ballades':
        # Pour l'instant, toutes les visites sont des ballades
        filtered_visites = visites
    else:
        # Pour les autres catégories, on peut filtrer plus tard
        filtered_visites = []
    
    # Trouver le menu actuel
    current_menu = None
    if config and config.get('menus'):
        current_menu = next((menu for menu in config['menus'] if menu['id'] == menu_id), None)
    
    # Charger les carnets de culture si c'est la page des cultures
    carnets_culture = None
    if menu_id == 'cultures':
        carnets_culture = load_carnets_culture()
    
    # Charger les carnets d'organisation si c'est la page d'organisation
    carnets_organisation = None
    categories_organisation = None
    if menu_id == 'carnet_organisation':
        carnets_organisation = load_carnets_organisation()
        categories_organisation = load_categories_organisation()
    
    # Charger les catégories pour les autres menus
    menu_categories = categories.get(menu_id, {}) if menu_id != 'ballades' else {}
    
    return render_template('menu_page.html', 
                         visites=filtered_visites, 
                         config=config, 
                         current_menu=current_menu,
                         menu_id=menu_id,
                         carnets_culture=carnets_culture,
                         carnets_organisation=carnets_organisation,
                         categories=categories,
                         categories_organisation=categories_organisation,
                         menu_categories=menu_categories)

@app.route('/visite/<slug>')
def visite_detail(slug):
    visites = load_visites()
    visite = next((v for v in visites if v['slug'] == slug), None)
    if not visite:
        return 'Visite non trouvée', 404
    config = load_config()
    return render_template('visite_detail.html', visite=visite, config=config)

@app.route('/admin')
def admin_login():
    config = load_config()
    return render_template('admin_login.html', config=config)

@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    if username == 'Marie' and password == 'Jousselin':
        session['admin_logged_in'] = True
        return redirect(url_for('admin_dashboard'))
    else:
        flash('Identifiants incorrects', 'error')
        return redirect(url_for('admin_login'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    visites = load_visites()
    config = load_config()
    return render_template('admin_dashboard.html', visites=visites, config=config)

@app.route('/admin/visite/new')
@admin_required
def admin_new_visite_page():
    config = load_config()
    return render_template('admin_visite_form.html', config=config)

@app.route('/admin/visite/create', methods=['POST'])
@admin_required
def admin_create_visite():
    titre = request.form.get('titre')
    description_complete = request.form.get('description_complete')
    image_url = request.form.get('image_url')
    
    if not titre or not description_complete:
        flash('Titre et description requis', 'error')
        return redirect(url_for('admin_new_visite_page'))
    
    # Gestion de l'upload d'image
    uploaded_image_path = None
    if 'image_file' in request.files:
        file = request.files['image_file']
        if file and file.filename and allowed_file(file.filename):
            uploaded_image_path = save_uploaded_file(file, 'visites')
            if uploaded_image_path:
                image_url = uploaded_image_path
        elif file and file.filename:
            flash('Format de fichier non autorisé. Utilisez PNG, JPG, JPEG, GIF ou WEBP.', 'error')
            return redirect(url_for('admin_new_visite_page'))
    
    # Récupérer les étapes
    etapes = []
    i = 0
    while f'etapes[{i}][titre]' in request.form:
        titre_etape = request.form.get(f'etapes[{i}][titre]')
        description_etape = request.form.get(f'etapes[{i}][description]')
        duree_etape = request.form.get(f'etapes[{i}][duree]')
        adresse_etape = request.form.get(f'etapes[{i}][adresse]', '')
        metro_etape = request.form.get(f'etapes[{i}][metro]', '')
        
        if titre_etape and description_etape and duree_etape:
            etapes.append({
                'titre': titre_etape,
                'description': description_etape,
                'duree': duree_etape,
                'adresse': adresse_etape,
                'metro': metro_etape
            })
        i += 1
    
    # Récupérer les conseils
    conseils = []
    i = 0
    while f'conseils[{i}]' in request.form:
        conseil = request.form.get(f'conseils[{i}]')
        if conseil:
            conseils.append(conseil)
        i += 1
    
    visite = {
        'id': str(uuid.uuid4()),
        'titre': titre,
        'slug': slugify(titre),
        'description_courte': description_complete[:100] + '...' if len(description_complete) > 100 else description_complete,
        'description_complete': description_complete,
        'etapes': etapes,
        'conseils': conseils,
        'image_url': image_url,
        'date_creation': datetime.now().isoformat()
    }
    
    visites = load_visites()
    visites.append(visite)
    save_visites(visites)
    
    flash('Visite créée avec succès !', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/visite/edit/<visite_id>')
@admin_required
def admin_edit_visite_page(visite_id):
    visites = load_visites()
    visite = next((v for v in visites if v['id'] == visite_id), None)
    if not visite:
        flash('Visite non trouvée', 'error')
        return redirect(url_for('admin_dashboard'))
    config = load_config()
    return render_template('admin_visite_edit.html', visite=visite, config=config)

@app.route('/admin/visite/update/<visite_id>', methods=['POST'])
@admin_required
def admin_update_visite(visite_id):
    titre = request.form.get('titre')
    description_complete = request.form.get('description_complete')
    image_url = request.form.get('image_url')
    
    if not titre or not description_complete:
        flash('Titre et description requis', 'error')
        return redirect(url_for('admin_edit_visite_page', visite_id=visite_id))
    
    visites = load_visites()
    visite = next((v for v in visites if v['id'] == visite_id), None)
    if not visite:
        flash('Visite non trouvée', 'error')
        return redirect(url_for('admin_dashboard'))
    
    # Gestion de l'upload d'image
    if 'image_file' in request.files:
        file = request.files['image_file']
        if file and file.filename and allowed_file(file.filename):
            # Supprimer l'ancienne image si elle existe
            if visite.get('image_url') and not visite['image_url'].startswith('http'):
                delete_file(visite['image_url'])
            
            # Sauvegarder la nouvelle image
            uploaded_image_path = save_uploaded_file(file, 'visites')
            if uploaded_image_path:
                image_url = uploaded_image_path
        elif file and file.filename:
            flash('Format de fichier non autorisé. Utilisez PNG, JPG, JPEG, GIF ou WEBP.', 'error')
            return redirect(url_for('admin_edit_visite_page', visite_id=visite_id))
    
    # Récupérer les étapes
    etapes = []
    i = 0
    while f'etapes[{i}][titre]' in request.form:
        titre_etape = request.form.get(f'etapes[{i}][titre]')
        description_etape = request.form.get(f'etapes[{i}][description]')
        duree_etape = request.form.get(f'etapes[{i}][duree]')
        adresse_etape = request.form.get(f'etapes[{i}][adresse]', '')
        metro_etape = request.form.get(f'etapes[{i}][metro]', '')
        
        if titre_etape and description_etape and duree_etape:
            etapes.append({
                'titre': titre_etape,
                'description': description_etape,
                'duree': duree_etape,
                'adresse': adresse_etape,
                'metro': metro_etape
            })
        i += 1
    
    # Récupérer les conseils
    conseils = []
    i = 0
    while f'conseils[{i}]' in request.form:
        conseil = request.form.get(f'conseils[{i}]')
        if conseil:
            conseils.append(conseil)
        i += 1
    
    visite['titre'] = titre
    visite['slug'] = slugify(titre)
    visite['description_courte'] = description_complete[:100] + '...' if len(description_complete) > 100 else description_complete
    visite['description_complete'] = description_complete
    visite['image_url'] = image_url
    visite['etapes'] = etapes
    visite['conseils'] = conseils
    

    
    save_visites(visites)
    flash('Visite mise à jour avec succès !', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/visite/delete/<visite_id>')
@admin_required
def admin_delete_visite(visite_id):
    visites = load_visites()
    visite = next((v for v in visites if v['id'] == visite_id), None)
    if not visite:
        flash('Visite non trouvée', 'error')
        return redirect(url_for('admin_dashboard'))
    
    # Supprimer l'image associée si elle existe
    if visite.get('image_url') and not visite['image_url'].startswith('http'):
        delete_file(visite['image_url'])
    
    visites = [v for v in visites if v['id'] != visite_id]
    save_visites(visites)
    
    flash(f'Visite "{visite["titre"]}" supprimée avec succès !', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/config')
@admin_required
def admin_config():
    config = load_config()
    return render_template('admin_config.html', config=config)

@app.route('/admin/config/update', methods=['POST'])
@admin_required
def admin_update_config():
    site_title = request.form.get('site_title')
    site_subtitle = request.form.get('site_subtitle')
    admin_email = request.form.get('admin_email')
    
    if not site_title or not site_subtitle:
        flash('Titre et sous-titre requis', 'error')
        return redirect(url_for('admin_config'))
    
    config = load_config()
    config['site_title'] = site_title
    config['site_subtitle'] = site_subtitle
    config['admin_email'] = admin_email
    
    # Mettre à jour les champs du footer
    footer_about = request.form.get('footer_about')
    footer_contact_text = request.form.get('footer_contact_text')
    footer_contact_email = request.form.get('footer_contact_email')
    
    if footer_about:
        config['footer_about'] = footer_about
    if footer_contact_text:
        config['footer_contact_text'] = footer_contact_text
    if footer_contact_email:
        config['footer_contact_email'] = footer_contact_email
    
    # Mettre à jour les champs de la page "À propos"
    about_text = request.form.get('about_text')
    about_image = request.form.get('about_image')
    
    if about_text:
        config['about_text'] = about_text
    
    # Gestion de l'upload d'image pour la page "À propos"
    if 'about_image_file' in request.files:
        file = request.files['about_image_file']
        if file and file.filename and allowed_file(file.filename):
            # Supprimer l'ancienne image si elle existe
            if config.get('about_image') and not config['about_image'].startswith('http'):
                delete_file(config['about_image'])
            
            # Sauvegarder la nouvelle image
            uploaded_image_path = save_uploaded_file(file, 'about')
            if uploaded_image_path:
                config['about_image'] = uploaded_image_path
        elif file and file.filename:
            flash('Format de fichier non autorisé pour l\'image "À propos". Utilisez PNG, JPG, JPEG, GIF ou WEBP.', 'error')
            return redirect(url_for('admin_config'))
    elif about_image:
        config['about_image'] = about_image
    
    config['last_updated'] = datetime.now().isoformat()
    
    # Sauvegarder la configuration après les mises à jour de base
    save_config(config)
    
    # Gérer la suppression d'un menu
    delete_menu_id = request.form.get('delete_menu_id')
    if delete_menu_id:
        if config.get('menus'):
            config['menus'] = [menu for menu in config['menus'] if menu['id'] != delete_menu_id]
        save_config(config)
        flash(f'Menu "{delete_menu_id}" supprimé avec succès !', 'success')
        return redirect(url_for('admin_dashboard'))
    
    # Gérer l'ajout d'un nouveau menu
    new_menu_id = request.form.get('new_menu_id')
    new_menu_title = request.form.get('new_menu_title')
    new_menu_description = request.form.get('new_menu_description')
    new_menu_active = request.form.get('new_menu_active')
    
    if new_menu_id and new_menu_title and new_menu_description:
        # Vérifier que l'ID n'existe pas déjà
        existing_ids = [menu['id'] for menu in config.get('menus', [])]
        if new_menu_id in existing_ids:
            flash(f'Un menu avec l\'identifiant "{new_menu_id}" existe déjà !', 'error')
            return redirect(url_for('admin_config'))
        
        # Créer le nouveau menu
        new_menu = {
            'id': new_menu_id,
            'title': new_menu_title,
            'description': new_menu_description,
            'active': new_menu_active == 'true'
        }
        
        if not config.get('menus'):
            config['menus'] = []
        config['menus'].append(new_menu)
        save_config(config)
        flash(f'Menu "{new_menu_title}" ajouté avec succès !', 'success')
        return redirect(url_for('admin_dashboard'))
    
    # Mettre à jour les textes de la page des ballades
    ballades_page_title = request.form.get('ballades_page_title')
    ballades_page_description = request.form.get('ballades_page_description')
    
    # Mettre à jour les textes de la page des cultures
    cultures_page_title = request.form.get('cultures_page_title')
    cultures_page_description = request.form.get('cultures_page_description')
    
    # Mettre à jour les menus existants
    if config.get('menus'):
        for menu in config['menus']:
            # Mettre à jour les propriétés générales du menu
            menu_title = request.form.get(f'menu_title_{menu["id"]}')
            menu_description = request.form.get(f'menu_description_{menu["id"]}')
            menu_active = request.form.get(f'menu_active_{menu["id"]}')
            
            if menu_title:
                menu['title'] = menu_title
            if menu_description:
                menu['description'] = menu_description
            if menu_active is not None:
                menu['active'] = menu_active == 'true'
            
            # Mettre à jour les propriétés spécifiques de la page des ballades
            if menu['id'] == 'ballades':
                if ballades_page_title:
                    menu['page_title'] = ballades_page_title
                if ballades_page_description:
                    menu['page_description'] = ballades_page_description
            
            # Mettre à jour les propriétés spécifiques de la page des cultures
            if menu['id'] == 'cultures':
                if cultures_page_title:
                    menu['page_title'] = cultures_page_title
                if cultures_page_description:
                    menu['page_description'] = cultures_page_description
    
    save_config(config)
    flash('Configuration mise à jour avec succès !', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/about')
def about_page():
    config = load_config()
    return render_template('about.html', config=config)

@app.route('/admin/config/delete_menu/<menu_id>', methods=['POST'])
@admin_required
def admin_delete_menu(menu_id):
    config = load_config()
    
    if config.get('menus'):
        # Trouver le menu à supprimer
        menu_to_delete = None
        for menu in config['menus']:
            if menu['id'] == menu_id:
                menu_to_delete = menu
                break
        
        if menu_to_delete:
            config['menus'] = [menu for menu in config['menus'] if menu['id'] != menu_id]
            save_config(config)
            flash(f'Menu "{menu_to_delete["title"]}" supprimé avec succès !', 'success')
        else:
            flash(f'Menu avec l\'ID "{menu_id}" non trouvé !', 'error')
    else:
        flash('Aucun menu à supprimer !', 'error')
    
    return redirect(url_for('admin_config'))

# Routes pour les carnets de culture
@app.route('/admin/carnet-culture/new')
@admin_required
def admin_new_carnet_culture_page():
    config = load_config()
    categorie = request.args.get('categorie', 'musees_expositions')
    return render_template('admin_carnet_culture_form.html', config=config, categorie=categorie)

@app.route('/carnet-culture/<categorie>/<slug>')
def carnet_culture_detail(categorie, slug):
    carnets_culture = load_carnets_culture()
    if categorie not in carnets_culture:
        return 'Catégorie non trouvée', 404
    
    carnet = next((c for c in carnets_culture[categorie] if c['id'] == slug), None)
    if not carnet:
        return 'Carnet non trouvé', 404
    
    config = load_config()
    return render_template('carnet_culture_detail.html', carnet=carnet, categorie=categorie, config=config)

@app.route('/carnets-culture/<categorie>')
def carnets_culture_categorie(categorie):
    carnets_culture = load_carnets_culture()
    if categorie not in carnets_culture:
        return 'Catégorie non trouvée', 404
    
    # Définir les informations de la catégorie
    categories_info = {
        'musees_expositions': {
            'titre': '🏛️ Musées & Expositions',
            'description': 'Découvrez les plus beaux musées et expositions de Paris. Chaque carnet vous guide à travers les collections les plus remarquables.',
            'icon': '🏛️',
            'nom_court': 'musée'
        },
        'theatre_spectacles': {
            'titre': '🎭 Théâtre & Spectacles',
            'description': 'Plongez dans l\'univers du théâtre et des spectacles. Découvrez les salles mythiques et les productions les plus captivantes.',
            'icon': '🎭',
            'nom_court': 'théâtre'
        },
        'litterature': {
            'titre': '📚 Littérature',
            'description': 'Explorez les lieux qui ont inspiré les plus grands écrivains. Suivez les traces des auteurs et découvrez leurs univers.',
            'icon': '📚',
            'nom_court': 'littérature'
        }
    }
    
    categorie_info = categories_info.get(categorie, {
        'titre': categorie.replace('_', ' ').title(),
        'description': 'Carnets de culture',
        'icon': '📖',
        'nom_court': 'culture'
    })
    
    config = load_config()
    
    # Utiliser les données sauvegardées si elles existent
    if 'category_headers' in config and categorie in config['category_headers']:
        saved_data = config['category_headers'][categorie]
        if 'titre' in saved_data:
            categorie_info['titre'] = saved_data['titre']
        if 'description' in saved_data:
            categorie_info['description'] = saved_data['description']
    
    return render_template('carnets_culture_categorie.html',
                         categorie=categorie,
                         carnets=carnets_culture[categorie],
                         categorie_titre=categorie_info['titre'],
                         categorie_description=categorie_info['description'],
                         categorie_icon=categorie_info['icon'],
                         categorie_nom_court=categorie_info['nom_court'],
                         config=config)

@app.route('/carnets/<menu_id>/<categorie>')
def carnets_categorie(menu_id, categorie):
    """Route générique pour tous les carnets (sante, jardin, organisation)"""
    categories = load_categories()
    
    if menu_id not in categories or categorie not in categories[menu_id]:
        return 'Catégorie non trouvée', 404
    
    category = categories[menu_id][categorie]
    
    # Créer des données fictives pour les carnets (à remplacer par de vrais fichiers JSON plus tard)
    carnets = []
    
    config = load_config()
    
    # Utiliser les données sauvegardées si elles existent
    if 'category_headers' in config and categorie in config['category_headers']:
        saved_data = config['category_headers'][categorie]
        if 'titre' in saved_data:
            category['titre'] = saved_data['titre']
        if 'description' in saved_data:
            category['description'] = saved_data['description']
    
    return render_template('carnets_categorie.html',
                         menu_id=menu_id,
                         categorie=categorie,
                         carnets=carnets,
                         categorie_titre=category.get('titre', category.get('nom', '')),
                         categorie_description=category.get('description', ''),
                         categorie_icon=category.get('icon', '📖'),
                         categorie_nom_court=category.get('nom_court', 'page'),
                         config=config)

@app.route('/admin/menu-page/edit/<menu_id>')
@admin_required
def admin_edit_menu_page(menu_id):
    """Modifier le titre et la description d'une page de menu"""
    config = load_config()
    
    # Trouver le menu actuel
    current_menu = None
    if config and config.get('menus'):
        current_menu = next((menu for menu in config['menus'] if menu['id'] == menu_id), None)
    
    if not current_menu:
        flash('Menu non trouvé', 'error')
        return redirect(url_for('menu_page', menu_id=menu_id))
    
    return render_template('admin_menu_page_edit.html',
                         menu_id=menu_id,
                         menu=current_menu,
                         config=config)

@app.route('/admin/menu-page/update/<menu_id>', methods=['POST'])
@admin_required
def admin_update_menu_page(menu_id):
    """Mettre à jour le titre et la description d'une page de menu"""
    config = load_config()
    
    # Trouver le menu actuel
    current_menu = None
    if config and config.get('menus'):
        current_menu = next((menu for menu in config['menus'] if menu['id'] == menu_id), None)
    
    if not current_menu:
        flash('Menu non trouvé', 'error')
        return redirect(url_for('menu_page', menu_id=menu_id))
    
    # Récupérer les nouvelles valeurs
    new_title = request.form.get('page_title', '').strip()
    new_description = request.form.get('page_description', '').strip()
    
    if not new_title:
        flash('Le titre de la page ne peut pas être vide', 'error')
        return redirect(url_for('admin_edit_menu_page', menu_id=menu_id))
    
    # Mettre à jour le menu
    current_menu['page_title'] = new_title
    current_menu['page_description'] = new_description
    
    # Sauvegarder la configuration
    save_config(config)
    
    flash('Page mise à jour avec succès', 'success')
    return redirect(url_for('menu_page', menu_id=menu_id))

@app.route('/admin/carnet/new/<menu_id>/<categorie>')
@admin_required
def admin_new_carnet_page(menu_id, categorie):
    """Page pour créer un nouveau carnet (générique pour tous les menus)"""
    config = load_config()
    categories = load_categories()
    
    if menu_id not in categories or categorie not in categories[menu_id]:
        flash('Catégorie non trouvée', 'error')
        return redirect(url_for('carnets_categorie', menu_id=menu_id, categorie=categorie))
    
    category = categories[menu_id][categorie]
    
    return render_template('admin_carnet_form.html',
                         menu_id=menu_id,
                         categorie=categorie,
                         category=category,
                         config=config)

@app.route('/admin/carnet/create/<menu_id>/<categorie>', methods=['POST'])
@admin_required
def admin_create_carnet(menu_id, categorie):
    """Créer un nouveau carnet (générique pour tous les menus)"""
    titre = request.form.get('titre')
    description_courte = request.form.get('description_courte')
    description_complete = request.form.get('description_complete')
    
    if not titre or not description_complete:
        flash('Titre et description requis', 'error')
        return redirect(url_for('admin_new_carnet_page', menu_id=menu_id, categorie=categorie))
    
    # Gestion de l'upload d'image
    uploaded_image_path = None
    if 'image_file' in request.files:
        file = request.files['image_file']
        if file and file.filename and allowed_file(file.filename):
            uploaded_image_path = save_uploaded_file(file, f'carnets_{menu_id}')
            if uploaded_image_path:
                image_url = uploaded_image_path
            else:
                flash('Erreur lors de l\'upload de l\'image', 'error')
                return redirect(url_for('admin_new_carnet_page', menu_id=menu_id, categorie=categorie))
        elif file and file.filename:
            flash('Format de fichier non autorisé. Utilisez PNG, JPG, JPEG, GIF ou WEBP.', 'error')
            return redirect(url_for('admin_new_carnet_page', menu_id=menu_id, categorie=categorie))
    
    # Créer le nouveau carnet
    carnet_id = str(uuid.uuid4())
    new_carnet = {
        'id': carnet_id,
        'titre': titre,
        'description_courte': description_courte,
        'description_complete': description_complete,
        'date_creation': datetime.now().isoformat(),
        'image_url': image_url if uploaded_image_path else None,
        'categorie': categorie,
        'etapes': [],
        'conseils': []
    }
    
    # Pour l'instant, on sauvegarde dans un fichier temporaire
    # TODO: Créer des fichiers JSON spécifiques pour chaque type de carnet
    flash('Carnet créé avec succès ! (Fonctionnalité en développement)', 'success')
    return redirect(url_for('carnets_categorie', menu_id=menu_id, categorie=categorie))

@app.route('/admin/carnet/edit/<menu_id>/<categorie>/<carnet_id>')
@admin_required
def admin_edit_carnet_page(menu_id, categorie, carnet_id):
    """Page pour éditer un carnet existant (générique pour tous les menus)"""
    config = load_config()
    categories = load_categories()
    
    if menu_id not in categories or categorie not in categories[menu_id]:
        flash('Catégorie non trouvée', 'error')
        return redirect(url_for('carnets_categorie', menu_id=menu_id, categorie=categorie))
    
    category = categories[menu_id][categorie]
    
    # Pour l'instant, on utilise des données fictives
    # TODO: Charger les vraies données depuis les fichiers JSON
    carnet = {
        'id': carnet_id,
        'titre': 'Carnet en développement',
        'description_courte': 'Description courte',
        'description_complete': 'Description complète',
        'etapes': [],
        'conseils': []
    }
    
    return render_template('admin_carnet_edit.html',
                         menu_id=menu_id,
                         categorie=categorie,
                         carnet_id=carnet_id,
                         carnet=carnet,
                         category=category,
                         config=config)

@app.route('/admin/carnet/delete/<menu_id>/<categorie>/<carnet_id>')
@admin_required
def admin_delete_carnet(menu_id, categorie, carnet_id):
    """Supprimer un carnet (générique pour tous les menus)"""
    # TODO: Implémenter la vraie suppression
    flash('Carnet supprimé avec succès ! (Fonctionnalité en développement)', 'success')
    return redirect(url_for('carnets_categorie', menu_id=menu_id, categorie=categorie))

@app.route('/carnet/<menu_id>/<categorie>/<slug>')
def carnet_detail(menu_id, categorie, slug):
    """Page de détail d'un carnet (générique pour tous les menus)"""
    # TODO: Charger les vraies données depuis les fichiers JSON
    carnet = {
        'id': slug,
        'titre': 'Carnet en développement',
        'description_complete': 'Ce carnet est en cours de développement.',
        'image_url': None,
        'etapes': [],
        'conseils': []
    }
    
    config = load_config()
    return render_template('carnet_detail.html',
                         menu_id=menu_id,
                         categorie=categorie,
                         carnet=carnet,
                         config=config)

@app.route('/admin/carnet/update/<menu_id>/<categorie>/<carnet_id>', methods=['POST'])
@admin_required
def admin_update_carnet(menu_id, categorie, carnet_id):
    """Mettre à jour un carnet existant (générique pour tous les menus)"""
    # TODO: Implémenter la vraie mise à jour
    flash('Carnet mis à jour avec succès ! (Fonctionnalité en développement)', 'success')
    return redirect(url_for('carnets_categorie', menu_id=menu_id, categorie=categorie))

@app.route('/admin/carnet-culture/create', methods=['POST'])
@admin_required
def admin_create_carnet_culture():
    titre = request.form.get('titre')
    description_courte = request.form.get('description_courte')
    description_complete = request.form.get('description_complete')
    categorie = request.form.get('categorie')
    
    if not titre or not description_complete or not categorie:
        flash('Titre, description et catégorie requis', 'error')
        return redirect(url_for('admin_new_carnet_culture_page'))
    
    # Gestion de l'upload d'image
    uploaded_image_path = None
    if 'image_file' in request.files:
        file = request.files['image_file']
        if file and file.filename and allowed_file(file.filename):
            uploaded_image_path = save_uploaded_file(file, 'carnets_culture')
            if uploaded_image_path:
                image_url = uploaded_image_path
            else:
                flash('Erreur lors de l\'upload de l\'image', 'error')
                return redirect(url_for('admin_new_carnet_culture_page'))
        elif file and file.filename:
            flash('Format de fichier non autorisé. Utilisez PNG, JPG, JPEG, GIF ou WEBP.', 'error')
            return redirect(url_for('admin_new_carnet_culture_page'))
    
    # Récupérer les étapes
    etapes = []
    etapes_data = request.form.to_dict()
    etape_index = 0
    
    while f'etapes[{etape_index}][titre]' in etapes_data:
        titre_etape = etapes_data[f'etapes[{etape_index}][titre]']
        description_etape = etapes_data[f'etapes[{etape_index}][description]']
        duree_etape = etapes_data[f'etapes[{etape_index}][duree]']
        adresse_etape = etapes_data.get(f'etapes[{etape_index}][adresse]', '')
        metro_etape = etapes_data.get(f'etapes[{etape_index}][metro]', '')
        
        if titre_etape and description_etape and duree_etape:
            etapes.append({
                'titre': titre_etape,
                'description': description_etape,
                'duree': duree_etape,
                'adresse': adresse_etape,
                'metro': metro_etape
            })
        
        etape_index += 1
    
    # Récupérer les conseils
    conseils = []
    conseil_index = 0
    while f'conseils[{conseil_index}]' in etapes_data:
        conseil = etapes_data[f'conseils[{conseil_index}]']
        if conseil:
            conseils.append(conseil)
        conseil_index += 1
    
    # Créer le nouveau carnet
    nouveau_carnet = {
        'id': slugify(titre),
        'titre': titre,
        'description_courte': description_courte,
        'description_complete': description_complete,
        'date_creation': datetime.now().strftime('%Y-%m-%d'),
        'image_url': uploaded_image_path,
        'categorie': categorie,
        'etapes': etapes,
        'conseils': conseils
    }
    
    # Sauvegarder dans le fichier JSON
    carnets_culture = load_carnets_culture()
    if categorie not in carnets_culture:
        carnets_culture[categorie] = []
    
    carnets_culture[categorie].append(nouveau_carnet)
    save_carnets_culture(carnets_culture)
    
    flash(f'Carnet "{titre}" créé avec succès !', 'success')
    return redirect(url_for('menu_page', menu_id='cultures'))

@app.route('/admin/carnet-culture/edit/<categorie>/<carnet_id>')
@admin_required
def admin_edit_carnet_culture_page(categorie, carnet_id):
    carnets_culture = load_carnets_culture()
    if categorie not in carnets_culture:
        return 'Catégorie non trouvée', 404
    
    carnet = next((c for c in carnets_culture[categorie] if c['id'] == carnet_id), None)
    if not carnet:
        return 'Carnet non trouvé', 404
    
    config = load_config()
    return render_template('admin_carnet_culture_edit.html', carnet=carnet, categorie=categorie, config=config)

@app.route('/admin/carnet-culture/update/<categorie>/<carnet_id>', methods=['POST'])
@admin_required
def admin_update_carnet_culture(categorie, carnet_id):
    carnets_culture = load_carnets_culture()
    if categorie not in carnets_culture:
        return 'Catégorie non trouvée', 404
    
    # Trouver le carnet à modifier
    carnet_index = None
    for i, carnet in enumerate(carnets_culture[categorie]):
        if carnet['id'] == carnet_id:
            carnet_index = i
            break
    
    if carnet_index is None:
        return 'Carnet non trouvé', 404
    
    titre = request.form.get('titre')
    description_courte = request.form.get('description_courte')
    description_complete = request.form.get('description_complete')
    
    if not titre or not description_complete:
        flash('Titre et description requis', 'error')
        return redirect(url_for('admin_edit_carnet_culture_page', categorie=categorie, carnet_id=carnet_id))
    
    # Gestion de l'upload d'image
    uploaded_image_path = None
    if 'image_file' in request.files:
        file = request.files['image_file']
        if file and file.filename and allowed_file(file.filename):
            uploaded_image_path = save_uploaded_file(file, 'carnets_culture')
            if uploaded_image_path:
                # Supprimer l'ancienne image si elle existe
                old_image = carnets_culture[categorie][carnet_index]['image_url']
                if old_image and not old_image.startswith('http'):
                    delete_file(old_image)
                carnets_culture[categorie][carnet_index]['image_url'] = uploaded_image_path
            else:
                flash('Erreur lors de l\'upload de l\'image', 'error')
                return redirect(url_for('admin_edit_carnet_culture_page', categorie=categorie, carnet_id=carnet_id))
        elif file and file.filename:
            flash('Format de fichier non autorisé. Utilisez PNG, JPG, JPEG, GIF ou WEBP.', 'error')
            return redirect(url_for('admin_edit_carnet_culture_page', categorie=categorie, carnet_id=carnet_id))
    
    # Récupérer les étapes
    etapes = []
    etapes_data = request.form.to_dict()
    etape_index = 0
    
    while f'etapes[{etape_index}][titre]' in etapes_data:
        titre_etape = etapes_data[f'etapes[{etape_index}][titre]']
        description_etape = etapes_data[f'etapes[{etape_index}][description]']
        duree_etape = etapes_data[f'etapes[{etape_index}][duree]']
        adresse_etape = etapes_data.get(f'etapes[{etape_index}][adresse]', '')
        metro_etape = etapes_data.get(f'etapes[{etape_index}][metro]', '')
        
        if titre_etape and description_etape and duree_etape:
            etapes.append({
                'titre': titre_etape,
                'description': description_etape,
                'duree': duree_etape,
                'adresse': adresse_etape,
                'metro': metro_etape
            })
        
        etape_index += 1
    
    # Récupérer les conseils
    conseils = []
    conseil_index = 0
    while f'conseils[{conseil_index}]' in etapes_data:
        conseil = etapes_data[f'conseils[{conseil_index}]']
        if conseil:
            conseils.append(conseil)
        conseil_index += 1
    
    # Mettre à jour le carnet
    carnets_culture[categorie][carnet_index].update({
        'titre': titre,
        'description_courte': description_courte,
        'description_complete': description_complete,
        'etapes': etapes,
        'conseils': conseils
    })
    
    save_carnets_culture(carnets_culture)
    flash(f'Carnet "{titre}" modifié avec succès !', 'success')
    return redirect(url_for('carnets_culture_categorie', categorie=categorie))

@app.route('/admin/carnet-culture/delete/<categorie>/<carnet_id>')
@admin_required
def admin_delete_carnet_culture(categorie, carnet_id):
    carnets_culture = load_carnets_culture()
    if categorie not in carnets_culture:
        return 'Catégorie non trouvée', 404
    
    # Trouver le carnet à supprimer
    carnet_to_delete = None
    for carnet in carnets_culture[categorie]:
        if carnet['id'] == carnet_id:
            carnet_to_delete = carnet
            break
    
    if carnet_to_delete:
        # Supprimer l'image si elle existe
        if carnet_to_delete['image_url'] and not carnet_to_delete['image_url'].startswith('http'):
            delete_file(carnet_to_delete['image_url'])
        
        # Supprimer le carnet
        carnets_culture[categorie] = [c for c in carnets_culture[categorie] if c['id'] != carnet_id]
        save_carnets_culture(carnets_culture)
        flash(f'Carnet "{carnet_to_delete["titre"]}" supprimé avec succès !', 'success')
    else:
        flash(f'Carnet avec l\'ID "{carnet_id}" non trouvé !', 'error')
    
    return redirect(url_for('carnets_culture_categorie', categorie=categorie))

# Routes pour la gestion des catégories
@app.route('/admin/category/new/<menu_id>')
@admin_required
def admin_new_category_page(menu_id):
    if menu_id == 'ballades':
        flash('Les catégories ne sont pas disponibles pour les ballades', 'error')
        return redirect(url_for('menu_page', menu_id=menu_id))
    
    config = load_config()
    categories = load_categories()
    menu_categories = categories.get(menu_id, {})
    
    return render_template('admin_category_form.html', 
                         menu_id=menu_id, 
                         config=config,
                         categories=menu_categories)

@app.route('/admin/category/create/<menu_id>', methods=['POST'])
@admin_required
def admin_create_category(menu_id):
    if menu_id == 'ballades':
        flash('Les catégories ne sont pas disponibles pour les ballades', 'error')
        return redirect(url_for('menu_page', menu_id=menu_id))
    
    categories = load_categories()
    if menu_id not in categories:
        categories[menu_id] = {}
    
    # Générer un ID unique pour la catégorie
    category_id = request.form.get('category_id', '').strip()
    if not category_id:
        category_id = slugify(request.form.get('nom', ''))
    
    # Vérifier si l'ID existe déjà
    if category_id in categories[menu_id]:
        flash('Une catégorie avec cet ID existe déjà', 'error')
        return redirect(url_for('admin_new_category_page', menu_id=menu_id))
    
    # Créer la nouvelle catégorie
    new_category = {
        'id': category_id,
        'nom': request.form.get('nom', '').strip(),
        'description': request.form.get('description', '').strip(),
        'icon': request.form.get('icon', '📁'),
        'ordre': len(categories[menu_id]) + 1
    }
    
    categories[menu_id][category_id] = new_category
    save_categories(categories)
    
    flash('Catégorie créée avec succès', 'success')
    return redirect(url_for('menu_page', menu_id=menu_id))

@app.route('/admin/category/edit/<menu_id>/<category_id>')
@admin_required
def admin_edit_category_page(menu_id, category_id):
    if menu_id == 'ballades':
        flash('Les catégories ne sont pas disponibles pour les ballades', 'error')
        return redirect(url_for('menu_page', menu_id=menu_id))
    
    config = load_config()
    categories = load_categories()
    
    if menu_id not in categories or category_id not in categories[menu_id]:
        flash('Catégorie non trouvée', 'error')
        return redirect(url_for('menu_page', menu_id=menu_id))
    
    category = categories[menu_id][category_id]
    
    return render_template('admin_category_edit.html', 
                         menu_id=menu_id, 
                         category_id=category_id,
                         category=category,
                         config=config)

@app.route('/admin/category/update/<menu_id>/<category_id>', methods=['POST'])
@admin_required
def admin_update_category(menu_id, category_id):
    if menu_id == 'ballades':
        flash('Les catégories ne sont pas disponibles pour les ballades', 'error')
        return redirect(url_for('menu_page', menu_id=menu_id))
    
    categories = load_categories()
    
    if menu_id not in categories or category_id not in categories[menu_id]:
        flash('Catégorie non trouvée', 'error')
        return redirect(url_for('menu_page', menu_id=menu_id))
    
    # Mettre à jour la catégorie
    categories[menu_id][category_id].update({
        'nom': request.form.get('nom', '').strip(),
        'description': request.form.get('description', '').strip(),
        'icon': request.form.get('icon', '📁')
    })
    
    save_categories(categories)
    
    flash('Catégorie mise à jour avec succès', 'success')
    return redirect(url_for('menu_page', menu_id=menu_id))

@app.route('/admin/category/delete/<menu_id>/<category_id>')
@admin_required
def admin_delete_category(menu_id, category_id):
    if menu_id == 'ballades':
        flash('Les catégories ne sont pas disponibles pour les ballades', 'error')
        return redirect(url_for('menu_page', menu_id=menu_id))
    
    categories = load_categories()
    
    if menu_id not in categories or category_id not in categories[menu_id]:
        flash('Catégorie non trouvée', 'error')
        return redirect(url_for('menu_page', menu_id=menu_id))
    
    # Supprimer la catégorie
    del categories[menu_id][category_id]
    save_categories(categories)
    
    flash('Catégorie supprimée avec succès', 'success')
    return redirect(url_for('menu_page', menu_id=menu_id))

@app.route('/admin/page-title/edit/<menu_id>/<category_id>')
@admin_required
def admin_edit_page_title(menu_id, category_id):
    if menu_id == 'ballades':
        flash('Les pages de titre ne sont pas disponibles pour les ballades', 'error')
        return redirect(url_for('menu_page', menu_id=menu_id))
    
    config = load_config()
    categories = load_categories()
    
    if menu_id not in categories or category_id not in categories[menu_id]:
        flash('Catégorie non trouvée', 'error')
        return redirect(url_for('menu_page', menu_id=menu_id))
    
    category = categories[menu_id][category_id]
    
    return render_template('admin_page_title_edit.html', 
                         menu_id=menu_id, 
                         category_id=category_id,
                         category=category,
                         config=config)

@app.route('/admin/page-title/update/<menu_id>/<category_id>', methods=['POST'])
@admin_required
def admin_update_page_title(menu_id, category_id):
    if menu_id == 'ballades':
        flash('Les pages de titre ne sont pas disponibles pour les ballades', 'error')
        return redirect(url_for('menu_page', menu_id=menu_id))
    
    categories = load_categories()
    
    if menu_id not in categories or category_id not in categories[menu_id]:
        flash('Catégorie non trouvée', 'error')
        return redirect(url_for('carnets_culture_categorie', categorie=category_id))
    
    # Mettre à jour le titre de la page
    new_title = request.form.get('page_title', '').strip()
    if not new_title:
        flash('Le titre de la page ne peut pas être vide', 'error')
        return redirect(url_for('admin_edit_page_title', menu_id=menu_id, category_id=category_id))
    
    categories[menu_id][category_id]['titre'] = new_title
    save_categories(categories)
    
    flash('Titre de la page mis à jour avec succès', 'success')
    return redirect(url_for('carnets_culture_categorie', categorie=category_id))

@app.route('/admin/category-header/edit/<menu_id>/<category_id>')
@admin_required
def admin_edit_category_header(menu_id, category_id):
    if menu_id == 'ballades':
        flash('Les pages de titre ne sont pas disponibles pour les ballades', 'error')
        return redirect(url_for('menu_page', menu_id=menu_id))
    
    config = load_config()
    
    # Définir les informations de la catégorie (même que dans carnets_culture_categorie)
    categories_info = {
        'musees_expositions': {
            'titre': '🏛️ Musées & Expositions',
            'description': 'Découvrez les plus beaux musées et expositions de Paris. Chaque carnet vous guide à travers les collections les plus remarquables.',
            'icon': '🏛️',
            'nom_court': 'musée'
        },
        'theatre_spectacles': {
            'titre': '🎭 Théâtre & Spectacles',
            'description': 'Plongez dans l\'univers du théâtre et des spectacles. Découvrez les salles mythiques et les productions les plus captivantes.',
            'icon': '🎭',
            'nom_court': 'théâtre'
        },
        'litterature': {
            'titre': '📚 Littérature',
            'description': 'Explorez les lieux qui ont inspiré les plus grands écrivains. Suivez les traces des auteurs et découvrez leurs univers.',
            'icon': '📚',
            'nom_court': 'littérature'
        }
    }
    
    categorie_info = categories_info.get(category_id, {
        'titre': category_id.replace('_', ' ').title(),
        'description': 'Carnets de culture',
        'icon': '📖',
        'nom_court': 'culture'
    })
    
    # Utiliser les données sauvegardées si elles existent
    if 'category_headers' in config and category_id in config['category_headers']:
        saved_data = config['category_headers'][category_id]
        if 'titre' in saved_data:
            categorie_info['titre'] = saved_data['titre']
        if 'description' in saved_data:
            categorie_info['description'] = saved_data['description']
    
    return render_template('admin_category_header_edit.html', 
                         menu_id=menu_id, 
                         category_id=category_id,
                         category=categorie_info,
                         config=config)

@app.route('/admin/category-header/update/<menu_id>/<category_id>', methods=['POST'])
@admin_required
def admin_update_category_header(menu_id, category_id):
    if menu_id == 'ballades':
        flash('Les pages de titre ne sont pas disponibles pour les ballades', 'error')
        return redirect(url_for('menu_page', menu_id=menu_id))
    
    # Mettre à jour le titre et la description de la section
    new_title = request.form.get('section_title', '').strip()
    new_description = request.form.get('section_description', '').strip()
    
    if not new_title:
        flash('Le titre de la section ne peut pas être vide', 'error')
        return redirect(url_for('admin_edit_category_header', menu_id=menu_id, category_id=category_id))
    
    # Sauvegarder dans le fichier de configuration
    config = load_config()
    if 'category_headers' not in config:
        config['category_headers'] = {}
    
    if category_id not in config['category_headers']:
        config['category_headers'][category_id] = {}
    
    config['category_headers'][category_id]['titre'] = new_title
    config['category_headers'][category_id]['description'] = new_description
    save_config(config)
    
    flash('Section mise à jour avec succès', 'success')
    return redirect(url_for('carnets_culture_categorie', categorie=category_id))

# Routes pour les carnets d'organisation
@app.route('/carnets-organisation/<category_id>')
def carnets_organisation_categorie(category_id):
    config = load_config()
    categories_organisation = load_categories_organisation()
    carnets_organisation = load_carnets_organisation()
    
    # Trouver la catégorie
    category = categories_organisation.get('carnet_organisation', {}).get(category_id)
    if not category:
        return 'Catégorie non trouvée', 404
    
    # Récupérer les carnets de cette catégorie
    carnets = carnets_organisation.get(category_id, [])
    
    return render_template('carnets_organisation_categorie.html',
                         category=category,
                         carnets=carnets,
                         config=config,
                         category_id=category_id)

@app.route('/carnet-organisation/<category_id>/<slug>')
def carnet_organisation_detail(category_id, slug):
    config = load_config()
    categories_organisation = load_categories_organisation()
    carnets_organisation = load_carnets_organisation()
    
    # Trouver la catégorie
    category = categories_organisation.get('carnet_organisation', {}).get(category_id)
    if not category:
        return 'Catégorie non trouvée', 404
    
    # Trouver le carnet
    carnets = carnets_organisation.get(category_id, [])
    carnet = next((c for c in carnets if c['id'] == slug), None)
    if not carnet:
        return 'Carnet non trouvé', 404
    
    return render_template('carnet_organisation_detail.html',
                         category=category,
                         carnet=carnet,
                         config=config,
                         category_id=category_id)

@app.route('/admin/carnet-organisation/new/<category_id>')
@admin_required
def admin_new_carnet_organisation_page(category_id):
    config = load_config()
    categories_organisation = load_categories_organisation()
    
    # Trouver la catégorie
    category = categories_organisation.get('carnet_organisation', {}).get(category_id)
    if not category:
        return 'Catégorie non trouvée', 404
    
    return render_template('admin_carnet_organisation_form.html',
                         category=category,
                         config=config,
                         category_id=category_id)

@app.route('/admin/carnet-organisation/create/<category_id>', methods=['POST'])
@admin_required
def admin_create_carnet_organisation(category_id):
    config = load_config()
    categories_organisation = load_categories_organisation()
    carnets_organisation = load_carnets_organisation()
    
    # Trouver la catégorie
    category = categories_organisation.get('carnet_organisation', {}).get(category_id)
    if not category:
        flash('Catégorie non trouvée', 'error')
        return redirect(url_for('admin_dashboard'))
    
    # Récupérer les données du formulaire
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    
    if not title:
        flash('Le titre est obligatoire', 'error')
        return redirect(url_for('admin_new_carnet_organisation_page', category_id=category_id))
    
    # Gérer l'upload d'image
    image_url = ''
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename and allowed_file(file.filename):
            image_url = save_uploaded_file(file, 'carnets_organisation')
    
    # Créer le nouveau carnet
    new_carnet = {
        'id': str(uuid.uuid4()),
        'title': title,
        'description': description,
        'image_url': image_url,
        'date_created': datetime.now().isoformat()
    }
    
    # Ajouter le carnet à la catégorie
    if category_id not in carnets_organisation:
        carnets_organisation[category_id] = []
    
    carnets_organisation[category_id].append(new_carnet)
    save_carnets_organisation(carnets_organisation)
    
    # Si c'est un bullet journal, créer aussi l'entrée dans bullet_journal_pages.json
    if category_id == 'bullet_journal':
        bullet_journal_data = load_bullet_journal_pages()
        
        # S'assurer que la structure existe
        if 'pages' not in bullet_journal_data:
            bullet_journal_data['pages'] = {}
        if 'bullet_journal' not in bullet_journal_data['pages']:
            bullet_journal_data['pages']['bullet_journal'] = {}
        
        # Créer le nouveau journal dans la structure bullet journal
        bullet_journal_data['pages']['bullet_journal'][new_carnet['id']] = {
            'id': new_carnet['id'],
            'title': new_carnet['title'],
            'description': new_carnet['description'],
            'created_at': new_carnet['date_created'],
            'pages': []
        }
        
        save_bullet_journal_pages(bullet_journal_data)
    
    flash('Carnet d\'organisation créé avec succès', 'success')
    
    # Si c'est un bullet journal, rediriger vers l'interface d'édition
    if category_id == 'bullet_journal':
        return redirect(url_for('bullet_journal_view', journal_id=new_carnet['id']))
    else:
        return redirect(url_for('carnets_organisation_categorie', category_id=category_id))

@app.route('/admin/carnet-organisation/edit/<category_id>/<carnet_id>')
@admin_required
def admin_edit_carnet_organisation_page(category_id, carnet_id):
    config = load_config()
    categories_organisation = load_categories_organisation()
    carnets_organisation = load_carnets_organisation()
    
    # Trouver la catégorie
    category = categories_organisation.get('carnet_organisation', {}).get(category_id)
    if not category:
        return 'Catégorie non trouvée', 404
    
    # Trouver le carnet
    carnets = carnets_organisation.get(category_id, [])
    carnet = next((c for c in carnets if c['id'] == carnet_id), None)
    if not carnet:
        return 'Carnet non trouvé', 404
    
    return render_template('admin_carnet_organisation_edit.html',
                         category=category,
                         carnet=carnet,
                         config=config,
                         category_id=category_id,
                         carnet_id=carnet_id)

@app.route('/admin/carnet-organisation/update/<category_id>/<carnet_id>', methods=['POST'])
@admin_required
def admin_update_carnet_organisation(category_id, carnet_id):
    config = load_config()
    categories_organisation = load_categories_organisation()
    carnets_organisation = load_carnets_organisation()
    
    # Trouver la catégorie
    category = categories_organisation.get('carnet_organisation', {}).get(category_id)
    if not category:
        flash('Catégorie non trouvée', 'error')
        return redirect(url_for('admin_dashboard'))
    
    # Trouver le carnet
    carnets = carnets_organisation.get(category_id, [])
    carnet_index = next((i for i, c in enumerate(carnets) if c['id'] == carnet_id), None)
    if carnet_index is None:
        flash('Carnet non trouvé', 'error')
        return redirect(url_for('admin_dashboard'))
    
    # Récupérer les données du formulaire
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    
    if not title:
        flash('Le titre est obligatoire', 'error')
        return redirect(url_for('admin_edit_carnet_organisation_page', category_id=category_id, carnet_id=carnet_id))
    
    # Gérer l'upload d'image
    image_url = carnets[carnet_index]['image_url']
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename and allowed_file(file.filename):
            # Supprimer l'ancienne image si elle existe
            if image_url and not image_url.startswith('http'):
                delete_file(image_url)
            image_url = save_uploaded_file(file, 'carnets_organisation')
    
    # Mettre à jour le carnet
    carnets[carnet_index].update({
        'title': title,
        'description': description,
        'image_url': image_url
    })
    
    save_carnets_organisation(carnets_organisation)
    flash('Carnet d\'organisation mis à jour avec succès', 'success')
    return redirect(url_for('carnets_organisation_categorie', category_id=category_id))

@app.route('/admin/carnet-organisation/delete/<category_id>/<carnet_id>')
@admin_required
def admin_delete_carnet_organisation(category_id, carnet_id):
    carnets_organisation = load_carnets_organisation()
    
    # Trouver le carnet
    carnets = carnets_organisation.get(category_id, [])
    carnet = next((c for c in carnets if c['id'] == carnet_id), None)
    if not carnet:
        flash('Carnet non trouvé', 'error')
        return redirect(url_for('admin_dashboard'))
    
    # Supprimer l'image si elle existe
    if carnet.get('image_url') and not carnet['image_url'].startswith('http'):
        delete_file(carnet['image_url'])
    
    # Supprimer le carnet
    carnets_organisation[category_id] = [c for c in carnets if c['id'] != carnet_id]
    save_carnets_organisation(carnets_organisation)
    
    flash('Carnet d\'organisation supprimé avec succès', 'success')
    return redirect(url_for('carnets_organisation_categorie', category_id=category_id))

# Routes pour la gestion des catégories d'organisation
@app.route('/admin/category-organisation/edit/<category_id>')
@admin_required
def admin_edit_category_organisation_page(category_id):
    config = load_config()
    categories_organisation = load_categories_organisation()
    
    # Trouver la catégorie
    category = categories_organisation.get('carnet_organisation', {}).get(category_id)
    if not category:
        flash('Catégorie non trouvée', 'error')
        return redirect(url_for('menu_page', menu_id='carnet_organisation'))
    
    return render_template('admin_category_organisation_edit.html',
                         category=category,
                         config=config,
                         category_id=category_id)

@app.route('/admin/category-organisation/update/<category_id>', methods=['POST'])
@admin_required
def admin_update_category_organisation(category_id):
    categories_organisation = load_categories_organisation()
    
    # Trouver la catégorie
    if 'carnet_organisation' not in categories_organisation or category_id not in categories_organisation['carnet_organisation']:
        flash('Catégorie non trouvée', 'error')
        return redirect(url_for('menu_page', menu_id='carnet_organisation'))
    
    # Récupérer les données du formulaire
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    icon = request.form.get('icon', '').strip()
    
    if not name:
        flash('Le nom de la catégorie est obligatoire', 'error')
        return redirect(url_for('admin_edit_category_organisation_page', category_id=category_id))
    
    # Mettre à jour la catégorie
    categories_organisation['carnet_organisation'][category_id].update({
        'name': name,
        'description': description,
        'icon': icon
    })
    
    save_categories_organisation(categories_organisation)
    flash('Catégorie mise à jour avec succès', 'success')
    return redirect(url_for('menu_page', menu_id='carnet_organisation'))

@app.route('/admin/category-organisation/delete/<category_id>')
@admin_required
def admin_delete_category_organisation(category_id):
    categories_organisation = load_categories_organisation()
    carnets_organisation = load_carnets_organisation()
    
    # Vérifier si la catégorie existe
    if 'carnet_organisation' not in categories_organisation or category_id not in categories_organisation['carnet_organisation']:
        flash('Catégorie non trouvée', 'error')
        return redirect(url_for('menu_page', menu_id='carnet_organisation'))
    
    # Supprimer les carnets de cette catégorie
    if category_id in carnets_organisation:
        # Supprimer les images des carnets
        for carnet in carnets_organisation[category_id]:
            if carnet.get('image_url') and not carnet['image_url'].startswith('http'):
                delete_file(carnet['image_url'])
        del carnets_organisation[category_id]
        save_carnets_organisation(carnets_organisation)
    
    # Supprimer la catégorie
    del categories_organisation['carnet_organisation'][category_id]
    save_categories_organisation(categories_organisation)
    
    flash('Catégorie supprimée avec succès', 'success')
    return redirect(url_for('menu_page', menu_id='carnet_organisation'))

# Routes pour le Bullet Journal
@app.route('/bullet-journal/<journal_id>')
def bullet_journal_view(journal_id):
    config = load_config()
    bullet_journal_data = load_bullet_journal_pages()
    
    # Trouver le journal
    journal = bullet_journal_data.get('pages', {}).get('bullet_journal', {}).get(journal_id)
    if not journal:
        return 'Journal non trouvé', 404
    
    return render_template('bullet_journal_view.html',
                         journal=journal,
                         journal_id=journal_id,
                         config=config)

@app.route('/bullet-journal/<journal_id>/page/<page_id>')
def bullet_journal_page_edit(journal_id, page_id):
    config = load_config()
    bullet_journal_data = load_bullet_journal_pages()
    
    # Trouver le journal et la page
    journal = bullet_journal_data.get('pages', {}).get('bullet_journal', {}).get(journal_id)
    if not journal:
        return 'Journal non trouvé', 404
    
    page = next((p for p in journal.get('pages', []) if p['id'] == page_id), None)
    if not page:
        return 'Page non trouvée', 404
    
    templates = bullet_journal_data.get('templates', {})
    media_library = bullet_journal_data.get('media_library', {})
    
    return render_template('bullet_journal_complete.html',
                         journal=journal,
                         page=page,
                         journal_id=journal_id,
                         page_id=page_id,
                         templates=templates,
                         media_library=media_library,
                         config=config)

@app.route('/bullet-journal/<journal_id>/page/new')
def bullet_journal_new_page(journal_id):
    config = load_config()
    bullet_journal_data = load_bullet_journal_pages()
    
    # Trouver le journal
    journal = bullet_journal_data.get('pages', {}).get('bullet_journal', {}).get(journal_id)
    if not journal:
        return 'Journal non trouvé', 404
    
    templates = bullet_journal_data.get('templates', {})
    
    return render_template('bullet_journal_new_page.html',
                         journal=journal,
                         journal_id=journal_id,
                         templates=templates,
                         config=config)

@app.route('/bullet-journal/<journal_id>/page/create', methods=['POST'])
def bullet_journal_create_page(journal_id):
    bullet_journal_data = load_bullet_journal_pages()
    
    # Trouver le journal
    if 'pages' not in bullet_journal_data or 'bullet_journal' not in bullet_journal_data['pages'] or journal_id not in bullet_journal_data['pages']['bullet_journal']:
        return 'Journal non trouvé', 404
    
    # Récupérer les données du formulaire
    title = request.form.get('title', '').strip()
    template = request.form.get('template', 'blank')
    
    if not title:
        flash('Le titre de la page est obligatoire', 'error')
        return redirect(url_for('bullet_journal_new_page', journal_id=journal_id))
    
    # Créer la nouvelle page
    new_page = {
        'id': str(uuid.uuid4()),
        'title': title,
        'template': template,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'elements': []
    }
    
    # Ajouter la page au journal
    if 'pages' not in bullet_journal_data['pages']['bullet_journal'][journal_id]:
        bullet_journal_data['pages']['bullet_journal'][journal_id]['pages'] = []
    
    bullet_journal_data['pages']['bullet_journal'][journal_id]['pages'].append(new_page)
    save_bullet_journal_pages(bullet_journal_data)
    
    flash('Page créée avec succès', 'success')
    return redirect(url_for('bullet_journal_page_edit', journal_id=journal_id, page_id=new_page['id']))

@app.route('/bullet-journal/<journal_id>/page/<page_id>/save', methods=['POST'])
def bullet_journal_save_page(journal_id, page_id):
    bullet_journal_data = load_bullet_journal_pages()
    
    # Trouver le journal et la page
    if 'pages' not in bullet_journal_data or 'bullet_journal' not in bullet_journal_data['pages'] or journal_id not in bullet_journal_data['pages']['bullet_journal']:
        return jsonify({'success': False, 'error': 'Journal non trouvé'}), 404
    
    journal = bullet_journal_data['pages']['bullet_journal'][journal_id]
    page_index = next((i for i, p in enumerate(journal.get('pages', [])) if p['id'] == page_id), None)
    
    if page_index is None:
        return jsonify({'success': False, 'error': 'Page non trouvée'}), 404
    
    # Récupérer les données JSON de la page
    page_data = request.get_json()
    if not page_data:
        return jsonify({'success': False, 'error': 'Données invalides'}), 400
    
    print(f"Sauvegarde de la page {page_id} dans le journal {journal_id}")
    print(f"Données reçues: {page_data}")
    
    # Mettre à jour la page avec le nouveau format
    journal['pages'][page_index].update({
        'title': page_data.get('title', journal['pages'][page_index].get('title', '')),
        'content': page_data.get('content', ''),
        'notebook': page_data.get('notebook', 'daily'),
        'stickers': page_data.get('stickers', []),
        'tasks': page_data.get('tasks', []),
        'drawing': page_data.get('drawing', {}),
        'timestamp': page_data.get('timestamp', ''),
        'updated_at': datetime.now().isoformat()
    })
    
    print(f"Page sauvegardée: {journal['pages'][page_index]}")
    
    save_bullet_journal_pages(bullet_journal_data)
    
    return jsonify({'success': True, 'message': 'Page sauvegardée avec succès'})

@app.route('/bullet-journal/<journal_id>/page/<page_id>/export')
def bullet_journal_export_page(journal_id, page_id):
    bullet_journal_data = load_bullet_journal_pages()
    
    # Trouver le journal et la page
    journal = bullet_journal_data.get('pages', {}).get('bullet_journal', {}).get(journal_id)
    if not journal:
        return 'Journal non trouvé', 404
    
    page = next((p for p in journal.get('pages', []) if p['id'] == page_id), None)
    if not page:
        return 'Page non trouvée', 404
    
    # Pour l'instant, retourner la page en JSON
    # Plus tard, on pourra implémenter l'export PDF
    return jsonify(page)

@app.route('/bullet-journal/<journal_id>/page/<page_id>/data')
def bullet_journal_get_page_data(journal_id, page_id):
    bullet_journal_data = load_bullet_journal_pages()
    
    # Trouver le journal et la page
    journal = bullet_journal_data.get('pages', {}).get('bullet_journal', {}).get(journal_id)
    if not journal:
        return jsonify({'success': False, 'error': 'Journal non trouvé'}), 404
    
    page = next((p for p in journal.get('pages', []) if p['id'] == page_id), None)
    if not page:
        return jsonify({'success': False, 'error': 'Page non trouvée'}), 404
    
    return jsonify({
        'success': True,
        'page': {
            'id': page['id'],
            'title': page.get('title', ''),
            'content': page.get('content', ''),
            'notebook': page.get('notebook', 'daily'),
            'stickers': page.get('stickers', []),
            'tasks': page.get('tasks', []),
            'drawing': page.get('drawing', {}),
            'timestamp': page.get('timestamp', '')
        }
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
