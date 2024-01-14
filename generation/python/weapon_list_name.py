from lxml import etree

def giveBlueprintsList(data, name):
    xml = etree.Element("blueprintList")
    xml.set("name", name)
    for module_name, module in data.items():

        add = etree.SubElement(xml, "name")
        add.text = module.get("name")
    
    print(etree.tostring(xml, pretty_print=True, encoding="unicode"))

    with open(f"output/data/autoBlueprints.xml.append", "a") as f:
        f.write(etree.tostring(xml, pretty_print=True, encoding="unicode"))
        
    
    
""" <blueprintList name="HEKTAR_MODULAR_LASERS">
	<name>MODULAR_LASER_BASE</name>
	<name>MODULAR_LASER_BASE_BIO</name>
	<name>MODULAR_LASER_BASE_COOLDOWN</name>
	<name>MODULAR_LASER_BASE_LOCKDOWN</name>
	<name>MODULAR_LASER_BASE_PIERCE</name>
	<name>MODULAR_LASER_BASE_STUN</name> """