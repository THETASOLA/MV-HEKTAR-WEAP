from lxml import etree
import json
from generation.python.weapon_stats import *
from generation.python.weapon_list_name import *

additional_data = ""

def generate_weapon(json_weapon_data):
    weapon_dictionary["BASE"] = create_new_weapon(json_weapon_data)
    weapon_dictionary["BASE"].set("name", weapon_dictionary["BASE"].get("name") + "_BASE")
    module_dictionary = {}
    main_module_dictionary = {}
    data_written = ""

    for module_name in json_weapon_data:
        if module_name != "weaponBlueprint":
            create_module_weapon(json_weapon_data, module_name)
            module_data = json_weapon_data[module_name]
            if module_data["main"]:
                main_module_dictionary[module_name] = module_data
            else:
                module_dictionary[module_name] = module_data

    for _, main_module_data in main_module_dictionary.items():
        for _, module_data in module_dictionary.items():
            create_two_module_weapon(json_weapon_data, main_module_data, module_data)

    for module_name, module in weapon_dictionary.items():
        xml_str = etree.tostring(module, pretty_print=True, encoding="unicode")
        data_written += xml_str + "\n"
    return data_written

data_to_be_written = ""

with open("generation/json/weapon_pinpoint.json", "r") as f:
    json_data_weapon_pinpoint = json.load(f)

with open("generation/json/weapon_flak.json", "r") as f:
    json_data_weapon_flak = json.load(f)

with open("generation/json/weapon_bomb.json", "r") as f:
    json_data_weapon_bomb = json.load(f)

# -------------------------------------------------------------- WEAPON
data_to_be_written += generate_weapon(json_data_weapon_pinpoint)
#data_to_be_written += generate_weapon(json_data_weapon_flak)
#data_to_be_written += generate_weapon(json_data_weapon_bomb)

with open("output/data/blueprints.xml.append", "w") as f:
    f.write(data_to_be_written)
