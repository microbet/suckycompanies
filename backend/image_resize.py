#! /usr/bin/python

from PIL import Image

image = Image.open('./static/images/museum.jpg')

image.thumbnail((400, 400))

image.save('./static/images/museum.jpg')

print(image.size)
