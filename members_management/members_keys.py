

class MembersKeys:
    def __init__(self, config):
        default_config = config['DEFAULT']
        self.id = default_config['id']
        self.name, self.surname, self.birthday = default_config['name'], default_config['surname'], default_config['birthday']
        self.email, self.phone =  default_config['email'], default_config['phone']
        self.address, self.city, self.zip = default_config['address'], default_config['city'], default_config['zip']
        self.country = default_config['country']
        self.subs_date, self.subs_type = default_config['subs_date'], default_config['subs_type']
        self.subs_amount, self.subs_card_url = default_config['subs_amount'], default_config['subs_card_url']
