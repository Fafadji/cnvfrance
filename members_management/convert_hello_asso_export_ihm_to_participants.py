import csv, sys, os, errno


def create_path_n_file_if_needed(filename):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise     

def get_member_hello_asso_email(m_hello_asso):
    m_hello_asso_email = m_hello_asso["Champ additionnel: Email"]
    if m_hello_asso_email == "":
        if m_hello_asso["Nom"].upper() == m_hello_asso["Nom acheteur"].upper() and m_hello_asso["Prénom"].title() == m_hello_asso["Prénom acheteur"].title():
            m_hello_asso_email = m_hello_asso["Email"]
            
    return m_hello_asso_email.lower()
       
            
def main(argv):
    csv_hello_asso = "export-adhesion-01_01_2018-30_11_2018.csv"
    csv_participants_db = "./participants_db-to_import-01_01_2018-30_11_2018.csv"
    members_participants_db_list = []
    
    csv_dic_reader = csv.DictReader(open(csv_hello_asso, 'r'), delimiter=';')
    
    participants_db_keys = ["last_name", "first_name", "email", "phone", "address", "city", 
                            "zip", "country", "member_2018", "m_source_2018", "newsletter"]
    
    for m_hello_asso in csv_dic_reader:
        m_participants_db = {"last_name" : m_hello_asso["Nom"].upper(), "first_name" : m_hello_asso["Prénom"].title(), 
                             "email" : get_member_hello_asso_email(m_hello_asso), 
                             "phone" : m_hello_asso["Champ additionnel: Numéro de téléphone"], 
                             "address" : m_hello_asso["Adresse acheteur"].lower(), "city" : m_hello_asso["Ville acheteur"].title(),
                              "zip" : m_hello_asso["Code Postal acheteur"], "country" : m_hello_asso["Pays acheteur"].upper(),
                              "member_2018" : int(float(m_hello_asso["Montant adhésion"].replace(",", "."))), "m_source_2018" : "helloAsso",
                              "newsletter" : m_hello_asso["Champ additionnel: Recevoir la newsletter ACNV (Info indicative pour l'ACNV. Dans tous les cas l'abonnement est manuel et à réaliser depuis le site cnvfrance.fr)"].lower()}
        
        members_participants_db_list.append(m_participants_db)

    #print(members_participants_db_list)


    create_path_n_file_if_needed(csv_participants_db)
    #participants_db_keys = members_participants_db_list[0].keys()
    csv_writer = csv.DictWriter(open(csv_participants_db, 'w'), participants_db_keys, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL) 
    csv_writer.writeheader() 
    csv_writer.writerows(members_participants_db_list)

if __name__ == "__main__":
    main(sys.argv[1:])