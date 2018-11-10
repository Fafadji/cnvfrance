# hello_asso_remove_duplicate_subscriptions.py
# Python3
# author : Fafadji GNOFAME
# Date : 07 mars 2018
# Version : 1.0
# Description :  
#   Script to delete duplicate entries on the hello_asso members list csv file
#   If there is a duplicate entry, the one kept is the one with the lastest subscription date

#   Algorithm
#   IF name+surmane identical with another line THEN
#      IF email OR full postal address identical THEN **
#         Delete duplicate entry
#
# if some info are absent from last member subscription and present in some previous subscription
# we complete the last subscription with info from previous subscription

# ** Hypothesis :
# When we have the name and surname identical, we assume that 
# if the email or the zip code is also identical, then it is the same person
# Indeed, when those condition are met, it is higthly probable that it is the same person
# Why email OR full postal address ? Because it is also probable that when registering twice
# the subscriber induce an error when filling his or her email or full postal address. 
# It is less probable that an error is done on both information . 
# Note that the error migth be on the line we keep, 
# but we will consider that it is an error in the same way that 
# a subscriber (without duplicate) would make the same kind of error when subscribing

# Plaese note that this is a help script, it is advised to check manually afterward.
# For exemple, if there is a duplicate entry with a slice error on the name 
# (Sophie and Sopie), that won't be detected


import requests, csv, sys, argparse, configparser
from operator import itemgetter
from members_keys import MembersKeys
from functions import *

def delete_duplicate_entries(args):
    print("[INFO] Debut Traitement") 
    
    config = configparser.ConfigParser()
    config.read(args.m_k_config_file)    
    
    m_keys = MembersKeys(config)
        
    # Reading the csv file to build a member list
    members_list = []
    csv_dic_reader = csv.DictReader(open(args.input, 'r'), delimiter='|')
    for member in csv_dic_reader:
        member[m_keys.name], member[m_keys.surname] = member[m_keys.name].upper(), member[m_keys.surname].title()
        member[m_keys.email] = member[m_keys.email].lower()
        member[m_keys.address], member[m_keys.city] = member[m_keys.address].lower(), member[m_keys.city].lower()
        member[m_keys.zip] =  member[m_keys.zip].lower()
        
        members_list.append(member)
    
    members_all, members_all_final, duplicates_number = len(members_list), 0, 0

    if members_all > 0:
    
        members_list_ref, members_list_search = list(members_list), list(members_list)
        members_list_final = []
        
        # Algorithm : 
        # Loop on members_list_ref and then for each member
        # search the member on members_list_search : check if name and surname identical and (email or postal address identical)
        # when found delete member from members_list_search and
        # add the member on a temporary list to check for duplicate
        # Then sort the temporary list and then add the member on members_list_final
        # If duplicate entry cannot be identified clearly, add the member on members_list_final_log
           
        for m_ref in members_list_ref:
            members_list_duplicate = []
    
            m_ref_full_address = m_ref[m_keys.address] + m_ref[m_keys.city] + m_ref[m_keys.zip]
            
            for m_seach in members_list_search:
                
                m_search_full_address = m_seach[m_keys.address] + m_seach[m_keys.city] + m_seach[m_keys.zip]
                
                test_same_name_surname = (m_ref[m_keys.name] == m_seach[m_keys.name] and m_ref[m_keys.surname]  == m_seach[m_keys.surname])
                test_same_email_or_address = (m_ref[m_keys.email] == m_seach[m_keys.email] or m_ref_full_address == m_search_full_address)
                
                if test_same_name_surname and test_same_email_or_address: 
                    members_list_duplicate.append(m_seach)
                    
            # Removing found items so that in next iteration it will not be in the search_list to be found again                            
            members_list_search = [x for x in members_list_search if x not in members_list_duplicate]
            
            members_list_duplicate_len = len(members_list_duplicate)
            if members_list_duplicate_len >= 1:
                members_list_duplicate_sorted = sorted(members_list_duplicate, key=itemgetter(m_keys.subs_date), reverse=True)
                
                # if some info are absent from last member subscription and present in some previous subscription
                # we complete the last subscription with info from previous subscription
                member_final = members_list_duplicate_sorted[0].copy()
                for m in members_list_duplicate:
                    for k,v in m.items():
                        if k not in member_final or member_final[k] == '':
                            member_final[k] = v            
                
                members_list_final.append(member_final)
                
        
        members_all_final = len(members_list_final)
        duplicates_number = members_all - members_all_final
        
        dict_keys = members_list[0].keys()
        create_path_n_file_if_needed(args.output)
        csv_writer = csv.DictWriter(open(args.output, 'w'), dict_keys, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL) 
        csv_writer.writeheader() 
        csv_writer.writerows(members_list_final)
        
    print("[INFO] Nombre total de membres helloAsso : " + str(members_all)) 
    print("[INFO] Nombre de membres helloAsso sans doublon : " + str(members_all_final)) 
    print("[INFO] Nombre de doublon : " + str(duplicates_number)) 
    
    print("[INFO] Fin Traitement") 


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=False, default="csv/adherents_hello_asso.csv",
                        help="Fichier d'entree helloAsso")    
    parser.add_argument('-o', '--output', required=False, default="csv/adherents_hello_asso_sans_doublon.csv",
                        help="Fichier de sortie")     
    parser.add_argument('-mc', '--m_k_config_file', required=True, 
                        help="Chemin vers le fichier de configuration des clef d'identification d'un membre")   
    args = parser.parse_args(argv)

    delete_duplicate_entries(args)

if __name__ == "__main__":
    main(sys.argv[1:])



