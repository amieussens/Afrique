import http.server
import socketserver
import sqlite3
import json

from urllib.parse import urlparse, parse_qs, unquote

# Définition du nouveau handler

class RequestHandler(http.server.SimpleHTTPRequestHandler):

  # sous-répertoire racine des documents statiques
  static_dir = '/client'

  # version du serveur
  server_version = 'countries/0.1'

  #
  # Surcharge de la méthode qui traite les requêtes GET
  #
  def do_GET(self):
    # Récupération des paramètres
    self.init_params()

    # le chemin d'accès commence par /countries
    if self.path.startswith('/countries'):
      self.send_countries()

    # le chemin d'accès commence par /country et se poursuit par un nom de pays
    elif self.path_info[0] == 'country' and len(self.path_info) > 1:
      self.send_country(self.path_info[1])
      
    # le chemin d'accès commence par /service/countries/...
    elif self.path_info[0] == 'service' and self.path_info[1] == 'countries' and len(self.path_info) > 1:
      continent = self.path_info[2] if len(self.path_info) > 2 else None
      self.send_json_countries('africa')

    # le chemin d'accès commence par /service/country/...
    elif self.path_info[0] == 'service' and self.path_info[1] == 'country' and len(self.path_info) > 2:
      self.send_json_country(self.path_info[2])
      
      
    elif self.path_info[0] == "location":
      r = self.db_get_countries('africa')
      data = [{k:a[k] for k in a.keys()} for a in r]
      print(data)
      self.send_json(data)
      
    elif self.path_info[0] == "description":
      r = self.db_get_countries('africa') 
      data = [{k:a[k] for k in a.keys()} for a in r]
      for c in data:
        if c['id'] == int(self.path_info[1]):
          self.send_json(c)
          break

    # ou pas...
    else:
      self.send_static()

  # Surcharge de la méthode qui traite les requêtes HEAD

  def do_HEAD(self):
    self.send_static()

  # Envoi du document statique demandé

  def send_static(self):

    # Modification du chemin d'accès en insérant un répertoire préfixe
    self.path = self.static_dir + self.path

    # Appel de la méthode parent (do_GET ou do_HEAD)
    # à partir du verbe HTTP (GET ou HEAD)
    if (self.command=='HEAD'):
        http.server.SimpleHTTPRequestHandler.do_HEAD(self)
    else:
        http.server.SimpleHTTPRequestHandler.do_GET(self)
    
  # Analyse de la requête pour initialiser nos paramètres

  def init_params(self):
    # Analyse de l'adresse
    info = urlparse(self.path)
    self.path_info = [unquote(v) for v in info.path.split('/')[1:]]  # info.path.split('/')[1:]
    self.query_string = info.query
    self.params = parse_qs(info.query)

    # Récupération du corps
    length = self.headers.get('Content-Length')
    ctype = self.headers.get('Content-Type')
    if length:
      self.body = str(self.rfile.read(int(length)),'utf-8')
      if ctype == 'application/x-www-form-urlencoded' : 
        self.params = parse_qs(self.body)
    else:
      self.body = ''
   
    # Traces
    print('path_info =',self.path_info)
    print('body =',length,ctype,self.body)
    print('params =', self.params)