# Big Commerce - Scrape latam marketplace
Big commerce is a scraping tool for marketplace ecommerce in latam

## Prerequisites

- python >= 3.7.4
- Pip Installed (Recommended >= 21.0.1)
- Install Python packages with pip and requirements.txt
    ```sh
    $ pip install -r requirements.txt
    ```
## Running the Scraper

**Run command:**

```sh
$ python main.py
```
![alt text](https://github.com/91-julian-sanchez/big-commerce/blob/master/_assetes/mercadolibre.gif "Mercadolibre scraper")

1. Select marketplace to scraper (Equivalent a `--marketplace` option)
2. select marketplace country (Equivalent a `--country` option)
3. select products category to scrape

**whats happen?**
1. Bigcommerce crawl the subcategories of the selected category and save the data in a csv file in root directory ./output/{PID}-{MARKETPLACE}-{COUNTRY}-categories.csv

    What does it scrape?


    | Value | Description |
    | --- | --- |
    | id | category id in marketplace |
    | name | category name in marketplace |
    | href | category link in marketplace |
    | hierarchy | level in category tree in marketplace (Init 1 hierarchy) |
    | parent | parent of category in category tree |
    | index | order category in category tree |
    | subcategories | number of child categories |

2. Big commerce crawl all the products of each category, browses through all the pages of the category and scraper the page of each product, 
in each iteration of the category pages, the product data is saved in a csv file in the directory ./output/{PID}-{MARKETPLACE}-{COUNTRY}-products.csv

    What does it scrape?

    | Value | Description |
    | --- | --- |
    | name | name of product |
    | link | link product in marketplace |
    | price_simbol | currency symbol |
    | price | price product|
    | price_discount | product discount percentage |
    | best_seller | indicates if the product have flag best sellers |
    | promotional | indicates if the product is sponsored |
    | category_id | product category in the marketplace |
    | number_sales | public number of sales in the marketplace |
    | seller | product seller |
    | rating | product rating |

3. Play time with data

**Options**
Optional argument | Description
--- | --- 
`--marketplace` | name marketplace to scrape
`--country` | Country code where you want to scrape marketplace, available: co, mx 
`--recursive` | Browse product pages recursively, available: True or False


**Marketplace and available commands:**

```sh
$ python main.py --help
```
## Contributing

 1. **Fork** the repo on GitHub
 2. **Clone** the project to your own machine
 3. **Commit** changes to your own branch
 4. **Push** your work back up to your fork
 5. Submit a **Pull request** so that we can review your changes

### Join our supergroup on Telegram [https://t.me/joinchat/BwvX7B03bTg4Y2Fh](https://t.me/joinchat/BwvX7B03bTg4Y2Fh)