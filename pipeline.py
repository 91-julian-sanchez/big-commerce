import subprocess
import os

def scrapy_crawl_category_glossary():
    wd = os.getcwd()
    os.chdir("scraper_motor/scraper_motor/spiders/")
    # subprocess.Popen("scrapy crawl category_glossary")
    p= subprocess.Popen("scrapy crawl category_glossary", shell=True, stdout=subprocess.PIPE)
    print(p.communicate())
    print("Acabe...............")
    os.chdir(wd)

def run_main():
    list_files = subprocess.run(["python", "main.py", "mercadolibre",
                                 "--categories_path","./scraper_motor/scraper_motor/spiders/category_glossary.csv",
                                 "--recursive","True"
                                 ])
    print("The exit code was: %d" % list_files.returncode)


if __name__ == '__main__':
    scrapy_crawl_category_glossary()
    # run_main()
