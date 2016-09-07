#!/usr/bin/python

from bs4 import BeautifulSoup
import textwrap
import urllib2
import argparse
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser(description='Make Term for Dictionary.')
parser.add_argument('-p', '--property_name', help='Name to be given to the property')
parser.add_argument('-c', '--cde_id',  help='Public ID for the CDE')

args = parser.parse_args()
property_name = args.property_name
cde_id = args.cde_id

def getAttribute(attribName, xTree):
    for field in xTree.iter('field'):
        if (field.get('name') == attribName):
            return field.text

url = "http://cadsrapi.nci.nih.gov/cadsrapi41/GetXML?query=DataElement[@publicId=%s]" % cde_id
res = urllib2.urlopen(url)
cadsr_xml = res.read()
root = ET.fromstring(cadsr_xml)

definition = getAttribute("preferredDefinition", root)
cleaned_def = textwrap.dedent(definition).strip()

long_name = getAttribute("longName",root)
cde_version = getAttribute("version",root)
term_url = "https://cdebrowser.nci.nih.gov/CDEBrowser/search?elementDetails=9&FirstTimer=0&PageId=ElementDetailsGroup&publicId=%s&version=%s" % (cde_id, cde_version)

# Print out the term
print("%s:" % property_name)
print("  description: >")
print("%s" % textwrap.fill(cleaned_def, width=96, initial_indent='    ', subsequent_indent='    ')) 
print("  termDef:")
print("    term: %s" % long_name)
print("    source: caDSR")
print("    cde_id: %s" % cde_id)
print("    cde_version: %s" % cde_version)
print("    term_url: \"%s\"\n" % term_url)


pv_url = "http://cadsrapi.nci.nih.gov/cadsrapi41/GetHTML?query=PermissibleValue,ValueDomainPermissibleValue,EnumeratedValueDomain,ValueDomain&DataElement[@publicID=%s][@latestVersionIndicator=Yes]" %cde_id
pv_res = urllib2.urlopen(pv_url)
cadsr_html = pv_res.read()
soup = BeautifulSoup(cadsr_html, 'html.parser')
pvalues = []

for row in soup.findAll(attrs={"summary":"Data Summary"})[0].findAll(attrs={"class":"dataRowLight"}):
    pvalues.append(row.findAll('td')[7].text)

uniq_pvs = sorted(set(pvalues))

# Print out the property
print("%s:" % property_name)
print("  term:")
print('    $ref: "terms,yaml#/%s"' % property_name)
print("  enum:")
for i in uniq_pvs:
    print("    - %s" % i) 
print("")
