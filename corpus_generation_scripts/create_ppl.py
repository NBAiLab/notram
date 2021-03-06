####################################################################################
# Read all files in a directory with accompanying json meta file and validate ######
# * ocr date ######################################################################
# * publication year  ##############################################################
# * language  ######################################################################
# * wc document ####################################################################
# * wc paragraph  ##################################################################
# * language  ######################################################################
####################################################################################


import sys, glob, os, re, argparse
from tqdm import tqdm
import numpy as np
import pandas as pd
sys.path.append(r'../utils')
sys.path.append(r'../')
from utils.misc import ArgParseDefault, add_bool_arg
from datetime import datetime, timedelta
from utils.textCleaner import cleanTextBlock, cleanTextBlock_notram
from pathlib import Path


def main(args):
    input_files = get_input_files(args.input_folder)
    print(f'Found {len(input_files):,} input text files')
    stat_error_meta = 0
    stat_error_empty = 0
    stat_error_text = 0
    stat_too_old_scan = 0
    stat_too_old_publish = 0
    stat_wrong_language = 0
    stat_conf_article = 0
    stat_too_few_words = 0
    stat_too_few_words_article = 0
    langstats = {}

    complete = pd.Series([],dtype=pd.StringDtype())

    #Read everything into one large pandas frame 
    for input_file in tqdm(input_files):
    #for input_file in input_files:
        article = pd.Series([],dtype=pd.StringDtype())
        meta_file = str(input_file).replace(".txt",".meta")
        keep = True
        
        #print(f'reading {input_file}')
        
        try:
            article = pd.read_csv(input_file, sep='\r', skip_blank_lines=False, encoding='utf-8',squeeze=True, header=None,quotechar=None, quoting=3, dtype='str')
        except Exception as e:
            if e=="No columns to parse from file" and not meta.debug:
                print(f'Unable to read {input_file}')
                print(e)
            stat_error_text += 1
            continue

        try:
            meta = pd.read_json(meta_file, typ='index')
        except Exception as e:
            print(f'Unable to read {meta_file}.')
            print(e)
            stat_error_meta += 1
            continue

        #Uncomment to see only filename in output
        #input_file_name = os.path.basename(input_file)
        input_file_name = input_file        
        
        #Set basic variables
        if hasattr(meta, 'publishYear'):
            if meta.publishYear == "<unknown>":
                publishYear = args.unknown_year
            else:
                publishYear = meta.publishYear
        else:
            publishYear = args.unknown_year


        if hasattr(meta, 'language_detected'):
            if meta.language_detected == "<unknown>":
                mods_language_detected = args.unknown_language
            else:
                mods_language_detected = meta.language
        else:
            mods_language_detected = args.unknown_language

        if hasattr(meta, 'language'):
            if meta.language == "<unknown>":
                mods_language = args.unknown_language
            else:
                mods_language = meta.language
        else:
            mods_language = args.unknown_language

        modsl = f'{mods_language}-{mods_language_detected}'
        if modsl in langstats.keys():
            langstats[modsl] += 1
        else:
            langstats[modsl] = 1

        if hasattr(meta,'scandate'):
            scanDate = meta.scandate
            ocrDate = scanDate[0:2]+"-"+scanDate[2:4]+"-"+scanDate[4:8]
        else:
            ocrDate = f'{meta.urn[14:16]}-{meta.urn[12:14]}-{meta.urn[8:12]}'
       
        try:
            ocrDateTime = datetime.strptime(ocrDate, '%d-%m-%Y')
        except:
            print("Error - No valid date!!!")
            print(meta)
            ocrDate = "01-01-1900"
            continue
        if hasattr(meta,'bookOcrWordconfidence'):
            confidenceArticle = meta.bookOcrWordconfidence
        if hasattr(meta,'ocrWordconfidence'):
             confidenceArticle = meta.ocrWordconfidence

        if hasattr(meta, 'paragraphs'):
            confidenceParagraphs = meta.paragraphs
        else:
            confidenceParagraphs = ""

        if hasattr(meta, 'averageNumberOfWordsPerParagraph'):
            averageNumberOfWordsPerParagraph = meta.averageNumberOfWordsPerParagraph 
        else:
            averageNumberOfWordsPerParagraph = 99

        if hasattr(meta, 'numberOfWordsInArticle'):
            numberOfWordsInArticle = meta.numberOfWordsInArticle 
        else:
            numberOfWordsInArticle = 9999

        #Make a sanity check regarding the length of the article and the length of the meta file. 
        if hasattr(meta,'paragraphs'):
            if len(meta.paragraphs) != len(article) and len(meta.paragraphs) != len(article)+1:
                print(f'ERROR: {input_file_name}: The length of input file is {len(article)} while the corresponding meta-file has a length of {len(meta.paragraphs)}. Skipping file!')
                if len(meta.paragraphs) < 10:
                    print(meta.paragraphs)        
                stat_error_meta += 1
                keep = False

        #Scan Date
        if (datetime.strptime(args.min_ocr_date, '%d-%m-%Y') > datetime.strptime(ocrDate, '%d-%m-%Y')) and keep:
            if args.debug: print(f'{input_file_name} deleted because minimum ocr date is {args.min_ocr_date}. This book is ocr-ed {ocrDate}.')
            stat_too_old_scan += 1
            keep = False

        #Language
        if (args.language != '') and keep:
            if (args.language != language) and keep:
                if args.debug: print(f'{input_file_name} deleted because article language is {language} and only {args.language} should be included.')
                stat_wrong_language += 1
                keep = False
        
        #Publish Year
        if (int(args.min_publish_year) > int(publishYear)) and keep:
            if args.debug: print(f'{input_file_name} deleted because minimum publication year is {args.min_publish_year}. This book was published in {publishYear}.')
            stat_too_old_publish += 1
            keep = False
        
        #Confidence Article
        if (float(args.min_confidence_article) > float(confidenceArticle)) and keep:
            if args.debug: print(f'{input_file_name} deleted because minimum article confidence is {args.min_confidence_article}. This book has a confidence of {confidenceArticle}.')
            stat_conf_article += 1
            keep = False
        
        if not keep:
            article.drop(article.index, inplace=True)
        
        ##Words per paragraph
        if (float(args.min_words_paragraph) > float(averageNumberOfWordsPerParagraph)) and keep:
            if args.debug: print(f'{input_file_name} deleted because minimum words per paragraph article {args.min_words_paragraph}. This book has an average word-paragraph count of {averageNumberOfWordsPerParagraph}.')
            stat_too_few_words += 1
            keep = False
        
        #Words per article
        if (float(args.min_words_article) > int(numberOfWordsInArticle)) and keep:
            if args.debug: print(f'{input_file_name} deleted because minimum words per article {args.min_words_article}. This book/article has an word count of {numberOfWordsInArticle}.')
            stat_too_few_words_article += 1
            keep = False
        
        if not keep:
            article.drop(article.index, inplace=True)
        

        #Else evaluate every paragraph
        else:
            preProcessArticleLength = len(article)
            
            if confidenceParagraphs:
                #Paragraph Confidence
                for aid,text in enumerate(article):
                    pconf = float(meta.paragraphs[aid]['confidence'])
                    if pconf < float(args.min_confidence_paragraph):
                        if args.debug: print(f'P{aid} - Conf={pconf} - this is less then {args.min_confidence_paragraph}. Dropping line.\n{text}\n')
                        article.drop([aid], inplace=True)
                article.reset_index(drop=True, inplace=True)
            
            #Do cleaning
            if args.clean:
                for aid,text in enumerate(article):
                    article[aid] = cleanTextBlock_notram(text,do_lower_case=False)
                    if article[aid] == "":
                        article.drop([aid], inplace=True)
            article.reset_index(drop=True, inplace=True)
            
            #Add an extra lineshift at the end
            article = article.append(pd.Series(['']), ignore_index=True)
            
            if args.debug:
                print(f'{input_file_name} is valid. Keeping {len(article)} of {preProcessArticleLength -1} paragraphs.')

        #Append whatever is left into a dataframe
        complete = complete.append(article, ignore_index=True)

    #Save
    #complete.to_csv(args.output_file, header=None, index=None, sep=' ')
    #pd.set_option("display.max_colwidth", 10000)
    #with open(args.output_file, 'w+') as f:
    #    f.write(complete.to_string(header = False, index = False, justify = "left"))
    numpy_array = complete.to_numpy()
    np.savetxt(args.output_file, numpy_array, fmt = '%s')


    print(f'Final file with {len(complete)} lines was saved to {args.output_file}')
    
    #Some of this just takes too long time on the large corpuses. Disabled
    
    #print(f'Number of valid words in corpus= {complete.str.split().apply(len).sum():,}')
    print(f'Total number of articles processed =  {len(input_files):,}')
    print(f'\nThe following files were deleted:')
    print(f'Stat error meta = {stat_error_meta:,}')
    print(f'Stat error empty = {stat_error_empty:,}')
    print(f'Stat too old scan = {stat_too_old_scan:,}')
    print(f'Stat too old publish = {stat_too_old_publish:,}')
    print(f'Stat wrong language = {stat_wrong_language:,}')
    print(f'Stat conf article = {stat_conf_article:,}')
    print(f'Stat too few words average = {stat_too_few_words:,}')
    print(f'Stat too few words article = {stat_too_few_words_article:,}')
    
    print(f'\nThe following settings were used:')
    print(f'{args}')
    print(f'\nThe following languages were detected:')
    print(f'{langstats}')


def get_input_files(input_folder):
    #return glob.glob(os.path.join(input_folder, '*.txt'))
    return list(Path(input_folder).rglob('*.txt'))


def parse_args():
    # Parse commandline
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_folder', required=True, help='Path to input folder. All files ending with *.txt will be parsed.')
    parser.add_argument('-o', '--output_file', required=True, help='Output file. Will overwrite it exists')
    parser.add_argument('-s', '--min_ocr_date', required=False, default='01-01-2009', help='Will drop all articles that was ocr-ed prior to this date')
    parser.add_argument('-p', '--min_publish_year', required=False, default='1814', help='Will drop all articles published prior to this year')
    parser.add_argument('-l', '--language', required=False, default='', help='If set, only articles in this language will be included')
    parser.add_argument('-L', '--unknown_language', required=False, default='nob', help='Any unknown language is set to this value')
    parser.add_argument('-y', '--unknown_year', required=False, default='1900', help='Any unknown year is set to this value')
    parser.add_argument('-C', '--min_confidence_article', required=False, default='0.9', help='Will drop all articles with lower average word confidence')
    parser.add_argument('-c', '--min_confidence_paragraph', required=False, default='0.8', help='Will drop all paragraphs with lower average word confidence')
    parser.add_argument('-a', '--min_words_paragraph', required=False, default='5.0', help='Minimum average number of words per paragraph in the entire article/book')
    parser.add_argument('-w', '--min_words_article', required=False, default='20', help='Minimum words in the entire article/book')
    add_bool_arg(parser, 'debug', default=False, help='Print debug info about paragraphs.')
    add_bool_arg(parser, 'clean', default=False, help='Run precedure for cleaning text. Specified in sub-routine.')
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    main(args)




