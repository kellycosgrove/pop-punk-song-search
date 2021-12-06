# import libraries
from lyricsgenius import Genius
#https://lyricsgenius.readthedocs.io/en/master/
from gensim import corpora, models, similarities, downloader, utils
import json
import tempfile
import csv

# define vars
token = 'tiWxIWPADF87dXvHZXGNJDe432jqB1yRQBjFsvQAKlbU2HHoZGAZLrrvwjwasXOM'
# token for Genius API
#art_list = ['Hands Like Houses', 'The Bouncing Souls', 'Millencolin', 'Evanescence', 'Fountains Of Wayne',
#            'AFI', 'Yours Truly', 'A Day To Remember', 'Mayday Parade', 'New Found Glory', 'Relient K',
#            'The Red Jumpsuit Apparatus', 'Redhook', 'We The Kings', 'American Hi-Fi', 'Rise Against',
#            'Lit', 'The Offspring', 'Alkaline Trio', 'Neck Deep', 'Jimmy Eat World', 'Bowling For Soup',
#            'Simple Plan', 'Ramones', 'Lustra', 'Wheatus', 'Fall Out Boy', 'Sugarcult', 'Taking Back Sunday',
#            'The All-American Rejects', 'All Time Low', 'Yellowcard', 'Paramore', 'Good Charlotte',
#            'My Chemical Romance', 'Sum 41', 'Green Day', 'blink-182']

art_list = ['My Chemical Romance', 'blink-182']
#artist list source: https://indiepanda.net/best-pop-punk-bands/

# functions
def get_lyrics(_in_art_list):
    '''
    Gets lyrics and associated song title/artist of top 50 songs per artist through Genius API
    Returns a dictionary like {song_lyrics_1: [title_1, artist_1], song_lyrics_2: [title_2, artist_2],...}
    '''
    genius = Genius(token)

    lyrics_dict = {}
    for art in _in_art_list:
        artist = genius.search_artist(art, sort='popularity', max_songs=5)
        for song in artist.songs:
            lyrics_dict[song.lyrics]=[song.title, song.artist]

    lyrics_json = json.dumps(lyrics_dict, indent = 4)
    with open('artifacts/lyrics.json', 'w') as convert_file:
        convert_file.write(json.dumps(lyrics_json))

    return lyrics_dict

def prepare_corpus(_in_lyrics):
    '''
    Creates all artifacts necessary to create a VSM using Gensim. 
    Returns corpus and corpus dictionary.
    '''
    lyric_list = []
    for key in _in_lyrics:
        lyric_list.append(key)

    with open('artifacts/lyric_list.csv', 'w') as f:
        write = csv.writer(f)
        write.writerows(zip(lyric_list))
    
    clean_lyric_list = []
    for l in lyric_list:
        l = l.replace('\n', ' ').replace('embedshare', '').replace('urlcopyembedcopy', '')
        clean_lyric_list.append(utils.simple_preprocess(l, deacc=True, min_len=2, max_len=15))

    _out_corpus_dict = corpora.Dictionary(clean_lyric_list)
    _out_corpus = [_out_corpus_dict.doc2bow(l) for l in clean_lyric_list]

    _out_corpus_dict.save('artifacts/pop_punk_dict')
    corpora.MmCorpus.serialize('artifacts/pop_punk_corpus', _out_corpus)
    
    return _out_corpus, _out_corpus_dict


def create_save_vsm(_in_corpus, _in_dict): 
    '''
    Creates TF-IDF VSM and similarity matrix to be used for comparison against strings.
    '''
    tfidf = models.TfidfModel(_in_corpus)
    tfidf.save('artifacts/pop_punk_tfidf_model')

    index = similarities.MatrixSimilarity(tfidf[_in_corpus])
    index.save('artifacts/pop_punk_vsm.index')


# main
if __name__ == "__main__":
    lyrics_dict = get_lyrics(art_list)
    corpus, corpus_dict = prepare_corpus(lyrics_dict)
    create_save_vsm(corpus, corpus_dict)
    
