import gradio as gr
from PIL import Image
import numpy as np
import cv2
from rembg import remove
import io
from datetime import datetime
import os
import utils
from tqdm import tqdm


def display_images(files):
    images = [Image.open(file) for file in files]
    return images


def create_centered_image(image):
    width, height = 2048, 1024
    background = Image.new('RGBA', (width, height), "white")
    x = (width - image.width) // 2
    y = (height - image.height) // 2
    background.paste(image, (x, y), image)

    return background


def remove_background(files, progress=gr.Progress(track_tqdm=True)):
    output_images = []

    for file in progress.tqdm(files):
        image = Image.open(file[0])
        image = remove(image)
        image = create_centered_image(image)
        #import pdb; pdb.set_trace()
        image = utils.crop_and_resize(image)
        output_images.append(image)

    return [output_images, gr.Button(f"Save images")]


def make_save_folder(output_folder='output'):
    now = datetime.now()
    os.makedirs(save_folder := f'{output_folder}/{now.strftime("%Y-%m-%d-%H%M%S")}', exist_ok=True)
    return save_folder


def save_images(inputs):
   save_folder = make_save_folder()
   for i, (img,params) in enumerate(inputs):
       print(params, i)
       img.save(os.path.join(save_folder, f'{i:04d}.png'))
   return f'Saved to "{save_folder}"'


with gr.Blocks(theme='abidlabs/banana') as demo:
    gr.Markdown(
    """
    # img2whiteback
    Start click "Run" bottun below to see how to work. 
    Add any iamges you want to remove background.
    """)
    with gr.Row():
        with gr.Column(scale=1):
            current_file_path = os.path.abspath(__file__)
            current_dir = os.path.dirname(current_file_path)

            sample_list = [f'{current_dir}/sample/sample1.jpg', f'{current_dir}/sample/sample2.jpg', f'{current_dir}/sample/sample3.png']
            input_gallery = gr.Gallery(label="inputs", value=sample_list, interactive=True, columns=[3], rows=[1], object_fit="scale-down", height="auto")
            submit_button = gr.Button('Run')
        with gr.Column(scale=1):
            output_gallery = gr.Gallery(label="outputs", object_fit='contain', columns=[3], preview=False, type='pil', show_download_button=True)
            save_btn = gr.Button('Save')
    
    submit_button.click(
            fn=remove_background,
            inputs=input_gallery,
            outputs=[output_gallery, save_btn]
            )
    save_btn.click(save_images, inputs=[output_gallery], outputs=save_btn)


demo.queue()
demo.launch(server_port=7800)

