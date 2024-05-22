# chinese-anki-gen

Generate Anki Deck from chinese audio files.
You can split audio files by words e.g. with [mp3split](https://wiki.ubuntuusers.de/mp3splt/)

e.g. 
```sh
mp3splt -s -d $targetDir -p th=-54,shots=10 $FileName
```

Make manual overwrites where needed to either the chinese character, pinyin, or translation by setting the overwrite dicitionary with the file name for which you want to override as key. 

```python
# use these chinese chars instead of the result from text2speech model
overwrite_char = {
    "input/file_1.mp3" : "日本",
    "input/file_2.mp3" : "人",
}
```