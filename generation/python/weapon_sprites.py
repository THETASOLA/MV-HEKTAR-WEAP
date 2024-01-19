from PIL import Image, ImageDraw
import json
import random

def multiply_horizontal(image_path, multiplier):
    original_image = Image.open(image_path).convert("RGBA")
    width, height = original_image.size
    new_width = width * multiplier

    new_image = Image.new("RGBA", (new_width, height))
    for i in range(multiplier):
        new_image.paste(original_image, (i * width, 0), original_image)

    return new_image, width

def get_position_x(position, separation_width):
    return position * separation_width

def add_layer(image, layer_image, position):
    image.alpha_composite(layer_image, position)

def detect_first_pixel(image, up=True):
    width, height = image.size
    pixels = image.load()

    range_values = range(height) if up else reversed(range(height))

    for y in range_values:
        for x in range(width):
            if pixels[x, y][3] != 0:
                return y

def remove_percentage(image, percentage, position):
    width, height = image.size
    sprite_height = detect_first_pixel(image, False) - detect_first_pixel(image)

    pixels_to_remove = sprite_height - int(sprite_height * percentage * (position + 5) / 100) + detect_first_pixel(image)

    pixels_to_remove = max(pixels_to_remove, detect_first_pixel(image))

    new_image = image.crop((0, 0, width, pixels_to_remove))
    return new_image

def process_sprite_data(data, base_image, sprite_dict, used_layer_names, separation_width):
    if 'sprite' in sprite_dict:
        for key in sprite_dict['sprite'].keys():
            for layers in data['spriteData']['layers']:
                if layers['name'] == key:
                    used_layer_names.add(key)
            if key in used_layer_names:
                continue
            

            path = sprite_dict['sprite'][key]
            sprite_range = range(data['spriteData']['base']['multiplier'] + 1)
            
            if path.__class__ == list:
                sprite_range = path[0]
                path = path[1]
                
            for i in sprite_range:
                layer_image = Image.open(path)
                position = (get_position_x(i, separation_width), 0)
                add_layer(base_image, layer_image, position)
                used_layer_names.add(key)

def find_translate(count, separation_width, movData):
    positionY = 0
    positionX = get_position_x(count - 1, separation_width)

    if movData:
        for set in movData:
            if count in set[0]:
                positionX += set[1][0]
                positionY += set[1][1]
    return (positionX, positionY)

def teleportation_effect(image, separation_width, movData):
    width, height = image.size
    #isolate the pixel between separation_width * movData and separation_width * (movData + 1) < width
    maxRange = 0
    opacity = 0.8
    while separation_width * (movData + maxRange) < width:
        maxRange += 1
    for i in range(1, maxRange + 1):
        nDisplaced = maxRange - i + 3
        count = 0
        for y in range(height):
            displacement = random.randint(1, i+1)
            
            if count < nDisplaced:
                for x in range(separation_width * (i - 1), separation_width * i - 10):
                    pixel = image.getpixel((separation_width * movData + x, y))
                    if pixel[3] != 0:
                        moved_pixel = (
                            pixel[0],
                            pixel[1],
                            pixel[2],
                            int(pixel[3] * opacity ** i)
                        )
                        image.putpixel(
                            (separation_width * movData + x - displacement, y),
                            moved_pixel
                        )
                        image.putpixel(
                            (separation_width * movData + x, y),
                            (0, 0, 0, 0)
                        )
            else:
                for x in range(separation_width * i - 10, separation_width * (i - 1), -1):
                    pixel = image.getpixel((separation_width * movData + x, y))
                    if pixel[3] != 0:
                        moved_pixel = (
                            pixel[0],
                            pixel[1],
                            pixel[2],
                            int(pixel[3] * opacity ** i)
                        )
                        image.putpixel(
                            (separation_width * movData + x + displacement, y),
                            moved_pixel
                        )
                        image.putpixel(
                            (separation_width * movData + x, y),
                            (0, 0, 0, 0)
                        )
            count = (count + 1)%(nDisplaced*2)
                
def delete_below_pixels(base_image, layer_image, movData=None, position=None):
    base_image = Image.open(base_image).convert("RGBA")
    width, height = base_image.size
    
    for y in range(height):
        for x in range(width):
            
            posX = x
            posY = y

            if movData:
                for set in movData:
                    if position in set[0]:
                        posX -= set[1][0]
                        posY -= set[1][1]

            if base_image.getpixel((x, y))[3] != 0:
                layer_image.putpixel((posX, posY), (0, 0, 0, 0))

def add_layers_with_positions(data, base_image, layer_path, positions, separation_width, layer_config, percentage=None):
    for i in positions:
        layer_image = Image.open(layer_path)
        position = find_translate(i, separation_width, layer_config.get('movement', None))
        if 'below' in layer_config:
            delete_below_pixels(data['spriteData']['base']['path'], layer_image, layer_config.get('movement', None), i)
        add_layer(base_image, layer_image, position)

    positions_start = layer_config.get('positionsStart', None)

    if positions_start:
        for i in range(positions_start, data['spriteData']['base']['multiplier'] + 1):
            layer_image = Image.open(layer_path)

            if 'remove_from' in layer_config and layer_config['remove_from'] <= i:
                layer_image = remove_percentage(layer_image, percentage, i - 4)

            position = find_translate(i, separation_width, layer_config.get('movement', None))
            if 'below' in layer_config:
                delete_below_pixels(data['spriteData']['base']['path'], layer_image, layer_config.get('movement', None), i)
            add_layer(base_image, layer_image, position)

def handle_layer_addition(base_image, data, separation_width, main, second):
    
    percentage = (1 / (data['spriteData']['base']['multiplier'] + 5)) * 100
    used_layer_names = set()

    for layer_config in data['spriteData']['layers']:
        layer_name = layer_config['name']
        layer_path = layer_config['path']
        main_sprite_override, second_sprite_override = None, None

        if 'sprite' in main:
            main_sprite_override = main['sprite'].get(layer_name)
        if 'sprite' in second:
            second_sprite_override = second['sprite'].get(layer_name)

        if main_sprite_override or second_sprite_override:
            layer_path = main_sprite_override or second_sprite_override or layer_path
            used_layer_names.add(layer_name)

        process_sprite_data(data, base_image, main, used_layer_names, separation_width)
        process_sprite_data(data, base_image, second, used_layer_names, separation_width)

        positions = layer_config.get('positions', [])

        add_layers_with_positions(data, base_image, layer_path, positions, separation_width, layer_config, percentage)

def acquire_modules_data(data):
    modules_data = {'main': {"base":{
        'name': 'BASE'},
    }, 'second': {"base":{
        'name': 'BASE'},
    }}

    for module, module_data in data['modules'].items():
        if module_data['main']:
            modules_data['main'][module] = module_data
        else:
            modules_data['second'][module] = module_data

    return modules_data

def generate_animation_data_pinpoint(xml, name):
    name = name.lower()

    xml += f"""
<animSheet name="modular_focus_{name}_s" w="270" h="65" fw="30" fh="65">modular_weapon/modular_focus_{name}.png</animSheet>
<weaponAnim name="modular_focus_{name}">
	<sheet>modular_focus_{name}_s</sheet>
	<desc length="9" x="0" y="0"/>
	<chargedFrame>1</chargedFrame>
	<fireFrame>2</fireFrame>
	<firePoint  x="18" y="38"/>
	<mountPoint x="5" y="59"/>
	<chargeImage>weapon_focus/modular_focus_{name}_glow.png</chargeImage>
</weaponAnim>
"""

    return xml

def generate_animation_data_bombL(xml, name):
    name = name.lower()

    xml += f"""
<animSheet name="modular_bomb_launcher_{name}_s" w="518" h="65" fw="37" fh="65">modular_weapon/modular_bomb_launcher_{name}.png</animSheet>
<weaponAnim name="modular_bomb_launcher_{name}">
	<sheet>modular_bomb_launcher_{name}_s</sheet>
	<desc length="14" x="0" y="0"/>
	<chargedFrame>1</chargedFrame>
	<fireFrame>11</fireFrame>
	<firePoint  x="22" y="27"/>
	<mountPoint x="6" y="40"/>
	<chargeImage>weapon_bomb/modular_bomb_launcher_{name}_glow.png</chargeImage>
</weaponAnim>
"""

    return xml

def generate_animation_data_bomb(xml, name):
    name = name.lower()

    xml += f"""
<animSheet name="modular_bomb_{name}_s" w="930" h="62" fw="62" fh="62">modular_weapon/modular_bomb_{name}.png</animSheet>
<anim name="modular_bomb_{name}">
	<sheet>modular_bomb_{name}_s</sheet>
	<desc length="15" x="0" y="0"/>
	<time>1.0</time>
</anim>
"""

    return xml

def generate_animation_data_flak(xml, name):
    name = name.lower()

    xml += f"""
<animSheet name="modular_shotgun_{name}_s" w="342" h="53" fw="38" fh="53">modular_weapon/modular_shotgun_{name}.png</animSheet>
<weaponAnim name="modular_shotgun_{name}">
	<sheet>modular_shotgun_{name}_s</sheet>
	<desc length="9" x="0" y="0"/>
	<chargedFrame>1</chargedFrame>
	<fireFrame>4</fireFrame>
	<firePoint  x="17" y="13"/>
	<mountPoint x="4" y="35"/>
	<chargeImage>weapon_focus/modular_shotgun_{name}_glow.png</chargeImage>
</weaponAnim>
"""

    return xml

def generate_glow(data, modules_data, main_module, second_module):
    glow_image_path = next((layer['path'] for layer in data['spriteData']['layers'] if layer['name'] == 'glow'), data['spriteData']['base']['path'])
    glow_image = Image.open(glow_image_path)

    if 'sprite' in modules_data['main'][main_module] and 'glow' in modules_data['main'][main_module]['sprite']:
        glow_image = Image.open(modules_data['main'][main_module]['sprite']['glow'])
    if 'sprite' in modules_data['second'][second_module] and 'glow' in modules_data['second'][second_module]['sprite']:
        glow_image = Image.open(modules_data['second'][second_module]['sprite']['glow'])
    
    glow_image.save(f"output/img/modular_weapon/{data['spriteData']['name']}_{str.lower(modules_data['main'][main_module]['name'])}_{str.lower(modules_data['second'][second_module]['name'])}_glow.png")

animation_data = {
    'pinpoint': generate_animation_data_pinpoint,
    'bomb_launcher': generate_animation_data_bombL,
    'bomb': generate_animation_data_bomb,
    'flak': generate_animation_data_flak
}

def generate(data, animation_xml):
    
    sprite_data = data['spriteData']
    sprite_base = sprite_data['base']

    base_path = sprite_base['path']
    multiplier = sprite_base['multiplier']
    

    base_image, separation_width = multiply_horizontal(base_path, multiplier)

    modules_data = acquire_modules_data(data)

    for main_module in modules_data['main']:
        for second_module in modules_data['second']:

            print(f"{modules_data['main'][main_module]['name']}_{modules_data['second'][second_module]['name']}")
            copy_image = base_image.copy()
            
            handle_layer_addition(copy_image, data, separation_width, modules_data['main'][main_module], modules_data['second'][second_module])
            animation_xml[0] = animation_data[sprite_data['animation']](animation_xml[0], f"{modules_data['main'][main_module]['name']}_{modules_data['second'][second_module]['name']}")

            if 'tpfrom' in sprite_data:
                teleportation_effect(copy_image, separation_width, sprite_data['tpfrom'])

            result_image = copy_image
            result_image.save(f"output/img/modular_weapon/{sprite_data['name']}_{str.lower(modules_data['main'][main_module]['name'])}_{str.lower(modules_data['second'][second_module]['name'])}.png")

            if 'noglow' not in sprite_data:
                generate_glow(data, modules_data, main_module, second_module)
    
    

if __name__ == "__main__":

    animation_xml = [""]
    animation_xml[0] = "<FTL>"

    #with open('generation/json/weapon_pinpoint.json') as json_file:
    #    data = json.load(json_file)
    #generate(data, animation_xml)
#
    #with open('generation/json/weapon_bomb.json') as json_file:
    #    data = json.load(json_file)
    #generate(data, animation_xml)
#
    #with open('generation/json/weapon_bombL.json') as json_file:
    #    data = json.load(json_file)
    #generate(data, animation_xml)

    with open('generation/json/weapon_flak.json') as json_file:
        data = json.load(json_file)
    generate(data, animation_xml)
    
    with open("output/data/animations.xml.append", "w") as xml_file:
        xml_file.write(animation_xml[0] + "</FTL>")
