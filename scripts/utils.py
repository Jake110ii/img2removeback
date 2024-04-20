from PIL import Image
import numpy as np
import cv2


def pil2cv(pil_image):
    image_np = np.array(pil_image)
    image_cv = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
    return image_cv


def find_other_from_white(pil_image):
    image = pil2cv(pil_image)
    non_white_pixels = np.where(np.all(image != [255, 255, 255], axis=-1))
    return np.column_stack(non_white_pixels)


def cut_white(pil_image, x1, x2):
    image = pil_image
    cropped_image = image.crop(image.getbbox())
    cropped_image = image.crop((x1[0], x1[1], x2[0], x2[1]))
    return cropped_image


def resize(pil_image):
    image = pil_image
    new_size = (1024, 512)
    cropped_image = image.resize(new_size)
    return cropped_image


def add_white_back(pil_image):
    img = pil_image.convert("RGBA")
    background = Image.new('RGBA', img.size, "WHITE")
    background.paste(img, (0, 0), img)
    return background.convert("RGB")


def crop_and_resize(pil_image):
    pil_image = add_white_back(pil_image)
    black_pixels = find_other_from_white(pil_image)

    x1 = [np.array(black_pixels)[:, 1].min(), np.array(black_pixels)[:, 0].min()]
    x2 = [np.array(black_pixels)[:, 1].max(), np.array(black_pixels)[:, 0].max()]

    length = x2[0] - x1[0]
    eps = length * 0.01
    x1 = [x1[0]-eps, x1[1]]
    x2 = [x2[0]+eps, x2[1]]
    length = x2[0] - x1[0]
    x1[0] = int(x1[0])-1
    x2[0] = int(x2[0])
    center_y = (x2[1]+x1[1])/2
    x1[1] = int(center_y - length/4)
    x2[1] = int(center_y + length/4)
    pil_image = cut_white(pil_image, x1, x2)
    pil_image = resize(pil_image)
    pil_image = add_white_back(pil_image)    

    return pil_image
