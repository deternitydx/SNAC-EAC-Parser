# Provides the graph entities for our server
from bulbs.model import Node, Relationship
from bulbs.property import String, Integer, DateTime
from bulbs.utils import current_datetime

class Person(Node):
    element_type = "person"
    name = String(nullable=False)

class Corporation(Node):
    element_type = "corporate"
    name = String(nullable=False)

class Document(Node):
    element_type = "document"
    name = String(nullable=False)

class AssociatedWith(Relationship):
    label = "associatedWith"

class CorrespondedWith(Relationship):
    label = "correspondedWith"

class ReferencedIn(Relationship):
    label = "referencedIn"
