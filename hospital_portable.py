"""
🏥 SYSTÈME HOSPITALIER NATIONAL CAMEROUN 🇨🇲
Version Finale Améliorée - Avec actualisation automatique
Toutes les fonctionnalités de base + améliorations + nouvelles tables
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
from datetime import datetime
import random
import re
import csv
import os
import shutil

class HospitalCamerounApp:
    def __init__(self, root):
        """Initialise l'application"""
        self.root = root
        self.root.title("🏥 Système Hospitalier - Cameroun 🇨🇲")
        
        # Configuration fenêtre
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{int(screen_width*0.85)}x{int(screen_height*0.85)}")
        
        # Couleurs
        self.colors = {
            'primary': '#2563eb',
            'secondary': '#8b5cf6',
            'success': '#22c55e',
            'danger': '#ef4444',
            'warning': '#f59e0b',
            'info': '#06b6d4',
            'pediatrie': '#ec4899',
            'adulte': '#4f46e5',
            'bg_primary': '#ffffff',
            'bg_secondary': '#f8fafc'
        }
        
        self.root.configure(bg=self.colors['bg_secondary'])
        
        # Variables
        self.current_user = None
        self.user_role = None
        
        # Base de données
        self.db_path = "hospital_cameroun.db"
        
        # Créer une sauvegarde automatique
        self.create_backup()
        
        # Vérifier et mettre à jour la base de données
        self.setup_database()
        self.update_database_schema()
        
        # Démarrer
        self.show_login()
    
    def create_backup(self):
        """Crée une sauvegarde automatique de la base de données"""
        try:
            if os.path.exists(self.db_path):
                backup_name = f"backup_hospital_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                shutil.copy2(self.db_path, backup_name)
                print(f"✅ Sauvegarde créée : {backup_name}")
        except Exception as e:
            print(f"⚠️ Erreur lors de la sauvegarde : {e}")
    
    def setup_database(self):
        """Crée la base de données avec tables améliorées"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Patients (inchangé)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_dossier TEXT UNIQUE NOT NULL,
                nom TEXT NOT NULL,
                prenom TEXT NOT NULL,
                date_naissance TEXT NOT NULL,
                sexe TEXT CHECK(sexe IN ('M', 'F')),
                telephone TEXT NOT NULL,
                adresse TEXT,
                type_patient TEXT CHECK(type_patient IN ('adulte', 'enfant')),
                cni TEXT,
                cni_parent TEXT,
                pere_nom TEXT,
                mere_nom TEXT,
                poids REAL,
                taille REAL,
                date_creation TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Personnel (inchangé)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS personnel (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                nom TEXT NOT NULL,
                prenom TEXT NOT NULL,
                role TEXT DEFAULT 'personnel',
                specialite TEXT,
                date_creation TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Consultations (inchangé)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS consultations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                personnel_id INTEGER,
                motif TEXT NOT NULL,
                diagnostic TEXT NOT NULL,
                prescription TEXT,
                temperature REAL,
                tension TEXT,
                date_consultation TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients (id),
                FOREIGN KEY (personnel_id) REFERENCES personnel (id)
            )
        ''')
        
        # Hospitalisations (inchangé)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hospitalisations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                chambre TEXT,
                lit TEXT,
                date_entree TEXT DEFAULT CURRENT_TIMESTAMP,
                date_sortie TEXT,
                statut TEXT DEFAULT 'en_cours',
                motif TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
        ''')
        
        # Rendez-vous (inchangé)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rendez_vous (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                date_rdv TEXT NOT NULL,
                heure_rdv TEXT NOT NULL,
                motif TEXT,
                statut TEXT DEFAULT 'planifie',
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
        ''')
        
        # Factures (inchangé)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS factures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                type TEXT,
                montant REAL DEFAULT 0,
                paye REAL DEFAULT 0,
                reste REAL DEFAULT 0,
                statut TEXT DEFAULT 'impaye',
                date_facture TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
        ''')
        
        # Vaccinations (inchangé)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vaccinations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                vaccin TEXT NOT NULL,
                date_vaccination TEXT DEFAULT CURRENT_TIMESTAMP,
                dose TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
        ''')
        
        # Table audit_log pour journalisation
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                table_name TEXT NOT NULL,
                record_id INTEGER,
                details TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES personnel (id)
            )
        ''')
        
        # Table hospital_settings pour paramètres
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hospital_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_key TEXT UNIQUE NOT NULL,
                setting_value TEXT,
                description TEXT
            )
        ''')
        
        # Table prescriptions_details pour médicaments
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prescriptions_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                consultation_id INTEGER NOT NULL,
                medicament TEXT NOT NULL,
                posologie TEXT,
                duree TEXT,
                FOREIGN KEY (consultation_id) REFERENCES consultations (id)
            )
        ''')
        
        # Insérer paramètres par défaut
        default_settings = [
            ('hospital_name', 'Hôpital National - Cameroun', 'Nom de l\'hôpital'),
            ('currency', 'FCFA', 'Devise utilisée'),
            ('country', 'CM', 'Code pays'),
            ('min_consultation_fee', '5000', 'Tarif consultation minimum'),
            ('emergency_phone', '112', 'Numéro urgence'),
            ('working_hours_start', '08:00', 'Heure ouverture'),
            ('working_hours_end', '18:00', 'Heure fermeture')
        ]
        
        for key, value, desc in default_settings:
            cursor.execute('''
                INSERT OR IGNORE INTO hospital_settings (setting_key, setting_value, description)
                VALUES (?, ?, ?)
            ''', (key, value, desc))
        
        # Créer admin si inexistant
        cursor.execute("SELECT COUNT(*) FROM personnel WHERE email='admin@hospital.cm'")
        if cursor.fetchone()[0] == 0:
            hashed = hashlib.sha256("admin123".encode()).hexdigest()
            cursor.execute(
                "INSERT INTO personnel (email, password, nom, prenom, role, specialite) VALUES (?, ?, ?, ?, ?, ?)",
                ('admin@hospital.cm', hashed, 'Admin', 'System', 'admin', 'Administration')
            )
            print("✅ Compte admin créé")
        
        conn.commit()
        conn.close()
        print("✅ Base de données créée avec améliorations")
    
    def update_database_schema(self):
        """Met à jour le schéma de la base de données avec nouvelles tables"""
        print("🔄 Mise à jour du schéma de la base de données...")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # ========== 1. AJOUTER DES COLONNES MANQUANTES ==========
            print("📝 Vérification des colonnes manquantes...")
            
            # Liste des colonnes à ajouter
            columns_to_add = [
                ('patients', 'groupe_sanguin', 'TEXT'),
                ('patients', 'allergies', 'TEXT'),
                ('patients', 'antecedents', 'TEXT'),
                ('patients', 'profession', 'TEXT'),
                ('patients', 'email', 'TEXT'),
                ('consultations', 'poids', 'REAL'),
                ('consultations', 'taille', 'REAL'),
                ('consultations', 'imc', 'REAL'),
                ('consultations', 'pouls', 'INTEGER'),
                ('consultations', 'frequence_respiratoire', 'INTEGER'),
                ('factures', 'numero_facture', 'TEXT'),
                ('factures', 'mode_paiement', 'TEXT'),
                ('factures', 'date_paiement', 'TEXT'),
                ('factures', 'reference_paiement', 'TEXT')
                ('patients', 'lieu_naissance', 'TEXT'),
                ('patients', 'etat_civil', 'TEXT'),
                ('patients', 'nationalite', 'TEXT'),
                ('patients', 'photo', 'TEXT'),
                ('patients', 'assurance', 'TEXT'),
                ('patients', 'numero_assurance', 'TEXT'),
                ('patients', 'contact_urgence_nom', 'TEXT'),
                ('patients', 'contact_urgence_telephone', 'TEXT'),
                ('patients', 'contact_urgence_lien', 'TEXT'),
                ('consultations', 'heure_consultation', 'TEXT'),
                ('consultations', 'type_consultation', 'TEXT'),
                ('factures', 'tva', 'REAL'),
                ('factures', 'remise', 'REAL'),
                ('factures', 'net_a_payer', 'REAL'),
                ('hospitalisations', 'medecin_traitant', 'TEXT'),
                ('hospitalisations', 'service', 'TEXT'),
                ('personnel', 'telephone', 'TEXT'),
                ('personnel', 'matricule', 'TEXT'),
                ('personnel', 'date_embauche', 'TEXT'),
                ('personnel', 'statut', 'TEXT'),
                ('rendez_vous', 'duree_prevue', 'INTEGER'),
                ('rendez_vous', 'type_rdv', 'TEXT'),
                ('vaccinations', 'lot', 'TEXT'),
                ('vaccinations', 'fabricant', 'TEXT')
            ]
            
            for table, column, col_type in columns_to_add:
                try:
                    # Vérifier si la colonne existe déjà
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = [col[1] for col in cursor.fetchall()]
                    
                    if column not in columns:
                        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
                        print(f"   ✅ Colonne '{column}' ajoutée à la table '{table}'")
                    else:
                        print(f"   ℹ️  Colonne '{column}' existe déjà dans '{table}'")
                        
                except Exception as e:
                    print(f"   ⚠️  Erreur avec {table}.{column}: {e}")
            
            # ========== 2. CRÉER LES NOUVELLES TABLES ==========
            print("📊 Création des nouvelles tables...")
            
            # Table des médicaments
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS medicaments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL,
                    code TEXT UNIQUE NOT NULL,
                    categorie TEXT,
                    forme TEXT,
                    dosage TEXT,
                    stock INTEGER DEFAULT 0,
                    seuil_alerte INTEGER DEFAULT 10,
                    prix_unitaire REAL DEFAULT 0,
                    date_expiration TEXT,
                    date_ajout TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("   ✅ Table 'medicaments' créée")
            
            # Table des services
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS services (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT UNIQUE NOT NULL,
                    description TEXT,
                    responsable_id INTEGER,
                    tel_interne TEXT,
                    couleur TEXT DEFAULT '#4f46e5',
                    FOREIGN KEY (responsable_id) REFERENCES personnel (id)
                )
            ''')
            print("   ✅ Table 'services' créée")
            
            # Table des chambres
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chambres (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero TEXT UNIQUE NOT NULL,
                    type TEXT CHECK(type IN ('simple', 'double', 'collective', 'VIP')),
                    service_id INTEGER,
                    nombre_lits INTEGER DEFAULT 1,
                    lits_disponibles INTEGER DEFAULT 1,
                    prix_jour REAL DEFAULT 0,
                    statut TEXT DEFAULT 'disponible',
                    FOREIGN KEY (service_id) REFERENCES services (id)
                )
            ''')
            print("   ✅ Table 'chambres' créée")
            
            # Table des examens
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS examens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    consultation_id INTEGER NOT NULL,
                    type_examen TEXT NOT NULL,
                    resultat TEXT,
                    date_prescription TEXT DEFAULT CURRENT_TIMESTAMP,
                    date_realisation TEXT,
                    statut TEXT DEFAULT 'prescrit',
                    fichier_resultat TEXT,
                    FOREIGN KEY (consultation_id) REFERENCES consultations (id)
                )
            ''')
            print("   ✅ Table 'examens' créée")
            
            # Table des ordonnances
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ordonnances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    consultation_id INTEGER NOT NULL,
                    medicament_id INTEGER NOT NULL,
                    quantite INTEGER DEFAULT 1,
                    posologie TEXT,
                    duree_jours INTEGER,
                    notes TEXT,
                    date_prescription TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (consultation_id) REFERENCES consultations (id),
                    FOREIGN KEY (medicament_id) REFERENCES medicaments (id)
                )
            ''')
            print("   ✅ Table 'ordonnances' créée")
            
            # ========== 3. INSÉRER DES DONNÉES PAR DÉFAUT ==========
            print("📥 Insertion des données par défaut...")
            
            # Services par défaut
            services_defaut = [
                ('Urgences', 'Service des urgences 24h/24', None, '101', '#ef4444'),
                ('Pédiatrie', 'Service pédiatrique', None, '102', '#ec4899'),
                ('Maternité', 'Service maternité', None, '103', '#8b5cf6'),
                ('Chirurgie', 'Service chirurgie générale', None, '104', '#f59e0b'),
                ('Médecine Interne', 'Service médecine interne', None, '105', '#06b6d4'),
                ('Radiologie', 'Service imagerie médicale', None, '106', '#22c55e'),
                ('Laboratoire', 'Analyses médicales', None, '107', '#10b981'),
                ('Pharmacie', 'Service pharmacie', None, '108', '#8b5cf6')
            ]
            
            for service in services_defaut:
                cursor.execute('''
                    INSERT OR IGNORE INTO services (nom, description, responsable_id, tel_interne, couleur)
                    VALUES (?, ?, ?, ?, ?)
                ''', service)
            print("   ✅ Services par défaut insérés")
            
            # Chambres par défaut
            for i in range(1, 21):
                type_chambre = 'simple' if i <= 10 else 'double'
                service_id = 1 if i <= 5 else 2 if i <= 10 else 3 if i <= 15 else 4
                prix = 15000 if type_chambre == 'simple' else 25000
                
                cursor.execute('''
                    INSERT OR IGNORE INTO chambres (numero, type, service_id, prix_jour)
                    VALUES (?, ?, ?, ?)
                ''', (f'CH{i:03d}', type_chambre, service_id, prix))
            print("   ✅ Chambres par défaut insérées")
            
            # Médicaments par défaut
            medicaments_defaut = [
                ('Paracétamol 500mg', 'PARA500', 'Antalgique', 'Comprimé', '500mg', 100, 20, 150),
                ('Amoxicilline 500mg', 'AMOX500', 'Antibiotique', 'Comprimé', '500mg', 50, 10, 500),
                ('Ibuprofène 400mg', 'IBUP400', 'Anti-inflammatoire', 'Comprimé', '400mg', 80, 15, 300),
                ('Doliprane 1000mg', 'DOLI1000', 'Antalgique', 'Comprimé', '1000mg', 60, 10, 250),
                ('Vitamine C 500mg', 'VITC500', 'Vitamine', 'Comprimé', '500mg', 200, 30, 100)
            ]
            
            for med in medicaments_defaut:
                cursor.execute('''
                    INSERT OR IGNORE INTO medicaments (nom, code, categorie, forme, dosage, stock, seuil_alerte, prix_unitaire)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', med)
            print("   ✅ Médicaments par défaut insérés")
            
            # ========== 4. CRÉER DES INDEX POUR PERFORMANCE ==========
            print("⚡ Création des index de performance...")
            
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_patients_numero_dossier ON patients(numero_dossier)",
                "CREATE INDEX IF NOT EXISTS idx_patients_nom_prenom ON patients(nom, prenom)",
                "CREATE INDEX IF NOT EXISTS idx_patients_telephone ON patients(telephone)",
                "CREATE INDEX IF NOT EXISTS idx_consultations_patient_id ON consultations(patient_id)",
                "CREATE INDEX IF NOT EXISTS idx_consultations_date ON consultations(date_consultation)",
                "CREATE INDEX IF NOT EXISTS idx_hospitalisations_statut ON hospitalisations(statut)",
                "CREATE INDEX IF NOT EXISTS idx_rendez_vous_date ON rendez_vous(date_rdv)",
                "CREATE INDEX IF NOT EXISTS idx_factures_statut ON factures(statut)"
            ]
            
            for index_sql in indexes:
                try:
                    cursor.execute(index_sql)
                except:
                    pass
            print("   ✅ Index créés")
            
            # ========== 5. CRÉER DES TRIGGERS ==========
            print("🤖 Création des triggers d'automatisation...")
            
            # Trigger pour générer automatiquement le numéro de dossier
            cursor.execute('''
                CREATE TRIGGER IF NOT EXISTS generate_numero_dossier
                AFTER INSERT ON patients
                FOR EACH ROW
                WHEN NEW.numero_dossier IS NULL
                BEGIN
                    UPDATE patients 
                    SET numero_dossier = (
                        CASE 
                            WHEN NEW.type_patient = 'enfant' 
                            THEN 'ENF' || strftime('%Y%m%d') || substr('0000' || CAST(NEW.id AS TEXT), -4)
                            ELSE 'ADT' || strftime('%Y%m%d') || substr('0000' || CAST(NEW.id AS TEXT), -4)
                        END
                    )
                    WHERE id = NEW.id;
                END;
            ''')
            
            # Trigger pour calculer automatiquement le reste à payer
            cursor.execute('''
                CREATE TRIGGER IF NOT EXISTS calculate_reste_facture
                AFTER UPDATE OF paye ON factures
                FOR EACH ROW
                BEGIN
                    UPDATE factures 
                    SET reste = montant - NEW.paye,
                        statut = CASE 
                                    WHEN (montant - NEW.paye) <= 0 THEN 'paye'
                                    WHEN NEW.paye > 0 THEN 'partiel'
                                    ELSE 'impaye'
                                 END
                    WHERE id = NEW.id;
                END;
            ''')
            
            print("   ✅ Triggers créés")
            
            # ========== 6. CRÉER DES VUES ==========
            print("👁️ Création des vues...")
            
            # Vue pour les patients avec leurs dernières consultations
            cursor.execute('''
                CREATE VIEW IF NOT EXISTS vue_patients_consultations AS
                SELECT 
                    p.id,
                    p.numero_dossier,
                    p.nom || ' ' || p.prenom as patient_nom,
                    p.type_patient,
                    p.telephone,
                    MAX(c.date_consultation) as derniere_consultation,
                    COUNT(c.id) as nb_consultations
                FROM patients p
                LEFT JOIN consultations c ON p.id = c.patient_id
                GROUP BY p.id
            ''')
            
            # Vue pour les statistiques quotidiennes
            cursor.execute('''
                CREATE VIEW IF NOT EXISTS vue_statistiques_journalieres AS
                SELECT 
                    date('now') as date_jour,
                    (SELECT COUNT(*) FROM patients WHERE date(date_creation) = date('now')) as nouveaux_patients,
                    (SELECT COUNT(*) FROM consultations WHERE date(date_consultation) = date('now')) as consultations,
                    (SELECT COUNT(*) FROM rendez_vous WHERE date_rdv = date('now') AND statut = 'planifie') as rdv_aujourdhui,
                    (SELECT COUNT(*) FROM hospitalisations WHERE statut = 'en_cours') as hospitalises,
                    (SELECT COALESCE(SUM(montant), 0) FROM factures WHERE date(date_facture) = date('now')) as facturation_jour
            ''')
            
            print("   ✅ Vues créées")
            
            conn.commit()
            print("✅ Mise à jour du schéma terminée avec succès!")
            
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    # ==================== FONCTIONS UTILITAIRES AMÉLIORÉES ====================
    
    def get_connection(self):
        """Connexion BD"""
        return sqlite3.connect(self.db_path)
    
    def clear_window(self):
        """Efface la fenêtre"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def log_activity(self, action, table_name, record_id=None, details=None):
        """Journalise les activités"""
        if not self.current_user:
            return
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO audit_log (user_id, action, table_name, record_id, details)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.current_user[0], action, table_name, record_id, details))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ Erreur journalisation: {e}")
    
    def validate_date(self, date_text):
        """Valide le format date JJ/MM/AAAA"""
        try:
            datetime.strptime(date_text, '%d/%m/%Y')
            return True
        except ValueError:
            return False
    
    def validate_phone_cameroun(self, phone):
        """Valide téléphone camerounais (format: 6, 7, ou 9 chiffres)"""
        # Nettoyer le numéro
        phone_clean = re.sub(r'\D', '', phone)
        # Format Cameroun: commence par 6, 7, ou 9, 8-9 chiffres total
        return re.match(r'^[679]\d{7,8}$', phone_clean) is not None
    
    def validate_cni(self, cni):
        """Valide CNI camerounais (12 chiffres)"""
        if not cni:
            return True
        return re.match(r'^\d{12}$', cni) is not None
    
    def search_patients(self, search_term):
        """Recherche avancée de patients"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        search_pattern = f'%{search_term}%'
        cursor.execute('''
            SELECT numero_dossier, nom, prenom, type_patient, telephone, date_naissance
            FROM patients 
            WHERE numero_dossier LIKE ? 
            OR nom LIKE ? 
            OR prenom LIKE ? 
            OR telephone LIKE ?
            OR cni LIKE ?
            ORDER BY nom, prenom
            LIMIT 100
        ''', (search_pattern, search_pattern, search_pattern, 
              search_pattern, search_pattern))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def export_table_to_csv(self, table_name):
        """Exporte une table en CSV"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            
            filename = f'{table_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Écrire les en-têtes
                writer.writerow([i[0] for i in cursor.description])
                # Écrire les données
                writer.writerows(cursor.fetchall())
            
            conn.close()
            
            # Journaliser l'export
            self.log_activity('EXPORT', table_name, details=f'Fichier: {filename}')
            
            messagebox.showinfo("Export réussi", 
                              f"Données exportées avec succès dans:\n{os.path.abspath(filename)}")
            return True
        except Exception as e:
            messagebox.showerror("Erreur export", f"Erreur: {e}")
            return False
    
    def check_urgent_notifications(self):
        """Vérifie les notifications urgentes"""
        notifications = []
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Rendez-vous aujourd'hui
            cursor.execute('''
                SELECT COUNT(*) FROM rendez_vous 
                WHERE date_rdv = date('now') 
                AND statut = 'planifie'
            ''')
            rdv_aujourdhui = cursor.fetchone()[0]
            if rdv_aujourdhui > 0:
                notifications.append(f"📅 {rdv_aujourdhui} RDV aujourd'hui")
            
            # Hospitalisations longues (> 7 jours)
            cursor.execute('''
                SELECT COUNT(*) FROM hospitalisations 
                WHERE statut = 'en_cours'
                AND julianday('now') - julianday(date_entree) > 7
            ''')
            hosp_longues = cursor.fetchone()[0]
            if hosp_longues > 0:
                notifications.append(f"🏥 {hosp_longues} hospitalisations longues (>7j)")
            
            # Factures impayées urgentes
            cursor.execute('''
                SELECT COUNT(*) FROM factures 
                WHERE statut = 'impaye'
                AND montant - paye > 50000
            ''')
            factures_urgentes = cursor.fetchone()[0]
            if factures_urgentes > 0:
                notifications.append(f"💰 {factures_urgentes} factures impayées urgentes")
            
            # Médicaments en rupture de stock
            cursor.execute('''
                SELECT COUNT(*) FROM medicaments 
                WHERE stock <= seuil_alerte
            ''')
            med_rupture = cursor.fetchone()[0]
            if med_rupture > 0:
                notifications.append(f"💊 {med_rupture} médicaments à réapprovisionner")
            
            conn.close()
            
        except Exception as e:
            print(f"Erreur notifications: {e}")
        
        return notifications
    
    # ==================== CONNEXION ====================
    
    def show_login(self):
        """Écran de connexion"""
        self.clear_window()
        
        frame = tk.Frame(self.root, bg=self.colors['primary'])
        frame.pack(expand=True, fill='both')
        
        card = tk.Frame(frame, bg='white', padx=50, pady=50)
        card.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(card, text="🏥", font=('Arial', 48), bg='white').pack()
        tk.Label(card, text="HÔPITAL NATIONAL", font=('Arial', 20, 'bold'), bg='white').pack(pady=10)
        tk.Label(card, text="Cameroun 🇨🇲", font=('Arial', 12), bg='white').pack(pady=(0, 30))
        
        tk.Label(card, text="Email:", bg='white').pack(anchor='w')
        self.login_email = tk.StringVar(value="admin@hospital.cm")
        tk.Entry(card, textvariable=self.login_email, width=30).pack(pady=(0, 15))
        
        tk.Label(card, text="Mot de passe:", bg='white').pack(anchor='w')
        self.login_password = tk.StringVar(value="admin123")
        tk.Entry(card, textvariable=self.login_password, show="•", width=30).pack(pady=(0, 30))
        
        tk.Button(card, text="SE CONNECTER", command=self.login,
                 bg=self.colors['primary'], fg='white',
                 font=('Arial', 12, 'bold'), padx=30, pady=10).pack()
        
        # Version info
        tk.Label(card, text="v3.0 - Base de données améliorée", font=('Arial', 8), 
                bg='white', fg='gray').pack(pady=(20, 0))
    
    def login(self):
        """Authentification avec journalisation"""
        email = self.login_email.get()
        password = self.login_password.get()
        
        if not email or not password:
            messagebox.showwarning("Erreur", "Remplissez tous les champs")
            return
        
        hashed = hashlib.sha256(password.encode()).hexdigest()
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nom, prenom, role FROM personnel WHERE email=? AND password=?", 
                     (email, hashed))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            self.current_user = user
            self.user_role = user[3]
            
            # Journaliser la connexion
            self.log_activity('LOGIN', 'personnel', user[0], 
                            f"Connexion: {user[2]} {user[1]}")
            
            self.show_main_menu()
        else:
            messagebox.showerror("Erreur", "Identifiants incorrects")
    
    # ==================== MENU PRINCIPAL AMÉLIORÉ ====================
    
    def show_main_menu(self):
        """Menu principal avec notifications"""
        self.clear_window()
        
        # Header amélioré
        header = tk.Frame(self.root, bg=self.colors['primary'], height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        # Logo et titre
        title_frame = tk.Frame(header, bg=self.colors['primary'])
        title_frame.pack(side='left', padx=30, fill='y')
        
        tk.Label(title_frame, text="🏥", font=('Arial', 24), 
                bg=self.colors['primary'], fg='white').pack(side='left', padx=(0, 10))
        
        tk.Label(title_frame, text="HÔPITAL NATIONAL\nCAMEROUN 🇨🇲", 
                font=('Arial', 14, 'bold'), bg=self.colors['primary'], 
                fg='white', justify='left').pack(side='left')
        
        # Notifications
        notifications = self.check_urgent_notifications()
        if notifications:
            notif_frame = tk.Frame(header, bg=self.colors['warning'])
            notif_frame.pack(side='left', padx=20, fill='both', expand=True)
            
            notif_text = " | ".join(notifications[:3])  # Max 3 notifications
            tk.Label(notif_frame, text=f"⚠️ {notif_text}", 
                    font=('Arial', 10, 'bold'), bg=self.colors['warning'], 
                    fg='white').pack(pady=5)
        
        # User info
        user_frame = tk.Frame(header, bg=self.colors['primary'])
        user_frame.pack(side='right', padx=30)
        
        tk.Label(user_frame, text=f"👤 {self.current_user[2]} {self.current_user[1]}", 
                font=('Arial', 11), bg=self.colors['primary'], 
                fg='white').pack(side='left', padx=(0, 20))
        
        tk.Button(user_frame, text="🚪 Déconnexion", command=self.show_login,
                 bg=self.colors['danger'], fg='white',
                 padx=15, pady=5, font=('Arial', 10)).pack(side='left')
        
        # Notebook principal
        self.main_notebook = ttk.Notebook(self.root)
        self.main_notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Onglets
        self.create_dashboard_tab()
        self.create_patients_tab()
        self.create_consultations_tab()
        self.create_hospitalisation_tab()
        self.create_rendezvous_tab()
        self.create_facturation_tab()
        self.create_vaccinations_tab()
        
        # Nouveaux onglets
        self.create_medicaments_tab()
        self.create_services_tab()
        self.create_examens_tab()
        
        if self.user_role == 'admin':
            self.create_personnel_tab()
            self.create_statistiques_tab()
            self.create_admin_tab()
    
    def create_dashboard_tab(self):
        """Tableau de bord amélioré"""
        tab = tk.Frame(self.main_notebook, bg=self.colors['bg_secondary'])
        self.main_notebook.add(tab, text="📊 Tableau de bord")
        
        main_frame = tk.Frame(tab, bg='white', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        tk.Label(main_frame, text="TABLEAU DE BORD - VUE D'ENSEMBLE", 
                font=('Arial', 18, 'bold'), bg='white').pack(pady=(0, 20))
        
        # Stats rapides
        stats_frame = tk.Frame(main_frame, bg='white')
        stats_frame.pack(pady=20)
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            stats_queries = [
                ("👥 Total patients", "SELECT COUNT(*) FROM patients", self.colors['primary']),
                ("👶 Enfants", "SELECT COUNT(*) FROM patients WHERE type_patient='enfant'", self.colors['pediatrie']),
                ("👨 Adultes", "SELECT COUNT(*) FROM patients WHERE type_patient='adulte'", self.colors['adulte']),
                ("🩺 Consultations aujourd'hui", "SELECT COUNT(*) FROM consultations WHERE date(date_consultation) = date('now')", self.colors['info']),
                ("🏥 Hospitalisés", "SELECT COUNT(*) FROM hospitalisations WHERE statut='en_cours'", self.colors['warning']),
                ("📅 RDV aujourd'hui", "SELECT COUNT(*) FROM rendez_vous WHERE date_rdv = date('now') AND statut='planifie'", self.colors['secondary']),
                ("💰 Factures impayées", "SELECT COUNT(*) FROM factures WHERE statut!='paye'", self.colors['danger']),
                ("💉 Vaccins ce mois", "SELECT COUNT(*) FROM vaccinations WHERE strftime('%Y-%m', date_vaccination) = strftime('%Y-%m', 'now')", self.colors['success']),
                ("💊 Médicaments stock", "SELECT COUNT(*) FROM medicaments WHERE stock > 0", '#10b981'),
                ("🛌 Chambres dispo", "SELECT COUNT(*) FROM chambres WHERE lits_disponibles > 0", '#8b5cf6')
            ]
            
            for i, (label, query, color) in enumerate(stats_queries):
                cursor.execute(query)
                value = cursor.fetchone()[0]
                
                card = tk.Frame(stats_frame, bg='white', 
                               padx=15, pady=12, relief=tk.RAISED, borderwidth=2)
                card.grid(row=i//5, column=i%5, padx=8, pady=8, sticky='nsew')
                
                tk.Label(card, text=label, font=('Arial', 10), 
                        bg='white').pack()
                tk.Label(card, text=str(value), font=('Arial', 22, 'bold'), 
                        bg='white', fg=color).pack(pady=5)
            
            # Configurer grille
            for i in range(5):
                stats_frame.grid_columnconfigure(i, weight=1)
            
            conn.close()
            
        except Exception as e:
            tk.Label(main_frame, text=f"Erreur: {e}", bg='white', fg='red').pack()
        
        # Boutons actions rapides
        actions_frame = tk.Frame(main_frame, bg='white')
        actions_frame.pack(pady=30)
        
        quick_actions = [
            ("➕ Nouveau patient", self.show_new_patient_form),
            ("🩺 Nouvelle consultation", self.show_new_consultation),
            ("📅 Prendre RDV", self.show_new_rdv),
            ("💰 Nouvelle facture", self.show_new_facture),
            ("💉 Nouvelle vaccination", self.show_new_vaccination),
            ("💊 Gérer médicaments", self.show_medicaments_tab),
            ("🏥 Gérer services", self.show_services_tab)
        ]
        
        for i, (text, command) in enumerate(quick_actions):
            btn = tk.Button(actions_frame, text=text, command=command,
                          bg=self.colors['primary'], fg='white',
                          padx=20, pady=10, font=('Arial', 10))
            btn.grid(row=0, column=i, padx=5)
    
    def show_new_patient_form(self):
        """Affiche directement l'onglet nouveau patient"""
        self.main_notebook.select(1)  # Onglet Patients
    
    def show_new_consultation(self):
        """Affiche l'onglet consultations"""
        self.main_notebook.select(2)  # Onglet Consultations
    
    def show_new_rdv(self):
        """Affiche l'onglet rendez-vous"""
        self.main_notebook.select(4)  # Onglet Rendez-vous
    
    def show_new_facture(self):
        """Affiche l'onglet facturation"""
        self.main_notebook.select(5)  # Onglet Facturation
    
    def show_new_vaccination(self):
        """Affiche l'onglet vaccinations"""
        self.main_notebook.select(6)  # Onglet Vaccinations
    
    def show_medicaments_tab(self):
        """Affiche l'onglet médicaments"""
        self.main_notebook.select(7)  # Onglet Médicaments
    
    def show_services_tab(self):
        """Affiche l'onglet services"""
        self.main_notebook.select(8)  # Onglet Services
    
    # ==================== PATIENTS AMÉLIORÉ ====================
    
    def create_patients_tab(self):
        """Onglet Patients amélioré avec recherche"""
        tab = tk.Frame(self.main_notebook, bg=self.colors['bg_secondary'])
        self.main_notebook.add(tab, text="👥 Patients")
        
        notebook = ttk.Notebook(tab)
        notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Nouveau patient
        new_tab = tk.Frame(notebook, bg='white')
        notebook.add(new_tab, text="➕ Nouveau")
        self.create_patient_form(new_tab)
        
        # Liste avec recherche
        list_tab = tk.Frame(notebook, bg='white')
        notebook.add(list_tab, text="📋 Liste")
        self.create_patient_list(list_tab)
        
        # Recherche avancée
        search_tab = tk.Frame(notebook, bg='white')
        notebook.add(search_tab, text="🔍 Recherche")
        self.create_patient_search(search_tab)
    
    def create_patient_form(self, parent):
        """Formulaire patient amélioré avec validation"""
        main_frame = tk.Frame(parent, bg='white', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
tk.Label(form, text="Lieu de naissance:", bg='white', 
        font=('Arial', 10)).grid(row=row_idx, column=0, padx=10, pady=8, sticky='e')
self.patient_vars['lieu_naissance'] = tk.StringVar()
tk.Entry(form, textvariable=self.patient_vars['lieu_naissance'], 
        width=30).grid(row=row_idx, column=1, padx=10, pady=8)
row_idx += 1

# État civil
tk.Label(form, text="État civil:", bg='white', 
        font=('Arial', 10)).grid(row=row_idx, column=0, padx=10, pady=8, sticky='e')
self.patient_vars['etat_civil'] = tk.StringVar()
etats = ['célibataire', 'marié(e)', 'divorcé(e)', 'veuf(ve)']
ttk.Combobox(form, textvariable=self.patient_vars['etat_civil'], 
           values=etats, width=27).grid(row=row_idx, column=1, padx=10, pady=8)
row_idx += 1

# Nationalité
tk.Label(form, text="Nationalité:", bg='white', 
        font=('Arial', 10)).grid(row=row_idx, column=0, padx=10, pady=8, sticky='e')
self.patient_vars['nationalite'] = tk.StringVar(value="Camerounaise")
tk.Entry(form, textvariable=self.patient_vars['nationalite'], 
        width=30).grid(row=row_idx, column=1, padx=10, pady=8)
row_idx += 1

# Assurance
tk.Label(form, text="Assurance:", bg='white', 
        font=('Arial', 10)).grid(row=row_idx, column=0, padx=10, pady=8, sticky='e')
self.patient_vars['assurance'] = tk.StringVar()
tk.Entry(form, textvariable=self.patient_vars['assurance'], 
        width=30).grid(row=row_idx, column=1, padx=10, pady=8)
row_idx += 1

tk.Label(form, text="N° Assurance:", bg='white', 
        font=('Arial', 10)).grid(row=row_idx, column=0, padx=10, pady=8, sticky='e')
self.patient_vars['numero_assurance'] = tk.StringVar()
tk.Entry(form, textvariable=self.patient_vars['numero_assurance'], 
        width=30).grid(row=row_idx, column=1, padx=10, pady=8)
row_idx += 1

# Contact urgence
tk.Label(form, text="Contact urgence:", bg='white', 
        font=('Arial', 10)).grid(row=row_idx, column=0, padx=10, pady=8, sticky='ne')
urgence_frame = tk.Frame(form, bg='white')
urgence_frame.grid(row=row_idx, column=1, sticky='w', padx=10, pady=8)
row_idx += 1

tk.Label(urgence_frame, text="Nom:", bg='white').grid(row=0, column=0, padx=5, pady=2)
self.patient_vars['contact_urgence_nom'] = tk.StringVar()
tk.Entry(urgence_frame, textvariable=self.patient_vars['contact_urgence_nom'], 
        width=25).grid(row=0, column=1, padx=5, pady=2)

tk.Label(urgence_frame, text="Téléphone:", bg='white').grid(row=1, column=0, padx=5, pady=2)
self.patient_vars['contact_urgence_telephone'] = tk.StringVar()
tk.Entry(urgence_frame, textvariable=self.patient_vars['contact_urgence_telephone'], 
        width=25).grid(row=1, column=1, padx=5, pady=2)

tk.Label(urgence_frame, text="Lien:", bg='white').grid(row=2, column=0, padx=5, pady=2)
self.patient_vars['contact_urgence_lien'] = tk.StringVar()
tk.Entry(urgence_frame, textvariable=self.patient_vars['contact_urgence_lien'], 
        width=25).grid(row=2, column=1, padx=5, pady=2)
        
tk.Label(main_frame, text="NOUVEAU PATIENT", 
                font=('Arial', 16, 'bold'), bg='white').pack(pady=(0, 20))
        
        # Type
type_frame = tk.Frame(main_frame, bg='white')
type_frame.pack()
        
tk.Label(type_frame, text="Type de patient:", bg='white', 
                font=('Arial', 11)).pack(side='left', padx=10)
self.patient_type = tk.StringVar(value="adulte")
        
type_color_frame = tk.Frame(type_frame, bg='white')
type_color_frame.pack(side='left', padx=10)
        
tk.Radiobutton(type_color_frame, text="👨 Adulte", variable=self.patient_type, 
                      value="adulte", bg='white', fg=self.colors['adulte'],
                      font=('Arial', 10, 'bold'),
                      command=self.toggle_patient_fields).pack(side='left', padx=5)
        
tk.Radiobutton(type_color_frame, text="👶 Enfant", variable=self.patient_type, 
                      value="enfant", bg='white', fg=self.colors['pediatrie'],
                      font=('Arial', 10, 'bold'),
                      command=self.toggle_patient_fields).pack(side='left', padx=5)
        
        # Champs communs
self.patient_vars = {}
form_frame = tk.Frame(main_frame, bg='white')
form_frame.pack(pady=20)
        
fields = [
            ("Nom*:", "nom", 30),
            ("Prénom*:", "prenom", 30),
            ("Date naissance* (JJ/MM/AAAA):", "date_naissance", 30),
            ("Téléphone*:", "telephone", 30),
            ("Email:", "email", 30),
            ("Profession:", "profession", 30)
        ]
        
for i, (label, name, width) in enumerate(fields):
            tk.Label(form_frame, text=label, bg='white', 
                    font=('Arial', 10)).grid(row=i, column=0, padx=10, pady=8, sticky='e')
            self.patient_vars[name] = tk.StringVar()
            
            entry = tk.Entry(form_frame, textvariable=self.patient_vars[name], 
                           width=width, font=('Arial', 10))
            entry.grid(row=i, column=1, padx=10, pady=8)
            
            # Validation en temps réel pour téléphone
            if name == "telephone":
                entry.bind('<FocusOut>', lambda e: self.validate_phone_field())
        
        # Sexe
     tk.Label(form_frame, text="Sexe*:", bg='white', 
                font=('Arial', 10)).grid(row=len(fields), column=0, padx=10, pady=8, sticky='e')
sex_frame = tk.Frame(form_frame, bg='white')
    sex_frame.grid(row=len(fields), column=1, sticky='w', padx=10)
        
    self.patient_vars['sexe'] = tk.StringVar(value="M")
        
tk.Radiobutton(sex_frame, text="Masculin", variable=self.patient_vars['sexe'], 
                      value="M", bg='white', font=('Arial', 10)).pack(side='left')
tk.Radiobutton(sex_frame, text="Féminin", variable=self.patient_vars['sexe'], 
                      value="F", bg='white', font=('Arial', 10)).pack(side='left', padx=20)
        
        # Informations médicales
tk.Label(form_frame, text="Groupe sanguin:", bg='white', 
                font=('Arial', 10)).grid(row=len(fields)+1, column=0, padx=10, pady=8, sticky='e')
self.patient_vars['groupe_sanguin'] = tk.StringVar()
groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', 'Inconnu']
ttk.Combobox(form_frame, textvariable=self.patient_vars['groupe_sanguin'], 
                    values=groups, width=27).grid(row=len(fields)+1, column=1, padx=10, pady=8)
        
tk.Label(form_frame, text="Allergies:", bg='white', 
                font=('Arial', 10)).grid(row=len(fields)+2, column=0, padx=10, pady=8, sticky='ne')
        
 self.patient_vars['allergies'] = tk.Text(form_frame, height=3, width=30, 
                                               font=('Arial', 10))
self.patient_vars['allergies'].grid(row=len(fields)+2, column=1, padx=10, pady=8)
        
tk.Label(form_frame, text="Antécédents:", bg='white', 
                font=('Arial', 10)).grid(row=len(fields)+3, column=0, padx=10, pady=8, sticky='ne')
        
        self.patient_vars['antecedents'] = tk.Text(form_frame, height=3, width=30, 
                                                  font=('Arial', 10))
        self.patient_vars['antecedents'].grid(row=len(fields)+3, column=1, padx=10, pady=8)
        
        # Adresse
        tk.Label(form_frame, text="Adresse:", bg='white', 
                font=('Arial', 10)).grid(row=len(fields)+4, column=0, padx=10, pady=8, sticky='ne')
        
        self.patient_vars['adresse'] = tk.Text(form_frame, height=4, width=30, 
                                             font=('Arial', 10))
        self.patient_vars['adresse'].grid(row=len(fields)+4, column=1, padx=10, pady=8)
        
        # Champs spécifiques
        self.adult_frame = tk.Frame(main_frame, bg='white')
        self.child_frame = tk.Frame(main_frame, bg='white')
        
        # Adulte: CNI
        tk.Label(self.adult_frame, text="CNI (12 chiffres):", bg='white', 
                font=('Arial', 10)).grid(row=0, column=0, padx=10, pady=8, sticky='e')
        self.patient_vars['cni'] = tk.StringVar()
        cni_entry = tk.Entry(self.adult_frame, textvariable=self.patient_vars['cni'], 
                           width=30, font=('Arial', 10))
        cni_entry.grid(row=0, column=1, padx=10, pady=8)
        cni_entry.bind('<FocusOut>', lambda e: self.validate_cni_field())
        
        # Enfant: CNI parent, poids, taille, parents
        tk.Label(self.child_frame, text="CNI parent* (12 chiffres):", bg='white', 
                font=('Arial', 10)).grid(row=0, column=0, padx=10, pady=8, sticky='e')
        self.patient_vars['cni_parent'] = tk.StringVar()
        cni_parent_entry = tk.Entry(self.child_frame, textvariable=self.patient_vars['cni_parent'], 
                                  width=30, font=('Arial', 10))
        cni_parent_entry.grid(row=0, column=1, padx=10, pady=8)
        cni_parent_entry.bind('<FocusOut>', lambda e: self.validate_cni_field(parent=True))
        
        tk.Label(self.child_frame, text="Nom père:", bg='white', 
                font=('Arial', 10)).grid(row=1, column=0, padx=10, pady=8, sticky='e')
        self.patient_vars['pere_nom'] = tk.StringVar()
        tk.Entry(self.child_frame, textvariable=self.patient_vars['pere_nom'], 
                width=30, font=('Arial', 10)).grid(row=1, column=1, padx=10, pady=8)
        
        tk.Label(self.child_frame, text="Nom mère:", bg='white', 
                font=('Arial', 10)).grid(row=2, column=0, padx=10, pady=8, sticky='e')
        self.patient_vars['mere_nom'] = tk.StringVar()
        tk.Entry(self.child_frame, textvariable=self.patient_vars['mere_nom'], 
                width=30, font=('Arial', 10)).grid(row=2, column=1, padx=10, pady=8)
        
        tk.Label(self.child_frame, text="Poids (kg):", bg='white', 
                font=('Arial', 10)).grid(row=3, column=0, padx=10, pady=8, sticky='e')
        self.patient_vars['poids'] = tk.StringVar()
        tk.Entry(self.child_frame, textvariable=self.patient_vars['poids'], 
                width=30, font=('Arial', 10)).grid(row=3, column=1, padx=10, pady=8)
        
        tk.Label(self.child_frame, text="Taille (cm):", bg='white', 
                font=('Arial', 10)).grid(row=4, column=0, padx=10, pady=8, sticky='e')
        self.patient_vars['taille'] = tk.StringVar()
        tk.Entry(self.child_frame, textvariable=self.patient_vars['taille'], 
                width=30, font=('Arial', 10)).grid(row=4, column=1, padx=10, pady=8)
        
        self.toggle_patient_fields()
        
        # Boutons avec feedback
        btn_frame = tk.Frame(main_frame, bg='white')
        btn_frame.pack(pady=30)
        
        save_btn = tk.Button(btn_frame, text="💾 Enregistrer Patient", 
                           command=self.save_patient,
                           bg=self.colors['success'], fg='white',
                           padx=30, pady=12, font=('Arial', 11, 'bold'))
        save_btn.pack(side='left', padx=10)
        
        clear_btn = tk.Button(btn_frame, text="🗑️ Effacer Formulaire", 
                            command=self.clear_patient_form,
                            bg=self.colors['danger'], fg='white',
                            padx=30, pady=12, font=('Arial', 11))
        clear_btn.pack(side='left', padx=10)
        
        # Status label pour feedback
        self.patient_status_label = tk.Label(main_frame, text="",                                         bg='white', font=('Arial', 10))
        self.patient_status_label.pack(pady=10)
    
    def validate_phone_field(self):
        """Valide le téléphone en temps réel"""
        phone = self.patient_vars['telephone'].get()
        if phone and not self.validate_phone_cameroun(phone):
            self.patient_status_label.config(
                text="⚠️ Téléphone invalide (format: 6/7/9 suivi de 7-8 chiffres)", 
                fg=self.colors['danger'])
            return False
        return True
    
    def validate_cni_field(self, parent=False):
        """Valide CNI en temps réel"""
        if parent:
            cni = self.patient_vars['cni_parent'].get()
        else:
            cni = self.patient_vars['cni'].get()
        
        if cni and not self.validate_cni(cni):
            self.patient_status_label.config(
                text="⚠️ CNI invalide (12 chiffres requis)", 
                fg=self.colors['danger'])
            return False
        return True
    
    def toggle_patient_fields(self):
        """Affiche/masque champs selon type"""
        self.adult_frame.pack_forget()
        self.child_frame.pack_forget()
        
        if self.patient_type.get() == "adulte":
            self.adult_frame.pack(pady=10)
        else:
            self.child_frame.pack(pady=10)
    
    def save_patient(self):
        """Sauvegarde patient avec validation améliorée"""
        try:
            # Validation des champs obligatoires
            required = ['nom', 'prenom', 'date_naissance', 'telephone']
            missing_fields = []
            
            for field in required:
                value = self.patient_vars[field].get().strip()
                if not value:
                    missing_fields.append(field)
            
            if missing_fields:
                messagebox.showwarning("Champs manquants", 
                                     f"Champs obligatoires manquants:\n{', '.join(missing_fields)}")
                return
            
            # Validation date
            date_naissance = self.patient_vars['date_naissance'].get()
            if not self.validate_date(date_naissance):
                messagebox.showwarning("Date invalide", 
                                     "Format date: JJ/MM/AAAA\nExemple: 15/01/1990")
                return
            
            # Validation téléphone
            telephone = self.patient_vars['telephone'].get()
            if not self.validate_phone_cameroun(telephone):
                messagebox.showwarning("Téléphone invalide", 
                                     "Format téléphone Cameroun:\n- Commence par 6, 7 ou 9\n- 8-9 chiffres au total\nExemple: 677123456")
                return
            
            patient_type = self.patient_type.get()
            
            # Validation CNI selon type
            if patient_type == "adulte":
                cni = self.patient_vars['cni'].get()
                if cni and not self.validate_cni(cni):
                    messagebox.showwarning("CNI invalide", "CNI: 12 chiffres requis")
                    return
                cni_parent = None
            else:
                cni = None
                cni_parent = self.patient_vars['cni_parent'].get()
                if not cni_parent or not self.validate_cni(cni_parent):
                    messagebox.showwarning("CNI parent invalide", 
                                         "CNI parent: 12 chiffres requis pour les enfants")
                    return
            
            # Préparation des données
            adresse_text = ""
            if hasattr(self.patient_vars['adresse'], 'get'):
                adresse_text = self.patient_vars['adresse'].get("1.0", "end-1c").strip()
            else:
                adresse_text = self.patient_vars['adresse'].get()
            
            allergies_text = self.patient_vars['allergies'].get("1.0", "end-1c").strip()
            antecedents_text = self.patient_vars['antecedents'].get("1.0", "end-1c").strip()
            
            # Gestion des valeurs numériques
            poids_val = None
            taille_val = None
            
            if patient_type == "enfant":
                poids_str = self.patient_vars['poids'].get()
                taille_str = self.patient_vars['taille'].get()
                
                try:
                    if poids_str:
                        poids_val = float(poids_str)
                    if taille_str:
                        taille_val = float(taille_str)
                except ValueError:
                    messagebox.showwarning("Valeurs invalides", 
                                         "Poids et taille doivent être des nombres")
                    return
            
            # Insertion dans la base
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO patients 
                    (numero_dossier, nom, prenom, date_naissance, sexe, telephone, adresse,
                     type_patient, cni, cni_parent, pere_nom, mere_nom, poids, taille,
                     groupe_sanguin, allergies, antecedents, profession, email)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    None,  # Laissé NULL pour le trigger
                    self.patient_vars['nom'].get().upper(),
                    self.patient_vars['prenom'].get().title(),
                    date_naissance,
                    self.patient_vars['sexe'].get(),
                    telephone,
                    adresse_text,
                    patient_type,
                    cni,
                    cni_parent,
                    self.patient_vars.get('pere_nom', tk.StringVar()).get(),
                    self.patient_vars.get('mere_nom', tk.StringVar()).get(),
                    poids_val,
                    taille_val,
                    self.patient_vars['groupe_sanguin'].get(),
                    allergies_text,
                    antecedents_text,
                    self.patient_vars['profession'].get(),
                    self.patient_vars['email'].get()
                ))
                
                patient_id = cursor.lastrowid
                
                # Récupérer le numéro dossier généré
                cursor.execute('SELECT numero_dossier FROM patients WHERE id=?', (patient_id,))
                dossier = cursor.fetchone()[0]
                
                conn.commit()
                
                # Journaliser l'action
                self.log_activity('CREATE', 'patients', patient_id, 
                                f"Nouveau {patient_type}: {dossier}")
                
                # Actualiser la liste des patients
                self.refresh_patient_list()
                
                messagebox.showinfo("Succès", 
                                  f"✅ Patient enregistré avec succès!\n\n"
                                  f"📁 Numéro dossier: {dossier}\n"
                                  f"👤 Nom: {self.patient_vars['nom'].get().upper()} {self.patient_vars['prenom'].get().title()}\n"
                                  f"📞 Téléphone: {telephone}")
                
                # Réinitialiser le formulaire
                self.clear_patient_form()
                
                # Mettre à jour le status
                self.patient_status_label.config(
                    text=f"✅ Patient {dossier} enregistré avec succès!", 
                    fg=self.colors['success'])
                
            except sqlite3.IntegrityError as e:
                if "UNIQUE constraint" in str(e):
                    messagebox.showerror("Erreur", "Numéro dossier déjà existant, veuillez réessayer")
                else:
                    raise e
            finally:
                conn.close()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement:\n{str(e)}")
            self.patient_status_label.config(
                text=f"❌ Erreur: {str(e)}", 
                fg=self.colors['danger'])
    
    def clear_patient_form(self):
        """Efface formulaire patient"""
        for name, var in self.patient_vars.items():
            if isinstance(var, tk.StringVar):
                var.set("")
            elif hasattr(var, 'delete'):  # Pour les widgets Text
                var.delete("1.0", tk.END)
        
        self.patient_type.set("adulte")
        self.patient_vars['sexe'].set("M")
        self.toggle_patient_fields()
        self.patient_status_label.config(text="")
    
    def create_patient_list(self, parent):
        """Liste patients avec bouton d'actualisation"""
        main_frame = tk.Frame(parent, bg='white', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        # Header avec bouton d'actualisation
        header_frame = tk.Frame(main_frame, bg='white')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(header_frame, text="📋 LISTE DES PATIENTS", 
                font=('Arial', 14, 'bold'), bg='white').pack(side='left')
        
        # Bouton d'actualisation
        refresh_btn = tk.Button(header_frame, text="🔄 Actualiser la liste", 
                               command=self.load_patients_list,
                               bg=self.colors['info'], fg='white',
                               padx=15, pady=5, font=('Arial', 10))
        refresh_btn.pack(side='right', padx=5)
        
        # Bouton d'export
        export_btn = tk.Button(header_frame, text="📤 Exporter en CSV", 
                              command=lambda: self.export_table_to_csv('patients'),
                              bg=self.colors['secondary'], fg='white',
                              padx=15, pady=5, font=('Arial', 10))
        export_btn.pack(side='right', padx=5)
        
        # Tableau
        tree_frame = tk.Frame(main_frame, bg='white')
        tree_frame.pack(fill='both', expand=True)
        
        columns = ['Dossier', 'Nom', 'Prénom', 'Type', 'Téléphone', 'Date Naiss.', 'Sexe']
        self.patient_list_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
        
        # Configurer les colonnes
        col_widths = [120, 120, 120, 80, 100, 100, 60]
        for col, width in zip(columns, col_widths):
            self.patient_list_tree.heading(col, text=col)
            self.patient_list_tree.column(col, width=width, minwidth=50)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.patient_list_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.patient_list_tree.xview)
        self.patient_list_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Placement des widgets
        self.patient_list_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew', columnspan=2)
        
        # Configurer la grille
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Menu contextuel
        self.create_patient_context_menu()
        
        # Charger les données initiales
        self.load_patients_list()
    
    def create_patient_search(self, parent):
        """Interface de recherche de patients"""
        main_frame = tk.Frame(parent, bg='white', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        tk.Label(main_frame, text="🔍 RECHERCHE AVANCÉE DE PATIENTS", 
                font=('Arial', 14, 'bold'), bg='white').pack(pady=(0, 20))
        
        # Champ de recherche
        search_frame = tk.Frame(main_frame, bg='white')
        search_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(search_frame, text="Rechercher:", bg='white', 
                font=('Arial', 11)).pack(side='left', padx=(0, 10))
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, 
                              width=40, font=('Arial', 11))
        search_entry.pack(side='left', padx=(0, 10))
        
        search_btn = tk.Button(search_frame, text="🔍 Rechercher", 
                              command=self.perform_patient_search,
                              bg=self.colors['primary'], fg='white',
                              padx=20, pady=5)
        search_btn.pack(side='left', padx=(0, 10))
        
        # Info
        tk.Label(search_frame, text="(Nom, Prénom, Dossier, Téléphone, CNI)", 
                bg='white', fg='gray', font=('Arial', 9)).pack(side='left')
        
        # Résultats
        results_frame = tk.Frame(main_frame, bg='white')
        results_frame.pack(fill='both', expand=True)
        
        # Tableau des résultats
        columns = ['Dossier', 'Nom', 'Prénom', 'Type', 'Téléphone', 'Date Naiss.']
        self.search_results_tree = ttk.Treeview(results_frame, columns=columns, 
                                               show='headings', height=15)
        
        for col in columns:
            self.search_results_tree.heading(col, text=col)
            self.search_results_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, 
                                 command=self.search_results_tree.yview)
        self.search_results_tree.configure(yscrollcommand=scrollbar.set)
        
        self.search_results_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def perform_patient_search(self):
        """Exécute la recherche"""
        search_term = self.search_var.get().strip()
        
        if not search_term:
            messagebox.showwarning("Recherche vide", "Veuillez entrer un terme de recherche")
            return
        
        # Effacer anciens résultats
        for item in self.search_results_tree.get_children():
            self.search_results_tree.delete(item)
        
        # Effectuer la recherche
        results = self.search_patients(search_term)
        
        if not results:
            messagebox.showinfo("Aucun résultat", "Aucun patient trouvé pour cette recherche")
            return
        
        # Afficher les résultats
        for row in results:
            self.search_results_tree.insert('', tk.END, values=row)
    
    def load_patients_list(self):
        """Charge/Rafraîchit la liste des patients"""
        # Effacer anciennes données
        for item in self.patient_list_tree.get_children():
            self.patient_list_tree.delete(item)
        
        # Charger nouvelles données
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT numero_dossier, nom, prenom, type_patient, telephone, 
                       date_naissance, sexe
                FROM patients 
                ORDER BY date_creation DESC 
                LIMIT 200
            ''')
            
            # Style alterné
            row_color = True
            
            for row in cursor.fetchall():
                # Convertir type pour affichage
                display_type = "👶 Enfant" if row[3] == "enfant" else "👨 Adulte"
                display_sexe = "♂️" if row[6] == "M" else "♀️"
                
                display_row = (row[0], row[1], row[2], display_type, 
                             row[4], row[5], display_sexe)
                
                # Insérer avec tag alterné
                tag = 'evenrow' if row_color else 'oddrow'
                self.patient_list_tree.insert('', tk.END, values=display_row, tags=(tag,))
                row_color = not row_color
            
            # Configurer les tags pour l'alternance
            self.patient_list_tree.tag_configure('evenrow', background='#f9f9f9')
            self.patient_list_tree.tag_configure('oddrow', background='white')
            
            conn.close()
            
            # Afficher le nombre de patients
            self.update_patient_count()
            
        except Exception as e:
            print(f"Erreur chargement patients: {e}")
    
    def refresh_patient_list(self):
        """Fonction pour actualiser la liste des patients (appelée après ajout)"""
        self.load_patients_list()
    
    def update_patient_count(self):
        """Met à jour le compte des patients"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM patients")
            count = cursor.fetchone()[0]
            conn.close()
            
        except Exception as e:
            print(f"Erreur compte patients: {e}")
    
    def create_patient_context_menu(self):
        """Menu contextuel pour les patients"""
        self.patient_context_menu = tk.Menu(self.root, tearoff=0)
        self.patient_context_menu.add_command(label="📋 Voir détails", 
                                            command=self.view_patient_details)
        self.patient_context_menu.add_command(label="🩺 Nouvelle consultation", 
                                            command=self.create_consultation_for_patient)
        self.patient_context_menu.add_command(label="📅 Prendre RDV", 
                                            command=self.create_rdv_for_patient)
        self.patient_context_menu.add_separator()
        self.patient_context_menu.add_command(label="📤 Exporter cette ligne", 
                                            command=self.export_patient_row)
        
        # Lier le menu contextuel
        self.patient_list_tree.bind("<Button-3>", self.show_patient_context_menu)
    
    def show_patient_context_menu(self, event):
        """Affiche le menu contextuel pour patients"""
        item = self.patient_list_tree.identify_row(event.y)
        if item:
            self.patient_list_tree.selection_set(item)
            self.patient_context_menu.post(event.x_root, event.y_root)
    
    def view_patient_details(self):
        """Affiche les détails du patient sélectionné"""
        selection = self.patient_list_tree.selection()
        if not selection:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un patient")
            return
        
        item = selection[0]
        values = self.patient_list_tree.item(item, 'values')
        
        if values:
            dossier = values[0]
            
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM patients 
                    WHERE numero_dossier = ?
                ''', (dossier,))
                
                patient = cursor.fetchone()
                
                if patient:
                    # Afficher les détails dans une nouvelle fenêtre
                    self.show_patient_detail_window(patient)
                
                conn.close()
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur: {e}")
    
    def show_patient_detail_window(self, patient):
        """Affiche une fenêtre avec les détails du patient"""
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"Détails Patient - {patient[1]}")
        detail_window.geometry("700x600")
        detail_window.configure(bg='white')
        
        # Titre
        tk.Label(detail_window, text=f"📁 DOSSIER: {patient[1]}", 
                font=('Arial', 16, 'bold'), bg='white').pack(pady=20)
        
        # Frame pour les informations
        info_frame = tk.Frame(detail_window, bg='white', padx=30, pady=20)
        info_frame.pack(fill='both', expand=True)
        
        # Informations de base
        infos = [
            ("Nom complet:", f"{patient[2]} {patient[3]}"),
            ("Type:", "👶 Enfant" if patient[8] == "enfant" else "👨 Adulte"),
            ("Sexe:", "♂️ Masculin" if patient[5] == "M" else "♀️ Féminin"),
            ("Date naissance:", patient[4]),
            ("Téléphone:", patient[6]),
            ("Email:", patient[16] or "Non renseigné"),
            ("Profession:", patient[17] or "Non renseigné"),
            ("CNI:", patient[9] or "Non renseigné"),
            ("Groupe sanguin:", patient[15] or "Non renseigné"),
            ("Date création:", patient[14])
        ]
        
        for i, (label, value) in enumerate(infos):
            tk.Label(info_frame, text=label, bg='white', 
                    font=('Arial', 10, 'bold'), width=15, anchor='w').grid(row=i, column=0, pady=5, sticky='w')
            tk.Label(info_frame, text=value, bg='white', 
                    font=('Arial', 10)).grid(row=i, column=1, pady=5, sticky='w')
        
        # Adresse
        tk.Label(info_frame, text="Adresse:", bg='white', 
                font=('Arial', 10, 'bold')).grid(row=len(infos), column=0, pady=10, sticky='nw')
        
        address_text = tk.Text(info_frame, height=3, width=40, 
                              font=('Arial', 10), bg='#f9f9f9')
        address_text.grid(row=len(infos), column=1, pady=10, sticky='w')
        address_text.insert('1.0', patient[7] or "Non renseigné")
        address_text.config(state='disabled')
        
        # Allergies
        tk.Label(info_frame, text="Allergies:", bg='white', 
                font=('Arial', 10, 'bold')).grid(row=len(infos)+1, column=0, pady=10, sticky='nw')
        
        allergies_text = tk.Text(info_frame, height=2, width=40, 
                               font=('Arial', 10), bg='#f9f9f9')
        allergies_text.grid(row=len(infos)+1, column=1, pady=10, sticky='w')
        allergies_text.insert('1.0', patient[16] or "Aucune connue")
        allergies_text.config(state='disabled')
        
        # Antécédents
        tk.Label(info_frame, text="Antécédents:", bg='white', 
                font=('Arial', 10, 'bold')).grid(row=len(infos)+2, column=0, pady=10, sticky='nw')
        
        antecedents_text = tk.Text(info_frame, height=2, width=40, 
                                  font=('Arial', 10), bg='#f9f9f9')
        antecedents_text.grid(row=len(infos)+2, column=1, pady=10, sticky='w')
        antecedents_text.insert('1.0', patient[17] or "Non renseigné")
        antecedents_text.config(state='disabled')
        
        # Pour les enfants, afficher info supplémentaires
        if patient[8] == "enfant":
            child_infos = [
                ("CNI Parent:", patient[10] or "Non renseigné"),
                ("Père:", patient[11] or "Non renseigné"),
                ("Mère:", patient[12] or "Non renseigné"),
                ("Poids:", f"{patient[13] or 'N/A'} kg"),
                ("Taille:", f"{patient[14] or 'N/A'} cm")
            ]
            
            start_row = len(infos) + 3
            for i, (label, value) in enumerate(child_infos):
                tk.Label(info_frame, text=label, bg='white', 
                        font=('Arial', 10, 'bold'), width=15, anchor='w').grid(row=start_row+i, column=0, pady=5, sticky='w')
                tk.Label(info_frame, text=value, bg='white', 
                        font=('Arial', 10)).grid(row=start_row+i, column=1, pady=5, sticky='w')
        
        # Bouton fermer
        tk.Button(detail_window, text="Fermer", 
                 command=detail_window.destroy,
                 bg=self.colors['primary'], fg='white',
                 padx=30, pady=10).pack(pady=20)
    
    def create_consultation_for_patient(self):
        """Crée une consultation pour le patient sélectionné"""
        selection = self.patient_list_tree.selection()
        if not selection:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un patient")
            return
        
        item = selection[0]
        values = self.patient_list_tree.item(item, 'values')
        
        if values:
            dossier = values[0]
            # Naviguer vers l'onglet consultation et pré-remplir le dossier
            self.main_notebook.select(2)  # Onglet Consultations
            
            # Chercher le widget de dossier dans les consultations
            if hasattr(self, 'consult_vars') and 'dossier' in self.consult_vars:
                self.consult_vars['dossier'].set(dossier)
    
    def create_rdv_for_patient(self):
        """Crée un RDV pour le patient sélectionné"""
        selection = self.patient_list_tree.selection()
        if not selection:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un patient")
            return
        
        item = selection[0]
        values = self.patient_list_tree.item(item, 'values')
        
        if values:
            dossier = values[0]
            # Naviguer vers l'onglet RDV
            self.main_notebook.select(4)  # Onglet Rendez-vous
            
            # Pré-remplir le dossier si possible
            if hasattr(self, 'rdv_vars') and 'dossier' in self.rdv_vars:
                self.rdv_vars['dossier'].set(dossier)
    
    def export_patient_row(self):
        """Exporte la ligne sélectionnée"""
        selection = self.patient_list_tree.selection()
        if not selection:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un patient")
            return
        
        item = selection[0]
        values = self.patient_list_tree.item(item, 'values')
        
        if values:
            dossier = values[0]
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM patients WHERE numero_dossier = ?', (dossier,))
                patient = cursor.fetchone()
                
                if patient:
                    # Obtenir les noms de colonnes
                    cursor.execute('PRAGMA table_info(patients)')
                    columns = [col[1] for col in cursor.fetchall()]
                    
                    filename = f'patient_{dossier}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
                    
                    with open(filename, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(columns)
                        writer.writerow(patient)
                    
                    messagebox.showinfo("Export réussi", 
                                      f"Patient exporté dans:\n{os.path.abspath(filename)}")
                    
                    # Journaliser
                    self.log_activity('EXPORT_ROW', 'patients', patient[0], 
                                    f"Patient: {dossier}")
                
                conn.close()
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur export: {e}")
    
    # ==================== CONSULTATIONS AMÉLIORÉES ====================
    
    def create_consultations_tab(self):
        """Onglet Consultations amélioré"""
        tab = tk.Frame(self.main_notebook, bg='white')
        self.main_notebook.add(tab, text="🩺 Consultations")
        
        notebook = ttk.Notebook(tab)
        notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Nouvelle consultation
        new_tab = tk.Frame(notebook, bg='white')
        notebook.add(new_tab, text="➕ Nouvelle")
        self.create_consultation_form(new_tab)
        
        # Historique
        hist_tab = tk.Frame(notebook, bg='white')
        notebook.add(hist_tab, text="📜 Historique")
        self.create_consultation_history(hist_tab)
    
    def create_consultation_form(self, parent):
        """Formulaire consultation amélioré"""
        main_frame = tk.Frame(parent, bg='white', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        tk.Label(main_frame, text="NOUVELLE CONSULTATION", 
                font=('Arial', 14, 'bold'), bg='white').pack(pady=(0, 20))
        
        form = tk.Frame(main_frame, bg='white')
        form.pack()
        
        self.consult_vars = {}
        
        # Recherche patient
        search_frame = tk.Frame(form, bg='white')
        search_frame.grid(row=0, column=0, columnspan=2, pady=10, sticky='w')
        
        tk.Label(search_frame, text="Rechercher patient:", bg='white').pack(side='left', padx=(0, 10))
        self.consult_search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.consult_search_var, width=30)
        search_entry.pack(side='left', padx=(0, 10))
        
        tk.Button(search_frame, text="🔍", 
                 command=self.search_patient_for_consultation,
                 bg=self.colors['info'], fg='white').pack(side='left')
        
        # Numéro dossier
        tk.Label(form, text="Numéro dossier*:", bg='white').grid(row=1, column=0, padx=10, pady=10, sticky='e')
        self.consult_vars['dossier'] = tk.StringVar()
        tk.Entry(form, textvariable=self.consult_vars['dossier'], width=30).grid(row=1, column=1, padx=10, pady=10)
        
        # Signes vitaux
        vital_frame = tk.LabelFrame(form, text="Signes vitaux", bg='white', padx=10, pady=10)
        vital_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky='ew')
        
        vital_fields = [
            ("Température (°C):", "temperature", 10),
            ("Tension:", "tension", 15),
            ("Poids (kg):", "poids", 10),
            ("Taille (cm):", "taille", 10),
            ("Pouls (bpm):", "pouls", 10),
            ("Fréq. resp. (cpm):", "frequence_respiratoire", 10)
        ]
        
        for i, (label, name, width) in enumerate(vital_fields):
            tk.Label(vital_frame, text=label, bg='white').grid(row=i//3, column=(i%3)*2, padx=5, pady=5, sticky='e')
            self.consult_vars[name] = tk.StringVar()
            tk.Entry(vital_frame, textvariable=self.consult_vars[name], 
                    width=width).grid(row=i//3, column=(i%3)*2+1, padx=5, pady=5)
        
        # Autres champs
        other_fields = [
            ("Motif*:", "motif", 40, 4),
            ("Diagnostic*:", "diagnostic", 40, 4),
            ("Prescription:", "prescription", 40, 4)
        ]
        
        start_row = 3
        for i, (label, name, width, height) in enumerate(other_fields):
            tk.Label(form, text=label, bg='white').grid(row=start_row+i, column=0, padx=10, pady=10, sticky='ne')
            
            if height > 1:
                self.consult_vars[name] = tk.Text(form, height=height, width=width)
                self.consult_vars[name].grid(row=start_row+i, column=1, padx=10, pady=10)
            else:
                self.consult_vars[name] = tk.StringVar()
                tk.Entry(form, textvariable=self.consult_vars[name], 
                        width=width).grid(row=start_row+i, column=1, padx=10, pady=10)
        
        # Boutons
        btn_frame = tk.Frame(main_frame, bg='white')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="💾 Enregistrer Consultation", 
                 command=self.save_consultation,
                 bg=self.colors['success'], fg='white',
                 padx=30, pady=10).pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="🗑️ Effacer", 
                 command=self.clear_consultation_form,
                 bg=self.colors['danger'], fg='white',
                 padx=30, pady=10).pack(side='left', padx=10)
        
        # Status
        self.consult_status_label = tk.Label(main_frame, text="", bg='white')
        self.consult_status_label.pack()
    
    def search_patient_for_consultation(self):
        """Recherche un patient pour consultation"""
        search_term = self.consult_search_var.get().strip()
        if not search_term:
            messagebox.showwarning("Recherche", "Veuillez entrer un numéro dossier, nom ou téléphone")
            return
        
        results = self.search_patients(search_term)
        
        if not results:
            messagebox.showinfo("Aucun résultat", "Aucun patient trouvé")
            return
        
        # Prendre le premier résultat
        first_result = results[0]
        self.consult_vars['dossier'].set(first_result[0])
        
        self.consult_status_label.config(
            text=f"✅ Patient trouvé: {first_result[1]} {first_result[2]}", 
            fg=self.colors['success'])
    
    def save_consultation(self):
        """Sauvegarde consultation avec validation"""
        try:
            dossier = self.consult_vars['dossier'].get()
            motif = self.consult_vars['motif'].get("1.0", "end-1c").strip()
            diagnostic = self.consult_vars['diagnostic'].get("1.0", "end-1c").strip()
            
            if not all([dossier, motif, diagnostic]):
                messagebox.showwarning("Erreur", "Remplissez tous les champs obligatoires (*)")
                return
            
            # Trouver patient
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM patients WHERE numero_dossier=?', (dossier,))
            patient = cursor.fetchone()
            
            if not patient:
                messagebox.showerror("Erreur", "Patient introuvable")
                conn.close()
                return
            
            # Récupérer autres données
            prescription = self.consult_vars['prescription'].get("1.0", "end-1c").strip()
            temperature = self.consult_vars['temperature'].get()
            tension = self.consult_vars['tension'].get()
            poids = self.consult_vars['poids'].get()
            taille = self.consult_vars['taille'].get()
            pouls = self.consult_vars['pouls'].get()
            freq_resp = self.consult_vars['frequence_respiratoire'].get()
            
            # Calcul IMC si poids et taille fournis
            imc_val = None
            if poids and taille:
                try:
                    poids_float = float(poids)
                    taille_float = float(taille) / 100  # Convertir cm en m
                    if taille_float > 0:
                        imc_val = round(poids_float / (taille_float ** 2), 1)
                except:
                    pass
            
            # Insérer
            cursor.execute('''
                INSERT INTO consultations 
                (patient_id, personnel_id, motif, diagnostic, prescription, 
                 temperature, tension, poids, taille, imc, pouls, frequence_respiratoire)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                patient[0],
                self.current_user[0],
                motif,
                diagnostic,
                prescription,
                float(temperature) if temperature else None,
                tension if tension else None,
                float(poids) if poids else None,
                float(taille) if taille else None,
                imc_val,
                int(pouls) if pouls else None,
                int(freq_resp) if freq_resp else None
            ))
            
            consultation_id = cursor.lastrowid
            
            conn.commit()
            
            # Journaliser
            self.log_activity('CREATE', 'consultations', consultation_id, 
                            f"Pour patient: {dossier}")
            
            conn.close()
            
            messagebox.showinfo("Succès", "✅ Consultation enregistrée!")
            
            # Réinitialiser
            self.clear_consultation_form()
            
            self.consult_status_label.config(
                text="✅ Consultation enregistrée avec succès!", 
                fg=self.colors['success'])
            
        except ValueError as e:
            messagebox.showerror("Erreur", f"Valeurs numériques invalides: {e}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur: {str(e)}")
    
    def clear_consultation_form(self):
        """Efface formulaire consultation"""
        self.consult_vars['dossier'].set("")
        self.consult_vars['motif'].delete("1.0", tk.END)
        self.consult_vars['diagnostic'].delete("1.0", tk.END)
        self.consult_vars['prescription'].delete("1.0", tk.END)
        for field in ['temperature', 'tension', 'poids', 'taille', 'pouls', 'frequence_respiratoire']:
            if field in self.consult_vars:
                self.consult_vars[field].set("")
        self.consult_search_var.set("")
        self.consult_status_label.config(text="")
    
    def create_consultation_history(self, parent):
        """Historique des consultations"""
        main_frame = tk.Frame(parent, bg='white', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        header_frame = tk.Frame(main_frame, bg='white')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(header_frame, text="HISTORIQUE DES CONSULTATIONS", 
                font=('Arial', 14, 'bold'), bg='white').pack(side='left')
        
        tk.Button(header_frame, text="🔄 Actualiser", 
                 command=self.load_consultation_history,
                 bg=self.colors['info'], fg='white',
                 padx=15, pady=5).pack(side='right')
        
        # Tableau
        tree_frame = tk.Frame(main_frame, bg='white')
        tree_frame.pack(fill='both', expand=True)
        
        columns = ['Date', 'Dossier', 'Patient', 'Motif', 'Diagnostic']
        self.consult_history_tree = ttk.Treeview(tree_frame, columns=columns, 
                                                show='headings', height=15)
        
        for col in columns:
            self.consult_history_tree.heading(col, text=col)
            self.consult_history_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, 
                                 command=self.consult_history_tree.yview)
        self.consult_history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.consult_history_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Charger les données
        self.load_consultation_history()
    
    def load_consultation_history(self):
        """Charge l'historique des consultations"""
        for item in self.consult_history_tree.get_children():
            self.consult_history_tree.delete(item)
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT c.date_consultation, p.numero_dossier, 
                       p.nom || ' ' || p.prenom, c.motif, c.diagnostic
                FROM consultations c
                JOIN patients p ON c.patient_id = p.id
                ORDER BY c.date_consultation DESC
                LIMIT 100
            ''')
            
            for row in cursor.fetchall():
                # Formater la date
                date_str = row[0][:10] if row[0] else ""
                # Limiter la longueur des textes
                motif = row[3][:50] + "..." if len(row[3]) > 50 else row[3]
                diagnostic = row[4][:50] + "..." if len(row[4]) > 50 else row[4]
                
                self.consult_history_tree.insert('', tk.END, 
                                               values=(date_str, row[1], row[2], motif, diagnostic))
            
            conn.close()
        except Exception as e:
            print(f"Erreur historique consultations: {e}")
    
    # ==================== HOSPITALISATION ====================
    
    def create_hospitalisation_tab(self):
        """Onglet Hospitalisation amélioré"""
        tab = tk.Frame(self.main_notebook, bg='white')
        self.main_notebook.add(tab, text="🏥 Hospitalisation")
        
        notebook = ttk.Notebook(tab)
        notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Nouvelle hospitalisation
        new_tab = tk.Frame(notebook, bg='white')
        notebook.add(new_tab, text="➕ Nouvelle")
        self.create_hospitalisation_form(new_tab)
        
        # Liste hospitalisés
        list_tab = tk.Frame(notebook, bg='white')
        notebook.add(list_tab, text="📋 Hospitalisés")
        self.create_hospitalised_list(list_tab)
    
    def create_hospitalisation_form(self, parent):
        """Formulaire hospitalisation amélioré"""
        main_frame = tk.Frame(parent, bg='white', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        tk.Label(main_frame, text="NOUVELLE HOSPITALISATION", 
                font=('Arial', 14, 'bold'), bg='white').pack(pady=(0, 20))
        
        form = tk.Frame(main_frame, bg='white')
        form.pack()
        
        self.hosp_vars = {}
        
        # Recherche patient
        search_frame = tk.Frame(form, bg='white')
        search_frame.grid(row=0, column=0, columnspan=2, pady=10, sticky='w')
        
        tk.Label(search_frame, text="Rechercher patient:", bg='white').pack(side='left', padx=(0, 10))
        self.hosp_search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.hosp_search_var, width=30)
        search_entry.pack(side='left', padx=(0, 10))
        
        tk.Button(search_frame, text="🔍", 
                 command=self.search_patient_for_hospitalisation,
                 bg=self.colors['info'], fg='white').pack(side='left')
        
        # Champs
        fields = [
            ("Dossier patient*:", "dossier"),
            ("Service:", "service"),
            ("Chambre:", "chambre"),
            ("Lit:", "lit")
        ]
        
        for i, (label, name) in enumerate(fields, start=1):
            tk.Label(form, text=label, bg='white').grid(row=i, column=0, padx=10, pady=10, sticky='e')
            self.hosp_vars[name] = tk.StringVar()
            
            if name == "service":
                cursor = self.get_connection().cursor()
                cursor.execute("SELECT nom FROM services ORDER BY nom")
                services = [row[0] for row in cursor.fetchall()]
                ttk.Combobox(form, textvariable=self.hosp_vars[name], 
                           values=services, width=27).grid(row=i, column=1, padx=10, pady=10)
            else:
                tk.Entry(form, textvariable=self.hosp_vars[name], 
                        width=30).grid(row=i, column=1, padx=10, pady=10)
        
        # Motif
        tk.Label(form, text="Motif hospitalisation*:", bg='white').grid(row=5, column=0, padx=10, pady=10, sticky='ne')
        self.hosp_vars['motif'] = tk.Text(form, height=4, width=30)
        self.hosp_vars['motif'].grid(row=5, column=1, padx=10, pady=10)
        
        # Boutons
        btn_frame = tk.Frame(main_frame, bg='white')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="🏥 Admettre patient", 
                 command=self.admit_patient,
                 bg=self.colors['danger'], fg='white',
                 padx=30, pady=10).pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="🗑️ Effacer", 
                 command=self.clear_hospitalisation_form,
                 bg=self.colors['danger'], fg='white',
                 padx=30, pady=10).pack(side='left', padx=10)
        
        # Status
        self.hosp_status_label = tk.Label(main_frame, text="", bg='white')
        self.hosp_status_label.pack()
    
    def search_patient_for_hospitalisation(self):
        """Recherche patient pour hospitalisation"""
        search_term = self.hosp_search_var.get().strip()
        if not search_term:
            messagebox.showwarning("Recherche", "Veuillez entrer un terme de recherche")
            return
        
        results = self.search_patients(search_term)
        
        if not results:
            messagebox.showinfo("Aucun résultat", "Aucun patient trouvé")
            return
        
        # Prendre le premier résultat
        first_result = results[0]
        self.hosp_vars['dossier'].set(first_result[0])
        
        self.hosp_status_label.config(
            text=f"✅ Patient trouvé: {first_result[1]} {first_result[2]}", 
            fg=self.colors['success'])
    
    def admit_patient(self):
        """Admet un patient en hospitalisation"""
        try:
            dossier = self.hosp_vars['dossier'].get()
            motif = self.hosp_vars['motif'].get("1.0", "end-1c").strip()
            
            if not all([dossier, motif]):
                messagebox.showwarning("Erreur", "Dossier et motif requis")
                return
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Vérifier patient
            cursor.execute('SELECT id FROM patients WHERE numero_dossier=?', (dossier,))
            patient = cursor.fetchone()
            
            if not patient:
                messagebox.showerror("Erreur", "Patient introuvable")
                conn.close()
                return
            
            # Vérifier si déjà hospitalisé
            cursor.execute('''
                SELECT id FROM hospitalisations 
                WHERE patient_id=? AND statut="en_cours"
            ''', (patient[0],))
            
            if cursor.fetchone():
                messagebox.showwarning("Déjà hospitalisé", 
                                     "Ce patient est déjà hospitalisé")
                conn.close()
                return
            
            # Vérifier disponibilité chambre
            chambre = self.hosp_vars['chambre'].get()
            if chambre:
                cursor.execute('SELECT lits_disponibles FROM chambres WHERE numero=?', (chambre,))
                chambre_info = cursor.fetchone()
                if chambre_info and chambre_info[0] <= 0:
                    messagebox.showwarning("Chambre indisponible", 
                                         "Cette chambre n'a plus de lits disponibles")
                    conn.close()
                    return
            
            # Admettre
            cursor.execute('''
                INSERT INTO hospitalisations (patient_id, chambre, lit, motif)
                VALUES (?, ?, ?, ?)
            ''', (
                patient[0],
                chambre,
                self.hosp_vars['lit'].get(),
                motif
            ))
            
            hosp_id = cursor.lastrowid
            
            # Mettre à jour les lits disponibles
            if chambre:
                cursor.execute('UPDATE chambres SET lits_disponibles = lits_disponibles - 1 WHERE numero=?', (chambre,))
            
            conn.commit()
            
            # Journaliser
            self.log_activity('CREATE', 'hospitalisations', hosp_id, 
                            f"Patient {dossier} admis en chambre {chambre}")
            
            conn.close()
            
            messagebox.showinfo("Succès", 
                              f"✅ Patient {dossier} admis en hospitalisation")
            
            # Réinitialiser
            self.clear_hospitalisation_form()
            
            # Actualiser la liste
            if hasattr(self, 'load_hospitalised_list'):
                self.load_hospitalised_list()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"{e}")
    
    def clear_hospitalisation_form(self):
        """Efface formulaire hospitalisation"""
        self.hosp_vars['dossier'].set("")
        self.hosp_vars['service'].set("")
        self.hosp_vars['chambre'].set("")
        self.hosp_vars['lit'].set("")
        self.hosp_vars['motif'].delete("1.0", tk.END)
        self.hosp_search_var.set("")
        self.hosp_status_label.config(text="")
    
    def create_hospitalised_list(self, parent):
        """Liste des patients hospitalisés"""
        main_frame = tk.Frame(parent, bg='white', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        header_frame = tk.Frame(main_frame, bg='white')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(header_frame, text="📋 PATIENTS HOSPITALISÉS", 
                font=('Arial', 14, 'bold'), bg='white').pack(side='left')
        
        refresh_btn = tk.Button(header_frame, text="🔄 Actualiser", 
                               command=self.load_hospitalised_list,
                               bg=self.colors['info'], fg='white',
                               padx=15, pady=5)
        refresh_btn.pack(side='right')
        
        # Tableau
        tree_frame = tk.Frame(main_frame, bg='white')
        tree_frame.pack(fill='both', expand=True)
        
        columns = ['Dossier', 'Patient', 'Chambre', 'Lit', 'Date entrée', 'Motif']
        self.hospitalised_tree = ttk.Treeview(tree_frame, columns=columns, 
                                             show='headings', height=15)
        
        for col in columns:
            self.hospitalised_tree.heading(col, text=col)
            self.hospitalised_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, 
                                 command=self.hospitalised_tree.yview)
        self.hospitalised_tree.configure(yscrollcommand=scrollbar.set)
        
        self.hospitalised_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Menu contextuel
        self.hosp_context_menu = tk.Menu(self.root, tearoff=0)
        self.hosp_context_menu.add_command(label="📋 Voir détails", 
                                          command=self.view_hospitalisation_details)
        self.hosp_context_menu.add_command(label="🏥 Sortie patient", 
                                          command=self.discharge_patient)
        
        self.hospitalised_tree.bind("<Button-3>", self.show_hosp_context_menu)
        
        # Charger les données
        self.load_hospitalised_list()
    
    def load_hospitalised_list(self):
        """Charge la liste des hospitalisés"""
        for item in self.hospitalised_tree.get_children():
            self.hospitalised_tree.delete(item)
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.numero_dossier, p.nom || ' ' || p.prenom, 
                       h.chambre, h.lit, h.date_entree, h.motif
                FROM hospitalisations h
                JOIN patients p ON h.patient_id = p.id
                WHERE h.statut = 'en_cours'
                ORDER BY h.date_entree DESC
            ''')
            
            for row in cursor.fetchall():
                # Formater la date
                date_str = row[4][:10] if row[4] else ""
                # Limiter la longueur du motif
                motif = row[5][:50] + "..." if len(row[5]) > 50 else row[5]
                
                self.hospitalised_tree.insert('', tk.END, 
                                            values=(row[0], row[1], row[2] or "N/A", 
                                                   row[3] or "N/A", date_str, motif))
            
            conn.close()
        except Exception as e:
            print(f"Erreur liste hospitalisés: {e}")
    
    def show_hosp_context_menu(self, event):
        """Affiche le menu contextuel pour hospitalisations"""
        item = self.hospitalised_tree.identify_row(event.y)
        if item:
            self.hospitalised_tree.selection_set(item)
            self.hosp_context_menu.post(event.x_root, event.y_root)
    
    def view_hospitalisation_details(self):
        """Affiche les détails de l'hospitalisation"""
        selection = self.hospitalised_tree.selection()
        if not selection:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un patient")
            return
        
        item = selection[0]
        values = self.hospitalised_tree.item(item, 'values')
        
        if values:
            dossier = values[0]
            
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT h.*, p.nom || ' ' || p.prenom as patient_nom
                    FROM hospitalisations h
                    JOIN patients p ON h.patient_id = p.id
                    WHERE p.numero_dossier = ? AND h.statut = 'en_cours'
                ''', (dossier,))
                
                hosp = cursor.fetchone()
                
                if hosp:
                    # Afficher les détails
                    detail_window = tk.Toplevel(self.root)
                    detail_window.title(f"Détails Hospitalisation - {dossier}")
                    detail_window.geometry("500x400")
                    
                    tk.Label(detail_window, text=f"🏥 HOSPITALISATION - {dossier}", 
                            font=('Arial', 14, 'bold')).pack(pady=20)
                    
                    info_frame = tk.Frame(detail_window, padx=20, pady=20)
                    info_frame.pack(fill='both', expand=True)
                    
                    infos = [
                        ("Patient:", hosp[8]),
                        ("Chambre:", hosp[2] or "Non attribuée"),
                        ("Lit:", hosp[3] or "Non attribué"),
                        ("Date entrée:", hosp[4]),
                        ("Motif:", hosp[7] or "Non spécifié")
                    ]
                    
                    for i, (label, value) in enumerate(infos):
                        tk.Label(info_frame, text=label, font=('Arial', 10, 'bold'), 
                                anchor='w').grid(row=i, column=0, pady=5, sticky='w')
                        tk.Label(info_frame, text=value, font=('Arial', 10)).grid(row=i, column=1, pady=5, sticky='w')
                    
                    # Bouton sortie
                    if self.user_role in ['admin', 'personnel']:
                        tk.Button(detail_window, text="🏥 Sortie du patient", 
                                 command=lambda: self.discharge_patient_from_window(dossier, detail_window),
                                 bg=self.colors['success'], fg='white',
                                 padx=20, pady=10).pack(pady=20)
                    
                    tk.Button(detail_window, text="Fermer", 
                             command=detail_window.destroy,
                             bg=self.colors['primary'], fg='white',
                             padx=20, pady=10).pack()
                
                conn.close()
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur: {e}")
    
    def discharge_patient(self):
        """Sort un patient de l'hospitalisation"""
        selection = self.hospitalised_tree.selection()
        if not selection:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un patient")
            return
        
        item = selection[0]
        values = self.hospitalised_tree.item(item, 'values')
        
        if values:
            dossier = values[0]
            self.discharge_patient_from_window(dossier)
    
    def discharge_patient_from_window(self, dossier, parent_window=None):
        """Sort un patient de l'hospitalisation (depuis fenêtre)"""
        response = messagebox.askyesno("Sortie patient", 
                                      f"Confirmer la sortie du patient {dossier} ?")
        
        if not response:
            return
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Récupérer info hospitalisation
            cursor.execute('''
                SELECT h.id, h.chambre FROM hospitalisations h
                JOIN patients p ON h.patient_id = p.id
                WHERE p.numero_dossier = ? AND h.statut = 'en_cours'
            ''', (dossier,))
            
            hosp = cursor.fetchone()
            
            if not hosp:
                messagebox.showerror("Erreur", "Hospitalisation non trouvée")
                conn.close()
                return
            
            # Mettre à jour statut
            cursor.execute('''
                UPDATE hospitalisations 
                SET statut = 'sortie', date_sortie = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (hosp[0],))
            
            # Libérer le lit si chambre attribuée
            if hosp[1]:
                cursor.execute('UPDATE chambres SET lits_disponibles = lits_disponibles + 1 WHERE numero=?', (hosp[1],))
            
            conn.commit()
            
            # Journaliser
            self.log_activity('UPDATE', 'hospitalisations', hosp[0], 
                            f"Sortie patient {dossier}")
            
            conn.close()
            
            messagebox.showinfo("Succès", f"✅ Patient {dossier} sorti avec succès")
            
            # Fermer fenêtre parente si fournie
            if parent_window:
                parent_window.destroy()
            
            # Actualiser la liste
            self.load_hospitalised_list()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur: {e}")
    
    # ==================== RENDEZ-VOUS AMÉLIORÉS ====================
    
    def create_rendezvous_tab(self):
        """Onglet Rendez-vous amélioré"""
        tab = tk.Frame(self.main_notebook, bg='white')
        self.main_notebook.add(tab, text="📅 Rendez-vous")
        
        notebook = ttk.Notebook(tab)
        notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Nouveau RDV
        new_tab = tk.Frame(notebook, bg='white')
        notebook.add(new_tab, text="➕ Nouveau")
        self.create_rdv_form(new_tab)
        
        # RDV aujourd'hui
        today_tab = tk.Frame(notebook, bg='white')
        notebook.add(today_tab, text="📅 Aujourd'hui")
        self.create_rdv_today_list(today_tab)
        
        # RDV futurs
        future_tab = tk.Frame(notebook, bg='white')
        notebook.add(future_tab, text="📋 Tous")
        self.create_rdv_all_list(future_tab)
    
    def create_rdv_form(self, parent):
        """Formulaire RDV amélioré"""
        main_frame = tk.Frame(parent, bg='white', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        tk.Label(main_frame, text="PRENDRE UN RENDEZ-VOUS", 
                font=('Arial', 14, 'bold'), bg='white').pack(pady=(0, 20))
        
        form = tk.Frame(main_frame, bg='white')
        form.pack()
        
        self.rdv_vars = {}
        
        # Recherche patient
        search_frame = tk.Frame(form, bg='white')
        search_frame.grid(row=0, column=0, columnspan=2, pady=10, sticky='w')
        
        tk.Label(search_frame, text="Rechercher patient:", bg='white').pack(side='left', padx=(0, 10))
        self.rdv_search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.rdv_search_var, width=30)
        search_entry.pack(side='left', padx=(0, 10))
        
        tk.Button(search_frame, text="🔍", 
                 command=self.search_patient_for_rdv,
                 bg=self.colors['info'], fg='white').pack(side='left')
        
        # Champs
        fields = [
            ("Dossier patient*:", "dossier", 30),
            ("Date (JJ/MM/AAAA)*:", "date", 30),
            ("Heure (HH:MM)*:", "heure", 30)
        ]
        
        for i, (label, name, width) in enumerate(fields, start=1):
            tk.Label(form, text=label, bg='white').grid(row=i, column=0, padx=10, pady=10, sticky='e')
            self.rdv_vars[name] = tk.StringVar()
            tk.Entry(form, textvariable=self.rdv_vars[name], 
                    width=width).grid(row=i, column=1, padx=10, pady=10)
        
        # Motif
        tk.Label(form, text="Motif:", bg='white').grid(row=4, column=0, padx=10, pady=10, sticky='ne')
        self.rdv_vars['motif'] = tk.Text(form, height=3, width=30)
        self.rdv_vars['motif'].grid(row=4, column=1, padx=10, pady=10)
        
        # Boutons
        btn_frame = tk.Frame(main_frame, bg='white')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="📅 Enregistrer RDV", 
                 command=self.save_rdv,
                 bg=self.colors['success'], fg='white',
                 padx=30, pady=10).pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="🗑️ Effacer", 
                 command=self.clear_rdv_form,
                 bg=self.colors['danger'], fg='white',
                 padx=30, pady=10).pack(side='left', padx=10)
        
        # Status
        self.rdv_status_label = tk.Label(main_frame, text="", bg='white')
        self.rdv_status_label.pack()
    
    def search_patient_for_rdv(self):
        """Recherche patient pour RDV"""
        search_term = self.rdv_search_var.get().strip()
        if not search_term:
            messagebox.showwarning("Recherche", "Veuillez entrer un terme de recherche")
            return
        
        results = self.search_patients(search_term)
        
        if not results:
            messagebox.showinfo("Aucun résultat", "Aucun patient trouvé")
            return
        
        # Prendre le premier résultat
        first_result = results[0]
        self.rdv_vars['dossier'].set(first_result[0])
        
        self.rdv_status_label.config(
            text=f"✅ Patient trouvé: {first_result[1]} {first_result[2]}", 
            fg=self.colors['success'])
    
    def save_rdv(self):
        """Sauvegarde rendez-vous avec validation"""
        try:
            dossier = self.rdv_vars['dossier'].get()
            date_rdv = self.rdv_vars['date'].get()
            heure_rdv = self.rdv_vars['heure'].get()
            motif = self.rdv_vars['motif'].get("1.0", "end-1c").strip()
            
            if not all([dossier, date_rdv, heure_rdv]):
                messagebox.showwarning("Erreur", "Remplissez tous les champs obligatoires")
                return
            
            # Validation date
            if not self.validate_date(date_rdv):
                messagebox.showwarning("Date invalide", "Format: JJ/MM/AAAA")
                return
            
            # Validation heure
            try:
                datetime.strptime(heure_rdv, '%H:%M')
            except ValueError:
                messagebox.showwarning("Heure invalide", "Format: HH:MM")
                return
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Vérifier patient
            cursor.execute('SELECT id FROM patients WHERE numero_dossier=?', (dossier,))
            patient = cursor.fetchone()
            
            if not patient:
                messagebox.showerror("Erreur", "Patient introuvable")
                conn.close()
                return
            
            # Vérifier conflit d'horaire
            cursor.execute('''
                SELECT COUNT(*) FROM rendez_vous 
                WHERE date_rdv = ? AND heure_rdv = ? AND statut = 'planifie'
            ''', (date_rdv, heure_rdv))
            
            if cursor.fetchone()[0] > 0:
                messagebox.showwarning("Conflit", "Un RDV existe déjà à cette heure")
                conn.close()
                return
            
            # Insérer RDV
            cursor.execute('''
                INSERT INTO rendez_vous (patient_id, date_rdv, heure_rdv, motif)
                VALUES (?, ?, ?, ?)
            ''', (patient[0], date_rdv, heure_rdv, motif))
            
            rdv_id = cursor.lastrowid
            
            conn.commit()
            
            # Journaliser
            self.log_activity('CREATE', 'rendez_vous', rdv_id, 
                            f"RDV pour {dossier} le {date_rdv} à {heure_rdv}")
            
            conn.close()
            
            messagebox.showinfo("Succès", 
                              f"✅ Rendez-vous enregistré!\n\n"
                              f"📅 Date: {date_rdv}\n"
                              f"⏰ Heure: {heure_rdv}\n"
                              f"📁 Patient: {dossier}")
            
            # Réinitialiser et actualiser les listes
            self.clear_rdv_form()
            self.refresh_rdv_lists()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"{e}")
    
    def clear_rdv_form(self):
        """Efface formulaire RDV"""
        self.rdv_vars['dossier'].set("")
        self.rdv_vars['date'].set("")
        self.rdv_vars['heure'].set("")
        self.rdv_vars['motif'].delete("1.0", tk.END)
        self.rdv_search_var.set("")
        self.rdv_status_label.config(text="")
    
    def refresh_rdv_lists(self):
        """Actualise les listes de RDV"""
        if hasattr(self, 'load_rdv_today'):
            self.load_rdv_today()
        if hasattr(self, 'load_rdv_all'):
            self.load_rdv_all()
    
    def create_rdv_today_list(self, parent):
        """Liste des RDV d'aujourd'hui"""
        main_frame = tk.Frame(parent, bg='white', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        header_frame = tk.Frame(main_frame, bg='white')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(header_frame, text=f"📅 RENDEZ-VOUS AUJOURD'HUI - {datetime.now().strftime('%d/%m/%Y')}", 
                font=('Arial', 14, 'bold'), bg='white').pack(side='left')
        
        refresh_btn = tk.Button(header_frame, text="🔄 Actualiser", 
                               command=self.load_rdv_today,
                               bg=self.colors['info'], fg='white',
                               padx=15, pady=5)
        refresh_btn.pack(side='right')
        
        # Tableau
        tree_frame = tk.Frame(main_frame, bg='white')
        tree_frame.pack(fill='both', expand=True)
        
        columns = ['Heure', 'Dossier', 'Patient', 'Motif', 'Statut']
        self.rdv_today_tree = ttk.Treeview(tree_frame, columns=columns, 
                                          show='headings', height=15)
        
        for col in columns:
            self.rdv_today_tree.heading(col, text=col)
            self.rdv_today_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, 
                                 command=self.rdv_today_tree.yview)
        self.rdv_today_tree.configure(yscrollcommand=scrollbar.set)
        
        self.rdv_today_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Charger les données
        self.load_rdv_today()
    
    def load_rdv_today(self):
        """Charge les RDV d'aujourd'hui"""
        for item in self.rdv_today_tree.get_children():
            self.rdv_today_tree.delete(item)
        
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT r.heure_rdv, p.numero_dossier, 
                       p.nom || ' ' || p.prenom, r.motif, r.statut
                FROM rendez_vous r
                JOIN patients p ON r.patient_id = p.id
                WHERE r.date_rdv = ? AND r.statut = 'planifie'
                ORDER BY r.heure_rdv
            ''', (today,))
            
            for row in cursor.fetchall():
                self.rdv_today_tree.insert('', tk.END, values=row)
            
            conn.close()
            
            # Mettre à jour le nombre
            count = len(self.rdv_today_tree.get_children())
            
        except Exception as e:
            print(f"Erreur RDV aujourd'hui: {e}")
    
    def create_rdv_all_list(self, parent):
        """Liste de tous les RDV futurs"""
        main_frame = tk.Frame(parent, bg='white', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        header_frame = tk.Frame(main_frame, bg='white')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(header_frame, text="📋 TOUS LES RENDEZ-VOUS FUTURS", 
                font=('Arial', 14, 'bold'), bg='white').pack(side='left')
        
        refresh_btn = tk.Button(header_frame, text="🔄 Actualiser", 
                               command=self.load_rdv_all,
                               bg=self.colors['info'], fg='white',
                               padx=15, pady=5)
        refresh_btn.pack(side='right')
        
        # Tableau
        tree_frame = tk.Frame(main_frame, bg='white')
        tree_frame.pack(fill='both', expand=True)
        
        columns = ['Date', 'Heure', 'Dossier', 'Patient', 'Motif', 'Statut']
        self.rdv_all_tree = ttk.Treeview(tree_frame, columns=columns, 
                                        show='headings', height=15)
        
        for col in columns:
            self.rdv_all_tree.heading(col, text=col)
            self.rdv_all_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, 
                                 command=self.rdv_all_tree.yview)
        self.rdv_all_tree.configure(yscrollcommand=scrollbar.set)
        
        self.rdv_all_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Charger les données
        self.load_rdv_all()
    
    def load_rdv_all(self):
        """Charge tous les RDV futurs"""
        for item in self.rdv_all_tree.get_children():
            self.rdv_all_tree.delete(item)
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT r.date_rdv, r.heure_rdv, p.numero_dossier, 
                       p.nom || ' ' || p.prenom, r.motif, r.statut
                FROM rendez_vous r
                JOIN patients p ON r.patient_id = p.id
                WHERE r.date_rdv >= date('now') AND r.statut = 'planifie'
                ORDER BY r.date_rdv, r.heure_rdv
                LIMIT 100
            ''')
            
            for row in cursor.fetchall():
                # Formater la date
                date_str = row[0]
                if len(row[0]) > 10:
                    date_str = row[0][:10]
                
                self.rdv_all_tree.insert('', tk.END, 
                                       values=(date_str, row[1], row[2], row[3], row[4], row[5]))
            
            conn.close()
        except Exception as e:
            print(f"Erreur RDV futurs: {e}")
    
    # ==================== FACTURATION AMÉLIORÉE ====================
    
    def create_facturation_tab(self):
        """Onglet Facturation amélioré"""
        tab = tk.Frame(self.main_notebook, bg='white')
        self.main_notebook.add(tab, text="💰 Facturation")
        
        notebook = ttk.Notebook(tab)
        notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Nouvelle facture
        new_tab = tk.Frame(notebook, bg='white')
        notebook.add(new_tab, text="➕ Nouvelle")
        self.create_facture_form(new_tab)
        
        # Factures impayées
        unpaid_tab = tk.Frame(notebook, bg='white')
        notebook.add(unpaid_tab, text="📋 Impayées")
        self.create_unpaid_factures_list(unpaid_tab)
        
        # Historique
        hist_tab = tk.Frame(notebook, bg='white')
        notebook.add(hist_tab, text="📜 Historique")
        self.create_facture_history(hist_tab)
    
    def create_facture_form(self, parent):
        """Formulaire facture amélioré"""
        main_frame = tk.Frame(parent, bg='white', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        tk.Label(main_frame, text="NOUVELLE FACTURE", 
                font=('Arial', 14, 'bold'), bg='white').pack(pady=(0, 20))
        
        form = tk.Frame(main_frame, bg='white')
        form.pack()
        
        self.fact_vars = {}
        
        # Recherche patient
        search_frame = tk.Frame(form, bg='white')
        search_frame.grid(row=0, column=0, columnspan=2, pady=10, sticky='w')
        
        tk.Label(search_frame, text="Rechercher patient:", bg='white').pack(side='left', padx=(0, 10))
        self.fact_search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.fact_search_var, width=30)
        search_entry.pack(side='left', padx=(0, 10))
        
        tk.Button(search_frame, text="🔍", 
                 command=self.search_patient_for_facture,
                 bg=self.colors['info'], fg='white').pack(side='left')
        
        # Champs
        tk.Label(form, text="Dossier patient*:", bg='white').grid(row=1, column=0, padx=10, pady=10, sticky='e')
        self.fact_vars['dossier'] = tk.StringVar()
        tk.Entry(form, textvariable=self.fact_vars['dossier'], width=30).grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(form, text="Type*:", bg='white').grid(row=2, column=0, padx=10, pady=10, sticky='e')
        self.fact_vars['type'] = tk.StringVar()
        types = ['Consultation', 'Hospitalisation', 'Médicaments', 'Examens', 'Chirurgie', 'Autre']
        ttk.Combobox(form, textvariable=self.fact_vars['type'], values=types, 
                    width=27, state='readonly').grid(row=2, column=1, padx=10, pady=10)
        
        tk.Label(form, text="Montant (FCFA)*:", bg='white').grid(row=3, column=0, padx=10, pady=10, sticky='e')
        self.fact_vars['montant'] = tk.StringVar()
        tk.Entry(form, textvariable=self.fact_vars['montant'], width=30).grid(row=3, column=1, padx=10, pady=10)
        
        # Boutons
        btn_frame = tk.Frame(main_frame, bg='white')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="💰 Créer Facture", 
                 command=self.save_facture,
                 bg=self.colors['success'], fg='white',
                 padx=30, pady=10).pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="🗑️ Effacer", 
                 command=self.clear_facture_form,
                 bg=self.colors['danger'], fg='white',
                 padx=30, pady=10).pack(side='left', padx=10)
        
        # Status
        self.fact_status_label = tk.Label(main_frame, text="", bg='white')
        self.fact_status_label.pack()
    
    def search_patient_for_facture(self):
        """Recherche patient pour facture"""
        search_term = self.fact_search_var.get().strip()
        if not search_term:
            messagebox.showwarning("Recherche", "Veuillez entrer un terme de recherche")
            return
        
        results = self.search_patients(search_term)
        
        if not results:
            messagebox.showinfo("Aucun résultat", "Aucun patient trouvé")
            return
        
        # Prendre le premier résultat
        first_result = results[0]
        self.fact_vars['dossier'].set(first_result[0])
        
        self.fact_status_label.config(
            text=f"✅ Patient trouvé: {first_result[1]} {first_result[2]}", 
            fg=self.colors['success'])
    
    def save_facture(self):
        """Sauvegarde facture avec validation"""
        try:
            dossier = self.fact_vars['dossier'].get()
            type_fact = self.fact_vars['type'].get()
            montant_str = self.fact_vars['montant'].get()
            
            if not all([dossier, type_fact, montant_str]):
                messagebox.showwarning("Erreur", "Remplissez tous les champs")
                return
            
            # Validation montant
            try:
                montant_val = float(montant_str)
                if montant_val <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Montant invalide", "Montant doit être un nombre positif")
                return
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Vérifier patient
            cursor.execute('SELECT id FROM patients WHERE numero_dossier=?', (dossier,))
            patient = cursor.fetchone()
            
            if not patient:
                messagebox.showerror("Erreur", "Patient introuvable")
                conn.close()
                return
            
            # Générer numéro facture
            facture_num = f"FACT{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"
            
            # Insérer facture
            cursor.execute('''
                INSERT INTO factures (patient_id, type, montant, reste, numero_facture)
                VALUES (?, ?, ?, ?, ?)
            ''', (patient[0], type_fact, montant_val, montant_val, facture_num))
            
            facture_id = cursor.lastrowid
            
            conn.commit()
            
            # Journaliser
            self.log_activity('CREATE', 'factures', facture_id, 
                            f"Facture {facture_num}: {montant_val} FCFA pour {dossier}")
            
            conn.close()
            
            messagebox.showinfo("Succès", 
                              f"✅ Facture créée!\n\n"
                              f"📋 N°: {facture_num}\n"
                              f"💰 Montant: {montant_val:,.0f} FCFA\n"
                              f"📁 Patient: {dossier}\n"
                              f"📋 Type: {type_fact}")
            
            # Réinitialiser et actualiser
            self.clear_facture_form()
            self.refresh_facture_lists()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"{e}")
    
    def clear_facture_form(self):
        """Efface formulaire facture"""
        self.fact_vars['dossier'].set("")
        self.fact_vars['type'].set("")
        self.fact_vars['montant'].set("")
        self.fact_search_var.set("")
        self.fact_status_label.config(text="")
    
    def refresh_facture_lists(self):
        """Actualise les listes de factures"""
        if hasattr(self, 'load_unpaid_factures'):
            self.load_unpaid_factures()
        if hasattr(self, 'load_facture_history'):
            self.load_facture_history()
    
    def create_unpaid_factures_list(self, parent):
        """Liste des factures impayées"""
        main_frame = tk.Frame(parent, bg='white', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        header_frame = tk.Frame(main_frame, bg='white')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(header_frame, text="📋 FACTURES IMPAYÉES", 
                font=('Arial', 14, 'bold'), bg='white').pack(side='left')
        
        refresh_btn = tk.Button(header_frame, text="🔄 Actualiser", 
                               command=self.load_unpaid_factures,
                               bg=self.colors['info'], fg='white',
                               padx=15, pady=5)
        refresh_btn.pack(side='right')
        
        # Tableau
        tree_frame = tk.Frame(main_frame, bg='white')
        tree_frame.pack(fill='both', expand=True)
        
        columns = ['Date', 'N° Facture', 'Dossier', 'Patient', 'Type', 'Montant', 'Reste', 'Statut']
        self.unpaid_tree = ttk.Treeview(tree_frame, columns=columns, 
                                       show='headings', height=15)
        
        for col in columns:
            self.unpaid_tree.heading(col, text=col)
            self.unpaid_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, 
                                 command=self.unpaid_tree.yview)
        self.unpaid_tree.configure(yscrollcommand=scrollbar.set)
        
        self.unpaid_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Menu contextuel pour paiement
        self.facture_context_menu = tk.Menu(self.root, tearoff=0)
        self.facture_context_menu.add_command(label="💰 Enregistrer paiement", 
                                            command=self.register_payment)
        
        self.unpaid_tree.bind("<Button-3>", self.show_facture_context_menu)
        
        # Charger les données
        self.load_unpaid_factures()
    
    def load_unpaid_factures(self):
        """Charge les factures impayées"""
        for item in self.unpaid_tree.get_children():
            self.unpaid_tree.delete(item)
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT f.date_facture, f.numero_facture, p.numero_dossier, 
                       p.nom || ' ' || p.prenom, f.type, f.montant, f.reste, f.statut
                FROM factures f
                JOIN patients p ON f.patient_id = p.id
                WHERE f.statut != 'paye'
                ORDER BY f.date_facture DESC
                LIMIT 100
            ''')
            
            for row in cursor.fetchall():
                # Formater les montants
                date_str = row[0][:10] if row[0] else ""
                montant = f"{row[5]:,.0f}" if row[5] else "0"
                reste = f"{row[6]:,.0f}" if row[6] else "0"
                
                self.unpaid_tree.insert('', tk.END, 
                                      values=(date_str, row[1] or "N/A", row[2], row[3], 
                                             row[4], montant, reste, row[7]))
            
            conn.close()
        except Exception as e:
            print(f"Erreur factures impayées: {e}")
    
    def show_facture_context_menu(self, event):
        """Affiche le menu contextuel pour factures"""
        item = self.unpaid_tree.identify_row(event.y)
        if item:
            self.unpaid_tree.selection_set(item)
            self.facture_context_menu.post(event.x_root, event.y_root)
    
    def register_payment(self):
        """Enregistre un paiement pour une facture"""
        selection = self.unpaid_tree.selection()
        if not selection:
            messagebox.showwarning("Sélection", "Veuillez sélectionner une facture")
            return
        
        item = selection[0]
        values = self.unpaid_tree.item(item, 'values')
        
        if values:
            facture_num = values[1]
            dossier = values[2]
            montant_total = float(values[5].replace(',', ''))
            reste = float(values[6].replace(',', ''))
            
            # Fenêtre de paiement
            payment_window = tk.Toplevel(self.root)
            payment_window.title(f"Paiement Facture {facture_num}")
            payment_window.geometry("400x300")
            
            tk.Label(payment_window, text=f"💰 PAIEMENT FACTURE", 
                    font=('Arial', 14, 'bold')).pack(pady=20)
            
            info_frame = tk.Frame(payment_window, padx=20, pady=10)
            info_frame.pack()
            
            tk.Label(info_frame, text=f"Facture N°: {facture_num}", 
                    font=('Arial', 10, 'bold')).grid(row=0, column=0, columnspan=2, pady=5, sticky='w')
            tk.Label(info_frame, text=f"Patient: {dossier}").grid(row=1, column=0, columnspan=2, pady=5, sticky='w')
            tk.Label(info_frame, text=f"Montant total: {montant_total:,.0f} FCFA").grid(row=2, column=0, columnspan=2, pady=5, sticky='w')
            tk.Label(info_frame, text=f"Reste à payer: {reste:,.0f} FCFA").grid(row=3, column=0, columnspan=2, pady=5, sticky='w')
            
            tk.Label(info_frame, text="Montant payé (FCFA):").grid(row=4, column=0, pady=15, sticky='e')
            montant_paye_var = tk.StringVar()
            montant_entry = tk.Entry(info_frame, textvariable=montant_paye_var, width=15)
            montant_entry.grid(row=4, column=1, pady=15, sticky='w')
            montant_entry.insert(0, str(reste))
            
            tk.Label(info_frame, text="Mode de paiement:").grid(row=5, column=0, pady=5, sticky='e')
            mode_var = tk.StringVar()
            modes = ['Espèces', 'Carte bancaire', 'Chèque', 'Mobile Money', 'Virement']
            ttk.Combobox(info_frame, textvariable=mode_var, values=modes, width=13).grid(row=5, column=1, pady=5, sticky='w')
            
            def save_payment():
                try:
                    montant_paye = float(montant_paye_var.get())
                    mode_paiement = mode_var.get()
                    
                    if montant_paye <= 0:
                        messagebox.showwarning("Montant invalide", "Le montant doit être positif")
                        return
                    
                    if not mode_paiement:
                        messagebox.showwarning("Mode manquant", "Veuillez sélectionner un mode de paiement")
                        return
                    
                    conn = self.get_connection()
                    cursor = conn.cursor()
                    
                    # Mettre à jour la facture
                    cursor.execute('''
                        UPDATE factures 
                        SET paye = paye + ?, 
                            mode_paiement = COALESCE(mode_paiement, ?),
                            date_paiement = CURRENT_TIMESTAMP,
                            reference_paiement = ?
                        WHERE numero_facture = ?
                    ''', (montant_paye, mode_paiement, 
                          f"PAY{datetime.now().strftime('%Y%m%d%H%M%S')}",
                          facture_num))
                    
                    conn.commit()
                    
                    # Journaliser
                    cursor.execute('SELECT id FROM factures WHERE numero_facture = ?', (facture_num,))
                    facture_id = cursor.fetchone()[0]
                    
                    self.log_activity('PAYMENT', 'factures', facture_id, 
                                    f"Paiement de {montant_paye:,.0f} FCFA sur facture {facture_num}")
                    
                    conn.close()
                    
                    messagebox.showinfo("Succès", f"✅ Paiement de {montant_paye:,.0f} FCFA enregistré")
                    payment_window.destroy()
                    
                    # Actualiser les listes
                    self.refresh_facture_lists()
                    
                except ValueError:
                    messagebox.showerror("Erreur", "Montant invalide")
                except Exception as e:
                    messagebox.showerror("Erreur", f"Erreur: {e}")
            
            btn_frame = tk.Frame(payment_window)
            btn_frame.pack(pady=20)
            
            tk.Button(btn_frame, text="💳 Enregistrer Paiement", 
                     command=save_payment,
                     bg=self.colors['success'], fg='white',
                     padx=20, pady=10).pack(side='left', padx=10)
            
            tk.Button(btn_frame, text="Annuler", 
                     command=payment_window.destroy,
                     bg=self.colors['danger'], fg='white',
                     padx=20, pady=10).pack(side='left', padx=10)
    
    def create_facture_history(self, parent):
        """Historique des factures"""
        main_frame = tk.Frame(parent, bg='white', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        header_frame = tk.Frame(main_frame, bg='white')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(header_frame, text="📜 HISTORIQUE DES FACTURES", 
                font=('Arial', 14, 'bold'), bg='white').pack(side='left')
        
        refresh_btn = tk.Button(header_frame, text="🔄 Actualiser", 
                               command=self.load_facture_history,
                               bg=self.colors['info'], fg='white',
                               padx=15, pady=5)
        refresh_btn.pack(side='right')
        
        # Tableau
        tree_frame = tk.Frame(main_frame, bg='white')
        tree_frame.pack(fill='both', expand=True)
        
        columns = ['Date', 'N° Facture', 'Dossier', 'Patient', 'Type', 'Montant', 'Payé', 'Statut']
        self.fact_history_tree = ttk.Treeview(tree_frame, columns=columns, 
                                             show='headings', height=15)
        
        for col in columns:
            self.fact_history_tree.heading(col, text=col)
            self.fact_history_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, 
                                 command=self.fact_history_tree.yview)
        self.fact_history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.fact_history_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Charger les données
        self.load_facture_history()
    
    def load_facture_history(self):
        """Charge l'historique des factures"""
        for item in self.fact_history_tree.get_children():
            self.fact_history_tree.delete(item)
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT f.date_facture, f.numero_facture, p.numero_dossier, 
                       p.nom || ' ' || p.prenom, f.type, f.montant, f.paye, f.statut
                FROM factures f
                JOIN patients p ON f.patient_id = p.id
                ORDER BY f.date_facture DESC
                LIMIT 100
            ''')
            
            for row in cursor.fetchall():
                # Formater les montants
                date_str = row[0][:10] if row[0] else ""
                montant = f"{row[5]:,.0f}" if row[5] else "0"
                paye = f"{row[6]:,.0f}" if row[6] else "0"
                
                self.fact_history_tree.insert('', tk.END, 
                                            values=(date_str, row[1] or "N/A", row[2], row[3], 
                                                   row[4], montant, paye, row[7]))
            
            conn.close()
        except Exception as e:
            print(f"Erreur historique factures: {e}")
    
    # ==================== VACCINATIONS AMÉLIORÉES ====================
    
    def create_vaccinations_tab(self):
        """Onglet Vaccinations amélioré"""
        tab = tk.Frame(self.main_notebook, bg='white')
        self.main_notebook.add(tab, text="💉 Vaccinations")
        
        notebook = ttk.Notebook(tab)
        notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Nouvelle vaccination
        new_tab = tk.Frame(notebook, bg='white')
        notebook.add(new_tab, text="➕ Nouvelle")
        self.create_vaccination_form(new_tab)
        
        # Historique
        hist_tab = tk.Frame(notebook, bg='white')
        notebook.add(hist_tab, text="📜 Historique")
        self.create_vaccination_history(hist_tab)
    
    def create_vaccination_form(self, parent):
        """Formulaire vaccination amélioré"""
        main_frame = tk.Frame(parent, bg='white', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        tk.Label(main_frame, text="VACCINATION - PROGRAMME ÉLARGI DE VACCINATION (PEV)", 
                font=('Arial', 14, 'bold'), bg='white').pack(pady=(0, 20))
        
        form = tk.Frame(main_frame, bg='white')
        form.pack()
        
        self.vacc_vars = {}
        
        # Recherche patient
        search_frame = tk.Frame(form, bg='white')
        search_frame.grid(row=0, column=0, columnspan=2, pady=10, sticky='w')
        
        tk.Label(search_frame, text="Rechercher patient:", bg='white').pack(side='left', padx=(0, 10))
        self.vacc_search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.vacc_search_var, width=30)
        search_entry.pack(side='left', padx=(0, 10))
        
        tk.Button(search_frame, text="🔍", 
                 command=self.search_patient_for_vaccination,
                 bg=self.colors['info'], fg='white').pack(side='left')
        
        # Champs
        tk.Label(form, text="Dossier patient*:", bg='white').grid(row=1, column=0, padx=10, pady=10, sticky='e')
        self.vacc_vars['dossier'] = tk.StringVar()
        tk.Entry(form, textvariable=self.vacc_vars['dossier'], width=30).grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(form, text="Vaccin*:", bg='white').grid(row=2, column=0, padx=10, pady=10, sticky='e')
        self.vacc_vars['vaccin'] = tk.StringVar()
        vaccins = ['BCG', 'VPO 0', 'VPO 1', 'VPO 2', 'VPO 3', 
                  'Penta 1', 'Penta 2', 'Penta 3', 
                  'VPI', 'Rougeole', 'Fièvre Jaune', 'VAR', 
                  'COVID-19', 'Tétanos', 'Hépatite B']
        ttk.Combobox(form, textvariable=self.vacc_vars['vaccin'], values=vaccins, 
                    width=27, state='readonly').grid(row=2, column=1, padx=10, pady=10)
        
        tk.Label(form, text="Dose/Rappel:", bg='white').grid(row=3, column=0, padx=10, pady=10, sticky='e')
        self.vacc_vars['dose'] = tk.StringVar()
        doses = ['1ère dose', '2ème dose', '3ème dose', 'Rappel', 'Unique']
        ttk.Combobox(form, textvariable=self.vacc_vars['dose'], values=doses, 
                    width=27).grid(row=3, column=1, padx=10, pady=10)
        
        # Boutons
        btn_frame = tk.Frame(main_frame, bg='white')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="💉 Enregistrer Vaccination", 
                 command=self.save_vaccination,
                 bg=self.colors['success'], fg='white',
                 padx=30, pady=10).pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="🗑️ Effacer", 
                 command=self.clear_vaccination_form,
                 bg=self.colors['danger'], fg='white',
                 padx=30, pady=10).pack(side='left', padx=10)
        
        # Status
        self.vacc_status_label = tk.Label(main_frame, text="", bg='white')
        self.vacc_status_label.pack()
    
    def search_patient_for_vaccination(self):
        """Recherche patient pour vaccination"""
        search_term = self.vacc_search_var.get().strip()
        if not search_term:
            messagebox.showwarning("Recherche", "Veuillez entrer un terme de recherche")
            return
        
        results = self.search_patients(search_term)
        
        if not results:
            messagebox.showinfo("Aucun résultat", "Aucun patient trouvé")
            return
        
        # Prendre le premier résultat
        first_result = results[0]
        self.vacc_vars['dossier'].set(first_result[0])
        
        self.vacc_status_label.config(
            text=f"✅ Patient trouvé: {first_result[1]} {first_result[2]}", 
            fg=self.colors['success'])
    
    def save_vaccination(self):
        """Sauvegarde vaccination"""
        try:
            dossier = self.vacc_vars['dossier'].get()
            vaccin = self.vacc_vars['vaccin'].get()
            dose = self.vacc_vars['dose'].get()
            
            if not all([dossier, vaccin]):
                messagebox.showwarning("Erreur", "Remplissez dossier et vaccin")
                return
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Vérifier patient
            cursor.execute('SELECT id FROM patients WHERE numero_dossier=?', (dossier,))
            patient = cursor.fetchone()
            
            if not patient:
                messagebox.showerror("Erreur", "Patient introuvable")
                conn.close()
                return
            
            # Vérifier si enfant (pour certains vaccins)
            cursor.execute('SELECT type_patient FROM patients WHERE id=?', (patient[0],))
            patient_type = cursor.fetchone()[0]
            
            if patient_type == "adulte" and vaccin in ['BCG', 'Penta 1', 'Penta 2', 'Penta 3']:
                response = messagebox.askyesno("Vaccin enfant", 
                                             "Ce vaccin est généralement pour les enfants.\nContinuer quand même?")
                if not response:
                    conn.close()
                    return
            
            # Insérer vaccination
            cursor.execute('''
                INSERT INTO vaccinations (patient_id, vaccin, dose)
                VALUES (?, ?, ?)
            ''', (patient[0], vaccin, dose))
            
            vacc_id = cursor.lastrowid
            
            conn.commit()
            
            # Journaliser
            self.log_activity('CREATE', 'vaccinations', vacc_id, 
                            f"Vaccin {vaccin} pour {dossier}")
            
            conn.close()
            
            messagebox.showinfo("Succès", 
                              f"✅ Vaccination enregistrée!\n\n"
                              f"💉 Vaccin: {vaccin}\n"
                              f"📁 Patient: {dossier}\n"
                              f"🔢 Dose: {dose or 'Non spécifié'}")
            
            # Réinitialiser et actualiser
            self.clear_vaccination_form()
            self.refresh_vaccination_history()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"{e}")
    
    def clear_vaccination_form(self):
        """Efface formulaire vaccination"""
        self.vacc_vars['dossier'].set("")
        self.vacc_vars['vaccin'].set("")
        self.vacc_vars['dose'].set("")
        self.vacc_search_var.set("")
        self.vacc_status_label.config(text="")
    
    def refresh_vaccination_history(self):
        """Actualise l'historique des vaccinations"""
        if hasattr(self, 'load_vaccination_history'):
            self.load_vaccination_history()
    
    def create_vaccination_history(self, parent):
        """Historique des vaccinations"""
        main_frame = tk.Frame(parent, bg='white', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        header_frame = tk.Frame(main_frame, bg='white')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(header_frame, text="📜 HISTORIQUE DES VACCINATIONS", 
                font=('Arial', 14, 'bold'), bg='white').pack(side='left')
        
        refresh_btn = tk.Button(header_frame, text="🔄 Actualiser", 
                               command=self.load_vaccination_history,
                               bg=self.colors['info'], fg='white',
                               padx=15, pady=5)
        refresh_btn.pack(side='right')
        
        # Tableau
        tree_frame = tk.Frame(main_frame, bg='white')
        tree_frame.pack(fill='both', expand=True)
        
        columns = ['Date', 'Dossier', 'Patient', 'Vaccin', 'Dose']
        self.vacc_history_tree = ttk.Treeview(tree_frame, columns=columns, 
                                             show='headings', height=15)
        
        for col in columns:
            self.vacc_history_tree.heading(col, text=col)
            self.vacc_history_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, 
                                 command=self.vacc_history_tree.yview)
        self.vacc_history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.vacc_history_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Charger les données
        self.load_vaccination_history()
    
    def load_vaccination_history(self):
        """Charge l'historique des vaccinations"""
        for item in self.vacc_history_tree.get_children():
            self.vacc_history_tree.delete(item)
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT v.date_vaccination, p.numero_dossier, 
                       p.nom || ' ' || p.prenom, v.vaccin, v.dose
                FROM vaccinations v
                JOIN patients p ON v.patient_id = p.id
                ORDER BY v.date_vaccination DESC
                LIMIT 100
            ''')
            
            for row in cursor.fetchall():
                # Formater la date
                date_str = row[0][:10] if row[0] else ""
                
                self.vacc_history_tree.insert('', tk.END, 
                                            values=(date_str, row[1], row[2], row[3], row[4] or ""))
            
            conn.close()
        except Exception as e:
            print(f"Erreur historique vaccinations: {e}")
    
    # ==================== NOUVEAUX ONGLETS ====================
    
    def create_medicaments_tab(self):
        """Onglet Gestion des médicaments"""
        tab = tk.Frame(self.main_notebook, bg='white')
        self.main_notebook.add(tab, text="💊 Médicaments")
        
        notebook = ttk.Notebook(tab)
        notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Nouveau médicament
        new_tab = tk.Frame(notebook, bg='white')
        notebook.add(new_tab, text="➕ Nouveau")
        self.create_medicament_form(new_tab)
        
        # Liste médicaments
        list_tab = tk.Frame(notebook, bg='white')
        notebook.add(list_tab, text="📋 Liste")
        self.create_medicament_list(list_tab)
        
        # Alertes stock
        alert_tab = tk.Frame(notebook, bg='white')
        notebook.add(alert_tab, text="⚠️ Alertes")
        self.create_stock_alerts(alert_tab)
    
    def create_medicament_form(self, parent):
        """Formulaire pour ajouter un médicament"""
        main_frame = tk.Frame(parent, bg='white', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        tk.Label(main_frame, text="NOUVEAU MÉDICAMENT", 
                font=('Arial', 14, 'bold'), bg='white').pack(pady=(0, 20))
        
        form = tk.Frame(main_frame, bg='white')
        form.pack()
        
        self.med_vars = {}
        
        fields = [
            ("Nom*:", "nom", 30),
            ("Code*:", "code", 30),
            ("Catégorie:", "categorie", 30),
            ("Forme:", "forme", 30),
            ("Dosage:", "dosage", 30),
            ("Stock initial:", "stock", 10),
            ("Seuil alerte:", "seuil_alerte", 10),
            ("Prix unitaire (FCFA):", "prix_unitaire", 15),
            ("Date expiration (JJ/MM/AAAA):", "date_expiration", 20)
        ]
        
        for i, (label, name, width) in enumerate(fields):
            tk.Label(form, text=label, bg='white').grid(row=i, column=0, padx=10, pady=8, sticky='e')
            self.med_vars[name] = tk.StringVar()
            
            if name in ['stock', 'seuil_alerte', 'prix_unitaire']:
                tk.Entry(form, textvariable=self.med_vars[name], 
                        width=width).grid(row=i, column=1, padx=10, pady=8)
            else:
                tk.Entry(form, textvariable=self.med_vars[name], 
                        width=width).grid(row=i, column=1, padx=10, pady=8)
        
        # Boutons
        btn_frame = tk.Frame(main_frame, bg='white')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="💾 Enregistrer", 
                 command=self.save_medicament,
                 bg=self.colors['success'], fg='white',
                 padx=30, pady=10).pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="🗑️ Effacer", 
                 command=self.clear_medicament_form,
                 bg=self.colors['danger'], fg='white',
                 padx=30, pady=10).pack(side='left', padx=10)
        
        # Status
        self.med_status_label = tk.Label(main_frame, text="", bg='white')
        self.med_status_label.pack()
    
    def save_medicament(self):
        """Sauvegarde un médicament"""
        try:
            nom = self.med_vars['nom'].get()
            code = self.med_vars['code'].get()
            
            if not all([nom, code]):
                messagebox.showwarning("Erreur", "Nom et code sont obligatoires")
                return
            
            # Validation des nombres
            try:
                stock = int(self.med_vars['stock'].get()) if self.med_vars['stock'].get() else 0
                seuil = int(self.med_vars['seuil_alerte'].get()) if self.med_vars['seuil_alerte'].get() else 10
                prix = float(self.med_vars['prix_unitaire'].get()) if self.med_vars['prix_unitaire'].get() else 0
            except ValueError:
                messagebox.showwarning("Erreur", "Stock, seuil et prix doivent être des nombres")
                return
            
            # Validation date
            date_exp = self.med_vars['date_expiration'].get()
            if date_exp and not self.validate_date(date_exp):
                messagebox.showwarning("Date invalide", "Format: JJ/MM/AAAA")
                return
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO medicaments 
                    (nom, code, categorie, forme, dosage, stock, seuil_alerte, prix_unitaire, date_expiration)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    nom,
                    code,
                    self.med_vars['categorie'].get(),
                    self.med_vars['forme'].get(),
                    self.med_vars['dosage'].get(),
                    stock,
                    seuil,
                    prix,
                    date_exp if date_exp else None
                ))
                
                med_id = cursor.lastrowid
                
                conn.commit()
                
                # Journaliser
                self.log_activity('CREATE', 'medicaments', med_id, f"Médicament: {code} - {nom}")
                
                messagebox.showinfo("Succès", 
                                  f"✅ Médicament enregistré!\n\n"
                                  f"💊 Nom: {nom}\n"
                                  f"🔢 Code: {code}\n"
                                  f"📦 Stock: {stock}")
                
                # Réinitialiser
                self.clear_medicament_form()
                
                # Actualiser les listes
                if hasattr(self, 'load_medicaments_list'):
                    self.load_medicaments_list()
                if hasattr(self, 'load_stock_alerts'):
                    self.load_stock_alerts()
                
            except sqlite3.IntegrityError:
                messagebox.showerror("Erreur", "Code déjà utilisé")
            finally:
                conn.close()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur: {str(e)}")
    
    def clear_medicament_form(self):
        """Efface formulaire médicament"""
        for var in self.med_vars.values():
            var.set("")
        
        self.med_status_label.config(text="")
    
    def create_medicament_list(self, parent):
        """Liste des médicaments"""
        main_frame = tk.Frame(parent, bg='white', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        header_frame = tk.Frame(main_frame, bg='white')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(header_frame, text="📋 LISTE DES MÉDICAMENTS", 
                font=('Arial', 14, 'bold'), bg='white').pack(side='left')
        
        refresh_btn = tk.Button(header_frame, text="🔄 Actualiser", 
                               command=self.load_medicaments_list,
                               bg=self.colors['info'], fg='white',
                               padx=15, pady=5)
        refresh_btn.pack(side='right')
        
        # Tableau
        tree_frame = tk.Frame(main_frame, bg='white')
        tree_frame.pack(fill='both', expand=True)
        
        columns = ['Code', 'Nom', 'Catégorie', 'Forme', 'Stock', 'Seuil', 'Prix']
        self.medicaments_tree = ttk.Treeview(tree_frame, columns=columns, 
                                            show='headings', height=15)
        
        col_widths = [80, 150, 100, 80, 60, 60, 80]
        for col, width in zip(columns, col_widths):
            self.medicaments_tree.heading(col, text=col)
            self.medicaments_tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, 
                                 command=self.medicaments_tree.yview)
        self.medicaments_tree.configure(yscrollcommand=scrollbar.set)
        
        self.medicaments_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Charger les données
        self.load_medicaments_list()
    
    def load_medicaments_list(self):
        """Charge la liste des médicaments"""
        for item in self.medicaments_tree.get_children():
            self.medicaments_tree.delete(item)
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT code, nom, categorie, forme, stock, seuil_alerte, prix_unitaire
                FROM medicaments
                ORDER BY nom
            ''')
            
            for row in cursor.fetchall():
                # Colorer les stocks faibles
                stock = row[4]
                seuil = row[5]
                prix = f"{row[6]:,.0f}" if row[6] else "0"
                
                self.medicaments_tree.insert('', tk.END, 
                                           values=(row[0], row[1], row[2] or "", 
                                                  row[3] or "", stock, seuil, prix))
            
            conn.close()
        except Exception as e:
            print(f"Erreur liste médicaments: {e}")
    
    def create_stock_alerts(self, parent):
        """Alertes de stock"""
        main_frame = tk.Frame(parent, bg='white', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        header_frame = tk.Frame(main_frame, bg='white')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(header_frame, text="⚠️ ALERTES STOCK", 
                font=('Arial', 14, 'bold'), bg='white').pack(side='left')
        
        refresh_btn = tk.Button(header_frame, text="🔄 Actualiser", 
                               command=self.load_stock_alerts,
                               bg=self.colors['info'], fg='white',
                               padx=15, pady=5)
        refresh_btn.pack(side='right')
        
        # Tableau
        tree_frame = tk.Frame(main_frame, bg='white')
        tree_frame.pack(fill='both', expand=True)
        
        columns = ['Code', 'Nom', 'Stock actuel', 'Seuil', 'Statut', 'Date expiration']
        self.alerts_tree = ttk.Treeview(tree_frame, columns=columns, 
                                       show='headings', height=15)
        
        for col in columns:
            self.alerts_tree.heading(col, text=col)
            self.alerts_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, 
                                 command=self.alerts_tree.yview)
        self.alerts_tree.configure(yscrollcommand=scrollbar.set)
        
        self.alerts_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Charger les données
        self.load_stock_alerts()
    
    def load_stock_alerts(self):
        """Charge les alertes de stock"""
        for item in self.alerts_tree.get_children():
            self.alerts_tree.delete(item)
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT code, nom, stock, seuil_alerte, date_expiration
                FROM medicaments
                WHERE stock <= seuil_alerte OR date_expiration IS NOT NULL
                ORDER BY stock, date_expiration
            ''')
            
            for row in cursor.fetchall():
                stock = row[2]
                seuil = row[3]
                date_exp = row[4]
                
                # Déterminer le statut
                if stock == 0:
                    statut = "RUPTURE"
                    tag = 'rupture'
                elif stock <= seuil:
                    statut = "FAIBLE"
                    tag = 'faible'
                else:
                    statut = "NORMAL"
                    tag = 'normal'
                
                # Vérifier expiration
                if date_exp:
                    try:
                        exp_date = datetime.strptime(date_exp, '%d/%m/%Y')
                        if exp_date < datetime.now():
                            statut = "EXPIRÉ"
                            tag = 'expire'
                    except:
                        pass
                
                self.alerts_tree.insert('', tk.END, 
                                      values=(row[0], row[1], stock, seuil, statut, date_exp or ""),
                                      tags=(tag,))
            
            # Configurer les tags de couleur
            self.alerts_tree.tag_configure('rupture', background='#fecaca')  # Rouge clair
            self.alerts_tree.tag_configure('faible', background='#fef3c7')   # Jaune clair
            self.alerts_tree.tag_configure('expire', background='#fca5a5')   # Rouge
            self.alerts_tree.tag_configure('normal', background='white')
            
            conn.close()
        except Exception as e:
            print(f"Erreur alertes stock: {e}")
    
    def create_services_tab(self):
        """Onglet Gestion des services"""
        tab = tk.Frame(self.main_notebook, bg='white')
        self.main_notebook.add(tab, text="🏥 Services")
        
        main_frame = tk.Frame(tab, bg='white', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        tk.Label(main_frame, text="GESTION DES SERVICES", 
                font=('Arial', 14, 'bold'), bg='white').pack(pady=(0, 20))
        
        # Liste des services
        tree_frame = tk.Frame(main_frame, bg='white')
        tree_frame.pack(fill='both', expand=True)
        
        columns = ['ID', 'Nom', 'Description', 'Téléphone', 'Responsable']
        self.services_tree = ttk.Treeview(tree_frame, columns=columns, 
                                         show='headings', height=15)
        
        for col in columns:
            self.services_tree.heading(col, text=col)
            self.services_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, 
                                 command=self.services_tree.yview)
        self.services_tree.configure(yscrollcommand=scrollbar.set)
        
        self.services_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Boutons
        btn_frame = tk.Frame(main_frame, bg='white')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="🔄 Actualiser", 
                 command=self.load_services,
                 bg=self.colors['info'], fg='white',
                 padx=20, pady=10).pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="📤 Exporter", 
                 command=lambda: self.export_table_to_csv('services'),
                 bg=self.colors['secondary'], fg='white',
                 padx=20, pady=10).pack(side='left', padx=10)
        
        # Charger les données
        self.load_services()
    
    def load_services(self):
        """Charge la liste des services"""
        for item in self.services_tree.get_children():
            self.services_tree.delete(item)
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT s.id, s.nom, s.description, s.tel_interne, 
                       p.nom || ' ' || p.prenom as responsable
                FROM services s
                LEFT JOIN personnel p ON s.responsable_id = p.id
                ORDER BY s.nom
            ''')
            
            for row in cursor.fetchall():
                self.services_tree.insert('', tk.END, values=row)
            
            conn.close()
        except Exception as e:
            print(f"Erreur liste services: {e}")
    
    def create_examens_tab(self):
        """Onglet Examens médicaux"""
        tab = tk.Frame(self.main_notebook, bg='white')
        self.main_notebook.add(tab, text="🔬 Examens")
        
        main_frame = tk.Frame(tab, bg='white', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        tk.Label(main_frame, text="GESTION DES EXAMENS MÉDICAUX", 
                font=('Arial', 14, 'bold'), bg='white').pack(pady=(0, 20))
        
        # Tableau des examens
        tree_frame = tk.Frame(main_frame, bg='white')
        tree_frame.pack(fill='both', expand=True)
        
        columns = ['Date', 'Patient', 'Type examen', 'Statut', 'Résultat']
        self.examens_tree = ttk.Treeview(tree_frame, columns=columns, 
                                        show='headings', height=15)
        
        for col in columns:
            self.examens_tree.heading(col, text=col)
            self.examens_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, 
                                 command=self.examens_tree.yview)
        self.examens_tree.configure(yscrollcommand=scrollbar.set)
        
        self.examens_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Boutons
        btn_frame = tk.Frame(main_frame, bg='white')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="🔄 Actualiser", 
                 command=self.load_examens,
                 bg=self.colors['info'], fg='white',
                 padx=20, pady=10).pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="➕ Nouvel examen", 
                 command=self.show_new_examen_form,
                 bg=self.colors['success'], fg='white',
                 padx=20, pady=10).pack(side='left', padx=10)
        
        # Charger les données
        self.load_examens()
    
    def load_examens(self):
        """Charge la liste des examens"""
        for item in self.examens_tree.get_children():
            self.examens_tree.delete(item)
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT e.date_prescription, p.nom || ' ' || p.prenom, 
                       e.type_examen, e.statut, e.resultat
                FROM examens e
                JOIN consultations c ON e.consultation_id = c.id
                JOIN patients p ON c.patient_id = p.id
                ORDER BY e.date_prescription DESC
                LIMIT 100
            ''')
            
            for row in cursor.fetchall():
                date_str = row[0][:10] if row[0] else ""
                resultat = row[4][:30] + "..." if row[4] and len(row[4]) > 30 else row[4] or ""
                
                self.examens_tree.insert('', tk.END, 
                                       values=(date_str, row[1], row[2], row[3], resultat))
            
            conn.close()
        except Exception as e:
            print(f"Erreur liste examens: {e}")
    
    def show_new_examen_form(self):
        """Affiche le formulaire pour nouvel examen"""
        # Cette fonction pourrait être implémentée pour créer de nouveaux examens
        messagebox.showinfo("Information", "Fonctionnalité à implémenter")
    
    # ==================== PERSONNEL AMÉLIORÉ ====================
    
    def create_personnel_tab(self):
        """Onglet Personnel amélioré avec actualisation"""
        tab = tk.Frame(self.main_notebook, bg='white')
        self.main_notebook.add(tab, text="👨‍⚕️ Personnel")
        
        notebook = ttk.Notebook(tab)
        notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Nouveau personnel
        new_tab = tk.Frame(notebook, bg='white')
        notebook.add(new_tab, text="➕ Nouveau")
        self.create_personnel_form(new_tab)
        
        # Liste du personnel
        list_tab = tk.Frame(notebook, bg='white')
        notebook.add(list_tab, text="📋 Liste")
        self.create_personnel_list(list_tab)
    
    def create_personnel_form(self, parent):
        """Formulaire personnel amélioré"""
        main_frame = tk.Frame(parent, bg='white', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        tk.Label(main_frame, text="AJOUTER UN MEMBRE DU PERSONNEL", 
                font=('Arial', 14, 'bold'), bg='white').pack(pady=(0, 20))
        
        form = tk.Frame(main_frame, bg='white')
        form.pack()
        
        self.pers_vars = {}
        
        fields = [
            ("Nom*:", "nom", 30),
            ("Prénom*:", "prenom", 30),
            ("Email*:", "email", 30),
            ("Mot de passe*:", "password", 30),
            ("Spécialité:", "specialite", 30)
        ]
        
        for i, (label, name, width) in enumerate(fields):
            tk.Label(form, text=label, bg='white').grid(row=i, column=0, padx=10, pady=10, sticky='e')
            self.pers_vars[name] = tk.StringVar()
            
            if name == "password":
                tk.Entry(form, textvariable=self.pers_vars[name], 
                        show="•", width=width).grid(row=i, column=1, padx=10, pady=10)
            else:
                tk.Entry(form, textvariable=self.pers_vars[name], 
                        width=width).grid(row=i, column=1, padx=10, pady=10)
        
        tk.Label(form, text="Rôle*:", bg='white').grid(row=len(fields), column=0, padx=10, pady=10, sticky='e')
        self.pers_vars['role'] = tk.StringVar(value="personnel")
        ttk.Combobox(form, textvariable=self.pers_vars['role'], 
                    values=['admin', 'personnel'], width=27).grid(row=len(fields), column=1, padx=10, pady=10)
        
        # Boutons avec actualisation
        btn_frame = tk.Frame(main_frame, bg='white')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="➕ Ajouter Personnel", 
                 command=self.add_personnel,
                 bg=self.colors['success'], fg='white',
                 padx=30, pady=10).pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="🔄 Ajouter & Actualiser", 
                 command=lambda: [self.add_personnel(), self.refresh_personnel_list()],
                 bg=self.colors['info'], fg='white',
                 padx=30, pady=10).pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="🗑️ Effacer", 
                 command=self.clear_personnel_form,
                 bg=self.colors['danger'], fg='white',
                 padx=30, pady=10).pack(side='left', padx=10)
        
        # Status
        self.pers_status_label = tk.Label(main_frame, text="", bg='white')
        self.pers_status_label.pack()
    
    def add_personnel(self):
        """Ajoute personnel avec validation"""
        try:
            required = ['nom', 'prenom', 'email', 'password']
            missing_fields = []
            
            for field in required:
                if not self.pers_vars[field].get():
                    missing_fields.append(field)
            
            if missing_fields:
                messagebox.showwarning("Champs manquants", 
                                     f"Champs obligatoires manquants:\n{', '.join(missing_fields)}")
                return
            
            email = self.pers_vars['email'].get()
            password = self.pers_vars['password'].get()
            
            # Validation email
            if '@' not in email or '.' not in email:
                messagebox.showwarning("Email invalide", "Format email: exemple@domaine.com")
                return
            
            # Validation mot de passe
            if len(password) < 6:
                messagebox.showwarning("Mot de passe faible", "Minimum 6 caractères")
                return
            
            hashed = hashlib.sha256(password.encode()).hexdigest()
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO personnel (email, password, nom, prenom, role, specialite)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    email,
                    hashed,
                    self.pers_vars['nom'].get().upper(),
                    self.pers_vars['prenom'].get().title(),
                    self.pers_vars['role'].get(),
                    self.pers_vars['specialite'].get()
                ))
                
                personnel_id = cursor.lastrowid
                
                conn.commit()
                
                # Journaliser
                self.log_activity('CREATE', 'personnel', personnel_id, 
                                f"Nouveau {self.pers_vars['role'].get()}: {email}")
                
                messagebox.showinfo("Succès", 
                                  f"✅ Personnel ajouté avec succès!\n\n"
                                  f"👤 Nom: {self.pers_vars['nom'].get()} {self.pers_vars['prenom'].get()}\n"
                                  f"📧 Email: {email}\n"
                                  f"🎭 Rôle: {self.pers_vars['role'].get()}")
                
                # Réinitialiser
                self.clear_personnel_form()
                
                self.pers_status_label.config(
                    text=f"✅ Personnel {email} ajouté avec succès!", 
                    fg=self.colors['success'])
                
            except sqlite3.IntegrityError:
                messagebox.showerror("Erreur", "Email déjà utilisé")
                self.pers_status_label.config(
                    text="❌ Email déjà utilisé", 
                    fg=self.colors['danger'])
            finally:
                conn.close()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur: {str(e)}")
            self.pers_status_label.config(
                text=f"❌ Erreur: {str(e)}", 
                fg=self.colors['danger'])
    
    def clear_personnel_form(self):
        """Efface formulaire personnel"""
        for var in self.pers_vars.values():
            if isinstance(var, tk.StringVar):
                var.set("")
        
        self.pers_vars['role'].set("personnel")
        self.pers_status_label.config(text="")
    
    def create_personnel_list(self, parent):
        """Liste du personnel avec bouton d'actualisation"""
        main_frame = tk.Frame(parent, bg='white', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        header_frame = tk.Frame(main_frame, bg='white')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(header_frame, text="📋 LISTE DU PERSONNEL", 
                font=('Arial', 14, 'bold'), bg='white').pack(side='left')
        
        # Bouton d'actualisation
        refresh_btn = tk.Button(header_frame, text="🔄 Actualiser la liste", 
                               command=self.refresh_personnel_list,
                               bg=self.colors['info'], fg='white',
                               padx=15, pady=5, font=('Arial', 10))
        refresh_btn.pack(side='right', padx=5)
        
        # Bouton d'export
        export_btn = tk.Button(header_frame, text="📤 Exporter en CSV", 
                              command=lambda: self.export_table_to_csv('personnel'),
                              bg=self.colors['secondary'], fg='white',
                              padx=15, pady=5, font=('Arial', 10))
        export_btn.pack(side='right', padx=5)
        
        # Tableau
        tree_frame = tk.Frame(main_frame, bg='white')
        tree_frame.pack(fill='both', expand=True)
        
        columns = ['Nom', 'Prénom', 'Email', 'Rôle', 'Spécialité', 'Date création']
        self.personnel_tree = ttk.Treeview(tree_frame, columns=columns, 
                                          show='headings', height=15)
        
        col_widths = [120, 120, 180, 80, 120, 100]
        for col, width in zip(columns, col_widths):
            self.personnel_tree.heading(col, text=col)
            self.personnel_tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, 
                                 command=self.personnel_tree.yview)
        self.personnel_tree.configure(yscrollcommand=scrollbar.set)
        
        self.personnel_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Charger les données
        self.refresh_personnel_list()
    
    def refresh_personnel_list(self):
        """Actualise la liste du personnel"""
        for item in self.personnel_tree.get_children():
            self.personnel_tree.delete(item)
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT nom, prenom, email, role, specialite, date_creation
                FROM personnel
                ORDER BY nom, prenom
            ''')
            
            # Style alterné
            row_color = True
            
            for row in cursor.fetchall():
                # Formater la date
                date_str = row[5][:10] if row[5] else ""
                
                # Formater le rôle
                role_display = "👑 Admin" if row[3] == "admin" else "👨‍⚕️ Personnel"
                
                display_row = (row[0], row[1], row[2], role_display, row[4] or "", date_str)
                
                # Insérer avec tag alterné
                tag = 'evenrow' if row_color else 'oddrow'
                self.personnel_tree.insert('', tk.END, values=display_row, tags=(tag,))
                row_color = not row_color
            
            # Configurer les tags pour l'alternance
            self.personnel_tree.tag_configure('evenrow', background='#f9f9f9')
            self.personnel_tree.tag_configure('oddrow', background='white')
            
            conn.close()
            
            # Mettre à jour le compte
            count = len(self.personnel_tree.get_children())
            
        except Exception as e:
            print(f"Erreur liste personnel: {e}")
    
    # ==================== STATISTIQUES AMÉLIORÉES ====================
    
    def create_statistiques_tab(self):
        """Onglet Statistiques amélioré"""
        tab = tk.Frame(self.main_notebook, bg='white')
        self.main_notebook.add(tab, text="📈 Statistiques")
        
        main_frame = tk.Frame(tab, bg='white', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        tk.Label(main_frame, text="📊 STATISTIQUES GÉNÉRALES", 
                font=('Arial', 18, 'bold'), bg='white').pack(pady=(0, 30))
        
        # Bouton d'actualisation
        refresh_frame = tk.Frame(main_frame, bg='white')
        refresh_frame.pack(pady=(0, 20))
        
        tk.Button(refresh_frame, text="🔄 Actualiser toutes les statistiques", 
                 command=self.refresh_all_statistics,
                 bg=self.colors['info'], fg='white',
                 padx=20, pady=10).pack()
        
        # Statistiques principales
        self.stats_frame = tk.Frame(main_frame, bg='white')
        self.stats_frame.pack(fill='both', expand=True)
        
        # Charger les statistiques initiales
        self.refresh_all_statistics()
    
    def refresh_all_statistics(self):
        """Actualise toutes les statistiques"""
        try:
            # Effacer anciennes statistiques
            for widget in self.stats_frame.winfo_children():
                widget.destroy()
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Statistiques principales
            stats_queries = [
                ("👥 Total patients", "SELECT COUNT(*) FROM patients", self.colors['primary']),
                ("👶 Enfants (<18 ans)", "SELECT COUNT(*) FROM patients WHERE type_patient='enfant'", self.colors['pediatrie']),
                ("👨 Adultes", "SELECT COUNT(*) FROM patients WHERE type_patient='adulte'", self.colors['adulte']),
                ("🩺 Consultations ce mois", "SELECT COUNT(*) FROM consultations WHERE strftime('%Y-%m', date_consultation) = strftime('%Y-%m', 'now')", self.colors['info']),
                ("🏥 Hospitalisés actifs", "SELECT COUNT(*) FROM hospitalisations WHERE statut='en_cours'", self.colors['warning']),
                ("📅 RDV aujourd'hui", "SELECT COUNT(*) FROM rendez_vous WHERE date_rdv = date('now') AND statut='planifie'", self.colors['secondary']),
                ("💰 Factures impayées", "SELECT COUNT(*) FROM factures WHERE statut!='paye'", self.colors['danger']),
                ("💉 Vaccins ce mois", "SELECT COUNT(*) FROM vaccinations WHERE strftime('%Y-%m', date_vaccination) = strftime('%Y-%m', 'now')", self.colors['success']),
                ("👨‍⚕️ Personnel actif", "SELECT COUNT(*) FROM personnel", '#666666'),
                ("📈 Nouveaux patients (30j)", "SELECT COUNT(*) FROM patients WHERE date(date_creation) >= date('now', '-30 days')", self.colors['primary'])
            ]
            
            # Afficher en grille 5x2
            for i, (label, query, color) in enumerate(stats_queries):
                cursor.execute(query)
                value = cursor.fetchone()[0]
                
                card = tk.Frame(self.stats_frame, bg='white', 
                               padx=20, pady=15, relief=tk.RAISED, borderwidth=2)
                card.grid(row=i//5, column=i%5, padx=10, pady=10, sticky='nsew')
                
                tk.Label(card, text=label, font=('Arial', 11), 
                        bg='white').pack()
                tk.Label(card, text=str(value), font=('Arial', 28, 'bold'), 
                        bg='white', fg=color).pack(pady=5)
            
            # Configurer la grille
            for i in range(5):
                self.stats_frame.grid_columnconfigure(i, weight=1)
            
            # Statistiques financières
            finance_frame = tk.Frame(main_frame, bg='white')
            finance_frame.pack(pady=40, fill='x')
            
            tk.Label(finance_frame, text="📊 STATISTIQUES FINANCIÈRES", 
                    font=('Arial', 14, 'bold'), bg='white').pack(pady=(0, 20))
            
            finance_queries = [
                ("💰 Total facturé", "SELECT COALESCE(SUM(montant), 0) FROM factures"),
                ("💰 Total perçu", "SELECT COALESCE(SUM(paye), 0) FROM factures"),
                ("💰 Total impayé", "SELECT COALESCE(SUM(reste), 0) FROM factures"),
                ("💰 Moyenne facture", "SELECT COALESCE(AVG(montant), 0) FROM factures"),
                ("📈 Taux recouvrement", "SELECT CASE WHEN SUM(montant) > 0 THEN ROUND((SUM(paye) * 100.0 / SUM(montant)), 1) ELSE 0 END FROM factures")
            ]
            
            finance_stats_frame = tk.Frame(finance_frame, bg='white')
            finance_stats_frame.pack()
            
            for i, (label, query) in enumerate(finance_queries):
                cursor.execute(query)
                value = cursor.fetchone()[0]
                
                card = tk.Frame(finance_stats_frame, bg='#f8f9fa', 
                               padx=15, pady=12, relief=tk.GROOVE, borderwidth=1)
                card.grid(row=0, column=i, padx=5, pady=5)
                
                tk.Label(card, text=label, font=('Arial', 10), 
                        bg='#f8f9fa').pack()
                
                if isinstance(value, (int, float)):
                    if label == "💰 Total facturé" or label == "💰 Total perçu" or label == "💰 Total impayé":
                        display_value = f"{value:,.0f} FCFA"
                    elif label == "💰 Moyenne facture":
                        display_value = f"{value:,.0f} FCFA"
                    else:
                        display_value = f"{value}%"
                else:
                    display_value = str(value)
                
                tk.Label(card, text=display_value, font=('Arial', 12, 'bold'), 
                        bg='#f8f9fa', fg=self.colors['primary']).pack(pady=3)
            
            # Statistiques par mois (graphique simple)
            month_frame = tk.Frame(main_frame, bg='white')
            month_frame.pack(pady=40, fill='x')
            
            tk.Label(month_frame, text="📈 ACTIVITÉ PAR MOIS", 
                    font=('Arial', 14, 'bold'), bg='white').pack(pady=(0, 20))
            
            # Requête pour activité des 6 derniers mois
            cursor.execute('''
                WITH months AS (
                    SELECT strftime('%Y-%m', date('now', '-' || (n-1) || ' months')) as month
                    FROM (SELECT 1 as n UNION SELECT 2 UNION SELECT 3 
                          UNION SELECT 4 UNION SELECT 5 UNION SELECT 6)
                )
                SELECT m.month,
                       COALESCE((SELECT COUNT(*) FROM patients p 
                                 WHERE strftime('%Y-%m', p.date_creation) = m.month), 0) as nouveaux_patients,
                       COALESCE((SELECT COUNT(*) FROM consultations c 
                                 WHERE strftime('%Y-%m', c.date_consultation) = m.month), 0) as consultations,
                       COALESCE((SELECT COUNT(*) FROM factures f 
                                 WHERE strftime('%Y-%m', f.date_facture) = m.month), 0) as factures
                FROM months m
                ORDER BY m.month DESC
            ''')
            
            month_data = cursor.fetchall()
            
            # Afficher les données
            data_frame = tk.Frame(month_frame, bg='white')
            data_frame.pack()
            
            # En-têtes
            headers = ['Mois', 'Nouveaux patients', 'Consultations', 'Factures']
            for i, header in enumerate(headers):
                tk.Label(data_frame, text=header, font=('Arial', 10, 'bold'), 
                        bg='white', padx=10, pady=5).grid(row=0, column=i)
            
            # Données
            for row_idx, row in enumerate(month_data, start=1):
                for col_idx, value in enumerate(row):
                    bg_color = '#f9f9f9' if row_idx % 2 == 0 else 'white'
                    tk.Label(data_frame, text=str(value), font=('Arial', 10), 
                            bg=bg_color, padx=10, pady=5).grid(row=row_idx, column=col_idx)
            
            conn.close()
            
        except Exception as e:
            tk.Label(self.stats_frame, text=f"Erreur: {e}", 
                    bg='white', fg='red').pack()
    
    # ==================== ADMIN ====================
    
    def create_admin_tab(self):
        """Onglet Admin pour fonctions avancées"""
        tab = tk.Frame(self.main_notebook, bg='white')
        self.main_notebook.add(tab, text="⚙️ Admin")
        
        main_frame = tk.Frame(tab, bg='white', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        tk.Label(main_frame, text="PANEL D'ADMINISTRATION", 
                font=('Arial', 18, 'bold'), bg='white').pack(pady=(0, 30))
        
        # Section sauvegarde
        backup_frame = tk.LabelFrame(main_frame, text="💾 Sauvegarde & Restauration", 
                                    font=('Arial', 12, 'bold'), bg='white', padx=20, pady=20)
        backup_frame.pack(fill='x', pady=(0, 20))
        
        tk.Button(backup_frame, text="📤 Sauvegarder la base de données", 
                 command=self.backup_database,
                 bg=self.colors['primary'], fg='white',
                 padx=20, pady=10).pack(pady=5)
        
        # Section export
        export_frame = tk.LabelFrame(main_frame, text="📤 Export des données", 
                                    font=('Arial', 12, 'bold'), bg='white', padx=20, pady=20)
        export_frame.pack(fill='x', pady=(0, 20))
        
        tables = ['patients', 'personnel', 'consultations', 'hospitalisations', 
                 'rendez_vous', 'factures', 'vaccinations', 'medicaments', 'services', 'examens']
        
        for table in tables:
            btn_frame = tk.Frame(export_frame, bg='white')
            btn_frame.pack(fill='x', pady=2)
            
            tk.Label(btn_frame, text=f"Table: {table}", bg='white', 
                    width=20, anchor='w').pack(side='left')
            
            tk.Button(btn_frame, text="📥 Exporter CSV", 
                     command=lambda t=table: self.export_table_to_csv(t),
                     bg=self.colors['secondary'], fg='white',
                     padx=10, pady=5).pack(side='right')
        
        # Section logs
        logs_frame = tk.LabelFrame(main_frame, text="📋 Journal d'activité", 
                                  font=('Arial', 12, 'bold'), bg='white', padx=20, pady=20)
        logs_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Tableau des logs
        tree_frame = tk.Frame(logs_frame, bg='white')
        tree_frame.pack(fill='both', expand=True)
        
        columns = ['Date/Heure', 'Utilisateur', 'Action', 'Table', 'Détails']
        logs_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            logs_tree.heading(col, text=col)
            logs_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=logs_tree.yview)
        logs_tree.configure(yscrollcommand=scrollbar.set)
        
        logs_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Charger les logs
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT a.timestamp, p.nom || ' ' || p.prenom, a.action, a.table_name, a.details
                FROM audit_log a
                LEFT JOIN personnel p ON a.user_id = p.id
                ORDER BY a.timestamp DESC
                LIMIT 100
            ''')
            
            for row in cursor.fetchall():
                logs_tree.insert('', tk.END, values=row)
            
            conn.close()
        except Exception as e:
            print(f"Erreur logs: {e}")
        
        # Bouton actualiser logs
        tk.Button(logs_frame, text="🔄 Actualiser les logs", 
                 command=lambda: self.refresh_logs(logs_tree),
                 bg=self.colors['info'], fg='white',
                 padx=15, pady=5).pack(pady=10)
    
    def backup_database(self):
        """Sauvegarde la base de données"""
        try:
            backup_name = f"backup_hospital_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            
            # Copier le fichier
            shutil.copy2(self.db_path, backup_name)
            
            # Journaliser
            self.log_activity('BACKUP', 'system', details=f"Sauvegarde: {backup_name}")
            
            messagebox.showinfo("Sauvegarde réussie", 
                              f"✅ Base de données sauvegardée dans:\n{os.path.abspath(backup_name)}")
        except Exception as e:
            messagebox.showerror("Erreur sauvegarde", f"Erreur: {e}")
    
    def refresh_logs(self, tree):
        """Actualise les logs"""
        for item in tree.get_children():
            tree.delete(item)
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT a.timestamp, p.nom || ' ' || p.prenom, a.action, a.table_name, a.details
                FROM audit_log a
                LEFT JOIN personnel p ON a.user_id = p.id
                ORDER BY a.timestamp DESC
                LIMIT 100
            ''')
            
            for row in cursor.fetchall():
                tree.insert('', tk.END, values=row)
            
            conn.close()
        except Exception as e:
            print(f"Erreur actualisation logs: {e}")

# ==================== LANCEMENT ====================

def main():
    """Lancement application"""
    print("="*70)
    print("🏥 SYSTÈME HOSPITALIER CAMEROUN 🇨🇲")
    print("="*70)
    print("Version: 3.0 - Base de données améliorée")
    print("="*70)
    print("AMÉLIORATIONS AJOUTÉES:")
    print("✅ Nouvelles tables: médicaments, services, chambres, examens")
    print("✅ Colonnes ajoutées: allergies, antécédents, groupe sanguin, etc.")
    print("✅ Index de performance pour requêtes rapides")
    print("✅ Triggers d'automatisation (numéros dossier, calculs)")
    print("✅ Vues pour statistiques et rapports")
    print("✅ Gestion complète des médicaments avec alertes stock")
    print("✅ Services et chambres avec gestion de disponibilité")
    print("✅ Interface améliorée avec nouveaux onglets")
    print("✅ Sauvegarde automatique au démarrage")
    print("="*70)
    print("CONNEXION:")
    print("• Email: admin@hospital.cm")
    print("• Mot de passe: admin123")
    print("="*70)
    
    root = tk.Tk()
    app = HospitalCamerounApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()