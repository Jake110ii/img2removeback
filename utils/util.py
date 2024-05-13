from PIL import Image
import numpy as np
import cv2


class Imgcrop():
    def __init__(self, size):
        self.width = int(size.split('x')[0])
        self.height = int(size.split('x')[1])

    
    @classmethod
    def create_centered_image(self, image):
        width, height = 2048*2, 1024*2
        background = Image.new('RGBA', (width, height), "white")
        x = (width - image.width) // 2
        y = (height - image.height) // 2
        background.paste(image, (x, y), image)
        return background

    
    @classmethod
    def resize_image(self, image):
        if image.width > 2048:
            aspect_ratio = image.width / image.height
            new_width = 2048
            new_height = int(new_width / aspect_ratio)
            image = image.resize((new_width, new_height), Image.ANTIALIAS)

        return image


    def pil2cv(self, pil_image):
        image_np = np.array(pil_image)
        image_cv = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        return image_cv


    def find_other_from_white(self, pil_image):
        image = self.pil2cv(pil_image)
        non_white_pixels = np.where(np.all(image != [255, 255, 255], axis=-1))
        return np.column_stack(non_white_pixels)


    def cut_white(self, pil_image, x1, x2):
        image = pil_image
        cropped_image = image.crop(image.getbbox())
        cropped_image = image.crop((x1[0], x1[1], x2[0], x2[1]))
        return cropped_image


    def resize(self, pil_image):
        width = self.width
        height = self.height
        image = pil_image
        new_size = (width, height)
        cropped_image = image.resize(new_size)
        return cropped_image


    def crop_and_resize(self, pil_image, size):
        black_pixels = self.find_other_from_white(pil_image)
        
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
        
        if self.width == self.height:
            division_num = 2
        else:
            division_num = 4
            
        x1[1] = int(center_y - length/division_num)
        x2[1] = int(center_y + length/division_num)
        pil_image = self.cut_white(pil_image, x1, x2)
        pil_image = self.resize(pil_image)

        return pil_image
