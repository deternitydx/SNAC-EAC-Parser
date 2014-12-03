import codecs
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
        "xlink" : "http://www.w3.org/1999/xlink"}
ET.register_namespace("snac", "urn:isbn:1-931666-33-4")
ET.register_namespace("snac2", "http://socialarchive.iath.virginia.edu/control/term#")
ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")

files = [ 'sample_eac.xml', 'sample_eac2.xml' ]
# For each file, parse and look at

for filename in files:

    tree = ET.parse(filename)
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
    #need birth/death/active dates

    # Handle identifier
    node = root.find(".//snac:recordId", namespaces)
    identifier = node.text

    # Handle entity type
    node = root.find(".//snac:entityType", namespaces)
    if node.text == "person":
        entity_type = "foaf:Person"
    elif node.text == "corporateBody":
        entity_type = "foaf:Organization"
    else:
        entity_type = "foaf:Agent"

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
    for node in root.findall(".//snac:place", namespaces):
        print node[0].text
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
    output.write(''.join(["<",identifier,"> foaf:name \"", name, "\" .\n"]))
    for altname in alt_names:
        if altname is not None:
            output.write(''.join(["<",identifier,"> snac:altName \"", altname, "\" .\n"]))
    for subject in subjects:
        if subject is not None:
            output.write(''.join(["<",identifier,"> snac:hasSubject \"", subject, "\" .\n"]))
    for nationality in nationalities:
        if nationality is not None:
            output.write(''.join(["<",identifier,"> snac:hasNationality \"", nationality, "\" .\n"]))
    for language in languages:
        if language is not None:
            output.write(''.join(["<",identifier,"> snac:hasLanguage \"", language, "\" .\n"]))
    for place in places:
        if place is not None:
            output.write(''.join(["<",identifier,"> snac:hasPlace \"", place, "\" .\n"]))
    for occupation in occupations:
        if occupation is not None:
            output.write(''.join(["<",identifier,"> snac:hasOccupation \"", occupation, "\" .\n"]))
    for assn in associated:
        if assn is not None:
            output.write(''.join(["<",identifier,"> snac:associatedWith <", assn , "> .\n"]))
    for corr in corresponded:
        if corr is not None:
            output.write(''.join(["<",identifier,"> snac:correspondedWith <", corr, "> .\n"]))
    for same in sameas:
        if same is not None:
            output.write(''.join(["<",identifier,"> owl:sameAs <", same, "> .\n"]))

