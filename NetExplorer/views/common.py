from django.shortcuts   import render
from django.shortcuts   import render_to_response
from django.http        import HttpResponse
from django.template    import RequestContext
from NetExplorer.models import *
from subprocess import Popen, PIPE, STDOUT
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db import connection
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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

# -----------------------
# CONSTANTS
# -----------------------
BLAST_DB_DIR    = "/home/sergio/code/PlanNET/blast/"
MAX_NUMSEQ      = 50
MAX_CHAR_LENGTH = 25000


# -----------------------
# FUNCTIONS
# -----------------------

def get_databases(request):
    '''
    This function returns the databases allowed for the user to see
    '''
    if not request.user.is_authenticated():
        return sorted(DATABASES)
    else:
        # User is logged in, get the allowed databases for the user
        try:
            cursor = connection.cursor()
            cursor.execute('''
                SELECT auth_user.username, user_db_permissions.database
                FROM auth_user
                INNER JOIN user_db_permissions ON auth_user.id=user_db_permissions.user_id
                WHERE auth_user.username = %s;
            ''', [request.user.username])
            rows = cursor.fetchall()
            user_databases = set(DATABASES)
            user_databases.update([row[1] for row in rows])
            return sorted(user_databases)
        except Exception:
            return sorted(DATABASES)


# ------------------------------------------------------------------------------
def symbol_is_empty(symbol):
    '''
    Checks if the input symbol from the forms is empty or not
    '''
    if re.match(r"[a-zA-Z0-9]", symbol):
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
                    graphelements[numpath].add_elements(path.graph.nodes)
                    graphelements[numpath].add_elements(path.graph.edges)
                    graphelements[numpath] = (graphelements[numpath].to_json, round(path.score, 2))
                    numpath += 1
    return graphelements, numpath
