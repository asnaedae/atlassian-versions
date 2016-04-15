#!/usr/local/bin/python3

import urllib.request, re, json, argparse, yaml
from bs4 import BeautifulSoup
from IPython import embed

class AtlassianVersion:
  def __init__(self):
    self.verbose    = 0
    self.baseURL    = 'https://my.atlassian.com/download/feeds/current/'

  def setVerbosity(self, verbose):
    self.verbose = verbose

  def returnLatestVersion(self, product=None):
    """return latest atlassian product version

    Args:
      product (str): product to return version of

    Returns:
      semantic version (str)
    """
    url = self.baseURL + product + ".json"
    response = urllib.request.urlopen(url)
    data = response.read()
    text = data.decode('utf-8')
    if text.startswith("downloads(["):
      data = data[10:]
    if text.endswith("])"):
      data = data[:-1]
    j = json.loads(data.decode("utf-8"))
    if self.verbose:
      print( json.dumps(j, sort_keys=True, indent=4))
    return(j[0]['version'])

  def installedVersion(self, url, product):
    """ check for the installed version

    Uses some nasty HTML parsing to locate version information, have not found
    a cleaner method

    Args:
      url (str): url to check
      product (str): atlassian product type
    Returns:
      semantic version (str)
    """

    """
        APIs for checking installed versions:
        stash - /rest/api/1.0/application-properties
    """
    soup = BeautifulSoup(urllib.request.urlopen(url).read().decode('utf-8'), "html.parser")

    if product == 'confluence':
      return soup.find('span', id='footer-build-information').contents[0]

    if product == 'stash':
      return soup.find('span', id='product-version').contents[0][2:]

    if product == 'jira':
      return soup.find_all('input', title='JiraVersion')[0]['value']

    if product == 'crowd':
      p = re.compile('.*Version:.*(\d+\.\d+\.\d+) \(Build.*')
      m = p.match(soup.find('footer').find('div').find('p').contents[2].split('\n')[1])
      if m:
       return m.group(1)

    return "Unknown product"

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Check Atlassian versions')
  parser.add_argument('--config', type=argparse.FileType('r'), nargs='?', default='versions.yml')
  parser.add_argument('--verbose', '-v', help='increase logging', action="store_true")
  args = parser.parse_args()

  cfg = yaml.load(args.config)
  for instance in sorted(cfg):
    if args.verbose:
      print("working on %s" %(cfg[instance]['url']))
    x = AtlassianVersion()
    x.setVerbosity(args.verbose)
    installed = x.installedVersion(cfg[instance]['url'], cfg[instance]['type'])
    available = x.returnLatestVersion(cfg[instance]['type'])
    print("{:<40}\t{:>6}\t{:>6}".format(cfg[instance]['url'], installed, available))
