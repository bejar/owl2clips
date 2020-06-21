"""
.. module:: owlobjects

owlobjects
******

:Description: owlobjects

    Classes for different owl objects

:Authors:
    bejar

:Version: 

:Date:  08/05/2020
"""
from rdflib import RDFS, RDF, OWL, XSD

__author__ = 'bejar'

datatypes = {XSD.string: 'STRING)',
             XSD.integer: 'INTEGER',
             XSD.int: 'INTEGER',
             XSD.float: 'FLOAT',
             XSD.double: 'FLOAT'}

class owlobject:
    def __init__(self, uriref):
        """
        Initialize the class
        """
        self.uriref = uriref
        self.name = self.chop(uriref)
        self.attributes = {RDFS.comment: '', RDFS.label:''}

    def get_attributes_from_graph(self, graph):
        for predicate in self.attributes:
            v = graph.value(self.uriref, predicate)
            self.attributes[predicate] = v if v is not None else ''

    def chop(self, uriref):
        if '#' in uriref:
            return uriref.toPython().split("#")[-1]
        elif '/' in uriref:
            return uriref.toPython().split("/")[-1]
        else:
            return uriref

class owlclass(owlobject):
    """
    Class for representing the data for an OWL class
    """

    def __init__(self, uriref):
        """
        Initialize the class
        """
        super(owlclass, self).__init__(uriref)
        self.properties = []
        self.parent = None

    def get_properties_from_graph(self, graph):
        # Get all properties that have this class as domain
        props = graph.subjects(RDFS.domain, self.uriref)

        for p in props:
            pr = owlprop(p)
            pr.get_attributes_from_graph(graph)
            self.properties.append(pr)

    def __repr__(self):
        s = f'N= {self.name} '
        for a in self.attributes:
            s+= f'{self.chop(a)} = {self.attributes[a]}'

        for p in self.properties:
            s+= f'\n PR= {p.__repr__()} '

        return s

    def toCLIPS(self):
        """
        Generates a representation of the class using COOL CLIPS language
        :return:
        """
        comment = self.attributes[RDFS.comment].strip("\n").strip(" ").strip("\n")
        s = f'(defclass {self.name} "{comment}"\n'
        if self.parent is None:
            s += '    (is-a USER)\n'
        else:
            s += f'    (is-a {self.parent.name})\n'
        s+= '    (role concrete)\n    (pattern-match reactive)\n'
        for p in self.properties:
            s += '    ' + p.toCLIPS()

        s += ')\n'
        return s


class owlprop(owlobject):
    """
    class for OWL properties
    """
    def __init__(self, uriref):
        """
        Initialize the class
        """
        super(owlprop, self).__init__(uriref)
        self.attributes[RDF.type] = ''
        self.attributes[RDFS.range] = ''

    def __repr__(self):
        s = f'N= {self.name} '
        for a in self.attributes:
            s += f'{self.chop(a)} = {self.chop(self.attributes[a])} '
        return s

    def toCLIPS(self):
        s = f'(multislot {self.name}'
        if self.attributes[RDF.type] == OWL.DatatypeProperty:
            if self.attributes[RDFS.range] in datatypes:
                s += f' (type {datatypes[self.attributes[RDFS.range]]})'
            else:
                s += ' (type SYMBOL)'
        else:
            s += ' (type INSTANCE)'
        return s + ')\n'


