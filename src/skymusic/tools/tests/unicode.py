import os, sys
this_dir = os.path.join(os.path.dirname(__file__))
SRC_ROOT = os.path.normpath(os.path.join(this_dir, '../../../'))
sys.path.append(SRC_ROOT)

import unicodedata
from PIL import Image, ImageDraw, ImageFont
from skymusic import Lang
from skymusic.resources import Resources


langs = {
    'ko': u'ᄀᄂᄃᄅᄆᄇᄉᄋᄌᄎᄏᄐᄑ하ᅣᅥᅧᅩᅭᅮᅲᅳᅵ',
    'ru': u'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ',
    'vi': u'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZàáảãạăắằẳẵặâấầẩẫậđèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵ',
    'th': u'กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรลวศษสหฬอฮ',
    'pl': u'aąbcćdeęfghijklłmnńoóprsśtuwyzźżAĄBCĆDEĘFGHIJKLŁMNŃOÓPRSŚTUWYZŹŻ',
    'he': u'אבגדהוזחטיכךלמםנןסעפףצץקרשת' ,
    'ja': u'あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんアイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン',
}

redherrings = ['COMBINING']
#fnt = ImageFont.truetype('../resources/fonts/NotoSans-Bold.ttf', 14)

for lang, chars in langs.items():
    
    oldnm=''
    for char in chars:
        if int(ord(char)) >=400:
            nm = unicodedata.name(char).upper()
            if nm != oldnm:
                matches = [red in nm for red in redherrings]
                if True not in matches: oldnm = nm
    print('\n'+lang+': '+oldnm)

    fnt_name = Resources.FONTS.get(lang, list(Resources.FONTS)[0])
    print(fnt_name)
    fnt_path = os.path.join(SRC_ROOT,'skymusic/resources/fonts',fnt_name)
    fnt = ImageFont.truetype(fnt_path, 14)
    w,h = fnt.getsize(chars)
    img = Image.new('RGB', (w,h), color=(255,255,255))
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), chars, font=fnt, fill=(0,0,0))
    img.show()

