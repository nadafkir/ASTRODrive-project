import os
import shutil
import gzip
import configparser
import getpass
import hashlib
import sys
import subprocess
import importlib
from PIL import Image
from cryptography.fernet import Fernet
import tkinter as tk
from tkinter import scrolledtext
sys.getdefaultencoding()
from colorama import Fore, Style, init
import time
import matplotlib.pyplot as plt
from datetime import datetime,timedelta
import datetime
fichier_map = '/space/teleportation/id_file'

dates_connexions_reussies = []
def verify_user(username, password, id_emploi, file_path):
    # Hachage du mot de passe pour la comparaison
    hashed_password_input = hashlib.sha256(password.encode()).hexdigest()

    try:
        with open(file_path, 'r') as user_file:
            for line in user_file:
                user_data = line.strip().split(':')
                if len(user_data) == 5:
                    file_username, hashed_password, _, _, file_id_emploi = user_data
                    if file_username == username and file_id_emploi == id_emploi:
                        if hashed_password == hashed_password_input:
                            dates_connexions_reussies.append(datetime.now())
                            print("\n\033[95mConnexion réussie.\033[0m")
                            return True
                        else:
                            print("\n\033[95mMot de passe incorrect\033[0m")  
                     
                            return False

        print("\033[95mUtilisateur non trouvé.\033[0m ")
        return False

    except FileNotFoundError:
        print("Le fichier des utilisateurs n'existe pas.")
        return False

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def connexion_utilisateur():
 while True:
    nom_utilisateur = input("\033[95mNom d'utilisateur : \033[0m")
    id_emploi=id_emploi = input("\033[95mEntrez l'ID d'employe d'utilisateur : \033[0m")
    mot_de_passe = getpass.getpass("\033[95mMot de passe :\033[0m ")
    if nom_utilisateur == "root" or  nom_utilisateur.startswith("sroot"):
         file_usr =chemin ("rootfile", "Settings")
    
    else:
         file_usr =chemin ("usersfile", "Settings") 
    if verify_user(nom_utilisateur, mot_de_passe, id_emploi, file_usr):
       chemin_repertoire_personnel = chemin("repertoire_perso",f"section_{id_emploi}")

       return nom_utilisateur, id_emploi, chemin_repertoire_personnel
    else:
       return None

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def concatener_chemin(chemin):
    # Construire le chemin complet du fichier de configuration
    config_path = os.path.join(sys.path[0], "/space/teleportation/config.ini")

    # Lecture du fichier de configuration
    config = configparser.ConfigParser()

    if not config.read(config_path) or not config.has_section('Settings'):
        print("Erreur : La section 'Settings' est absente dans le fichier de configuration.")
        sys.exit(1)

    # Accès à la variable de configuration originpath
    originpath = config['Settings'].get('originpath', '')

    if not originpath:
        print("Erreur : La clé 'originpath' est absente dans la section 'Settings'.")
        sys.exit(1)

    # Concaténation du chemin
    chemin_complet = os.path.join(originpath, chemin)

    return chemin_complet

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def stocker_fichier(nom_fichier, id_emploi, path):
    # Concaténer id_emploi avec le nom du fichier
    if "space/home" in path :
       nom_fichier = f"{id_emploi}_{nom_fichier}"  
    ligne = f"{nom_fichier}:{path}\n"

    # Ouverture du fichier en mode d'ajout (append)
    with open(fichier_map, "a") as fichier:
        # Écrire la ligne dans le fichier
        fichier.write(ligne)

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def fonction_commande_touch(username, id_emploi, chemin_repertoire_personnel, comnd_line_split):
    chemin_complet = os.path.join(concatener_chemin(comnd_line_split[1]), comnd_line_split[2])

    if not validation_root_sroot(username, chemin_repertoire_personnel, chemin_complet):
        print("Erreur : Vous n'avez pas la permission d'utiliser cette commande en dehors de space/home.")
    else:
        try:       
            # Créer un fichier en utilisant open() en mode écriture
            with open(chemin_complet, 'w') as fichier_obj:
                pass

            name_file, path_file = comnd_line_split[2], comnd_line_split[1]
            print("Fichier", comnd_line_split[2], "créé avec succès dans", comnd_line_split[1])
            
            # Prompt user for file compression
            answer = input("Voulez-vous compresser le fichier ? (Y/N) :").strip().lower()
            
            if answer == "y":
                # Appeler la fonction compress_processs avec les bons arguments
                name_file, path_file = compress_process( chemin_complet, id_emploi)
                
            # Sauvegarder les informations du fichier dans le fichier de configuration
            else:
                stocker_fichier(name_file, id_emploi, chemin_complet)
        except Exception as e:
            print(f"Erreur lors de la création du fichier : {e}")

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        
def fonction_commande_mkdir(username, id_emploi, chemin_repertoire_personnel, comnd_line_split):   
    chemin_complet=os.path.join(concatener_chemin(comnd_line_split[1]), comnd_line_split[2])

    if not validation_root_sroot(username, chemin_repertoire_personnel, chemin_complet):
        print("Erreur : Vous n'avez pas la permission d'utiliser cette commande en dehors de space/home.")
    else:
        try:
            # Check if the directory already exists
            if not os.path.exists(chemin_complet):
                # Create the directory using os.makedirs()
                os.makedirs(chemin_complet)
                print("Répertoire", comnd_line_split[2], "créé avec succès dans", comnd_line_split[1])
                
                # Save the directory information to the config file
                name_file = comnd_line_split[2]
                path_file = comnd_line_split[1]
                stocker_fichier(name_file, id_emploi, chemin_complet)
            else:
                print("Erreur : Le répertoire existe déjà.")
        except Exception as e:
            print(f"Erreur lors de la création du répertoire : {e}")
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
 
def validation_root_sroot(username, chemin_repertoire_personnel, position_origin):
   if username != "root" and not username.startswith("sroot") and not position_origin.startswith(chemin_repertoire_personnel):                
      return False
   return True
   
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def supprimer_ligne_par_id_emploi(id_emploi, nom_fichier):
    # Ouvrir le fichier en mode lecture
    with open(nom_fichier, 'r') as fichier:
        lignes = fichier.readlines()

    # Recherche de la ligne avec l'id_emploi
    lignes_a_garder = [ligne for ligne in lignes if id_emploi not in ligne]

    # Ouvrir le fichier en mode écriture et écrire les lignes restantes
    with open(nom_fichier, 'w') as fichier:
        fichier.writelines(lignes_a_garder)
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


#///////////////////////////////////////////////////////////////////////////////////////////////////////////

def chemin (cle, classe):

    # Charger le fichier de configuration
    config = configparser.ConfigParser()
    fichier_config='/space/teleportation/config.ini'
    try:
        config.read(fichier_config)
    except configparser.Error as e:
        print(f"Erreur lors de la lecture du fichier de configuration : {e}")
        sys.exit(1)

    # Extraire le chemin spécifique
    try:
        chemin = config.get(classe, cle)
        return chemin
    except configparser.NoSectionError:
        print(f"Erreur : La section '{classe}' est absente dans le fichier de configuration.")
        sys.exit(1)
    except configparser.NoOptionError:
        print(f"Erreur : La clé '{cle}' est absente dans la section '{classe}'.")
        sys.exit(1)

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////
      
#///////////////////////////////////////////////////////////////////////////////////////////////////////////
 
def creer_user_classe(username, id_emploi, chemin_reper_personnel):
    # Créer une nouvelle instance de ConfigParser
    config = configparser.ConfigParser()

    # Lire la configuration existante depuis le fichier
    config_path = '/space/teleportation/config.ini'
    config.read(config_path)

    # Vérifier si la section id_emploi existe déjà
    if not config.has_section(id_emploi):
        config.add_section(id_emploi)

    # Vérifier si la clé username n'existe pas déjà dans la section id_emploi
    if not config.has_option(id_emploi, username):
        config.set(id_emploi, "repertoire_perso", chemin_reper_personnel)

    # Écrire la configuration mise à jour dans un fichier
    with open(config_path, 'w') as configfile:
        config.write(configfile)

#///////////////////////////////////////////////////////////////////////////////////////////////////////////


def create_user(username, password, id_emploi, groupe, file_path):
    # Hachage du mot de passe avec SHA-256
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # Obtenir le numéro de ligne actuel
    try:
        with open(file_path, 'r') as user_file:
            lines = user_file.readlines()
            num_ligne = len(lines) + 1
    except FileNotFoundError:
        num_ligne = 1

    # Enregistrement des informations de l'utilisateur dans le fichier
    with open(file_path, 'a') as user_file:
        user_file.write(f"{username}:{hashed_password}:{num_ligne}:{groupe}:{id_emploi}\n")

#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////  
      
def saisie_coordon_new_user(username,id_emploi, chemin_repertoire_personnel,mots):
# Vérifier si l'utilisateur qui exécute le script est le superutilisateurroot)
  current_username ="root" #connexion_utilisateur()

  if not (current_username == "root"):
    print("\033[95mVous devez creer un autre utilisateur en tant que superutilisateur(ROOT || sroot). \033[0m")
  else:
    # Demander au superutilisateur de fournir un nom d'utilisateur et un mot de passe
    groupe = input("\033[95mEntrez le groupe d'utilisateur (root/other) : \033[0m ")
    
    if groupe == "root":
        # Demander les informations pour créer un root
        nom_utilisateur = input("\033[95mEntrez le nom d'utilisateur d' utilisateur sroot : \033[0m ")
        id_emploi = input("\033[95mEntrez l'ID d'employe d'utilisateur :\033[0m ")
        mot_de_passe = getpass.getpass ("\033[95mEntrez le mot de passe pour le root :\033[0m ")
        if not nom_utilisateur or not mot_de_passe or not id_emploi:
           print("\033[95mLe nom d'utilisateur et le mot de passe sont obligatoires.\033[0m ")
           exit()
        file_usr=chemin ('rootfile','Settings')
        file_key=chemin ('keyrootfile', 'Settings')
        #creer_utilisateur(nom_utilisateur, mot_de_passe,groupe, file_usr, 30, id_emploi, file_key)
        
    else:
    
        # Demander les informations pour créer un utilisateur simple
        nom_utilisateur = input("\033[95mEntrez le nom d'utilisateur pour le simple utilisateur : \033[0m ")
        id_emploi = input("\033[95mEntrez l'ID d'employe d'utilisateur :\033[0m ")
        mot_de_passe = getpass.getpass("\033[95mEntrez le mot de passe pour l'utilisateur simple : \033[0m")
        # Groupe users pour les utilisateurs simples
        if not nom_utilisateur or not mot_de_passe or not id_emploi:
            print("\033[95mLe nom d'utilisateur et le mot de passe sont  obligatoires.\033[0m ")
            exit()
        file_usr=chemin ('usersfile', 'Settings')
        file_key=chemin ('keyusersfile', 'Settings')
        #creer_utilisateur(nom_utilisateur, mot_de_passe, groupe, file_usr, 15, id_emploi, file_key)
        
    chemin_reper_perso=creer_repertoire_personnel(nom_utilisateur, id_emploi)
    create_user(nom_utilisateur, mot_de_passe, id_emploi, groupe ,file_usr)
    return nom_utilisateur
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////// 
       
def creer_repertoire_personnel(nom_utilisateur, id_emploi):
    try:
        # Construire le chemin du répertoire personnel
        chemin_resultant = concatener_chemin("space/home")  # Assurez-vous que cette fonction est définie ou importée

        # Analyser le nom d'utilisateur et déterminer le nom du répertoire personnel
        if nom_utilisateur == "root":
            nom_repertoire_personnel = "nexus"+ "_" + id_emploi
        elif nom_utilisateur.startswith("sroot"):
           nom_repertoire_personnel = f"comnder_{nom_utilisateur[len('sroot'):]}_{id_emploi}"
        else:
            nom_repertoire_personnel = "explorer_" + nom_utilisateur + "_" + id_emploi
        chemin_repertoire_personnel = os.path.join(chemin_resultant, nom_repertoire_personnel)

        os.makedirs(chemin_repertoire_personnel)
        print("\033[95mRepertoire personnel cree avec succes pour \033[0m", nom_utilisateur, ":", chemin_repertoire_personnel)
        return chemin_repertoire_personnel
    except FileExistsError:
        print(f"Erreur : Le répertoire {chemin_repertoire_personnel} existe deja.")
    except OSError as e:
        print(f"Erreur lors de la creation du répertoire personnel pour {nom_utilisateur} : {e}")
    except Exception as ex:
        print(f"Une erreur inattendue s'est produite : {ex}")
        
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def saisie_coordon_user_delete(username,id_emploi, chemin_repertoire_personnel, comnd_line_split):
    if comnd_line_split[1] == "root" or comnd_line_split[1].startswith("sroot"):
        fichier_utilisateurs = chemin("rootfile","Settings")

    else:
        fichier_utilisateurs = chemin("usersfile","Settings")  

    # Lire le fichier d'utilisateurs
    try:
        with open(fichier_utilisateurs, 'r') as fichier:
            lignes = fichier.readlines()
    except FileNotFoundError:
        print(f"Fichier d'utilisateurs non trouvé : {fichier_utilisateurs}")
        return False

    # Filtrer les lignes pour conserver uniquement celles qui ne correspondent pas à l'utilisateur spécifié
    nouvelles_lignes = [ligne for ligne in lignes if not (comnd_line_split[1] == ligne.split(":")[0] and str(comnd_line_split[2]) == ligne.split(":")[4].strip())]
    # Réécrire le fichier d'utilisateurs avec les nouvelles données
    try:
        with open(fichier_utilisateurs, 'w') as fichier:
            fichier.writelines(nouvelles_lignes)
        print(f"Utilisateur {comnd_line_split[1]} est supprime avec succes.")
    except Exception as e:
        print(f"Erreur lors de la suppression de l'utilisateur {comnd_line_split[1]} : {e}")

#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def saisie_grp_user_modify(username,id_emploi, chemin_repertoire_personnel, comnd_line_split):
    if not (username == "root" or username.startswith("sroot")):
        print("Vous devez être un root ou un sroot pour modifier le groupe d'un utilisateur.")
    else:
        if comnd_line_split[1] == "root" or comnd_line_split[1].startswith("sroot"):
            fichier_utilisateurs = chemin("rootfile", "Settings")  # Assurez-vous que la fonction chemin est définie
        else:
            fichier_utilisateurs = chemin("usersfile", "Settings")  # Assurez-vous que la fonction chemin est définie

        # Lire le fichier d'utilisateurs
        try:
            with open(fichier_utilisateurs, 'r') as fichier:
                lignes = fichier.readlines()
               
        except FileNotFoundError:
            print(f"Fichier d'utilisateurs non trouvé : {fichier_utilisateurs}")
            return
        except Exception as e:
            print(f"Erreur lors de l'ouverture du fichier d'utilisateurs : {e}")
            return

        utilisateur_modifie = False
        for i, ligne in enumerate(lignes):
            colonnes = ligne.split(":")
            if len(colonnes) >= 5 and colonnes[0] == comnd_line_split[1] and colonnes[4].strip() == comnd_line_split[2]:

                # Modifier la ligne complète avec le nouveau groupe
                lignes[i] = f"{colonnes[0]}:{colonnes[1]}:{colonnes[2]}:{comnd_line_split[3]}:{colonnes[4]}"
                utilisateur_modifie = True
                break  # Assurez-vous que le break est à l'intérieur de la boucle

        # Écrire les modifications dans le fichier d'utilisateurs
        if utilisateur_modifie:
            try:
                with open(fichier_utilisateurs, 'w') as fichier:
                    fichier.writelines(lignes)
                print(f"Groupe de l'utilisateur {comnd_line_split[1]} (ID d'emploi {comnd_line_split[2]}) modifie avec succes.")
            except Exception as e:
                print(f"Erreur lors de la modification du groupe de l'utilisateur {comnd_line_split[1]} : {e}")
        else:
            print(f"Utilisateur {comnd_line_split[1]} avec l'ID d'emploi {comnd_line_split[2]} non trouve.")

#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def saisie_passwd_user_modify(username,id_emploi, chemin_repertoire_personnel, comnd_line_split):                                                            
    if not (username == "root" or username.startswith("sroot")):
        print("Vous devez être un root ou un sroot pour modifier le mot de passe d'un utilisateur.")
    else:
        if comnd_line_split[1] == "root" or comnd_line_split[1].startswith("sroot"):
            fichier_utilisateurs = chemin("rootfile","Settings")
        else:
            fichier_utilisateurs = chemin("usersfile","Settings")  


        # Lire le fichier d'utilisateurs
        try:
            with open(fichier_utilisateurs, 'r') as fichier:
                lignes = fichier.readlines()
        except FileNotFoundError:
            print(f"Fichier d'utilisateurs non trouvé : {fichier_utilisateurs}")
            return
        # Rechercher l'utilisateur dans le fichier
        utilisateur_trouve = False
        for i, ligne in enumerate(lignes):
            colonnes = ligne.split(":")

            if len(colonnes) >= 5 and colonnes[0].strip() == comnd_line_split[1] and colonnes[4].strip() == comnd_line_split[2]:
                utilisateur_trouve = True
                # Demander à l'utilisateur de fournir le nouveau mot de passe
                password=getpass.getpass("\033[95mSaisie le nouveau mot de passe: \033[0m")
                hashed_password = hashlib.sha256(password.encode()).hexdigest()

                # Générer le nouveau hachage du mot de passe

                # Modifier la ligne avec le nouveau mot de passe
                lignes[i] = f"{colonnes[0]}:{hashed_password}:{colonnes[2]}:{colonnes[3]}:{colonnes[4].strip()}\n"
     
                break

        # Modifier le mot de passe de l'utilisateur si trouvé
        if utilisateur_trouve:
            try:

                # Écrire les modifications dans le fichier d'utilisateurs
                with open(fichier_utilisateurs, 'w') as fichier:
                    fichier.writelines(lignes)
                print(f"\033[95mMot de passe de l'utilisateur {comnd_line_split[1]} modifié avec succes.\033[0m")
            except Exception as e:
                print(f"Erreur lors de la modification du mot de passe de l'utilisateur {comnd_line_split[1]} : {e}")
        else:
            print(f"Utilisateur {comnd_line_split[1]} avec l'ID d'employe {comnd_line_split[2]} non trouve.")


#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def process_suppression(element_a_supprimer):
    try:
        # Afficher la nature de l'élément à supprimer
        #
        if os.path.isfile(element_a_supprimer):
            print(f"{element_a_supprimer} est un fichier.")
        elif os.path.isdir(element_a_supprimer):
            print(f"{element_a_supprimer} est un répertoire.")
        else:
            print(f"{element_a_supprimer} n'est ni un fichier ni un répertoire.")
        
        # Supprimer le fichier/répertoire
        if os.path.exists(element_a_supprimer):
            if os.path.isfile(element_a_supprimer):
                os.remove(element_a_supprimer)
            elif os.path.isdir(element_a_supprimer):
                shutil.rmtree(element_a_supprimer)
            
            print(f"{element_a_supprimer} supprimé avec succès.")
            return True
        else:
            print(f"{element_a_supprimer} n'existe pas.")
            return False
    except Exception as e:
        print(f"Erreur lors de la suppression : {e}")
        return False
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////// 

def supprimer_ligne_map(id_emploi, position_supprimer):
    try:
       
        # Ouvrir le fichier en mode lecture
        with open(fichier_map, 'r') as fichier:
            lignes = fichier.readlines()

        # Recherche de la ligne avec l'id_emploi
        lignes_a_garder = [ligne for ligne in lignes if position_supprimer not in ligne]

        # Ouvrir le fichier en mode écriture et écrire les lignes restantes
        with open(fichier_map, 'w') as fichier:
            fichier.writelines(lignes_a_garder)
    except FileNotFoundError:
        print(f"Fichier {fichier_map} non trouvé.")
        raise
    except Exception as e:
        print(f"Erreur inattendue : {e}")
        raise
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def chercher_paths_par_id_emploi(id_emploi, mots, username):
    try:
        # Lire le fichier qui contient les noms des fichiers/répertoires et leurs chemins
        with open("/space/teleportation/id_file", 'r') as fichier:
            lignes = fichier.readlines()     
        # Rechercher toutes les occurrences du nom spécifié dans le fichier      
        if (mots[0] == "astrodelete" or mots[0] == "astrowrite") and (username != "root" and username != "sroot"):
            mots[2] = f"{id_emploi}_{mots[2]}"
        occurrences = [ligne.strip().split(':') for ligne in lignes if mots[2] in ligne.strip().split(':')[0]]
        if not occurrences:
            print(f"Aucune occurrence de {mots[2]} trouvee.")
            return None, None
        # Afficher les occurrences et demander à l'utilisateur de choisir
        print("Occurrences trouvees :")
        for i, occ in enumerate(occurrences):
            print(f"{i + 1}. {occ[-1]}")  # afficher le chemin complet
      
        choix = input("Entrez le numéro de l'occurrence choisie : ")
        try:
            choix = int(choix)
            if 1 <= choix <= len(occurrences):
                selected_occurrence = occurrences[choix - 1]
                chemin_complet = selected_occurrence[-1]
                numero_au_debut = selected_occurrence[0].split('_')[0] if '_' in selected_occurrence[0] else None
                return chemin_complet, numero_au_debut
            else:
                print("Choix invalide.")
                return None, None
        except ValueError:
            print("Veuillez entrer un numéro valide.")
            return None, None
    except FileNotFoundError:
        print(f"Fichier '/space/teleportation/id_file' non trouvé.")
        return None, None
    except Exception as e:
        print(f"Erreur lors de la recherche du chemin : {e}")
        return None, None

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////// 

def fonction_commande_delete(username, id_emploi, chemin_repertoire_personnel, comnd_line_split):
    position_supprimer, _ = chercher_paths_par_id_emploi(id_emploi,comnd_line_split,username)
    
    if position_supprimer is None:
        return None

    print(f"{position_supprimer}")

    if not validation_root_sroot(username, chemin_repertoire_personnel, position_supprimer):
        print("Vous devez être un root ou un sroot pour supprimer ce fichier ou ce répertoire.")
    else:
        confirmation = input("Êtes-vous sûr de vouloir supprimer ce fichier ? (y/n): ").strip().lower()
        if confirmation == "y":
            if process_suppression(position_supprimer):
                supprimer_ligne_map(id_emploi, position_supprimer)
                  
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////// 

def process_ecriture(fichier_write, droit): 
    print(" TXT : ")              
    content_lines = []
    while True:
        line = input()
        if line == '#@#':
            # Si l'utilisateur saisit uniquement "@", la saisie se termine
            break
        content_lines.append(line)

    content = '\n'.join(content_lines)
    if droit[1] == "+a":
        with open(fichier_write, 'a', encoding='utf-8') as file:
            file.write(content)
        print("Ecriture reussie!")
    elif droit[1] == "+w":
        with open(fichier_write, 'w', encoding='utf-8') as file:
            file.write(content)
        print("Ecriture reussie! ")
    else:
        print("IL FAUT UTILISER +a POUR L'AJOUT ET +w POUR L' ECRITURE (ecraser)")
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def fonction_commande_ecrire(username, id_emploi, chemin_repertoire_personnel, comnd_line_split):
    position_write, _ = chercher_paths_par_id_emploi(id_emploi, comnd_line_split,username)
 
    if not validation_root_sroot(username, chemin_repertoire_personnel, position_write):
        print("Vous devez être un root ou un sroot pour écrire dans ce fichier ou ce répertoire.")
    elif position_write is not None:
        if position_write.endswith('.gz'):
            nom_fichier_name, _ = os.path.splitext(os.path.basename(position_write))
            comnd_line_split[2] = nom_fichier_name
            # Décompresser le fichier
            file_path_write = decompresser_fichier_gz(position_write)

            print("debut1") 

        print("debut2")
        process_ecriture(position_write, comnd_line_split)
        print("fin1")
        compress_process( position_write, id_emploi)  
        print("fin2")
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////    

def compress_process(input_file, id_emploi):
    try:
        output_file=input_file + ".gz"

        with open(input_file, 'rb') as f_in, gzip.open(output_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
        name_file =os.path.basename(input_file)
        supprimer_ligne_map(id_emploi, input_file)
        stocker_fichier(name_file, id_emploi, output_file)
        
        
        print(f"Compression réussie! Le fichier compressé est enregistré sous le nom: {output_file}")
        return True
    except FileNotFoundError:
        print(f"Le fichier {output_file} n'existe pas.")
        return False
    except (PermissionError, OSError) as e:
        print(f"Erreur lors de l'ouverture du fichier source : {e}")
        return False
    except Exception as e:
        print(f"Une erreur s'est produite lors de la compression : {e}")
        return False

#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def decompresser_fichier_gz(chemin_fichier_comprime, chemin_sortie=None):
    try:
        if chemin_sortie is None:
            chemin_sortie, _ = os.path.splitext(chemin_fichier_comprime)

        with gzip.open(chemin_fichier_comprime, 'rb') as fichier_comprime, open(chemin_sortie, 'wb') as fichier_sortie:
            shutil.copyfileobj(fichier_comprime, fichier_sortie)
        
        print(f"Le fichier '{chemin_fichier_comprime}' a été décompressé avec succès.")
        os.remove(chemin_fichier_comprime)
        print(f"Le fichier compressé '{chemin_fichier_comprime}' a été supprimé.")  
        return chemin_sortie
    except FileNotFoundError:
        print(f"Le fichier '{chemin_fichier_comprime}' n'existe pas.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de la décompression : {e}")
        return None

#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def fonction_commande_lire(username,id_emploi, chemin_repertoire_personnel,comnd_line_split):
   
    position_read, _  = chercher_paths_par_id_emploi( id_emploi,comnd_line_split,username)

    with gzip.open(position_read, 'rt') as fichier_gzip:
        contenu = fichier_gzip.read()
        print(f"{contenu}")


#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        
def fonction_commande_touch_speed (username,id_emploi, chemin_repertoire_personnel,comnd_line_split):
       if comnd_line_split[0] == "generate" :
           comnd_line_split[1]="space/milky_way/solar_system/stars"
       elif comnd_line_split[0]== "build" :
           comnd_line_split[1]="space/milky_way/solar_system/planets"
       elif comnd_line_split[0] == "compose":
           comnd_line_split[1]="space/milky_way/solar_system/constellation"
       fonction_commande_touch(username, id_emploi, chemin_repertoire_personnel, comnd_line_split)

#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def fonction_commande_delete_speed(username,id_emploi, chemin_repertoire_personnel,comnd_line_split):

       if comnd_line_split[0] == "eclipse" :
           comnd_line_split[1]="space/milky_way/solar_system/stars"
       elif comnd_line_split[0]== "erase" :
           comnd_line_split[1]="space/milky_way/solar_system/planets"
       elif comnd_line_split[0] == "purge":
           comnd_line_split[1]="space/milky_way/solar_system/constellation"
       fonction_commande_touch(username, id_emploi, chemin_repertoire_personnel, comnd_line_split)

#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def fonction_commande_read_speed(username,id_emploi, chemin_repertoire_personnel,comnd_line_split):

       if comnd_line_split[0] == "observe" :
           comnd_line_split[1]="space/milky_way/solar_system/stars"
       elif comnd_line_split[0]== "track" :
           comnd_line_split[1]="space/milky_way/solar_system/planets"
       elif comnd_line_split[0] == "scan":
           comnd_line_split[1]="space/milky_way/solar_system/constellation"
       fonction_commande_lire(username,id_emploi, chemin_repertoire_personnel,comnd_line_split)

#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def afficher_contenu_repertoire(username, id_emploi, chemin_repertoire_personnel, mots):
    print(f"{chemin_repertoire_personnel}")
    perso_dir =os.path.basename(chemin_repertoire_personnel)
    if mots[2] == perso_dir:
         chemin = chemin_repertoire_personnel
    else:     
         chemin, _ = chercher_paths_par_id_emploi(id_emploi, mots, username)

            # Liste tous les fichiers et répertoires dans le chemin spécifié
    contenu = os.listdir(chemin)

            # Affiche chaque élément du contenu
    for element in contenu:
        print(element)

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def naviguer_arriere(username,id_emploi, chemin_repertoire_personnel,  mots):
    chemin_actuel = os.getcwd()

    while True:
        # Si l'utilisateur entre 'exit', sortir de la boucle
        if commande.lower() == 'exit':
            break

        # Sinon, essayer de changer le répertoire
        try:
            chemin_actuel = os.path.abspath(os.path.join(chemin_actuel, 'exit'))
            os.chdir(chemin_actuel)
        except FileNotFoundError:
            print(f"Répertoire ou fichier '{commande}' non trouvé.")
        except Exception as e:
            print(f"Erreur inattendue : {e}")
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def lire_fichier_aide(username,id_emploi, chemin_repertoire_personnel,mots):
    #nom_fichier=chemin("helpfile", "Settings")
    nom_fichier="/space/teleportation/helpfile"
    try:
        with open(nom_fichier, 'r') as fichier:
            contenu = fichier.read()
            print(contenu)
    except FileNotFoundError:
        print(f"Fichier d'aide '{nom_fichier}' non trouvé.")
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier d'aide : {e}")
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def copier_coller_renomer_file(username,id_emploi, chemin_repertoire_personnel,mots):
    if mots[0] == "astrocopy-paste" :
         x='at'
    else:
         x='wt'
    source_path=concatener_chemin(mots[1])
    destination_path=concatener_chemin(mots[2])
    with gzip.open(source_path, 'rt') as source_file:
        contenu = source_file.read()

    with gzip.open(destination_path, x) as destination_file:
        destination_file.write(contenu)

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def envoyer_fichier(username,id_emploi, chemin_repertoire_personnel,mots):
    try:
        # Vérifier si le fichier source existe
        mots[1]=concatener_chemin(mots[1])
        if not os.path.isfile(mots[1]):
            print(f"Le fichier {mots[1]} n'existe pas.")
            return
        chemin_repertoire_dest=chemin ('repertoire_perso', f"section_{mots[2]}")
        # Construire le chemin complet de destination
        chemin_fichier_dest = os.path.join(chemin_repertoire_dest, os.path.basename(mots[1]))

        # Copier le fichier vers le répertoire de destination
        shutil.copy(mots[1], chemin_fichier_dest)

        print(f"Le fichier {os.path.basename(mots[1])} a ete envoye au user de ID employee {mots[2]} avec succes.")
    
    except Exception as e:
        print(f"Erreur lors de l'envoi du fichier : {e}")
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
from datetime import datetime
def obtenir_meta_donnees(username,id_emploi, chemin_repertoire_personnel,mots):
 
    if mots[2] == os.path.basename(chemin_repertoire_personnel):
        chemin=chemin_repertoire_personnel
        id_createur="root"
    else:
        chemin, id_createur = chercher_paths_par_id_emploi(id_emploi, mots, username)
        if id_createur is None: 
           id_createur = "groupe root"
    if not chemin:
        return "Le chemin spécifié n'existe pas."

    # Vérifie si le chemin existe



    # Obtenir les informations communes (nom de l'utilisateur, chemin absolu, date de création, date de dernière modification)
    chemin_absolu = os.path.abspath(chemin)
    date_creation = datetime.fromtimestamp(os.path.getctime(chemin))
    date_modification = datetime.fromtimestamp(os.path.getmtime(chemin))
   
    print(f"{date_creation}{date_modification}")
    print("\n====META-DATA====\n")
    print(f">>Createur                     : {id_createur}")
    print(f">>Chemin absolu                : {chemin_absolu}")
    print(f">>Date de creation             : {date_creation}")
    print(f">>Date de dernière modification: {date_modification}")

    # Vérifier si c'est un fichier
    if os.path.isfile(chemin):
        # Obtenir le type et la taille
        type_fichier = "Fichier"
        taille = os.path.getsize(chemin)

        print(f">>Type                       : {type_fichier}")
        print(f">>Taille                     : {taille} octets")

    # Vérifier si c'est un répertoire
    elif os.path.isdir(chemin):
        print(">>Type                    : Repertoire")

        # Afficher les fichiers et répertoires dans le répertoire
        print("\n>>Contenu du répertoire:")
        for element in os.listdir(chemin):
            element_chemin = os.path.join(chemin, element)
            element_type = "Fichier" if os.path.isfile(element_chemin) else "Répertoire"

            print(f"\n>>Nom              : {element}")
            print(f">>Type             : {element_type}")

    else:
        print(">>Type inconnu.<<")
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


def generer_courbe_connexions(username,id_emploi, chemin_repertoire_personnel,mots):
    # Comptez le nombre de connexions réussies pour chaque jour
    compteur_dates = {}
    for date_connexion in dates_connexions_reussies:
        date_str = date_connexion.strftime('%Y-%m-%d')
        compteur_dates[date_str] = compteur_dates.get(date_str, 0) + 1

    # Extraire les dates et les fréquences
    dates, frequences = zip(*compteur_dates.items())

    # Créer un graphique
    plt.plot(dates, frequences, marker='o', linestyle='-')
    plt.xlabel('Date')
    plt.ylabel('Nombre de connexions')
    plt.title('Nombre de connexions réussies par jour')

    # Afficher le graphique
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def filtre_commande(username,chemin_repertoire_personnel,id_emploi, ligne_commande):
     try:
        mots = ligne_commande.split()
        # Définir un dictionnaire associant chaque commande à sa fonction correspondante
        commandes = {
            "astrocreate-user":saisie_coordon_new_user,
             "astrodelete-user": saisie_coordon_user_delete,
             "astromodify-user-grp": saisie_grp_user_modify,
             "astromodify-user-passwd": saisie_passwd_user_modify,
             "astrotouch": fonction_commande_touch,
             "astromkdir": fonction_commande_mkdir,
             "astrodelete": fonction_commande_delete,
             "astrowrite": fonction_commande_ecrire,
             "astroread": fonction_commande_lire,             
            # SPEED FONCTION
             "generate": fonction_commande_touch_speed,
             "build": fonction_commande_touch_speed,
             "compose": fonction_commande_touch_speed,
             #"forge": fonction_commande_forge,
             "explore": afficher_contenu_repertoire,
             "observe": fonction_commande_read_speed,
             "track": fonction_commande_read_speed,
             "scan": fonction_commande_read_speed,
             "eclipse": fonction_commande_delete_speed,
             "erase": fonction_commande_delete_speed,
             "purge": fonction_commande_delete_speed,
             #"exit":
             "HELP":lire_fichier_aide,
             "astrocopy-paste": copier_coller_renomer_file,
             "astrosignal" : envoyer_fichier,
             "md":obtenir_meta_donnees,
             "kpi" : generer_courbe_connexions
             
        }

        
        if mots:
            commande = mots[0].lower()
            # Utiliser le dictionnaire pour obtenir la fonction associée à la commande
            fonction_execute = commandes.get(commande, None)
            
            if fonction_execute:
                # Exécuter la fonction avec le nom d'utilisateur et les mots
                fonction_execute(username,id_emploi, chemin_repertoire_personnel,mots)

            else:
                print(f"Commande inconnue : {commande}")
        else:
            print("Commande vide.")
     except Exception as e:
        print(f"Erreur : {e}")
        

#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////   

def set_terminal_background_color(color_code):
    os.system(f"printf '\033]11;#{color_code}\033\\'") 
           
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

init(autoreset=True)

def afficher_fil_telechargement(progress):
    bar_length = 50
    block = int(round(bar_length * progress))
    progress_percent = round(progress * 100, 2)
   
    progress_bar = "                                         [" + Fore.MAGENTA + "#" * block + Style.RESET_ALL + "-" * (bar_length - block) + "]"
    sys.stdout.write(f"\r{progress_bar} {Fore.MAGENTA}{progress_percent}%{Style.RESET_ALL}")
    sys.stdout.flush()
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

class AstroBotPresenter:
    @staticmethod
    def display_message(message, color="white", style="normal"):
        color_codes = {
            "black": "30",
            "purple": "35",
            "cyan": "36",
            "white": "37",
        }

        style_codes = {
            "normal": "0",
            "bold": "1",
            "underline": "4",
            "reverse": "7",
        }

        color_code = color_codes.get(color, "37")
        style_code = style_codes.get(style, "0")

        formatted_message = f"\033[{style_code};{color_code}m{message}\033[0m"
        print(formatted_message)
class AstroBotArt:
    @staticmethod
    def display_robot():
        robot_art = """
'        ___           ___                       ___           ___          _____          ___                                    ___          '
'       /  /\         /  /\          ___        /  /\         /  /\        /  /::\        /  /\        ___           ___         /  /\         '
'      /  /::\       /  /:/_        /  /\      /  /::\       /  /::\      /  /:/\:\      /  /::\      /  /\         /__/\       /  /:/_        '
'     /  /:/\:\     /  /:/ /\      /  /:/     /  /:/\:\     /  /:/\:\    /  /:/  \:\    /  /:/\:\    /  /:/         \  \:\     /  /:/ /\       '
'    /  /:/~/::\   /  /:/ /::\    /  /:/     /  /:/~/:/    /  /:/  \:\  /__/:/ \__\:|  /  /:/~/:/   /__/::\          \  \:\   /  /:/ /:/_      '
'   /__/:/ /:/\:\ /__/:/ /:/\:\  /  /::\    /__/:/ /:/___ /__/:/ \__\:\ \  \:\ /  /:/ /__/:/ /:/___ \__\/\:\__   ___  \__\:\ /__/:/ /:/ /\     '
'   \  \:\/:/__\/ \  \:\/:/~/:/ /__/:/\:\   \  \:\/:::::/ \  \:\ /  /:/  \  \:\  /:/  \  \:\/:::::/    \  \:\/\ /__/\ |  |:| \  \:\/:/ /:/     '
'    \  \::/       \  \::/ /:/  \__\/  \:\   \  \::/~~~~   \  \:\  /:/    \  \:\/:/    \  \::/~~~~      \__\::/ \  \:\|  |:|  \  \::/ /:/      '
'     \  \:\        \__\/ /:/        \  \:\   \  \:\        \  \:\/:/      \  \::/      \  \:\          /__/:/   \  \:\__|:|   \  \:\/:/       '
'      \  \:\         /__/:/          \__\/    \  \:\        \  \::/        \__\/        \  \:\         \__\/     \__\::::/     \  \::/        '
'       \__\/         \__\/                     \__\/         \__\/                       \__\/                       ~~~~       \__\/         '

        """
        try:
            robot_color_code = "36"
            formatted_robot_art = f"\033[1;{robot_color_code}m{robot_art}\033[0m"
            print(formatted_robot_art.encode("utf-8").decode("latin-1"))
        except UnicodeEncodeError as e:
            print(f"Erreur d'encodage : {e}")
            print(f"Erreur d'encodage : {e}")
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def terminal_astrodrive(username, id_emploi, chemin_repertoire_personnel):


    distribution_name = "ASTRODrive"
    prompt_symbol = ">>>"
    set_terminal_background_color("12180d")
    while True:
        # Afficher le prompt du terminal
        print(f"\033[1;35m{username}\033[0m@\033[1;36m{distribution_name}\033[0m\033[1;35m{prompt_symbol}\033[0m", end="")
        commande_line=input()
        presenter = AstroBotPresenter()
        astrobot_message = "\n||| ASTROBot ||| >>>"
        presenter.display_message(astrobot_message, color="cyan", style="bold") 
        if commande_line.strip().lower() == "return-cpsul":
           presenter = AstroBotPresenter()
           astrobot_message = "                                          Fin de la mission spaciale avec ASTROBot en ASTRODrive!! \n"
           presenter.display_message(astrobot_message, color="purple", style="bold") 
           break   
        filtre_commande(username,chemin_repertoire_personnel,id_emploi, commande_line)
        # Traiter la commande si nécessaire
        # Pour l'instant, la fonction ne fait rien de plus qu'afficher le prompt.

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////  
if __name__ == "__main__":
   
  resultats_connexion = connexion_utilisateur()
  if resultats_connexion:
    nom_utilisateur, id_emploi, chemin_repertoire_personnel = resultats_connexion
    
    print("\n")
    for i in range(101):
       time.sleep(0.001)  # Simule le téléchargement
       progress = i / 100.0
       afficher_fil_telechargement(progress)
    
    print("\n")
    astrobot_art = AstroBotArt()   
    astrobot_art.display_robot()  # Display the robot art first
  
    presenter = AstroBotPresenter()
    astrobot_message = "                 Bienvenue sur ASTRODrive. Je suis votre assistant ASTROBot, Comment puis-je vous aider aujourd'hui?\n"
    presenter.display_message(astrobot_message, color="purple", style="bold")
    terminal_astrodrive(nom_utilisateur, id_emploi, chemin_repertoire_personnel)
 

