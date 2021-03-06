# Colossal Norwegian Corpus
The Colossal Norwegian Corpus consists of both publicly available sources and of sources that is handed over to the National Library of Norway in compliance with ["pliktavleveringslova"](https://lovdata.no/dokument/NL/lov/1989-06-09-32) - a Norwegian law that requires all published materials to be sent to the library so it can be made available for research and documentation. 


## Main Sources
These sources are available from the National Library. The National Library has the right to create text corpora from this, and we are planning on releasing as much as possible of this corpus. The time frames shown below is for the first version of the corpus. In later versions we will extend the tie frames.
### Norwegian National Library
The copyright issues of this part of the corpus needs to be cleared with Kopinor before publishing
* **Books** - Published between 1814 and 2020. OCR quality of books scanned between 2006 and 2008 have fairly low quality. Only books scanned from 2009 are included included. A rough estimate is that more than 50% of all published books in Norway is included.
* **Newspapers Paper** - Published between 2015 and 2020. 
* **Newspapers Pdf** - Published between 2015 and 2020. 
* **Newspapers Microfilm** - Published between 2015 and 2020. 
* **Periodicals** - Published between ??. A wide range of periodicas and yearbooks. Mostly OCR scans.
* **Legal** - LovData DVD (2005). This is a complete collection of all laws/regulations prior to this dates. The collection is originally OCR scanned but after that manually corrected. The DVD also contains verdicts but we have left this out in the current corpus.
* **Evaluation reports** -collected from the evaluation report portal written by various Norwegian public authorities. OCR scans and pdf.


### Public Sources
This part of the corpus can be downloaded directly. The rights to redistribute the cleaned versions needs to be cleared.
* **Wikipedia NOB** - [Norwegian Wikipedia Bokmål](https://www.nb.no/sprakbanken/ressurskatalog/oai-nb-no-sbr-50/) downloaded March 2019 and published by Språkbanken. Nynorsk and Bokmål are published in the same file.
* **Wikipedia NNO** - [Norwegian Wikipedia Nynorsk](https://www.nb.no/sprakbanken/ressurskatalog/oai-nb-no-sbr-50/) downloaded March 2019 and published by Språkbanken. Nynorsk and Bokmål are published in the same file.
* **Newspapers Online NOB** - A [Norwegian Newspaper Corpus](https://www.nb.no/sprakbanken/en/resource-catalogue/oai-nb-no-sbr-4/) with texts from online bokmål newspapers between 1998 and 2019 collected by Språkbanken. 
* **Newspapers Online NNO** - A [Norwegian Newspaper Corpus](https://www.nb.no/sprakbanken/en/resource-catalogue/oai-nb-no-sbr-4/) with texts from online nynorsk newspapers between 1998 and 2019 collected by Språkbanken. 
* **MC4** - The Norwegian part of the [Multilingual Colossal Clean Crawled Corpus](https://www.tensorflow.org/datasets/catalog/c4?hl=en) published by Google in cooperation with Common Crawl. This is the Norwegian part of the corpus used to train T5 in 2020. More details about how this archive is processed is available in [this article](https://github.com/NBAiLab/notram/blob/master/guides/prepare_common_crawl.md).
* **Norwegian Government Reports** - Collected by the Norwegian National Library from?
* **Parliament Archives** - Collected by the Norwegian National Library from?


## Processing Steps
1. Source files. For library files this is ocr/txt/meta-files, and the meta-information (OCR-quality) is used for next step processing. For the other files this is the raw downloaded file.
2. **P**aragraph**P**er**L**ine-files. Articles are separated by double line breaks, paragraphs with single linebreaks.
3. Cleaned text. Text is cleaned and evaluated before this step. Paragraphs is removed here, and segments of up to 1000 words are separated by linebreaks.
4. Deduplicated and randomised text. All sources are mixed at this stage and duplicates removed.
5. Sentence segmentation. A pre-trained [Spacy Model for Norwegian Bokmål] (https://spacy.io/models/nb)is used to segment sentences.
6. Tfrecords. Tfrecord-files are generated with various vocabularies and sequence lengths.


