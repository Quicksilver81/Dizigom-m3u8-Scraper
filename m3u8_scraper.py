import re
from select import select
import requests
from bs4 import BeautifulSoup
import json
import os
import subprocess

links = []
episode_m3u8_links = []
failed_links = []
episode_names = []

class bcolors: #If it is not working, please remove bcolors and variables
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    MIDDLELINE = '\033[9m'
    OKGRAY = '\033[2m'
    ITALIC = '\033[3m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
class M3U8Scrapper:
    def __init__(self,url):
        self.url = url # url of the m3u8 file  
         
    def getListSpecial(self):
        name_series = input('Dizi ismi(küçük ve boşluklarda "-" işaret kullanarak): ')
        season_counter = int(input('Sezon sayısı: '))
        counter = 1
        epis = []
        
        while counter != season_counter+1:
            episode_counter = int(input(f'{counter}. Sezon Bölüm sayısı: '))
            counter_epi = 1
            for episode in range(1,episode_counter+1):
                episode_name = f'{filename} {counter}. Sezon {episode}. Bölüm'
                episode_link = f"https://dizipal306.com/bolum/{name_series}-{counter}x{counter_epi}-izle/"
                epis.append(episode_name)
                links.append(episode_link)
                counter_epi += 1
            counter += 1
            
        with open(f"{filename}_Links.txt", "a", encoding="utf-8") as f:
            for link in links:
                f.write(link + "\n")
                
        with open(f"{filename}_Names.txt", "a", encoding="utf-8") as f:
            for name in epis:
                f.write(name + "\n")
                
        return links,epis

    def getSeriesList(self, url) -> list:
        """Verilen url'deki dizileri listelemek için kullanılır.
        
        Parametreler: 
        • url(str): dizipal diziler urlsi
        
        Örnek Kullanım:
        
        scrapper = M3U8Scrapper()
        scrapper.getMovies("https://dizipal306.com/series/")
        """

        try:
            for i in range(1,60):
                
                viewsource = requests.get(url+str(i))
                soup = BeautifulSoup(viewsource.text, 'html.parser')
                lies = soup.find("div", {"id":"movies-a"}) # for series
                li = lies.find_all("li")
                with open("Diziler Güncel Liste.txt", "a", encoding="utf-8") as f:
                    f.write(f"SAYFA {i}\n\n")
                    for episode in li:
                        title = episode.find("h2", {"class" : "entry-title"})
                        vote = episode.find("span")
                        a = vote.text.split(" ")[1]
                        f.write(f"\nİsim: {title.text}\nPuan: {a}\n")
                    f.write("\n\n")
                    print(f"SAYFA {i}")
        except:
            print("Diziler Güncel Listesi Alındı.")

    def getEpisodes(self,url):
        """Verilen url'deki dizileri listelemek için kullanılır.
        
        Parametreler: 
        • url(str): dizilerin listelenmesi istenen url
        
        Örnek Kullanım:
        
        scrapper = M3U8Scrapper()
        scrapper.getMovies("https://www.trtizle.com/diziler/leyla-ile-mecnun")
        """
        epis = []
        viewsource = requests.get(url)
        soup = BeautifulSoup(viewsource.text, 'html.parser')
        uls = soup.find("ul", {"id":"episode_by_temp"})
        episodes = uls.find_all("li")
        
        for episode in episodes:
            epi = episode.find("a")
            links.append(epi.get("href"))            
            epi_names = episode.find("h2", {"class" : "entry-title"})
            epis.append(epi_names.text)
        print(epis,links)        
        return links,epis
            
    def getM3U8Links(self, link_list, epi_list):
        """Verilen liste içerisindeki linkleri kullanarak m3u8 linklerini listeler.
        
        Parametreler:
        • link_list(list): İçerik linklerini barındıran liste
        • epi_list(list): İçerik isimlerini barındıran liste
        
        Örnek Kullanım:
        
        episodes_list = [...]
        
        scrapper = M3U8Scrapper()
        
        scrapper.getM3U8Links(episode_list)
        """      
        i = 0
        try:
            with open(f"{filename}_Links.txt", "r", encoding="utf-8") as f:
                linky = f.readlines()
        except:
            linky = link_list
        for episode in linky:
            source = requests.get(episode)
            code = BeautifulSoup(source.content, "html.parser") 
            embed_link = code.find("iframe").get("src")
            source = requests.get(embed_link)
            code = BeautifulSoup(source.text, "html.parser")
            link = code.find_all("script", {"type" : "text/javascript"})   
            js_con = str(link[2]) # paste sitesine atığım kısmı veriyor
            js = re.search('Playerjs\((.+)\)', js_con)[1]
            last_js = js.replace("id",'"id"',1).replace("ready",'"ready"').replace("duration",'"duration"').replace("poster",'"poster"').replace("file",'"file"').replace("subtitle_start",'"subtitile_start"').replace("midroll",'"midroll"').replace("time",'"time"').replace("vast",'"vast"')
            listt = json.loads(last_js)
            episode_link = listt["file"]
            episode_name = epi_list[i]
            
            with open(filename + ".txt", "a", encoding="utf-8") as f:
                f.write(episode_name + "|" + episode_link + "\n")
                
            episode_m3u8_links.append(episode_link)
            
            print(f"{bcolors.ITALIC}{bcolors.WARNING}Çekilen Bölüm:{bcolors.ENDC} {episode_name}")
            if i == len(link_list)-1:
                break
            else:
                i += 1
                
        os.system("cls")
        if not failed_links:
            print(f"{bcolors.OKGREEN}İşlem tamamlandı.\nÇekilen Dizi: {bcolors.ENDC}{filename}\n{bcolors.OKGREEN}Bölüm sayısı:{bcolors.ENDC} {len(episode_m3u8_links)}\n{bcolors.WARNING}Hatalı Link(ler):{bcolors.ENDC} Yok")
        else:
            print(f"{bcolors.OKGREEN}İşlem tamamlandı.\nÇekilen Dizi:{bcolors.ENDC} {filename}\n{bcolors.OKGREEN}Bölüm sayısı:{bcolors.ENDC} {len(episode_m3u8_links)}\n{bcolors.WARNING}Hatalı Link(ler):{bcolors.ENDC} {failed_links}") 
        return episode_m3u8_links

    def getVideos(self, series_name): 
        with open(series_name + ".txt", "r", encoding="utf-8") as f:
            links = f.readlines()

        for link in links:
            episode_link = link.split("|")[1].replace("\n","")
            episode_name = link.split("|")[0].replace(" ","_")
            with open("Episode Names.txt","a",encoding="utf-8") as f:
              f.write(episode_name + "\n")
            output = f"{folder_name}{episode_name}"
            subprocess.run(['yt-dlp',episode_link,'-o',output])



if __name__ == "__main__":
    
    filename = input(bcolors.OKGREEN + "Dosya Adı: " + bcolors.ENDC)
    linkofseries = input(f"{bcolors.OKBLUE}Linki giriniz: {bcolors.ENDC}")
    select = int(input(f"{bcolors.OKBLUE}Listeyi çekmek için 1, indirmek için 2, özel üretim içn 3: {bcolors.ENDC}"))
    if select == 1:
        # try:
        #     os.mkdir(f"{filename}/")
        #     folder_name = f"{filename}/"
        # except FileExistsError:
        #     folder_name = f"{filename}/"
            
        scrapper = M3U8Scrapper(linkofseries)
        
        episode_links = scrapper.getListSpecial()
        epi_list = episode_links[1]
        scrapper.getM3U8Links(episode_links[0], epi_list)
        os.remove(f"{filename}_Links.txt")
        os.remove(f"{filename}_Names.txt")
            
    elif select == 2:
        try:
            os.mkdir(f"{filename}/")
            folder_name = f"{filename}/"
        except FileExistsError:
            folder_name = f"{filename}/"
            
        scrapper = M3U8Scrapper(linkofseries)
        
        episode_links = scrapper.getEpisodes(linkofseries)
        epi_list = episode_links[1]
        scrapper.getM3U8Links(episode_links[0], epi_list)    
        scrapper.getVideos(filename)
    elif select == 3:
        scrapper = M3U8Scrapper(linkofseries)
        scrapper.getListSpecial()
    else:
        print(f"{bcolors.FAIL}Geçersiz seçim.{bcolors.ENDC}")