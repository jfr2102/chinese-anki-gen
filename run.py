import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import os
import whisper
import shutil
from deep_translator import GoogleTranslator
import pinyin
import genanki
import random

def formatSound(file_name:str):
    return f"[sound:{file_name}]"

def formatGif(file_name:str):
    return f'<img src="{file_name}">'

def formatStrokeOrder(file_names:list[str]):
    gifs = ""
    for file_name in file_names:
        gifs += formatGif(file_name)
    return gifs

def getDeck(description:str):
    return  genanki.Deck(random.randint(1000000000, 9999999999), description)

def getModel():
    return genanki.Model(
      random.randint(1000000000, 9999999999),
      'Simple Model',
      fields=[
        {'name': 'Question'},
        {'name': 'Answer'},
        {'name': 'Pinyin'},
        {'name': 'Gif'},
        {'name': 'Mp3'},
      ],
      templates=[
        {
          'name': 'Card 1',
          'qfmt': '{{Question}}',
          'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}</hr> <p>{{Pinyin}}</p> <br> {{Gif}} <br> {{Mp3}}',
        },
      ])

overwrite_char = {}
overwrite_pinyin = {}
overwrite_translate = {}
CHAPTER = "U02-L02"

my_deck = getDeck(CHAPTER)

#output dir
os.makedirs(CHAPTER, exist_ok = True)

summary = ""

model = whisper.load_model("medium")
translator = GoogleTranslator(source='zh-CN', target='en')

#iterate files in input dir
directory = os.fsencode("input")
media_files = []
media_file_names = []

for index, file in enumerate(sorted(os.listdir(directory))):
    filename = os.fsdecode(directory) + os.sep + os.fsdecode(file)
    
    word: str = overwrite_char.get(filename) or model.transcribe(filename, language="zh", initial_prompt="这是简体中文请使用简体中文").get("text")

    word = word.replace(" ", "")

    word_translated = overwrite_translate.get(filename) or translator.translate(word)
    word_pinyin = overwrite_pinyin.get(filename) or pinyin.get(word)

    summary += ("FILE: "+ filename +  " TEXT:" + word + " TRANSLATION: " + word_translated + " PINYIN: "+ word_pinyin + " \n ")

    audio_file_name = f"{word}.mp3"
    dest_audio = os.path.join(CHAPTER, audio_file_name)
    shutil.copyfile(filename, dest_audio)
    media_files.append(dest_audio)
    gif_files = []

    

    for char in word:
        query = urllib.parse.urlencode({'q': char})
        
        try:
            fp = urllib.request.urlopen(f"http://www.strokeorder.info/mandarin.php?{query}")
            mybytes = fp.read()
            mystr = mybytes.decode("utf8")
            fp.close()

            soup = BeautifulSoup(mystr, 'html.parser')
            gif_source = soup.css.select_one('img[src*=".gif"]').attrs.get("src")

            gif_file_name = f"{word}-{char}.gif"
            gif_dest = os.path.join(CHAPTER, gif_file_name) 

            urllib.request.urlretrieve(gif_source, gif_dest)

            gif_files.append(gif_file_name)
            media_files.append(gif_dest)
        except Exception: 
            print(summary)
            print (f"Failed to rertrieve for {char} in {filename} {word}")

    my_note = genanki.Note(
    model=getModel(),
    fields=[word_translated, word, word_pinyin, formatStrokeOrder(gif_files) , formatSound(audio_file_name)])

    my_deck.add_note(my_note)

print(summary)
my_package = genanki.Package(my_deck)

#unique files
my_package.media_files = list(dict.fromkeys(media_files))
my_package.write_to_file(f"{CHAPTER}/{CHAPTER}.apkg")
