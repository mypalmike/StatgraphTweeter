#!/usr/bin/env python

from PIL import Image, ImageDraw, ImageFont
from random import choice, Random
import re
import tweepy

RNG = rng = Random()


def rndfloat(low, high):
  delta = high - low
  return low + (RNG.random() * delta)


def rnd_origin(width, height):
  originX = RNG.randint(int(width * 0.05), int(width * 0.95))
  originY = RNG.randint(int(height * 0.05), int(height * 0.95))
  return (originX, originY)


def rnd_bg_color():
  brightness = rndfloat( 0.0, 0.1 )
  red = green = blue = brightness
  return (int(red * 255), int(green*255), int(blue*255))


def rnd_axis_color():
  red = rndfloat( 0.4, 0.6 )
  green = rndfloat( 0.6, 0.9 )
  blue = rndfloat( 0.4, 0.6 )
  return (int(red * 255), int(green*255), int(blue*255))


def rnd_grid_color():
  red = rndfloat( 0.2, 0.4 )
  green = rndfloat( 0.2, 0.4 )
  blue = rndfloat( 0.2, 0.4 )
  return (int(red * 255), int(green*255), int(blue*255))


def rnd_text_color():
  red = 0.0
  green = 0.0
  blue = 0.0
  primary = RNG.randint(0, 3)
  if primary == 0:
    red = rndfloat( 0.9, 1.0 )
  elif primary == 1:
    green = rndfloat( 0.9, 1.0 )
  elif primary == 2:
    blue = rndfloat( 0.9, 1.0 )
  else:
    brightness = rndfloat( 0.9, 1.0 )
    red = brightness
    green = brightness
    blue = brightness
  return (int(red * 255), int(green*255), int(blue*255))


def rnd_line_color():
  red = rndfloat( 0.6, 0.9 )
  green = rndfloat( 0.6, 0.9 )
  blue = rndfloat( 0.6, 0.9 )
  return (int(red * 255), int(green*255), int(blue*255))


def rnd_axis_width():
  return RNG.randint(2,4)


class StatGrapher(object):
  def __init__(self, width, height, words_filename):
    self.width = width
    self.height = height
    self.origin = rnd_origin(width, height)
    self.img = Image.new('RGB', (width, height), rnd_bg_color())
    self.draw = ImageDraw.Draw(self.img)
    self.axis_color = rnd_axis_color()
    self.axis_width = rnd_axis_width()
    self.grid_color = rnd_grid_color()
    self.text_color = rnd_text_color()
    self.load_words(words_filename)
    self.generate_text()
    self.load_fonts()

  def load_words(self, filename):
    self.words = [[], [], [], []]
    section_re = re.compile('^\*([0-9]+)\*$')
    index = 0
    with open(filename, 'r') as f_in:
      for line in f_in:
        line = line.strip()
        match = section_re.match(line)
        if match:
          index = int(match.group(1)) - 1
        else:
          self.words[index].append(line)

  def load_fonts(self):
    self.fonts = []
    for font_size in [36, 24, 16, 12]:
      self.fonts.append(ImageFont.truetype('./Verdana.ttf', font_size))

  def generate_text(self):
    do_parens = (RNG.random() > 0.8)
    if do_parens:
      self.text = '{} {} {} {}'.format(
          choice(self.words[0]),
          choice(self.words[1]),
          choice(self.words[2]),
          choice(self.words[3]),
      )
    else:
      self.text = '{} {} {}'.format(
          choice(self.words[0]),
          choice(self.words[1]),
          choice(self.words[2]),
      )

  def random_line(self):
    centerX = rndfloat(self.width * 0.3, self.width * 0.7)
    centerY = rndfloat(self.height * 0.3, self.height * 0.7)
    slope = rndfloat(0.3, 1.5)
    if RNG.randint(0, 1):
      slope = -slope
    x0 = 0.0
    x1 = self.width
    deltaX = x1 - centerX
    deltaY = deltaX * slope
    y1 = centerY + deltaY
    deltaX = centerX - x0
    deltaY = deltaX * slope
    y0 = centerY - deltaY
    self.draw.line(
        (x0, y0, x1, y1),
        fill=rnd_line_color())

  def random_parabola(self):
    sign = 1
    if RNG.randint(0, 1):
      sign = -1
    a = rndfloat(0.1 / self.height, 50.0 / self.height) * sign
    h = rndfloat(self.width * 0.2, self.width * 0.8)
    k = rndfloat(self.height * 0.1, self.height * 0.9)

    points = []
    for x in range(-20, self.width + 20, 5):
      points.append((float(x), float(a * (x - h) * (x - h) + k)))
    self.draw.line(
        points,
        fill=rnd_line_color())

  def random_bend(self):
    focus = (rndfloat(0.1 * self.width, 0.9 * self.width),
        rndfloat(0.1 * self.height, 0.9 * self.height))

    rect = [0.0, 0.0, self.width, self.height]

    x_scale = rndfloat(2.0, 3.0)
    y_scale = rndfloat(2.0, 3.0)

    rect[0] *= x_scale
    rect[2] *= x_scale

    rect[1] *= y_scale
    rect[3] *= y_scale

    if focus[0] < 0.5 * self.width:
      rect[0] = focus[0]
      rect[2] = focus[0] + rect[2]
    else:
      rect[0] = focus[0] - rect[2]
      rect[2] = focus[0]

    if focus[1] < 0.5 * self.height:
      rect[1] = focus[1]
      rect[3] = focus[1] + rect[3]
    else:
      rect[1] = focus[1] - rect[3]
      rect[3] = focus[1]

    self.draw.ellipse(rect, outline=rnd_line_color())

  def render_text(self):
    for font in self.fonts:
      text_width, _ = self.draw.textsize(self.text, font=font)
      if text_width < 0.9 * self.width:
        break

    x = 0.5 * (self.width - text_width)
    y = self.height * rndfloat(0.1, 0.3)
    if RNG.randint(0, 1):
      y = self.height - y

    self.draw.text((x, y), self.text, font=font, fill=self.text_color)

  def text_secondary(self):
    pass

  def x_axis(self):
    originY = self.origin[1]
    self.draw.line(
        (0, originY, self.width, originY),
        fill=self.axis_color,
        width=self.axis_width)

  def y_axis(self):
    originX = self.origin[0]
    self.draw.line(
        (originX, 0, originX, self.height),
        fill=self.axis_color,
        width=self.axis_width)

  def verticals(self):
    originX = self.origin[0]
    logScale =  rndfloat(1.0, 1.25)
    initialLineDist = rndfloat(self.height / 40.0, self.height / 25.0)

    lineDist = initialLineDist
    x = originX - lineDist
    while( x > 0.0 ):
      lineDist *= logScale
      self.draw.line(
          (x, 0, x, self.height),
          fill=self.grid_color)
      x -= lineDist

    lineDist = initialLineDist
    x = originX + lineDist
    while( x < self.width ):
      lineDist *= logScale
      self.draw.line(
          (x, 0, x, self.height),
          fill=self.grid_color)
      x += lineDist

  def horizontals(self):
    originY = self.origin[1]
    logScale =  rndfloat(1.0, 1.25)
    initialLineDist = rndfloat(self.height / 40.0, self.height / 25.0)

    lineDist = initialLineDist
    y = originY - lineDist
    while( y > 0.0 ):
      lineDist *= logScale
      self.draw.line(
          (0, y, self.width, y),
          fill=self.grid_color)
      y -= lineDist

    lineDist = initialLineDist
    y = originY + lineDist
    while( y < self.height ):
      lineDist *= logScale
      self.draw.line(
          (0, y, self.width, y),
          fill=self.grid_color)
      y += lineDist

  def render(self):
    self.x_axis()
    self.y_axis()
    self.verticals()
    self.horizontals()
    n_parabolas = RNG.randint(0,2)
    n_bends = 2 # RNG.randint(0,2)
    n_lines = RNG.randint(0,3)
    if n_parabolas + n_bends + n_lines == 0:
      n_lines = RNG.randint(2,4)
    for _ in range(n_parabolas):
      self.random_parabola()
    for _ in range(n_bends):
      self.random_bend()
    for _ in range(n_lines):
      self.random_line()
    self.render_text()

  def save(self, filename):
    self.img.save(filename, 'PNG')


def get_creds():
  with open("creds", "r") as f:
    return [line.strip() for line in f]


def get_auth_api():
  consumer_key, consumer_secret, access_key, access_secret = get_creds()
  auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
  auth.secure = True
  auth.set_access_token(access_key, access_secret)
  return [auth, tweepy.API(auth)]


def tweet(sg):
  # auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
  # auth.secure = True
  # auth.set_access_token(access_key, access_secret)
  # # access the Twitter API using tweepy with OAuth
  # api = tweepy.API(auth)

  auth, api = get_auth_api()
  #getting the parameter passed via the shell command from the Arduino Sketch
  # filename = os.path.abspath('/mnt/sda1/moneyplant.png')
  #UpdateStatus of twitter called with the image file
  api.update_with_media('random_graph.png', status=sg.text[:139])


def main():
  # Twitter max image size is currently 506 x 506 pixels
  if RNG.random() > 0.9:
    # Boring words.
    sg = StatGrapher(506, 284, 'words.txt')
  else:
    # Funny words.
    sg = StatGrapher(506, 284, 'words.txt')
  sg.render()
  sg.save('random_graph.png')

  tweet(sg)


if __name__ == '__main__':
  main()
