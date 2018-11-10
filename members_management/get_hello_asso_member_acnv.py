# get_hello_asso_members.py
# Python3
# author : Fafadji GNOFAME
# Date : 03 mars 2018
# Version : 1.0
# Description :  get all helloAsso members and write then in a csv file
#      How to get the campaign ID :
#      Get organism ID with command :
#          curl -u <username>:<password> https://api.helloasso.com/v3/organizations.json
#      Get compaign ID with command 
#          curl -u <username>:<password> https://api.helloasso.com/v3/[organizations/<organism-id>/]campaigns.json[?type=<EVENT|FORM|FUNDRAISER|MEMBERSHIP>]


import requests, csv, sys, argparse, configparser, os, errno
from functions import *


def get_hello_asso_payment_url(compaign_id, created_from):
    results_per_page = 100
        
    hello_asso_url_params = "results_per_page="+str(results_per_page)+"&from="+created_from
    hello_asso_url_payment = "https://api.helloasso.com/v3/campaigns/"+compaign_id+"/payments.json?"+hello_asso_url_params
    
    return hello_asso_url_payment


def get_hello_asso_members_url(compaign_id, created_from):
    results_per_page = 100
        
    hello_asso_url_params = "type=SUBSCRIPTION&results_per_page="+str(results_per_page)+"&from="+created_from
    hello_asso_url_members = "https://api.helloasso.com/v3/campaigns/"+compaign_id+"/actions.json?"+hello_asso_url_params
    
    return hello_asso_url_members

def get_hello_asso_member_payment_url(payment_id):
    return "https://api.helloasso.com/v3/payments/"+payment_id+".json"

def get_hello_asso_member_payment_from_server(hello_asso_user, hello_asso_pass, member):
    r_payment = requests.get(get_hello_asso_member_payment_url(member.get("id_payment")), auth=(hello_asso_user, hello_asso_pass))
    member_payment = r_payment.json()
    
    return member_payment

def get_hello_asso_member_payment_from_local(hello_asso_all_payments, member):
    member_payment = hello_asso_all_payments[member.get("id_payment")]
    return member_payment

def get_hello_asso_all_payments(hello_asso_user, hello_asso_pass, compaign_id, created_from):
    hello_asso_url_payment = get_hello_asso_payment_url(compaign_id, created_from)
    
    # First request to retrieve the number of page on witch we will loop
    r = requests.get(hello_asso_url_payment+'&page=1', auth=(hello_asso_user, hello_asso_pass))
    if r.status_code != 200:
        print("[ERROR] Erreur lors de la requete. Code HTTP de la reponse: "+str(r.status_code))
        sys.exit(2)  
        
    pages_number = r.json().get("pagination").get("max_page")
    current_page = 0
    
    hello_asso_all_payments =  {}
    
    while current_page < pages_number:
        current_page += 1
        if(current_page > 1):
            r = requests.get(hello_asso_url_payment+'&page='+str(current_page), auth=(hello_asso_user, hello_asso_pass)) 
        r_json = r.json()
        payments = r_json.get("resources")
        
        for payment in payments:
            hello_asso_all_payments[payment.get("id")] = payment
    
    return hello_asso_all_payments


def format_member(member, member_payment):
    sub_source = "helloAsso"

    m_id, m_name, m_surname = member.get("id"), member.get("last_name").upper(), member.get("first_name").title()
    m_subs_type, m_subs_date, m_subs_amout = member.get("option_label"), member.get("date"), str(int(member.get("amount")))
    
    m_card_id = m_id.strip('0')
    m_card_id = m_card_id[:-1]
    m_card_url = "https://www.helloasso.com/associations/les-amis-de-demain/adhesions/adhesion-a-l-association-les-amis-de-demain/carte-adherent?id="+m_card_id
    
    m_email = member.get("email")
    
    m_address, m_city = member_payment.get("payer_address") , member_payment.get("payer_city"),
    m_zip_code, m_country = member_payment.get("payer_zip_code"), member_payment.get("payer_country")
    m_phone = ""
    m_newsletter = ""
    
    for custom_info in member.get("custom_infos"):
        label = custom_info.get("label")

        #if label == "Email": m_email = custom_info.get("value")                             
        if label == "Numéro de téléphone": m_phone = custom_info.get("value")  
        elif label == "Recevoir la newsletter ACNV (Info indicative pour l'ACNV. Dans tous les cas l'abonnement est manuel et à réaliser depuis le site cnvfrance.fr)": m_newsletter = custom_info.get("value")  
        
    m_email = "" if m_email is None else m_email.lower()
    m_address = "" if m_address is None else m_address.lower()
    m_city = "" if m_city is None else m_city.title()
    m_country = "" if m_country is None else m_country.upper()
    m_newsletter = "" if m_newsletter is None else m_newsletter.lower()
    
    if m_zip_code is None : m_zip_code = "" 
    
    
    # last_name|first_name|email|phone|address|city|zip|country|member_2018|m_source_2018|newsletter
    csv_line =  [m_name, m_surname, m_email, m_phone, m_address, m_city, m_zip_code, m_country, m_subs_amout, sub_source, m_newsletter]       
    # strip "\n" to prevent undesirable end of line in the csv file
    csv_line = [word.strip() for word in csv_line]
    
    return csv_line
        

def get_hello_asso_members(compaign_id, hello_asso_user, hello_asso_pass, output_file , config, created_from = ""):
    
    print("[INFO] Debut Traitement")    
    print("[INFO] Recuperation de la liste des adherents")
    print("[INFO]    ID de la campagne : "+str(compaign_id))
    
    print_date_debut = "[INFO]    Date debut : " 
    
    if created_from == "":
        print_date_debut +="Debut de la campagne"
    else:
        print_date_debut +=created_from
    
    print(print_date_debut)
    
    hello_asso_members_url = get_hello_asso_members_url(compaign_id, created_from)
    
    # First request to retrieve the number of page on witch we will loop
    r = requests.get(hello_asso_members_url+'&page=1', auth=(hello_asso_user, hello_asso_pass))
    if r.status_code != 200:
        print("[ERROR] Erreur lors de la requete. Code HTTP de la reponse: "+str(r.status_code))
        sys.exit(2)
    
    pages_number = r.json().get("pagination").get("max_page")
    
    current_page = 0
    members_count = 0
    
    sub_source_key = "m_source_2018"
    
    hello_asso_all_payments = get_hello_asso_all_payments(hello_asso_user, hello_asso_pass, compaign_id, created_from)

    create_path_n_file_if_needed(output_file)
    # Opening the csv file
    with open(output_file, 'w') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)   
                
        # Writting the header's line in the csv file

        # last_name|first_name|email|phone|address|city|zip|country|member_2018|m_source_2018
        csv_line_header =  ["last_name", "first_name", "email", "phone", "address", "city", 
                                    "zip", "country", "member_2018", "m_source_2018", "newsletter"]        
        
        csv_writer.writerow(csv_line_header)    
        
        # loop on the pages returned by helloAsso
        # On every page, retreiving the members list and writing them on the csv file
        while current_page < pages_number:
            current_page += 1
            if(current_page > 1):
                r = requests.get(hello_asso_members_url+'&page='+str(current_page), auth=(hello_asso_user, hello_asso_pass)) 
            r_json = r.json()
            members = r_json.get("resources")

            for member in members:
                members_count +=1
                
                #r_payment = requests.get(get_hello_asso_member_payment_url(member.get("id_payment")), auth=(hello_asso_user, hello_asso_pass))
                member_payment = get_hello_asso_member_payment_from_local(hello_asso_all_payments, member)
                
                csv_line = format_member(member, member_payment)
                csv_writer.writerow(csv_line)
            
            print("[INFO] Page " + str(current_page) + " sur " + str(pages_number) + " traitee")
            
    print("[INFO] Nombre d'adherents: " + str(members_count))
    print("[INFO] Fichier de sortie : " + output_file)
    print("[INFO] Fin Traitement")
    
    

def parse_params(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--campaign', required=True, help='Id de la campagne helloAsso') 
    parser.add_argument('-s', '--start_date', required=False, default="", 
        help='Date de debut a partir de laquelle recuperer les adhesions. Si non renseigne, correspond a la date de debut de la campagne. Exemple de date : -s "2017-04-01T00:00:00"')  
    parser.add_argument('-u', '--username', required=True, help='Nom utilisateur de API HelloAsso')    
    parser.add_argument('-p', '--password', required=True, help='Mot de passe de API HelloAsso') 
    parser.add_argument('-mc', '--m_k_config_file', required=False, default="param.conf",
                        help="Chemin vers le fichier de configuration des clef d'identification d'un membre")
    parser.add_argument('-o', '--output_file', required=False, default="csv/adherents_hello_asso_acnv.csv",
                        help="Chemin vers le fichier de sortie")     
    
    return parser.parse_args(argv)
    

def main(argv):
    args = parse_params(argv)
    
    m_k_config_file = args.m_k_config_file
    config = configparser.ConfigParser()
    config.read(m_k_config_file)
    
    get_hello_asso_members(args.campaign , args.username, args.password, args.output_file, config, args.start_date)

if __name__ == "__main__":
    main(sys.argv[1:])



