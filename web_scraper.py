import sys
from collections import deque
from pathlib import Path
import re
import argparse

import requests
from bs4 import BeautifulSoup

history = deque()
pattern = re.compile(
    r'^[Hh]ttps?://(www\.)?(\w+\.)+(com|info|co\.za|edu|org)/?((w+)+)?')  # what a link should look like..........or so I think


def url_checker(url):
    """This is used as a type checher for the url 
    argument on the command line......The function
    checks the url provided....

    Args:
        url (str): url to be scraped.

    Raises:
        argparse.ArgumentTypeError: Raises this if the url
        ain't an actual url.

    Returns:
        str: The url for further processing..............
    """
    if '.' in url:
        if not re.match(r'^[Hh]ttps://', url):
            url = 'https://' + url
        if pattern.match(url):
            return url
    else:
        msg = '{} is not a valid url!!'.format(url)
        raise argparse.ArgumentTypeError(msg)


def engine(url):
    """The engine of the program...It requests the url
    and parses the html provided with beautifulsoup4.
    
    Args:
        url (str): The url to be scraped for information.

    Returns:
        bs4 soup object: taken by other functions for
        further information extraction.
    """
    response = requests.get(url)
    if response.status_code != 200:
        sys.exit('Error')
    else:
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup


def link_finder(url):
    """This searches for all links available
    on the page.....

    Args:
        url (str): The url to be scraped...

    Returns:
        deque: Default....
    """
    links = engine(url).find_all('a')
    all_links = deque()
    for l in links:
        all_links.append(l.get('href'))
    print('\n*****Results*****\n')
    for link in all_links:
        print(link)
    return '\n*****End of results*****\n'


def advanced_search(url, tag=None, tag_id=None, tag_class=None):
    """This searches for a specific tag, tag_id or tag_class
    if provided of course...calls link finder without the
    recursive option if the tag is the a tag......

    Args:
        url (str): The url to be scraped..
        tag (str, optional): The tag being searched for....
        tag_id (str, optional): Css tag id of the tag being searched for. Defaults to None.
        tag_class (str, optional): CSS tag class of the tag being searched for. Defaults to None.

    Returns:
        str: The result of the scraping....
    """
    soup = engine(url)
    if tag == 'a':
        print('Redirecting you to link finder.....')
        link_finder(url)
    name = '{}'
    if tag:
        results_tag = soup.find_all(tag)
        if results_tag:
            print(name.format(tag).center(40, '*'), sep='\n')
            if tag == 'form':
                for f in results_tag:
                    print(f)
            for i in results_tag:
                print(i.get_text().strip())
        else:
            sys.exit("There 're no {} tags in the page".format(tag))
    if tag_id:
        results_id = soup.find_all(id=tag_id)
        if results_id:
            print(name.format(tag_id).center(40, '*'), sep='\n')
            for j in results_id:
                print(j.get_text().strip())
        else:
            sys.exit(
                "There 're no elements with {} id on the page".format(tag_id))
    if tag_class:
        results_class = soup.find_all(class_=tag_class)
        if results_class:
            print(name.format(tag_class).center(40, '*'), sep='\n')
            for k in results_class:
                print(k.get_text().strip())
        else:
            sys.exit(
                "There 're no elements with {} class on the page".format(tag_class))
    elif not tag and not tag_id and not tag_class:
        all_text = soup.get_text().strip().split('\n')
        all_text = [i for i in all_text if i]
        final_result = '\n'.join(all_text)
        return final_result
    return '\n'

parser = argparse.ArgumentParser(
    prog='Webscraper', description='Automated webscraping', epilog='New features coming soon.......')
parser.add_argument(
    'url', help='The url you want to scrape information from', type=url_checker)
parser.add_argument(
    '-l', '--links', help='Finds all the links in a page', action='store_true')
parser.add_argument(
    '-t', '--tags', help="Specify all the tag(s) you're looking for", nargs='+', type=str)
parser.add_argument(
    '-c', '--class_', help="Specify class(es) to look for", nargs='+', type=str)
parser.add_argument(
    '-i', '--id', help="Specify id(s) to look for", nargs='+', type=str)
args = parser.parse_args()

if args.links:
    print(link_finder(args.url))
if args.url and not args.tags and not args.class_ and not args.id:
    print(advanced_search(args.url))
if args.tags:
    for t in args.tags:
        print(advanced_search(args.url, tag=t))
if args.class_:
    for class_ in args.class_:
        print(advanced_search(args.url, tag_class=class_))
if args.id:
    for m in args.id:
        print(advanced_search(args.url, tag_id=m))
