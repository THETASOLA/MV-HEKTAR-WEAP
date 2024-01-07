from lxml import etree

def giveBlueprintsList(data, name):
    xml = etree.Element("blueprintList")
    xml.set("name", name)
    for module_name, module in data.items():
        #print(module.find("weaponBlueprint").text)
        add = etree.SubElement(xml, "name")
        add.text = module.find("weaponBlueprint").text

    with open(f"data/autoBlueprints.xml.append", "a") as f:
        f.write(etree.tostring(xml, pretty_print=True, encoding="unicode"))
        
    
    
""" <blueprintList name="HEKTAR_MODULAR_LASERS">
	<name>MODULAR_LASER_BASE</name>
	<name>MODULAR_LASER_BASE_BIO</name>
	<name>MODULAR_LASER_BASE_COOLDOWN</name>
	<name>MODULAR_LASER_BASE_LOCKDOWN</name>
	<name>MODULAR_LASER_BASE_PIERCE</name>
	<name>MODULAR_LASER_BASE_STUN</name> """