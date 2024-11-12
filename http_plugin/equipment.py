# Drop into REPL:
# python3.10 -i http_plugin/equipment.py

import requests
# import http_plugin.item_ids as item_ids
import item_ids

class Equipment:
    def __init__(self):
        self.reload()

    def reload(self):
        r = requests.get('http://localhost:8080/equip')
        self.i = r.json()

    def __str__(self):
        output = ""
        for slot in self.i:
            output += f"{self.get_item_name_from_id(slot['id'])}: {slot['quantity']} "
            output += "\n"
        return output
    
    # Debug helper
    def get_item_name_from_id(self, item_id):
        all_items = list(vars(item_ids).items())
        for name, id in all_items:
            if id == item_id:
                return name
        return None

if __name__ == '__main__':
    equip = Equipment()
    print(equip)



        