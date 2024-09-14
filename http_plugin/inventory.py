# Drop into REPL:
# python3.10 -i http_plugin/inventory.py

import requests
import http_plugin.item_ids as item_ids

class Inventory:
    def __init__(self):
        # Sets self.i
        self.reload()

    def is_empty(self):
        self.reload()
        ids = map(lambda s: s['id'], self.i)
        empties = map(lambda id: id == -1, ids)
        return all(empties)

    def is_full(self):
        self.reload()
        ids = map(lambda s: s['id'], self.i)
        not_empties = map(lambda id: id != -1, ids)
        return all(not_empties)

    # Returns (slot_index, quantity) for first slot with `item`
    def has_item(self, item_id):
        self.reload()
        for index, slot in enumerate(self.i):
            if slot['id'] == item_id:
                return index, slot['quantity']
        return None
    
    # Returns (slot_index, quantity) for first slot with any item in `items`
    # If `ignore` is passed, will not flag those items.
    def has_any_items(self, item_ids, ignore=[]):
        if not isinstance(ignore, list):
            ignore = [ignore]

        for index, slot in enumerate(self.i):
            if slot['id'] in item_ids and slot['id'] not in ignore:
                return index, slot['quantity']
        return None

    def reload(self):
        r = requests.get('http://localhost:8080/inv')
        self.i = r.json()

    def __str__(self):
        output = ""
        for row in range(0, 7):
            start = row * 4
            end = start + 4
            for slot in range(start, end):
                output += f"{self.i[slot]['id']}: {self.i[slot]['quantity']} "
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
    inv = Inventory()
    print("Inv is empty?", inv.is_empty())
    print("Has runes?", inv.has_any_items(item_ids.RUNES, ignore=item_ids.AIR_RUNE))
    print("Has air runes?", inv.has_item(item_ids.AIR_RUNE))
    print("Inv is full?", inv.is_full())



        