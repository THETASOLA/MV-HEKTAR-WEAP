from lxml import etree
import json
from weapon_stats import *
from weapon_list_name import *

additional_data = """
<mod:findName type="weaponBlueprint" name="MODULE_ACCURACY">
	<mod-append:desc>Hektar Industries(TM) brand Attribute Accuracy Module. Ensure your weaponry stays on target on the battlefield!
	Incompatible with the Modular Beam/Pinpoint.
	Laser/Ion Effects: +20% accuracy buff
	Missile/Bomb Effects: +100% accuracy buff
    Flak Effects: -10 spread, +10% accuracy buff</mod-append:desc>
</mod:findName>

<mod:findName type="weaponBlueprint" name="MODULE_BIO">
	<mod-append:desc>Hektar Industries(TM) brand Status RAD Module. Turn your modular weapons into the perfect anti-crew weaponry!
	No incompatibilities. When combined with the Hullbuster Module, will restore hull and system damage, but will not have hull bust properties.
	Laser Effects: 0 hull/system dmg, +30 crew damage, +1 shield pierce
	Beam Effects: 0 hull dmg (system dmg is preserved), +60 crew damage, +1 shield pierce
	Missile Effects: 0 hull/system dmg, +90 crew damage
	Ion Effects: +60 crew damage (must be a direct hit)
    Pinpoint/Bomb Effects: +90 crew damage
    Flak Effects: +30 crew damage
	Weapons also gain standard Anti-Bio crew debuffs. (66% slowed speed and repairs, 75% increased stun duration)</mod-append:desc>
</mod:findName>

<mod:findName type="weaponBlueprint" name="MODULE_COOLDOWN">
	<mod-append:desc>Hektar Industries(TM) brand Status Cooldown Module. Turn your modular weapons into power efficient fast firing assault weaponry!
	No incompatibilities.
	Effects for all weapons: Reduces cooldown by 25%
    </mod-append:desc>
</mod:findName>

<mod:findName type="weaponBlueprint" name="MODULE_LOCKDOWN">
	<mod-append:desc>Hektar Industries(TM) brand Status Lockdown Module. Turn your modular weapons into the next generation of tech and cause chaos on the enemy ship with patented lockdown tech!
	Incompatible with the Modular Beam/Pinpoint.
	Effects for all weapons: Applies lockdown on impact</mod-append:desc>
</mod:findName>

<mod:findName type="weaponBlueprint" name="MODULE_PIERCE">
	<mod-append:desc>Hektar Industries(TM) brand Status Pierce Module. Never deal with enemy fortifications ever again!
	Incompatible with the Modular Missile/Bomb.
	Laser/Beam/Pinpoint/Flak Effects: +1 shield pierce, +30% breach chance
	Ion Effects: +3 shield pierce (affects shield as it passes through)</mod-append:desc>
</mod:findName>

<mod:findName type="weaponBlueprint" name="MODULE_STUN">
	<mod-append:desc>Hektar Industries(TM) brand Status Neural Module. Turn your modular weapons into crew disrupting neural weaponry!
	No incompatibilities.
	Laser/Flak Effects: Projectiles apply 12 seconds of stun (projectiles do not stack the duration)
	Beam Effects: Beam applies 18 seconds of stun
	Missile Effects: Missile applies 14 seconds of stun
	Ion Effects: Ion applies stun equal to ion duration +2s
    Pinpoint Effects: Pinpoint applies 22 seconds of stun
    Bomb Effects: 0 system dmg [Power restores system dmg], +6 ion, applies 20 seconds of stun</mod-append:desc>
</mod:findName>

<mod:findName type="weaponBlueprint" name="MODULE_FIRE">
	<mod-append:desc>Hektar Industries(TM) brand Attribute Firestarter Module. Create devastating infernos with your modular weaponry!
	No incompatibilities.
	Laser Effects: +30% fire chance
	Beam/Flak Effects: +40% fire chance
	Missile/Bomb Effects: +100% fire chance
	Ion/Pinpoint Effects: +100% fire chance</mod-append:desc>
</mod:findName>

<mod:findName type="weaponBlueprint" name="MODULE_HULL">
	<mod-append:desc>Hektar Industries(TM) brand Attribute Hullbust Module. Decimate the enemy's hull with heavy hitting modular weaponry!
	No incompatibilities. When combined with the RAD module, will return to default hull damage but will not have hull bust properties.
	Laser/Beam/Missile/Flak Effects: x2 damage on systemless rooms, +10% breach chance. [Breach stacks with Pierce Module breach chance]
	Missile Effects: Increases cooldown by 2s.
    Pinpoint Effects: x2 damage on systemless rooms, +100% breach chance, +1 damage, -1 system damage.
    Bomb Effects: +1 damage, +100% breach chance.
	Ion Effects: Ion becomes Energy; hull damage equals ion damage (but no system/crew damage), +10% fire chance</mod-append:desc>
</mod:findName>

<mod:findName type="weaponBlueprint" name="MODULE_POWER">
	<mod-append:desc>Hektar Industries(TM) brand Attribute Power Module. Get more bang for your buck with your modular weaponry!
	Laser Effects: +2 projectiles, +1 power cost, +4s cooldown
	Beam Effects: +60 beam length, doubled beam speed, +30% breach chance, +1 power cost [Breach stacks with Pierce Module breach chance]
	Missile Effects: +1 damage, +1 power cost
	Ion Effects: +1 ion damage, +1 power cost
    Bomb Effects: +2 system damage, +1 power cost
    Pinpoint Effects: +2 damage, +1 power cost
    Flak Effects: +2 projectiles, +1 power, +10 radius</mod-append:desc>
</mod:findName>
"""


def generate_weapon(json_weapon_data):
    weapon_dictionary = {}
    weapon_dictionary["BASE"] = create_new_weapon(json_weapon_data)
    weapon_dictionary["BASE"].set("name", weapon_dictionary["BASE"].get("name") + "_BASE")
    module_dictionary = {}
    main_module_dictionary = {}
    data_written = ""

    for module_name in json_weapon_data["modules"]:
        weapon_dictionary = weapon_dictionary | create_module_weapon(json_weapon_data, module_name)
        module_data = json_weapon_data["modules"][module_name]
        if module_data["main"]:
            main_module_dictionary[module_name] = module_data
        else:
            module_dictionary[module_name] = module_data

    for _, main_module_data in main_module_dictionary.items():
        for _, module_data in module_dictionary.items():
            weapon_dictionary = weapon_dictionary | create_two_module_weapon(json_weapon_data, main_module_data, module_data)

    for module_name, module in weapon_dictionary.items():
        xml_str = etree.tostring(module, pretty_print=True, encoding="unicode")
        data_written += xml_str + "\n"

    #giveBlueprintsList(weapon_dictionary, "HEKTAR_MODULAR_")
    return data_written

data_to_be_written = ""

with open("generation/json/weapon_pinpoint.json", "r") as f:
    json_data_weapon_pinpoint = json.load(f)

with open("generation/json/weapon_flak.json", "r") as f:
    json_data_weapon_flak = json.load(f)

with open("generation/json/weapon_bombL.json", "r") as f:
    json_data_weapon_bomb = json.load(f)

# -------------------------------------------------------------- WEAPON
data_to_be_written += generate_weapon(json_data_weapon_pinpoint)
weapon_dictionary = {}
data_to_be_written += generate_weapon(json_data_weapon_flak)
weapon_dictionary = {}
data_to_be_written += generate_weapon(json_data_weapon_bomb)

with open("output/data/blueprints.xml.append", "w") as f:
    f.write(data_to_be_written)
