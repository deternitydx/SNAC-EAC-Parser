# Provides the graph entities for our server
from bulbs.model import Node, Relationship
from bulbs.property import String, Integer, DateTime
from bulbs.utils import current_datetime
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

class Person(Node):
    element_type = "person"
    identifier = String(nullable=False)
    name = String(nullable=False)

class Corporation(Node):
    element_type = "corporate"
    identifier = String(nullable=False)
    name = String(nullable=False)

class Place(Node):
    element_type = "place"
    identifier = String(nullable=False)
    name = String(nullable=False)
    latitude = String()
    longitude = String()

class Subject(Node):
    element_type = "subject"
    name = String(nullable=False)

class Document(Node):
    element_type = "document"
    identifier = String(nullable=False)
    name = String(nullable=False)

class Occupation(Node):
    element_type = "occupation"
    name = String(nullable=False)

class AssociatedWith(Relationship):
    label = "associatedWith"

class CorrespondedWith(Relationship):
    label = "correspondedWith"

class ReferencedIn(Relationship):
    label = "referencedIn"
