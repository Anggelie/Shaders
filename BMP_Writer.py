from PIL import Image

def save_framebuffer_as_image(framebuffer, filename="output.png"):
    height, width, _ = framebuffer.shape
    img = Image.fromarray(framebuffer.astype('uint8'), 'RGB')
    img.save(filename)