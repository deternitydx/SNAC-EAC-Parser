import codecs
import os
import fileinput
import sys
# Import XML parser
import xml.etree.ElementTree as ET

# Set up the triple output
#output = codecs.open(sys.stdout, encoding='utf-8', mode='w')
output = codecs.getwriter('utf8')(sys.stdout)
output.write("@prefix snac: <http://socialarchive.iath.virginia.edu/control/term#> .\n")
output.write("@prefix snacead: <http://socialarchive.iath.virginia.edu/control/term#ead/> .\n")
output.write("@prefix foaf: <http://xmlns.com/foaf/0.1/> .\n")
output.write("@prefix owl: <http://www.w3.org/2002/07/owl#> .\n")
output.write("@prefix schema: <http://schema.org/> .\n")
output.write("@prefix edm: <http://www.europeana.eu/schemas/edm/> .\n")
output.write("@prefix skos: <http://www.w3.org/2004/02/skos/core#> .\n")
output.write("@prefix rdaGr2: <http://RDVocab.info/ElementsGr2/> .\n")
output.write("@prefix dc: <http://purl.org/dc/elements/1.1/> .\n")
output.write("@prefix dcterms: <http://purl.org/dc/terms/> .\n")


# Define the namespaces to use
namespaces = { "snac" : "urn:isbn:1-931666-33-4" ,
        "snac2" : "http://socialarchive.iath.virginia.edu/control/term#",
        "schema" : "http://schema.org/",
        "xlink" : "http://www.w3.org/1999/xlink",
        "snac3" : "http://socialarchive.iath.virginia.edu/"}
# Register the namespaces
ET.register_namespace("snac", "urn:isbn:1-931666-33-4")
ET.register_namespace("snac2", "http://socialarchive.iath.virginia.edu/control/term#")
ET.register_namespace("snac3", "http://socialarchive.iath.virginia.edu/")
ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")

# For each file given on standard input, parse and look at
for filename in fileinput.input():

    tree = ET.parse(filename.strip())
    root = tree.getroot()

    # Definitions
    identifier = ""
    subjects = []
    nationalities = []
    alt_names = []
    name = ""
    places = []
    occupations = []
    languages = []
    referencedin = []
    creatorof = []
    associated = []
    corresponded = []
    sameas = []
    entity_type = ""
    start = None
    end = None

    # Handle Unique Identifier
    node = root.find(".//snac:recordId", namespaces)
    identifier = node.text

    # Handle birth/death/active dates
    node = root.find(".//snac:existDates", namespaces)
    if node is not None:
        tmp = node.find(".//snac:fromDate", namespaces)
        if tmp is not None:
            start = tmp.get("standardDate")
        tmp = node.find(".//snac:toDate", namespaces)
        if tmp is not None:
            end = tmp.get("standardDate")

    # Handle entity type
    node = root.find(".//snac:entityType", namespaces)
    if node.text == "person":
        entity_type = "edm:Agent"
    elif node.text == "corporateBody":
        entity_type = "edm:Agent"
    else:
        entity_type = "edm:Agent"
    hidden_type = node.text

    # Handle names
    first = True;
    for node in root.findall(".//snac:nameEntry", namespaces):
        if first:
            name = node[0].text
            first = False
        else:
            alt_names.append(node[0].text)

    # Handle local descriptions (subjects, nationalities)
    for node in root.findall(".//snac:localDescription", namespaces):
        for attr in node.attrib.items():
            if "AssociatedSubject" in attr[1]:
                subjects.append(node[0].text)
            if "nationalityOfEntity" in attr[1]:
                nationalities.append(node[0].text)
        
    # Handle places (only include likelySame places from GeoNames)
    for node in root.findall(".//snac3:placeEntryLikelySame", namespaces):
        places.append(node.get("vocabularySource"))

    # Handle occupations
    for node in root.findall(".//snac:occupation", namespaces):
        occupations.append(node[0].text)

    # Handle languages
    for node in root.findall(".//snac:languageUsed", namespaces):
        languages.append(node[0].get("languageCode"))

    # Handle cpf relationships
    for node in root.findall(".//snac:cpfRelation", namespaces):
        role = node.get("{http://www.w3.org/1999/xlink}arcrole")
        link = node.get("{http://www.w3.org/1999/xlink}href")
        if "associatedWith" in role:
            associated.append(link)
        elif "correspondedWith" in role:
            corresponded.append(link)
        elif "sameAs" in role:
            sameas.append(link)
    
    # Handle resource relationships
    for node in root.findall(".//snac:resourceRelation", namespaces):
        role = node.get("{http://www.w3.org/1999/xlink}arcrole")
        link = node.get("{http://www.w3.org/1999/xlink}href")
        if "referencedIn" in role:
            referencedin.append(link)
        elif "creatorOf" in role:
            creatorof.append(link)

    # Write out the triples for this file
    output.write(''.join(["<",identifier,"> a <", entity_type, "> .\n"]))
    output.write(''.join(["<",identifier,"> skos:prefLabel \"", name, "\" .\n"]))
    if start is not None:
        output.write(''.join(["<",identifier,"> edm:start \"", start, "\" .\n"]))
    if end is not None:
        output.write(''.join(["<",identifier,"> edm:end \"", end, "\" .\n"]))
    
    if hidden_type == 'person':
        output.write(''.join(["<",identifier,"> foaf:name \"", name, "\" .\n"]))
    for altname in alt_names:
        if altname is not None:
            output.write(''.join(["<",identifier,"> skos:altLabel \"", altname, "\" .\n"]))
    for subject in subjects:
        if subject is not None:
            output.write(''.join(["<",identifier,"> edm:isRelatedTo \"", subject, "\" .\n"]))
    for nationality in nationalities:
        if nationality is not None:
            output.write(''.join(["<",identifier,"> schema:nationality \"", nationality, "\" .\n"]))
    for language in languages:
        if language is not None:
            output.write(''.join(["<",identifier,"> rdaGr2:languageOfThePerson \"", language, "\" .\n"]))
    for place in places:
        if place is not None:
            output.write(''.join(["<",identifier,"> edm:hasMet <", place, "> .\n"]))
    for occupation in occupations:
        if occupation is not None:
            output.write(''.join(["<",identifier,"> rdaGr2:professionOrOccupation \"", occupation, "\" .\n"]))
    for assn in associated:
        if assn is not None:
            output.write(''.join(["<",identifier,"> edm:hasMet <", assn , "> .\n"]))
    for corr in corresponded:
        if corr is not None:
            output.write(''.join(["<",identifier,"> edm:hasMet <", corr, "> .\n"]))
    for same in sameas:
        if same is not None:
            output.write(''.join(["<",identifier,"> owl:sameAs <", same, "> .\n"]))
    for doc in referencedin:
        if doc is not None:
            output.write(''.join(["<",identifier,"> dcterms:isReferencedBy <", doc, "> .\n"]))
    for doc in creatorof:
        if doc is not None:
            output.write(''.join(["<",doc,"> dc:creator <", identifier, "> .\n"]))

