import sys, requests, shutil, os

class RedditScraper:

    def __init__(self, limit, mode):
        treeRpath = "./Downloads/"

        self.limit = limit
        self.mode = mode
        self.imgRpath = treeRpath + "IMG/"
        self.textRpath = treeRpath + "TEXT/"

    # Gets the list of subreddits from the subreddits.txt file and returns a list of it
    @staticmethod
    def get_subreddits():

        sbfile = r'subreddits.txt'

        subreddits = []

        try:
            with open(sbfile, 'r') as sb:

                t_sub = sb.readlines()
                t_sub.sort()

                for subreddit in t_sub:
                    subreddits.append(subreddit.strip())

            with open(sbfile, 'w') as sb:
                for sub in t_sub:
                    sb.write(sub)
            return subreddits
        except:
            with open(sbfile, 'w') as _f:
                pass
            print(sbfile, "not detected. Please specify all the subreddits you would like to scrape in the newly created subreddits.txt file and try again.")
            sys.exit(1)

    # Creates all the folders involved
    def init_tree(self, subreddits):

        if not os.path.exists(self.imgRpath): # Creates the IMG directory if it doesn't exist
            os.makedirs(self.imgRpath)
        
        if not os.path.exists(self.textRpath): # Creates the TEXT directory if it doesn't exist
            os.makedirs(self.textRpath)

        for subreddit in subreddits:
            fimgRpath = self.imgRpath + subreddit + "/images"
            ftxtRpath = self.textRpath + subreddit + "/texts"

            if not os.path.exists(fimgRpath):
                os.makedirs(fimgRpath)

            if not os.path.exists(ftxtRpath):
                os.makedirs(ftxtRpath)

    # Gets the direct image link to be passed to the downloader component later
    @staticmethod
    def get_image_link(item):
        try:
            itemlist = []
            for entry in item.media_metadata:
                ext = item.media_metadata[entry]["m"].split("/")[-1]
                itemlist.append("https://i.redd.it/" + str(entry) + "." + ext) # https://i.redd.it/chbos6soi2m51.jpg
            return itemlist
        except:
            target = str(item.url_overridden_by_dest)
            if target.split("/")[2] == "imgur.com" and "jpg" not in target and "png" not in target:
                target_sub_ext = str(item.media["oembed"]["thumbnail_url"]).split("/")[-1].split(".")[-1][0:3] # Extracts either 'jpg' or 'png'
                return "https://i.imgur.com/" + target.split("/")[-1] + "." + target_sub_ext # Construction of a new workable imgur link: https://i.imgur.com/voK4IdY.png
            else:
                return target

    # Gets the extension of the image for shutil
    @staticmethod
    def parse_extension(link):
        if not isinstance(link, list):
            return link.split("/")[-1].split(".")[-1][0:3]
        else:
            return link[0].split("/")[-1].split(".")[-1][0:3]

    # Gets the title of the filename from an item's permalink
    @staticmethod
    def get_filename(item):
        plink = str(item.permalink)
        return plink.split("/")[5]

    # Gets the last index number of downloaded images in a subreddit's images folder
    def get_fileindex(self, subreddit):
        joint_index = {"images": None, "texts": None}

        for key in joint_index:
            try:
                if key == "images":
                    x = os.listdir("./Downloads/IMG/" + subreddit + "/" + key)
                else:
                    x = os.listdir("./Downloads/TEXT/" + subreddit + "/" + key)

                def extract_index(s):
                    return int(s.split(" - ")[0])

                result = map(extract_index, x)
                result = list(result)
                result.sort()
                joint_index[key] = result[-1]
            except:
                joint_index[key] = 0

        return joint_index
    
    # Main method
    def main(self):
        
        import praw

        try:
            reddit = praw.Reddit("RS")
        except:
            print("Either your praw.ini file is missing or you didn't activate it yet. Uncomment the first line in praw.ini and try again.")
            sys.exit(1)

        subreddits = self.get_subreddits()
        subreddit_findex = {}

        for subreddit in subreddits:
            final_index = self.get_fileindex(subreddit)
            subreddit_findex[subreddit] = final_index # {"gardening": {"images": 123, "texts": 456}}

        def get_incremented_index(subreddit, dlc_type):
            subreddit_findex[subreddit][dlc_type] = subreddit_findex[subreddit][dlc_type] + 1
            return subreddit_findex[subreddit][dlc_type]

        self.init_tree(subreddits=subreddits)

        sessionsentinel = 1
        headers = {"User-Agent":reddit.config.user_agent} # For requests

        def worker(item_rep, childName=None):
            nonlocal sessionsentinel
            print(str(sessionsentinel) + ". Found:", str(item_rep.permalink))

            if not childName:
                subreddit = str(item_rep.subreddit) # Stores current subreddit as string
            else:
                subreddit = childName

            textarchivefile = self.textRpath + subreddit + "/archiveredditlinks.txt"
            archivelink = "https://old.reddit.com" + str(item_rep.permalink) + "\n" # Used by comment text and image processes

            def write_item_text(item_type):
                tsfindex = str(get_incremented_index(subreddit, "texts"))
                textOutfile = self.textRpath + subreddit + "/texts/" + tsfindex + " - " + self.get_filename(item) + ".txt"
                
                with open(textOutfile, "w", encoding="utf-8") as tr: # Write content
                        link = "https://old.reddit.com" + item_rep.permalink

                        if item_type == "post":
                            tr.write("Title: " + item_rep.title + "\nLink: " + link + "\n\n" + item_rep.selftext)
                        else:
                            tr.write("Title: " + item_rep.link_title + "\nLink: " + link + "\n\n" + item_rep.body)
                with open(textarchivefile, "a", encoding="utf-8") as ar: # Write link to archive file
                    ar.write(archivelink)
                print("< Written " + item_type + " content >")

            if hasattr(item_rep, "post_hint") and item_rep.post_hint == "link" and (hasattr(item_rep, "url_overridden_by_dest") and not "jpg" in item_rep.url_overridden_by_dest or "png" in item_rep.url_overridden_by_dest): # Saved post
                print("Third party content; skipping.")
            elif hasattr(item_rep, "is_self") and item_rep.is_self and item_rep.selftext != "":
                write_item_text("post")
            elif hasattr(item_rep, "body"): # Saved comment
                write_item_text("comment")
            else: # Saved image

                if self.mode == "image":
                    content_link = self.get_image_link(item_rep)
                    isfindex = str(get_incremented_index(subreddit, "images"))
                    
                    if not isinstance(content_link, list):
                        imgOutfile = self.imgRpath + subreddit + "/images/" + isfindex + " - " + self.get_filename(item_rep) + "." + self.parse_extension(content_link)
                        with requests.get(url=content_link, stream=True, headers=headers) as s:
                            print(s)
                            with open(imgOutfile, "wb") as b:
                                shutil.copyfileobj(s.raw, b)
                    else:
                        gallerysentinel = 1
                        for i in content_link:
                            imgOutfile = self.imgRpath + subreddit + "/images/" + isfindex + " - " + self.get_filename(item_rep) + " - " + str(gallerysentinel) + "." + self.parse_extension(content_link)
                            with requests.get(url=i, stream=True, headers=headers) as s:
                                print(s)
                                with open(imgOutfile, "wb") as b:
                                    shutil.copyfileobj(s.raw, b)
                            gallerysentinel = gallerysentinel + 1
                
            sessionsentinel = sessionsentinel + 1

            with open(self.imgRpath + subreddit + "/archiveredditlinks.txt", "a", encoding="utf-8") as ar:
                ar.write(archivelink)

            if not childName:
                item_rep.unsave()

        for item in reddit.user.me().saved(limit=self.limit):
            if item.subreddit in subreddits and not hasattr(item, "crosspost_parent"):
                worker(item)
            elif item.subreddit in subreddits and hasattr(item, "crosspost_parent"):
                parent = reddit.submission(id=item.crosspost_parent_list[0]["id"])
                worker(parent, str(item.subreddit))
                item.unsave()

if __name__ == "__main__":
    
    if len(sys.argv) > 2 and len(sys.argv) <= 3:
        try:
            arg = int(sys.argv[1])
        except:
            arg = sys.argv[1]
        
        if isinstance(arg, int):
            limit = int(arg)
        elif arg == "None":
            limit = None
        else:
            print("Invalid argument", arg, "please try again.")
            sys.exit(1)
    else:
        print("Please specify a numerical limit. Add 'None' if you want no limits.")
        sys.exit(1)

    RS = RedditScraper(limit=limit, mode='image')

    RS.main()

    if sys.argv[-1] == "-sort":

        from natsort import natsorted

        subreddits = os.listdir("./Downloads/IMG")

        for subreddit in subreddits:
            sentinel = 1

            rpath = "./Downloads/IMG/" + subreddit + "/images"

            files = natsorted(os.listdir(rpath))

            for file in files:
                
                f_name = file.split(" - ")[1]
                out_name = str(sentinel) + " - " + f_name
                
                try:
                    os.rename(rpath + "/" + file, rpath + "/" + out_name)
                except Exception as e:
                    print(file, " is correct.", e)
                sentinel = sentinel + 1
            print("Did", subreddit)