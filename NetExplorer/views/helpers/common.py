from django.shortcuts   import render
from django.shortcuts   import render_to_response
from django.template.loader import render_to_string
from django.http        import HttpResponse
from django.template    import RequestContext
from NetExplorer.models import *
from django.db.models import Func, F
from subprocess import Popen, PIPE, STDOUT
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import serializers
from statistics import stdev, mean
from django.db.models import Sum
from django.db.models import FloatField
from django.db.models.functions import Cast
import tempfile
import textwrap
import json
import re
import logging
import math
import time
import requests
import time
import os
import numpy as np
import random

#from django import template


# -----------------------
# CONSTANTS
# -----------------------
BLAST_DB_DIR    = "/home/sergio/code/PlanNET/blast/"
MAX_NUMSEQ      = 50
MAX_CHAR_LENGTH = 25000
#register = template.Library()


# -----------------------
# FUNCTIONS
# -----------------------
# ------------------------------------------------------------------------------
def symbol_is_empty(symbol):
    '''
    Checks if the input symbol from the forms is empty or not
    '''
    if re.match(r"[a-zA-Z0-9_]", symbol):
        return False
    else:
        return True

# ------------------------------------------------------------------------------
def get_shortest_paths(startnodes, endnodes, plen):
    '''
    This function gets all the possible shortest paths between the specified nodes.
    Returns a json string with all the nodes and edges, the length of the paths and
    the total number of paths
    '''
    graphelements = list()
    numpath = 0
    for snode in startnodes:
        for enode in endnodes:
            paths = snode.path_to_node(enode, plen)
            if paths is None:
                # Return no-path that matches the query_node
                continue
            else:
                for path in paths:
                    graphelements.append( GraphCytoscape() )
                    graphelements[numpath].add_elements(path.nodes)
                    graphelements[numpath].add_elements(path.edges)
                    graphelements[numpath] = (graphelements[numpath].to_json, round(path.score, 2))
                    numpath += 1
    return graphelements, numpath


def disambiguate_gene(gene_name, dataset):
    gene_graph = GraphCytoscape()
    gene_symbols = list()
    try:
        gene_graph.new_nodes([gene_name], dataset)
        gene_symbols = [ gene.symbol for gene in list(gene_graph.nodes) ]
    except Exception as err:
        gene_symbols = [ gene_name ]
    if not gene_symbols:
        gene_symbols = [gene_name]
    return gene_symbols



def condition_sort(x):
    '''
    Sort conditions by 
        - Single-vs-Interaction, 
        - Name.
        - Number (if any in name)
    Returns tuple (int, int, string)
    '''
    if "-" in x.name:
        # Interaction condition
        regex = re.search(r'(\d+).+\-(.+)', x.name)
        if regex:
            return (1, regex.group(2), int(regex.group(1)))
        else:
            regex = re.search(r'(.*?)(\d+)', x.name)
            if regex:
                return (1, str(regex.group(1)), int(regex.group(2)))
            else:
                return (1, x.name, 0)
    else:
        # Single condition
        regex = re.search(r'(\d+)([a-zA-Z]+)', x.name)
        if regex:
            return (0, str(regex.group(2)), int(regex.group(1)))
        else:
            regex = re.search(r'(.*?)(\d+)', x.name)
            if regex:
                return (0, str(regex.group(1)), int(regex.group(2)))
            else:
                return (0, x.name, 0)
