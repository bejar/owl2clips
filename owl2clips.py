"""
.. module:: owl2clips

owl2clips
******

:Description: owl2clips

    Transforms an OWL ontology to COOL CLIPS Language

:Authors:
    bejar

:Version: 

:Date:  08/05/2020
"""

__author__ = 'bejar'

from rdflib.util import find_roots, get_tree
from rdflib import Graph, URIRef, Literal
from rdflib import RDFS, RDF, OWL
from owlobjects import owlclass, owlprop, owlinstance

def tree_to_list(tree):
    """
    Transforms a tree structure on a list recursivelly
    :return:
    """
    root = [tree[0]]
    if tree[1] is not []:
        descendants =  [tree_to_list(l) for l in tree[1]]
    for f in descendants:
        root.extend(f)
    return root


def get_class_hierarchy(g):
    """
    Extract the class hierarchy

    :return:
    """
    # get all the classes
    r = g.subjects(RDF.type,OWL.Class)

    # get all the roots of the subClassOf relation (classes without subclasses will be missing)
    a = find_roots(g,RDFS.subClassOf)

    # Set of all classes on the subClassOf tree
    SCOset = set()
    roots = []
    for p in a:
        t = get_tree(g, p, RDFS.subClassOf)
        roots.append(t)
        tl = tree_to_list(t)
        for l in tl:
            SCOset.add(l)

    for c in r:
        if c not in SCOset:
            roots.append((c, []))

    return roots

def build_hierarchy(g, tree):
    """
    Creates the properties of each class
    :param trees:
    :return:
    """
    root = tree[0]
    node = owlclass(root)
    node.get_attributes_from_graph(g)
    node.get_properties_from_graph(g)
    desc = [build_hierarchy(g,n) for n in tree[1]]
    for d in desc:
        d[0].parent = node

    return [node, desc]

def get_individuals(g, cdict):
    """
    Obtains all instances
    :return:
    """
    # get all the individuals
    r = g.subjects(RDF.type,OWL.NamedIndividual)

    lins = []
    for i in r:
        ins = owlinstance(i)
        ins.get_attributes_from_graph(g)
        ins.get_info_from_graph(g, cdict)
        lins.append(ins)

    return lins

def generate_classes_clips(hierarchy):
    print(hierarchy[0].toCLIPS())
    lclass = []
    for h in hierarchy[1]:
        lclass.extend(generate_classes_clips(h))
    lclass.extend([hierarchy[0]])
    return lclass

def generate_individuals_clips(individuals):
    """
    Generates all the individuals
    :param individuals:
    :return:
    """

    print("(definstances instances\n")
    for i in individuals:
        print(i.toCLIPS())

    print(")\n")


if __name__ == '__main__':
    g = Graph()

    # Carga el grafo RDF desde el fichero
    g.parse("CLIPSTest.owl", format='turtle')
    #g.parse("proton-top.ttl", format='turtle')
   # g.parse("fipa-acl-new.owl", format='xml')
   #  g.parse("TravelOntology.owl", format='xml')

    hierarchy = get_class_hierarchy(g)

    if hierarchy[0][0] == OWL.Thing :
        hierarchy = hierarchy[0][1]

    classes_dict = {}
    for h in hierarchy:
        ch = build_hierarchy(g, h)
        lclass = generate_classes_clips(ch)
        for c in lclass:
            classes_dict[c.name] = c

    individuals = get_individuals(g, classes_dict)

    generate_individuals_clips(individuals)



