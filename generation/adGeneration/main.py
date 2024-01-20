from PIL import Image
import os

def process_images(input_folder, output_folder):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Dictionary to store images based on category
    size = {"shotgun": (38, 53), "bombL": (37, 65), "bomb": (62, 62), "focus": (30, 65)}
    image_dict = {"shotgun": [], "bombL": [], "bomb": [], "focus": []}
    spotmain = {"base": 1, "power": 2, "hull": 3, "fire": 4, "accuracy": 5}
    spot = {"base": 1, "bio": 2, "cooldown": 3, "pierce": 4, "stun": 5, "lockdown": 6}

    # Create a canvas to arrange images
    canvas_width = 0
    canvas_height = 0

    # Iterate through all files in the input folder
    for filename in os.listdir(input_folder):
        if not filename.endswith("glow.png"):
            # Extract information from the filename
            parts = os.path.splitext(filename)[0].split("_")

            if len(parts) >= 4:
                category = parts[1]
                if category == "bomb" and parts[2] == "launcher":
                    category = "bombL"
                    parts[2] = parts[3]
                    parts[3] = parts[4]
                row = int(spotmain[parts[2]])
                col = int(spot[parts[3]])
                print(category)

                # Open the image using Pillow
                img = Image.open(os.path.join(input_folder, filename))

                # Convert the image to RGBA and set the background to be transparent
                img = img.convert("RGBA")
                data = img.getdata()
                new_data = []
                for item in data:
                        new_data.append(item)
                img.putdata(new_data)

                if category == "bomb":
                    img = img.crop((0, 0, size[category][0], size[category][1]))
                else:
                    img = img.crop((size[category][0], 0, size[category][0] * 2, size[category][1]))

                # Append the image to the corresponding category
                image_dict[category].append((img, col, row, category))
                canvas_width = max(canvas_width, col * size[category][0])
                canvas_height = max(canvas_height, row * size[category][1]) + 2
    # Place images on the canvas and create collage
    for category, images in image_dict.items():
        canvas = Image.new('RGBA', (canvas_width, canvas_height), (0, 0, 0, 0))  # Transparent background
        for img, col, row, weapon_type in images:
            # Calculate position on the canvas
            x = (col - 1) * (size[weapon_type][0] - 14)
            y = (row - 1) * (size[weapon_type][1] + 10)

            # Paste the image on the canvas
            canvas.paste(img, (x, y), img)

        # Save the collage
        canvas.save(os.path.join(output_folder, 'output_collage_'+category+'.png'))

if __name__ == "__main__":
    input_folder = "output/img/modular_weapon"
    output_folder = "out"

    process_images(input_folder, output_folder)
