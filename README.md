# recommendationSystem

system for scraping and recommending books based on hybrid recommendation system
Repository includes 4 files:

- scraping.py
- inference.py
- books_reviwes.pkl
- requirements.txt

Firstly create a vitual environment in your project folder and activate the virtual environment

```
python -m venv venv
venv\Scripts\activate (in windows)
source venv/bin/activate (in linux/unix)
```

Secondly packages should be installed from the requirements.txt after the activation of virtual environment

```
pip install -r requirements.txt
```

Thirdly the data can be scraped from goodreads.com using the scraping.py. After installation it can be done using following command

```
python scraping.py
```

The output will be in base folder as book_reviwes.pkl

Finally, the inference and recommendation can be generated using inference.py. If book_reviwes.pkl exists then the following command can be used to generate the ineference.

```
python inference.py
```

A sample input can be as follows:

```
**Preferred genre separated by comma:** 'Graphic Novels', 'Comics', 'Fantasy', 'Science Fiction', 'Fiction', 'Graphic Novels Comics', 'Adult', 'Comic Book', 'Romance'
**Preferred author separated by comma:** frank hubert
**Preferred average rating (1-5):** 4
```

The output will then be printed as follows:

```
**Here are your recommendations:**
                   Saga, Volume 1
            Paper Girls, Volume 1
                   Saga, Volume 6
                   Saga, Volume 3
The Sandman Vol. 3: Dream Country
                   Saga, Volume 4
                     Dune Messiah
                           Misery
                             Dune
```
