import codecs
import os
# Import the bulbs graph ORM
from bulbs.neo4jserver import Graph
from relationships import *
# Import XML parser
import xml.etree.ElementTree as ET

# Set up the triple output
output = codecs.open("output.txt", encoding='utf-8', mode='w')
output.write("@prefix snac: <http://socialarchive.iath.virginia.edu/control/term#> .\n")
output.write("@prefix snacead: <http://socialarchive.iath.virginia.edu/control/term#ead/> .\n")
output.write("@prefix foaf: <http://xmlns.com/foaf/0.1/> .\n")
output.write("@prefix owl: <http://www.w3.org/2002/07/owl#> .\n")
output.write("@prefix schema: <http://schema.org/> .\n")
output.write("@prefix edm: <http://www.europeana.eu/schemas/edm/> .\n")
output.write("@prefix skos: <http://www.w3.org/2004/02/skos/core#> .\n")
output.write("@prefix rdaGr2: <http://RDVocab.info/ElementsGr2/> .\n")


# Neo4J Test
g = Graph()
g.add_proxy("people", Person)
g.add_proxy("corporation", Corporation)
g.add_proxy("document", Document)
g.add_proxy("associated", AssociatedWith)
g.add_proxy("corresponded", CorrespondedWith)
g.add_proxy("referencedIn", ReferencedIn)

#gw = g.people.create(name="Washington George")
#tj = g.people.create(name="Jefferson Thomas")
#rel = g.associated.create(gw, tj)
#gw.save()
#tj.save()
#rel.save()

#print g
#print "Vertices:",  g.V
#print "Edges:" , g.E

# XML Test
namespaces = { "snac" : "urn:isbn:1-931666-33-4" ,
        "snac2" : "http://socialarchive.iath.virginia.edu/control/term#",
        "schema" : "http://schema.org/",
        "xlink" : "http://www.w3.org/1999/xlink",
        "snac3" : "http://socialarchive.iath.virginia.edu/"}
ET.register_namespace("snac", "urn:isbn:1-931666-33-4")
ET.register_namespace("snac2", "http://socialarchive.iath.virginia.edu/control/term#")
ET.register_namespace("snac3", "http://socialarchive.iath.virginia.edu/")
ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")

# For each file, parse and look at
path = "sample/"
for filename in os.listdir(path):

    tree = ET.parse(os.path.join(path,filename))
    root = tree.getroot()
    #for child in root:
    #    print child.tag, child.attrib
    #    for little in child:
    #        print little.tag, little.attrib

    identifier = ""
    subjects = []
    nationalities = []
    alt_names = []
    name = ""
    places = []
    occupations = []
    languages = []
    associated = []
    corresponded = []
    sameas = []
    entity_type = ""
    start = None
    end = None
    #need birth/death/active dates

    # Handle identifier
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
        
    # Handle places
    for node in root.findall(".//snac3:placeEntryLikelySame", namespaces):
        places.append(node.get("vocabularySource"))
        # this will be tricky:
        #   if LikelySameAs exists, then use it and also grab coordinates and geonames entry for owl:sameAs
        #   else, then just grab the text that exists (node[0].text)

    # Handle occupations
    for node in root.findall(".//snac:occupation", namespaces):
        occupations.append(node[0].text)

    # Handle languages
    for node in root.findall(".//snac:languageUsed", namespaces):
        languages.append(node[0].get("languageCode"))

    # Handle relationships
    for node in root.findall(".//snac:cpfRelation", namespaces):
        role = node.get("{http://www.w3.org/1999/xlink}arcrole")
        link = node.get("{http://www.w3.org/1999/xlink}href")
        if "associatedWith" in role:
            associated.append(link)
        elif "correspondedWith" in role:
            corresponded.append(link)
        elif "sameAs" in role:
            sameas.append(link)
        
        #for attr in node.attrib.items():
        #print node.attrib.items()

    #print "ID: " , identifier
    #print "Name: " , name
    #print "Alternate Names: ", alt_names
    #print "Subjects: ", subjects
    #print "Nationalities: ", nationalities
    #print "Languages: ", languages
    #print "Places: ", places
    #print "Occupations: ", occupations
    #print "Associated with: ", associated
    #print "Corresponded with: ", corresponded
    #print "Same as: ", sameas

    # So, we can easily write these out as triples.  It will be much harder to build the neo4j database.
    # To build the database, we must first insert all the nodes, then make a second pass for the edges (associated withs)

    # Write out the triples
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
    # schema: has deathDate and birthDate

