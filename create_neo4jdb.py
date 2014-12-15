import datetime
import codecs
import os
# Import the bulbs graph ORM
from bulbs.neo4jserver import Graph, ExactIndex
from relationships import *
from bulbs.element import Vertex
# Import XML parser
import xml.etree.ElementTree as ET

print "Starting processing at ", datetime.datetime.now()

# Neo4J Test
g = Graph()
g.add_proxy("agents", Agent)
g.add_proxy("places", Place)
g.add_proxy("documents", Document)
g.add_proxy("associated", AssociatedWith)
g.add_proxy("corresponded", CorrespondedWith)
g.add_proxy("referencedIn", ReferencedIn)
g.add_proxy("location", Location)

g.vertices.occindex = g.factory.get_index(Vertex, ExactIndex, "occupationIndex")
g.vertices.subindex = g.factory.get_index(Vertex, ExactIndex, "subjectIndex")

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

# Counter
counter = 0

# For each file, parse and fill out node information
path = "sample/"
for filename in os.listdir(path):
    counter = counter + 1
    tree = ET.parse(os.path.join(path,filename))
    root = tree.getroot()

    identifier = ""
    subjects = []
    nationalities = []
    alt_names = []
    realname = ""
    places = []
    placesIDs = []
    occupations = []
    languages = []
    associated = []
    corresponded = []
    sameas = []
    entity_type = ""
    start = None
    end = None

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
            realname = node[0].text
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
        places.append([node.get("vocabularySource"), node.text, node.get("latitude"), node.get("longitude")])
        placesIDs.append(node.get("vocabularySource"))

    # Handle occupations
    for node in root.findall(".//snac:occupation", namespaces):
        occupations.append(node[0].text)

    # Handle languages
    for node in root.findall(".//snac:languageUsed", namespaces):
        languages.append(node[0].get("languageCode"))
    
    # Handle sameAs relationships
    for node in root.findall(".//snac:cpfRelation", namespaces):
        role = node.get("{http://www.w3.org/1999/xlink}arcrole")
        link = node.get("{http://www.w3.org/1999/xlink}href")
        if "sameAs" in role:
            sameas.append(link)
        
    # Create a node in the database for this object
    # Create an Agent
    pnode = g.agents.create(
            snac_type=hidden_type,
            identifier=identifier, 
            name=realname)
    if alt_names:
        pnode.altnames=alt_names
    if subjects:
        pnode.subjects=subjects
        for sub in subjects:
            g.vertices.subindex.put(pnode.eid, subject=sub)
    if occupations:
        pnode.occupations=occupations
        for occ in occupations:
            g.vertices.occindex.put(pnode.eid, occupation=occ)
    if languages:
        pnode.languages=languages
    if start:
        pnode.startDate=start
    if end:
        pnode.endDate=end
    if sameas:
        pnode.sameAs=sameas
    # Handle places (need to create them if they don't exist)
    if places:
        pnode.places=placesIDs
        for place in places:
            tonodes = g.places.index.lookup(identifier=place[0])
            tonode = None
            if tonodes:
                tonode = tonodes.next()
            else:
                tonode = g.places.create(identifier=place[0], name=place[1], latitude=place[2], longitude=place[3])

            if tonode:
                    rel = g.location.create(pnode, tonode)
                    rel.save()



    # Save the node so we can work on the next
    pnode.save()

    if counter % 1000 == 0:
        print "Imported ", counter, " nodes at ", datetime.datetime.now()

# Print that the nodes have been created
print "Nodes have been successfully created at ", datetime.datetime.now()

# Counter
counter = 0

# For each file, parse and fill out edge information
path = "sample/"
for filename in os.listdir(path):
    counter = counter + 1
    tree = ET.parse(os.path.join(path,filename))
    root = tree.getroot()

    associated = []
    corresponded = []
    
    # Handle identifier
    node = root.find(".//snac:recordId", namespaces)
    identifier = node.text
    
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

    
    # Input the relationships into the database
    #rel = g.associated.create(gw, tj)
    #rel.save()

    pnode = None
    pnodes = g.agents.index.lookup(identifier=identifier)
    pnode = pnodes.next()
    
    if pnode is not None:
        for assoc in associated:
            tonodes = g.agents.index.lookup(identifier=assoc)
            if tonodes:
                tonode = tonodes.next()
                if tonode:
                    rel = g.associated.create(pnode, tonode)
                    rel.save()
        for corr in corresponded:
            tonodes = g.agents.index.lookup(identifier=corr)
            if tonodes:
                tonode = tonodes.next()
                if tonode:
                    rel = g.corresponded.create(pnode, tonode)
                    rel.save()

    if counter % 1000 == 0:
        print "Imported ", counter, " node-edges at ", datetime.datetime.now()

print "Edges have been successfully created at ", datetime.datetime.now()

