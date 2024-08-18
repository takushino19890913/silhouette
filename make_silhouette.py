from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import numpy as np

def create_black_silhouette_with_text(image_path, upper_text, bottom_text, output_path):
    # Load the image
    image = Image.open(image_path).convert("RGBA")

    # Load a font
    font_path = "/mnt/data/Kaisotai-Next-UP-B.ttf"  # MacOS用のフォントパス
    font_size = 40
    font = ImageFont.truetype(font_path, font_size)

    # Calculate text sizes
    draw = ImageDraw.Draw(image)
    upper_text_bbox = draw.textbbox((0, 0), upper_text, font=font)
    bottom_text_bbox = draw.textbbox((0, 0), bottom_text, font=font)
    upper_text_height = upper_text_bbox[3] - upper_text_bbox[1]
    bottom_text_height = bottom_text_bbox[3] - bottom_text_bbox[1]

    # Calculate new image size
    width, height = image.size
    new_height = height + upper_text_height + bottom_text_height + 20  # 20 is for padding

    # Create a new image with the new size and a transparent background
    new_image = Image.new("RGBA", (width, new_height), (0, 0, 0, 0))

    # Paste the original image in the center of the new image
    paste_position = (0, upper_text_height + 10)  # 10 is for padding
    new_image.paste(image, paste_position)

    # Create black silhouette
    datas = new_image.getdata()
    new_data = []
    for item in datas:
        if item[3] > 0:
            new_data.append((0, 0, 0, 255))
        else:
            new_data.append((0, 0, 0, 0))
    new_image.putdata(new_data)

    # Draw text on the image
    draw = ImageDraw.Draw(new_image)

    # Calculate text positions
    upper_text_position = ((width - (upper_text_bbox[2] - upper_text_bbox[0])) // 2, 5)
    bottom_text_position = ((width - (bottom_text_bbox[2] - bottom_text_bbox[0])) // 2, new_height - bottom_text_height - 5)

    # Draw the text on the image
    draw.text(upper_text_position, upper_text, font=font, fill=(255, 255, 255, 255))
    draw.text(bottom_text_position, bottom_text, font=font, fill=(255, 255, 255, 255))

    # Save the new silhouette image with text
    new_image.save(output_path)
    
    # Display the image directly in the chat




def show_image(image_path):
    # Open the image file
    with Image.open(image_path) as img:
        # Convert image to numpy array
        img_array = np.array(img)
        
        # Get the size of the image
        height, width = img_array.shape[:2]

        # Adjust the size for display, assuming 165 dpi
        fig_width, fig_height = width / 165, height / 165

        # Create a figure with a size that matches the image
        fig, ax = plt.subplots(figsize=(fig_width, fig_height), facecolor='darkgray')

        # Adjust padding
        plt.subplots_adjust(top=1, bottom=0, left=0, right=1)

        # Create a dark gray background
        background = np.ones((height, width, 3), dtype=np.uint8) * 64  # Dark gray color

        # If the image has an alpha channel
        if img_array.shape[2] == 4:
            # Extract RGB and alpha channels
            rgb = img_array[:,:,:3]
            alpha = img_array[:,:,3]

            # Create a mask
            mask = alpha[:,:,np.newaxis] / 255.0

            # Blend the image with the background
            blended = rgb * mask + background * (1 - mask)
        else:
            blended = img_array

        # Display the image
        ax.imshow(blended.astype(np.uint8))
        ax.axis('off')  # Hide the axis

        # Display the image
        plt.show()