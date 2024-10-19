from sentence_transformers import SentenceTransformer
from scipy import spatial
from PIL import Image
from transformers import pipeline
from PIL import ImageDraw
from io import BytesIO
import base64
import openai
from dotenv import load_dotenv
import os

load_dotenv()
dataset_dir = "dataset"

def find_top_k_similar_images_by_text(description, k=3):
    model = SentenceTransformer('clip-ViT-B-32')
    text_embedding = model.encode(description)
    distances = []

    model = SentenceTransformer('clip-ViT-B-32')

    for image_name in os.listdir(dataset_dir):
        image_path = os.path.join(dataset_dir, image_name)
        image = Image.open(image_path)
        image_embedding = model.encode(image)
        similarity = spatial.distance.euclidean(text_embedding, image_embedding)
        distances.append((image_path, similarity))

    # Sort by similarity in descending order
    distances.sort(key=lambda x: x[1])

    # Get the top k similar images
    top_k_images = [name for name, _ in distances[:k]]
    return top_k_images

# TODO: Part 2
def classify_animal(image_path, labels):
    ...


def detect_object(image_path, description):
    """
    Detect an object in an image based on a given description.

    This function uses a pre-trained zero-shot object detection model to identify
    an object in the image that matches the provided description.

    Args:
        image_path (str): The path to the image file to be analyzed.
        description (str): A textual description of the object to detect.

    Returns:
        dict or None: If an object matching the description is found, returns a dictionary
        containing the detection details (box coordinates, label, and confidence score).
        If no matching object is found, returns None.

    Note:
        This function uses the google/owlv2-base-patch16-ensemble model for zero-shot
        object detection. The accuracy of detection may vary based on the clarity of
        the image and the specificity of the description.
    """
    checkpoint = "google/owlv2-base-patch16-ensemble"
    detector = pipeline(model=checkpoint, task="zero-shot-object-detection")
    image = Image.open(f"{image_path}")
    detected_objects = detector(image, candidate_labels=[description])

    if detected_objects:
        return detected_objects[0]
    return None

def draw_detected_object(image_path, detected_object):
    """
    Draw a bounding box and label on an image for a detected object.

    This function takes an image and information about a detected object,
    then draws a red bounding box around the object and labels it with
    its name and detection confidence score.

    Args:
        image_path (str): The path to the image file.
        detected_object (dict): A dictionary containing information about the detected object.
            It should have the following keys:
            - 'box': A dictionary with 'xmin', 'ymin', 'xmax', 'ymax' coordinates.
            - 'label': The label of the detected object.
            - 'score': The confidence score of the detection.

    Returns:
        None: The function modifies the image in-place and displays it.

    Note:
        This function uses the PIL library to draw on the image and display it.
        The bounding box is drawn in red, and the label is written in white.
    """
    image = Image.open(f"{image_path}")
    draw = ImageDraw.Draw(image)
    box = detected_object["box"]
    label = detected_object["label"]
    score = detected_object["score"]

    xmin, ymin, xmax, ymax = box.values()
    draw.rectangle((xmin, ymin, xmax, ymax), outline="red", width=1)
    draw.text((xmin, ymin), f"{label}: {round(score,2)}", fill="white")
    image.show()

def extract_object_mask(image_path, detected_object):
    """
    Extract a mask for a detected object in an image.

    This function creates a mask image where the detected object is transparent
    and the rest of the image is opaque.

    Args:
        image_path (str): The path to the original image file.
        detected_object (dict): A dictionary containing information about the detected object.
            It should have a 'box' key with 'xmin', 'ymin', 'xmax', 'ymax' coordinates.

    Returns:
        str: The file path of the saved mask image.

    Note:
        This function uses the PIL library to process the image.
        The resulting mask is saved as a PNG file named 'mask.png'.
        The mask is also displayed using the show() method.
    """
    image = Image.open(f"{image_path}")
    box = detected_object["box"]

    xmin, ymin, xmax, ymax = box.values()
    dimx, dimy = image.size

    mask_image = image.convert("RGBA")
    for y in range(dimy):
        for x in range(dimx):
            if xmin <= x < xmax and ymin <= y < ymax:
                r, g, b, a = mask_image.getpixel((x, y))
                mask_image.putpixel((x, y), (r, g, b, 0))
    
    mask_image.show()
    output_file = f"mask.png"
    mask_image.save(output_file)
    return output_file

def edit_image( original_image_path, mask_image_path, description):
    """
    Edit an image using OpenAI's DALL-E 2 model.

    This function takes an original image, a mask image, and a description to edit
    the original image based on the mask and the provided description.

    Args:
        original_image_path (str): The file path of the original image to be edited.
        mask_image_path (str): The file path of the mask image, where transparent areas
                               indicate regions to be edited.
        description (str): A text description of the desired edit to be applied to the image.

    Returns:
        str: The file path of the edited image saved as 'edited_image.png'.

    Note:
        This function uses the OpenAI API to perform the image edit.
        The edited image is displayed using the show() method and saved as a PNG file.
        The function requires the 'openai' library and appropriate API credentials.
    """
    client = openai.OpenAI()
    response = client.images.edit(
        model="dall-e-2",
        image=open(f"{original_image_path}", "rb"),
        mask=open(mask_image_path, "rb"),
        prompt=description,
        n=1,
        size="512x512",
        response_format="b64_json"
    )

    image_json = response.data[0].b64_json
    image_data = base64.b64decode(image_json)
    image = Image.open(BytesIO(image_data))
    image.show()
    output_file = f"edited_image.png"
    image.save(output_file)
    return output_file

if __name__ == "__main__":

    # Part 1: Find top k similar images by text
    top_k_images = find_top_k_similar_images_by_text("a cat reading a book", k=1)
    print(top_k_images)

    # Part 2: Classify animal

    # labels = ["cow", "horse", "sheep", "chicken", "goat", "pig"]
    # animal_label = classify_animal("original_image.png", labels)
    # print(animal_label)

    # Part 3: Detect object (demo)
    # image_path = "original_image.png"
    # detected_object = detect_object(image_path, "horse")
    # if detected_object:
    #     draw_detected_object(image_path, detected_object)
    #     # extract_object_mask(image_path, detected_object)
