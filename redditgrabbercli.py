"""

#############################################################################
######################## This script Made Owca525 ###########################
################################ Ver 1.2.2 ##################################
#############################################################################

Github: https://github.com/Owca525/

"""

import concurrent.futures
import urllib.request
import urllib.parse
import urllib.error
import argparse
import ctypes
import time
import re
import os

import httpx

if os.name == 'nt':
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

parser = argparse.ArgumentParser()
parser.usage = f"redditgrabbercli -u [url] or -s [Sub reddit] -o [output]"

def create_directory(location):
    location = [location + "/" if location.rfind("/") != len(location)-1 else location][0]
    if os.path.exists(location):
        print("[\033[34mInfo\033[0m] Location Exist " + location)
        return
    
    os.mkdir(location)

class downloader:
    header = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
        "Connection": "keep-alive",
        "Sec-GPC": "1",
        "DNT": "1",
    }

    def __init__(self,url: str, output: str, file = "", resume = True, headers = "", maxRetries = 3) -> None:
        self.url = url
        self.output = output
        self.file = file
        self.maxRetries = maxRetries
        self.resume = resume
        if headers != "":
            self.header = headers
        self.filename = self.file if self.file else urllib.parse.unquote(os.path.basename(self.url))
        if self.filename.rfind("?") != -1:
            self.filename = self.filename[:self.filename.rfind("?")]

        self.startTime = 0
    
    def download(self, response, downloadedBytes):
        with response as response:
            if response.status == 200 or (self.resume and response.status == 206):
                print(f"\r[\033[32m{response.status}\033[0m] {self.url}")

                # fixing issue with no showed file size
                if response.headers["Content-Length"]:
                    totalBytes = int(response.headers["Content-Length"])
                else:
                    totalBytes = 1
                
                with open(os.path.join(self.output, self.filename), "ab" if self.resume else "wb") as outputFile:
                    totalMB = (totalBytes + downloadedBytes) / (1024 * 1024)

                    while True:
                        chunk = response.read(1024)
                        if not chunk:
                            break

                        outputFile.write(chunk)

                        elapsedTime = time.time() - self.startTime
                        downloadSpeed = downloadedBytes / 1024 / elapsedTime

                        downloadedMB = downloadedBytes / (1024 * 1024)
                        
                        if totalBytes != 1:
                            progress = (downloadedBytes / totalBytes) * 100
                            downloadedBytes += len(chunk)

                            self.printDataKnow(downloadedMB, totalMB, progress, downloadSpeed)
                        else:
                            self.printDataUknown(downloadedMB, downloadSpeed)

    def printDataKnow(self, downloadedMB, totalMB, progress, downloadSpeed):
        print(f"\033[36mDownloaded\033[0m: \033[90m{downloadedMB:.2f} MB / {totalMB:.2f} MB ({progress:.2f}%)"
                f" \033[36mSpeed\033[0m: \033[90m{downloadSpeed:.2f} KB/s\033[0m", end="\r")

    def printDataUknown(self, downloadedMB, downloadSpeed):
        print(f"\033[36mDownloaded\033[0m: \033[90m{downloadedMB:.2f} MB"
                f" \033[36mSpeed\033[0m: \033[90m{downloadSpeed:.2f} KB/s\033[0m", end="\r")
        
    def option(self):
        opt = str(input("\033[34mDo you wan't delete file and Download?\033[0m [Y/n] "))

        if opt.lower() == "y" or opt.lower() == "yes" or opt == "":
            os.remove(self.output + self.filename)
            return
        
        if opt.lower() == "n" or opt.lower() == "no":
            print("\033[32mDownload will be resumed\033[0m")
            return

    def run(self):
        retryCounter = 0
        
        if os.path.exists(self.output + self.filename):
            self.option()

        while retryCounter < self.maxRetries:
            try:
                print(f"[\033[34mGET\033[0m] {self.url}")
                request = urllib.request.Request(self.url, headers=self.header)
                self.startTime = time.time()

                if self.resume and os.path.exists(os.path.join(self.output, self.filename)):
                    downloadedBytes = os.path.getsize(os.path.join(self.output, self.filename))
                    request.add_header('Range', 'bytes=%d-' % downloadedBytes)
                    response = urllib.request.urlopen(request)
                else:
                    response = urllib.request.urlopen(request)
                    downloadedBytes = 0
                
                self.download(response, downloadedBytes)
                print(f"\n\033[32mDownload is Done in location: {self.output + self.filename}\033[0m")
                return

            except Exception as e:
                if str("HTTP Error 403: Forbidden") == str(e):
                    print("\033[31mAccess forbidden. Stopping download.\033[0m")
                    return
                
                if str("HTTP Error 416: Requested Range Not Satisfiable") == str(e):
                    print("\033[32mDownload is Done\033[0m")
                    return
                
                print(f"[\033[31mError\033[0m] {e}. Retrying...")
                retryCounter += 1
                time.sleep(0.5)

head3 = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/jxl,image/webp,*/*;q=0.8",
    "Cookie": "loid=00000000006fqb9uoh.2.1589114664963.Z0FBQUFBQmstTjc2WVlXdGRpNjctQnJaWWhvb1F6d3V3Y05FMG1qM29XeUVqNnVySXNQWFJZZEg1N29hUEVLY1lCWDMwbFhJTFR4SVd6UFpiZjJHSHl6RXJKNjhwNGRPZWJ1OWg2em1CV1M5UFZzUUR6Rk0xZmtpYWdXczJtcy1nS0lZdTFBRGtpSjg; csv=2; edgebucket=VaIdTmiyMaji9Ij4CC; USER=eyJwcmVmcyI6eyJ0b3BDb250ZW50RGlzbWlzc2FsVGltZSI6MCwiZ2xvYmFsVGhlbWUiOiJSRURESVQiLCJuaWdodG1vZGUiOnRydWUsImNvbGxhcHNlZFRyYXlTZWN0aW9ucyI6eyJmYXZvcml0ZXMiOmZhbHNlLCJtdWx0aXMiOmZhbHNlLCJtb2RlcmF0aW5nIjpmYWxzZSwic3Vic2NyaXB0aW9ucyI6ZmFsc2UsInByb2ZpbGVzIjpmYWxzZX0sInRvcENvbnRlbnRUaW1lc0Rpc21pc3NlZCI6MH19; eu_cookie={%22opted%22:true%2C%22nonessential%22:false}; reddit_session=504427775633%2C2023-09-06T20%3A20%3A10%2Cccaaa79c03b13578b259b63b5b2eb1b94edce569; pc=1v; csrf_token=a4978681b41a51b1038f3e0fea89f5ad; generated_session_tracker=bcdeqbohkacdkccarm.1.1686347701000.WN6kDwKGndtKifT2gnQX87OLmKTDAESsIIu3jCM-cd0DwMvM7XskSlgt7fnSNA9q24mA1wszvXjRAsPVpH4SMA; session=8337fd15263be7c2f1915dc607809ac8fa2b2bf4gAWVSQAAAAAAAABKXCq9ZUdB2RXzRd5zFn2UjAdfY3NyZnRflIwoZDliOWYwYjBlYjhmYzU1NGFhMjQyMzVmYjVjZjRkNmM1MTk3MzU0MZRzh5Qu; session_tracker=mnajjagpnlergidojp.0.1706895975008.Z0FBQUFBQmx2U3BuMlN0RHhDMkY5YXBNVXBRaEo4b3NkZDBuaUViOHJHM1E0b2JYSFAyU0t3Zmp1eTlwX1V4WXdaXzZlaUQ3NnVERDROSy1rc2Z3cDBkUHAtZ2FhcXhwaHVfYzdJQjNXNkNraS1sdllfOW05bjJRa3E1SG1IVkFxQllDbWlxVnBBRG0; token_v2=eyJhbGciOiJSUzI1NiIsImtpZCI6IlNIQTI1NjpzS3dsMnlsV0VtMjVmcXhwTU40cWY4MXE2OWFFdWFyMnpLMUdhVGxjdWNZIiwidHlwIjoiSldUIn0.eyJzdWIiOiJ1c2VyIiwiZXhwIjoxNzA2OTgxNjQ2Ljk3NDEwOCwiaWF0IjoxNzA2ODk1MjQ2Ljk3NDEwOCwianRpIjoiS2F5cXRCc21tcnRCbk9yR2QyYVlVUmp6WGRXalRnIiwiY2lkIjoiOXRMb0Ywc29wNVJKZ0EiLCJsaWQiOiJ0Ml82ZnFiOXVvaCIsImFpZCI6InQyXzZmcWI5dW9oIiwibGNhIjoxNTg5MTE0NjY0OTYzLCJzY3AiOiJlSnhra2RHT3REQUloZC1sMXo3Ql95cF9OaHRzY1lhc0xRYW9rM243RFZvY2s3MDdjTDRpSFA4bktJcUZMRTJ1QktHa0tXRUZXdE9VTmlMdjU4eTlPWkVGU3lGVFI4NDN5d29rYVVwUFVtTjVweWxSd1daa0xsZmFzVUtEQjZZcFZTNloyMEtQUzV2UTNJMUZ6MDZNcWx4V0h0VFlvM0pwYkdNSzJ4UGp6Y1pxUXlxdXk2bE1ZRmtvbjhXTGZ2eUctdFktZjdiZmhIWXdyS2dLRF9UT3VGeHdZX0hERkhiX25wcjBiRjJ3cUwzWGc5US0xLU4yN2JObW9kbTVfVnpQdnphU2NUbUc1aWZZdjd0LUNSMTQ1SG1aVVFjd1lnMF95ckFqNl9Ddk9vREtCUVdNSlloUEk1QXJsMl9fSmRpdVRmOGF0eWQtLUdiRVRXXzRyUm1vNXhMRW9VX2o2emNBQVBfX1hEX2U0dyIsInJjaWQiOiJIbWcyN002UGQzR1Q0MkNnY01FMG4wRnhpTjc0Q2VGbEQxZkZPSC1FVUc0IiwiZmxvIjoyfQ.NCZx8kEd9G-4NOayk24t2j7kXuxphKR4mmdbmEONtfXKrfEQSCkUg0FcrizdiB0vRGhOIx89-2-aLmgDwTlLxcJfN4NyytqQIPOkccVdseHISO9Bxh3uz_8I_9RGP19-Uul1cL95iL4mSVxsHon5te9Si1yjogabmQidVjHcIJl5B-vaNewHOPmYodnvUuWGY6V3y17gpOQWq7tTKfb14D0btbFd6XTB9iTDlJtvmfvrYIGe4lDn5LVEySyLpFG-DEWzecdgFvrAxLNad6e44IHZT0VUTaeYKn4Zwbq8VIbiSLNt-fxj_RBjPG6PGOsIeCbWuJUyJvmdYyg5dNcCEw",
}

class post_grabber:
    def __init__(self, subreddit = str) -> None:
        self.media_prieview_patern = r'<div class="media-preview-content">.*?</div>'
        self.gallery_thumbnail_patern = r'<a class="may-blank gallery-item-thumbnail-link".*?href="(.*?)".*?>'
        self.url_find_pattern = r'<a[^>]*class="[^"]*title[^"]*may-blank[^"]*outbound[^"]*"[^>]*href="([^"]+)"[^>]*>'
        self.reddit_content_url_patern = r'https://i\.redd\.it/[^"]+'
        self.html_content = str
        self.subreddit = subreddit

        self.return_list = []
    
    def re_find(self, patern):
        return re.findall(patern, self.html_content, re.DOTALL)

    def find_content(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            run = executor.map(self.re_find, [self.media_prieview_patern, self.url_find_pattern])
        return list(run)

    def grabber(self, url: str):
        findID = re.findall(r'(?:https?:\/\/)?(?:www\.|old\.|i\.|new\.)?(?:reddit\.com|redd\.it)\/(?:r\/[^\s\/$.?#]+\/)?gallery\/',url)
        if findID != []:
            url = f"https://old.reddit.com/r/{self.subreddit[0]}/comments/" + re.findall(r'(?:https?:\/\/)?(?:www\.|old\.|i\.|new\.)?(?:reddit\.com|redd\.it)\/(?:r\/[^\s\/$.?#]+\/comments\/)?(?:gallery\/)?([^\s\/$.?#]+)',url)[0]

        req = httpx.get(url=url.replace("www.reddit.com","old.reddit.com").replace("i.reddit.com","old.reddit.com").replace("new.reddit.com","old.reddit.com"),headers=head3)
        if req.headers["location"] != None:
            req = httpx.get(url=str(req.headers["location"]), headers=head3)

        if req.text != None and req.status_code == 200:
            self.html_content = req.text
            content = self.find_content()
            print(req.url)

            if content[1] != [] and re.findall(r'(?:https?:\/\/)?(?:www\.|old\.|i\.|new\.)?(?:reddit\.com|redd\.it)\/(?:r\/[^\s\/$.?#]+\/)?gallery\/',content[1][0]) == []:
                return content[1]

            if content[0] != []:
                for item in content[0]:
                    self.html_content = item
                    self.return_list.append(self.re_find(self.gallery_thumbnail_patern)[0].replace("amp;",""))
                return self.return_list
            
            if content[1] != []:
                self.return_list.append(content[1][0])

            return self.return_list
        return []

class subreddit_grabber:
    def __init__(self) -> None:
        self.posts = []
        self.next_button = str

    def grabber(self, url):
        connect = httpx.get(url=url.replace("www.reddit.com","old.reddit.com").replace("i.reddit.com","old.reddit.com").replace("new.reddit.com","old.reddit.com"),headers=head3)

        if connect.status_code == 200:
            self.next_button = re.findall(r'<span\s+class="next-button"[^>]*>\s*<a\s+href="([^"]+)"[^>]*>.*?</a>\s*</span>', connect.text)[0].replace("amp;","")
            self.posts = re.findall(r'<a\s+[^>]*\bclass="[^"]*thumbnail[^"]*"\s+[^>]*\bhref="([^"]+)"[^>]*>',connect.text)
    
class main:
    def __init__(self, url: str, output: str, subreddit: str, page: int) -> None:
        self.url = url
        self.output = output
        self.page = page
        self.subreddit = subreddit
    
    def sort(self, url):
        if re.findall(r'(?:https?:\/\/)?(?:www\.|old\.|i\.|new\.)?(?:reddit\.com|redd\.it)\/(?:r\/[^\s\/$.?#]+\/comments\/)?(?:gallery\/)?([^\s\/$.?#]+)',url) == []:
            print(f"[\033[32mURL Extracted\033[0m]: {url}")
            return
        
        if re.findall(r'(?:https?:\/\/)?(?:www\.|old\.|i\.|new\.)?(?:reddit\.com|redd\.it)\/(?:r\/[^\s\/$.?#]+\/)?gallery\/',url) != []:
            print("[\033[34mInfo\033[0m] Gallery Download")
            postID = re.findall(r'(?:https?:\/\/)?(?:www\.|old\.|i\.|new\.)?(?:reddit\.com|redd\.it)\/(?:r\/[^\s\/$.?#]+\/comments\/)?(?:gallery\/)?([^\s\/$.?#]+)',url)[0]
            create_directory(self.output + postID)
            for item in post_grabber(subreddit=re.findall(r'(?:https?:\/\/)?(?:www\.|old\.|new\.)?reddit\.com\/r\/([^\s\/$.?#]+)', self.subreddit)).grabber(url):
                print(item)
                downloader(
                    url=item,
                    output=self.output + postID
                ).run()
            return

        downloader(
            url=url,
            output=self.output
        ).run()
    
    def run(self):
        if self.url != None:
            urls = post_grabber().grabber(self.url)
            if urls == []:
                print("[\033[34mInfo\033[0m] Nothing found")
                exit()
            
            if re.findall(r'(?:https?:\/\/)?(?:www\.|old\.|i\.|new\.)?(?:reddit\.com|redd\.it)\/(?:r\/[^\s\/$.?#]+\/comments\/)?(?:gallery\/)?([^\s\/$.?#]+)',urls[0]) == []:
                for item in urls:
                    print(f"[\033[32mURL Extracted\033[0m]: {item}")
                exit()

            if len(urls) == 1:
                downloader(
                    url=urls[0],
                    output=self.output
                ).run()
                exit()
            
            postID = re.findall(r'(?:https?:\/\/)?(?:www\.|old\.|i\.|new\.)?(?:reddit\.com|redd\.it)\/(?:r\/[^\s\/$.?#]+\/comments\/)?(?:gallery\/)?([^\s\/$.?#]+)',self.url)[0]
            create_directory(self.output + postID)
            for item in urls:
                downloader(
                    url=item,
                    output=self.output + postID
                ).run()
            exit()

        if self.subreddit != None:
            for i,item in enumerate(range(self.page)):
                print(f"[\033[34mInfo\033[0m] page {i} ({i * 25})")
                sub = subreddit_grabber()
                sub.grabber(self.subreddit)
                #map(self.sort, sub.post)9
                for item in list(set(sub.posts)):
                    self.sort(item)
                self.subreddit = sub.next_button

if __name__ == "__main__":
    parser.add_argument("-u","--url", help="url", type=str)
    parser.add_argument("-o","--output", help="set output location", type=str,metavar=('output'))
    parser.add_argument("-p", "--page", help="page download (default 1)",default=1, type=int)
    parser.add_argument("-s", "--subreddit", help="name subreddit", type=str)
    args = parser.parse_args()

    if args.subreddit == None and re.findall(r'^(https?:\/\/)?(www\.|old\.|i\.|new\.)?(reddit\.com|redd\.it)\/[^\s\/$.?#].[^\s]*$',str(args.url)) == [] and args.url:
        print('[\033[31mError\033[0m] Wrong url')
        exit()
    
    if args.subreddit != None:
        connect = httpx.get(url=re.findall(r'(?:https?:\/\/)?(?:www\.|old\.|new\.)?reddit\.com\/r\/[^\s\/$.?#]+', args.subreddit)[0])
        if connect.status_code == 404:
            print("[\033[31mError\033[0m] Subreddit Doesn't exist")
            exit()
        args.subreddit = re.findall(r'(?:https?:\/\/)?(?:www\.|old\.|new\.)?reddit\.com\/r\/[^\s\/$.?#]+', args.subreddit)[0] + "/"

    if args.output == None and os.path.exists(str(args.output)) != True:
        print(f"[\033[31mError\033[0m] Location is dosen't exist, please type good location")
        exit()
    
    main(
        url=args.url,
        output=args.output,
        subreddit=args.subreddit,
        page=args.page
    ).run()

