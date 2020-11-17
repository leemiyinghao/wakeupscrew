from MariaModel import Media, Tag
from peewee import *

if __name__ == '__main__':
    print(list(Media.select(Media.id).order_by(fn.Rand()).limit(5).dicts()))