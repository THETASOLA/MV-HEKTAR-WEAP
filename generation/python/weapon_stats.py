from lxml import etree

def generate_weapon_name(element, module_name, is_main_module, lower=False, submodule_name=""):
    base_name = element.get("name")

    if submodule_name:
        element.set("name", f"{base_name}_{module_name}_{submodule_name}")
    elif is_main_module:
        element.set("name", f"{base_name}_{module_name}")
    else:
        element.set("name", f"{base_name}_BASE_{module_name}")

def add_bio_stat_boosts(element):
    bio_stat_boosts = {
        "moveSpeedMultiplier": {"boostType": "MULT", "amount": "0.33", "shipTarget": "ALL",
                                "crewTarget": "ALL", "affectsSelf": "true", "maxStacks": "1", "duration": "10"},
        "stunMultiplier": {"boostType": "MULT", "amount": "1.75", "shipTarget": "ALL",
                           "crewTarget": "ALL", "affectsSelf": "true", "maxStacks": "1", "duration": "10"},
        "repairSpeed": {"boostType": "MULT", "amount": "0.33", "shipTarget": "ALL",
                        "crewTarget": "ALL", "affectsSelf": "true", "maxStacks": "1", "duration": "10"},
    }

    stat_boosts_element = etree.SubElement(element, "statBoosts")

    for stat_name, stat_properties in bio_stat_boosts.items():
        stat_boost_element = etree.SubElement(stat_boosts_element, "statBoost")
        stat_boost_element.set("name", stat_name)

        for prop_name, prop_value in stat_properties.items():
            prop_element = etree.SubElement(stat_boost_element, prop_name)
            prop_element.text = prop_value

def add_module_value(element, module_name, value):
    module_element = element.find(module_name)

    if module_element is None:
        module_element = etree.SubElement(element, module_name)

    module_element.text = value

def add_to_desc(element, main_text, additional_text=""):
    if additional_text:
        additional_text = "\n" + additional_text

    desc_element = element.find("desc")
    text = f"Produced by Hektar Industries(TM), this is the base for a Modular Laser. It supports 1 attribute module and 1 status module.\nHas no incompatible modules." \
           f"\n----CURRENTLY INSTALLED MODULES----\n{main_text}{additional_text}\n"
    desc_element.text = text

def create_new_weapon(json_data):
    new_weapon_element = etree.Element("weaponBlueprint")

    for key, value in json_data["weaponBlueprint"].items():
        if isinstance(value, dict):
            first = True
            outer_element = etree.SubElement(new_weapon_element, key)
            inner_element = etree.SubElement(outer_element, list(value.keys())[0])

            for inner_key in value:
                if isinstance(value[inner_key], list):
                    for item in value[inner_key]:
                        if first:
                            inner_element.text = item
                            first = False
                        else:
                            inner_element = etree.SubElement(outer_element, list(value.keys())[0])
                            inner_element.text = item
                else:
                    inner_element.text = value[inner_key]
        elif isinstance(value, list):
            for item in value:
                outer_element = etree.SubElement(new_weapon_element, key)
                outer_element.text = item
        elif key.startswith("@"):
            new_weapon_element.set(key[1:], value)
        else:
            outer_element = etree.SubElement(new_weapon_element, key)
            outer_element.text = value

    return new_weapon_element

weapon_dictionary = {}

def create_module_weapon(json_data, module_name):
    module_data = json_data[module_name]
    new_module_weapon = create_new_weapon(json_data)
    weapon_dictionary[module_data["name"]] = new_module_weapon

    is_main_module = module_data["main"]
    generate_weapon_name(new_module_weapon, module_data["name"], is_main_module)

    add_to_desc(new_module_weapon, module_data["desc"])

    module_data["bio"] = module_data["bio"] if "bio" in module_data else False
    if module_data["bio"]:
        add_bio_stat_boosts(new_module_weapon)

    for stat_name, stat_value in module_data["stats"].items():
        add_module_value(new_module_weapon, stat_name, stat_value)

def create_two_module_weapon(json_data, main_module_data, sub_module_data):
    new_module_weapon = create_new_weapon(json_data)
    weapon_dictionary[f"{main_module_data['name']}_{sub_module_data['name']}"] = new_module_weapon

    generate_weapon_name(new_module_weapon, main_module_data["name"], False, False, sub_module_data["name"])

    main_module_data["bio"] = main_module_data["bio"] if "bio" in main_module_data else False
    sub_module_data["bio"] = sub_module_data["bio"] if "bio" in sub_module_data else False

    if main_module_data["bio"] or sub_module_data["bio"]:
        add_bio_stat_boosts(new_module_weapon)

    add_to_desc(new_module_weapon, main_module_data["desc"], sub_module_data["desc"])

    to_be_removed = []

    # Handle special case for "breachChance"
    breach_chance_main = main_module_data["stats"].get("breachChance", "0")
    breach_chance_submodule = sub_module_data["stats"].get("breachChance", "0")
    breach_chance_sum = str(int(breach_chance_main) + int(breach_chance_submodule))

    if "breachChance" in main_module_data["stats"] and "breachChance" in sub_module_data["stats"]:
        add_module_value(new_module_weapon, "breachChance", breach_chance_sum)
        to_be_removed.append("breachChance")

    for stat_name, stat_value in main_module_data["stats"].items():
        for submodule_stat_name, submodule_stat_value in sub_module_data["stats"].items():
            if stat_name == submodule_stat_name and stat_name not in to_be_removed:
                adjusted_value = str(int(stat_value) + int(submodule_stat_value) - int(new_module_weapon.find(stat_name).text))
                add_module_value(new_module_weapon, stat_name, adjusted_value)
                to_be_removed.append(stat_name)

    for stat_to_remove in to_be_removed:
        del main_module_data["stats"][stat_to_remove]
        del sub_module_data["stats"][stat_to_remove]

    for stat_name, stat_value in main_module_data["stats"].items():
        add_module_value(new_module_weapon, stat_name, stat_value)

    for stat_name, stat_value in sub_module_data["stats"].items():
        add_module_value(new_module_weapon, stat_name, stat_value)
