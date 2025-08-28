import requests
import os
import pygame
import time
import arabic_reshaper
from bidi.algorithm import get_display

# ===== Fix Arabic display for terminal =====
def fix_arabic(text):
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)

# ===== Get full surah text =====
def get_surah_text(surah):
    url = f"https://quranapi.pages.dev/api/{surah}.json"
    response = requests.get(url)
    if response.status_code != 200:
        print("problem extracting surah")
        return
    data = response.json()
    surah_name = data.get("surahNameArabic")
    verses = data.get("arabic1")

    print(f"\nsurah: {fix_arabic(surah_name)}\n")

    if isinstance(verses, list):
        for idx, verse in enumerate(verses):
            print(f"{idx + 1}: {fix_arabic(verse)}")
    else:
        print(fix_arabic(verses))

# ===== Get single ayah text =====
def get_ayah_text(surah, ayah):
    url = f"https://quranapi.pages.dev/api/{surah}/{ayah}.json"
    response = requests.get(url)
    #if response.status_code != 200:
    #    print("problem extracting ayah")
    #    return
    data = response.json()
    print(f"\n{fix_arabic(data.get('surahNameArabic'))} ayah {ayah}:\n")
    print(fix_arabic(data.get("arabic1")))

# ===== Get audio URL for specific ayah =====
def get_audio_text(surah, ayah):
    url = f"https://quranapi.pages.dev/api/{surah}/{ayah}.json"
    response = requests.get(url)
    #if response.status_code != 200:
    #    print("problem getting ayah")
    #    return None
    data = response.json()
    surah_name = data.get("surahName")
    audio = data.get("audio", {}).get("1")
    if audio:
        audio_url = audio.get("url")
        reciter_name = audio.get("reciter", "unknown reciter")
        print(f"\nsurah {fix_arabic(surah_name)}")
        print(f"reciter {fix_arabic(reciter_name)}")
        print(f"playing ayah {ayah} from surah number {surah}...")
        return audio_url
    else:
        print("audio file not found")
        return None

# ===== Download, play, and delete the audio file from local folder =====
def play_sound(url, surah=None, ayah=None):
    if not url:
        print("no link found for audio.")
        return

    try:
        # Save the file in the current folder
        filename = f"quran_audio_{surah}_{ayah}.mp3" if surah and ayah else "quran_audio.mp3"
        file_path = os.path.join(os.getcwd(), filename)

        # Download the audio file
        response = requests.get(url)
        response.raise_for_status()

        with open(file_path, "wb") as f:
            f.write(response.content)

        # Play the file using pygame
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        print("playing ayah...\n")

        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.music.unload()

    except Exception as e:
        print(f"problem during opening: {e}")
    finally:
        # Clean up the file
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"file deleted successfully: {filename}")

# ===== Example usage =====
try:
    surah_number = int(input("surah number: "))
    if 1 > surah_number or surah_number > 114 :
        raise Exception
except Exception:
    print("Surahs number is between 1 and 114")
url = f"https://quranapi.pages.dev/api/{surah_number}.json"
response = requests.get(url)
data = response.json()
number_ayahs = int(data.get("totalAyah"))
surah_name = data.get("surahNameArabic")
print(fix_arabic(surah_name))
print(number_ayahs)

print("Choose an option")
print("1- Read Surah")
print("2- Read ayah")
print("3- hear ayah")
option = int(input())
if option == 1:get_surah_text(surah_number)
if option == 2:
    try :
        ayah_number = int(input("ayah's number = "))
        if not 1 <= ayah_number <= number_ayahs:
            raise Exception
    except Exception:
        print(f"ayah's number should be <= {number_ayahs}")

    get_ayah_text(surah_number,ayah_number)  
if option == 3:
    try :
        ayah_number = int(input("ayah's number = "))
        if not 1 <= ayah_number <= number_ayahs:
            raise Exception
    except Exception:
        print(f"ayah's number should be <= {number_ayahs}")

    audio_url = get_audio_text(surah_number,ayah_number)
    play_sound(audio_url,surah_number,ayah_number)        

