from PIL import Image, ImageDraw
import json

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

def add_layers_with_positions(data, base_image, layer_path, positions, separation_width, layer_config, percentage=None):
    for i in positions:
        layer_image = Image.open(layer_path)
        position = (get_position_x(i - 1, separation_width), 0)
        add_layer(base_image, layer_image, position)

    positions_start = layer_config.get('positionsStart', None)
    if positions_start:
        for i in range(positions_start, data['spriteData']['base']['multiplier'] + 1):
            layer_image = Image.open(layer_path)

            if 'remove_from' in layer_config and layer_config['remove_from'] <= i:
                layer_image = remove_percentage(layer_image, percentage, i - 4)

            position = (get_position_x(i - 1, separation_width), 0)
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

def generate_animation_data(xml, name):
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

def generate_glow(data, modules_data, main_module, second_module):
    glow_image_path = next((layer['path'] for layer in data['spriteData']['layers'] if layer['name'] == 'glow'), data['spriteData']['base']['path'])
    glow_image = Image.open(glow_image_path)

    if 'sprite' in modules_data['main'][main_module] and 'glow' in modules_data['main'][main_module]['sprite']:
        glow_image = Image.open(modules_data['main'][main_module]['sprite']['glow'])
    if 'sprite' in modules_data['second'][second_module] and 'glow' in modules_data['second'][second_module]['sprite']:
        glow_image = Image.open(modules_data['second'][second_module]['sprite']['glow'])
    
    glow_image.save(f"output/img/modular_weapon/modular_focus_{str.lower(modules_data['main'][main_module]['name'])}_{str.lower(modules_data['second'][second_module]['name'])}_glow.png")

def main():
    with open('generation/json/weapon_pinpoint.json') as json_file:
        data = json.load(json_file)
    
    sprite_data = data['spriteData']
    sprite_base = sprite_data['base']

    base_path = sprite_base['path']
    multiplier = sprite_base['multiplier']
    animation_xml = "<FTL>"

    base_image, separation_width = multiply_horizontal(base_path, multiplier)

    modules_data = acquire_modules_data(data)

    for main_module in modules_data['main']:
        for second_module in modules_data['second']:

            print(f"{modules_data['main'][main_module]['name']}_{modules_data['second'][second_module]['name']}")
            copy_image = base_image.copy()
            
            handle_layer_addition(copy_image, data, separation_width, modules_data['main'][main_module], modules_data['second'][second_module])
            animation_xml = generate_animation_data(animation_xml, f"{modules_data['main'][main_module]['name']}_{modules_data['second'][second_module]['name']}")

            result_image = copy_image
            result_image.save(f"output/img/modular_weapon/modular_focus_{str.lower(modules_data['main'][main_module]['name'])}_{str.lower(modules_data['second'][second_module]['name'])}.png")

            generate_glow(data, modules_data, main_module, second_module)
    
    with open("output/data/animations.xml.append", "w") as xml_file:
        xml_file.write(animation_xml + "</FTL>")

if __name__ == "__main__":
    main()
