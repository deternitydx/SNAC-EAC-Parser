# Provides the graph entities for our server
from bulbs.model import Node, Relationship
from bulbs.property import String, Integer, DateTime, List
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

class Agent(Node):
    element_type = "agent"
    snac_type = String(nullable=False, indexed=True)
    identifier = String(nullable=False, indexed=True)
    name = String(nullable=False)
    altNames = List()
    startDate = String()
    endDate = String()
    occupations = List()
    subjects = List()
    languages = List()
    nationalities = List()
    places = List()
    sameAs = List()

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

class Location(Relationship):
    label = "associatedPlace"
