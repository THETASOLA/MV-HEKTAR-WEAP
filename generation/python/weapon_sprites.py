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

def add_layer(image, layer_path, position):
    layer_image = Image.open(layer_path)
    image.alpha_composite(layer_image, position)

def remove_percentage(image, percentage):
    width, height = image.size
    pixels_to_remove = int(height * percentage / 100)

    new_image = image.crop((0, 0, width, height - pixels_to_remove))
    return new_image

def main():
    with open('generation/json/sprites_pinpoint.json') as json_file:
        data = json.load(json_file)

    base_path = data['base']['path']
    multiplier = data['base']['multiplier']

    base_image, separation_width = multiply_horizontal(base_path, multiplier)

    for layer_config in data['layers']:
        layer_path = layer_config['path']
        for i in layer_config['positions']:
            position = (get_position_x(i-1, separation_width), 0)
            add_layer(base_image, layer_path, position)

    result_image = base_image

    result_image.show()
    result_image.save('output/img/result.png')

if __name__ == "__main__":
    main()
