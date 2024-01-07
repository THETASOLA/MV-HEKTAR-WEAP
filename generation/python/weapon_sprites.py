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
    height_top = height - detect_first_pixel(image, True)
    pixels_to_remove = detect_first_pixel(image, False) - int(height_top * percentage * position / 100)

    pixels_to_remove = max(pixels_to_remove, detect_first_pixel(image, True))

    new_image = image.crop((0, 0, width, pixels_to_remove))
    return new_image

def handle_layer_addition(base_image, data, separation_width, main, second):
    percentage = (1 / (data['spriteData']['base']['multiplier'] + 1)) * 100
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
            # Use the sprite-specific override if available
            layer_path = main_sprite_override or second_sprite_override or layer_path
            used_layer_names.add(layer_name)

        if 'sprite' in main:
            for key in main['sprite'].keys():
                if key in used_layer_names:
                    continue

                main_path = main['sprite'][key]
                for i in range(data['spriteData']['base']['multiplier'] + 1):
                    layer_image = Image.open(main_path)
                    position = (get_position_x(i, separation_width), 0)
                    add_layer(base_image, layer_image, position)
        
        
        if 'sprite' in second:
            for key in second['sprite'].keys():
                if key in used_layer_names:
                    continue
                
                second_path = second['sprite'][key]
                for i in range(data['spriteData']['base']['multiplier'] + 1):
                    layer_image = Image.open(second_path)
                    position = (get_position_x(i, separation_width), 0)
                    add_layer(base_image, layer_image, position)

        positions = layer_config.get('positions', [])
        positions_start = layer_config.get('positionsStart', None)

        for i in positions:
            layer_image = Image.open(layer_path)
            position = (get_position_x(i-1, separation_width), 0)
            add_layer(base_image, layer_image, position)

        if positions_start:
            for i in range(positions_start, data['spriteData']['base']['multiplier'] + 1):
                layer_image = Image.open(layer_path)
                if 'remove_from' in layer_config and layer_config['remove_from'] <= i:
                    layer_image = remove_percentage(layer_image, percentage, i - 4)
                position = (get_position_x(i-1, separation_width), 0)
                add_layer(base_image, layer_image, position)

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

def main():
    with open('generation/json/weapon_pinpoint.json') as json_file:
        data = json.load(json_file)
    
    sprite_data = data['spriteData']
    sprite_base = sprite_data['base']

    base_path = sprite_base['path']
    multiplier = sprite_base['multiplier']

    base_image, separation_width = multiply_horizontal(base_path, multiplier)

    modules_data = acquire_modules_data(data)

    for main_module in modules_data['main']:
        for second_module in modules_data['second']:
            copy_image = base_image.copy()
            print(f"{modules_data['main'][main_module]['name']}_{modules_data['second'][second_module]['name']}")
            handle_layer_addition(copy_image, data, separation_width, modules_data['main'][main_module], modules_data['second'][second_module])

            result_image = copy_image
            #result_image.show()
            result_image.save(f"output/img/sprite_{str.lower(modules_data['main'][main_module]['name'])}_{str.lower(modules_data['second'][second_module]['name'])}.png")

if __name__ == "__main__":
    main()
