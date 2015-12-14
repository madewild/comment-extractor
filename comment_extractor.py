#!/usr/bin/env python
# coding: utf-8

import re, codecs, os, sys, time
import urllib,urllib2
import json
from bs4 import BeautifulSoup as bs
from collections import defaultdict

reload(sys)
sys.setdefaultencoding("utf-8")

corpus = "test"

output = codecs.open("comments.tsv", "w", "utf-8")
output.write("Journal\tMot clé\tArticle\tDate de publication\tDate de mise à jour\tURL\tCommentaire\tDate commentaire\tAuteur\tProfil FB\tRéponse à\n")
journaux = os.listdir(corpus)
for journal in sorted(journaux):
  motscles = os.listdir(os.path.join(corpus,journal))
  for motcle in sorted(motscles):
    articles = os.listdir(os.path.join(corpus,journal,motcle))
    for article in sorted(articles):
      if article.endswith("htm") or article.endswith("html"):
        title = ""
        url = ""
        datepub = ""
        datemaj = ""
        html = open(os.path.join(corpus,journal,motcle,article)).read()
        soup = bs(html, "html.parser")
        titre = soup.title.string
        if journal == "Lesoir":
          metas = soup.find_all("meta")
          prop = ""
          for meta in metas:
            try:
              prop = meta.get("property")
            except TypeError:
              pass
            if prop == "og:url":
              url = meta.get("content")
          metas = soup.find_all("div", attrs={'class':'meta'})
          for meta in metas:
            times = meta.find_all("time")
            datetext = times[0].string
            try:
              datepub = time.strptime(datetext, '%A %d %B %Y, %Hh%M')
            except (ValueError,TypeError):
              pass
        else:
          links = soup.find_all("link")
          for link in links:
            if link.get("rel")[0] == "canonical":
              url = link.get("href")
          spans = soup.find_all("span", attrs={'class':'publication'})
          for span in spans:
            times = span.find_all("time")
            datepub = times[0].get("datetime")
            if len(times)>1:
              datemaj = times[1].get("datetime")
        n = 4
        ext = "htm"
        if article.endswith("html"):
          n = 5
          ext="html"
        comdir1 = article[:-n]+"_fichiers"
        comdir2 = article[:-n]+"_files"
        comfile1 = os.path.join(comdir1,'comments.'+ext)
        comfile2 = os.path.join(comdir2,'comments.'+ext)
        try:
          comhtml = open(os.path.join(corpus,journal,motcle,comfile1)).read()
        except IOError:
          try:
            comhtml = open(os.path.join(corpus,journal,motcle,comfile2)).read()
          except IOError:
            print comdir2,comfile2
            break
        try:
          ia = comhtml.index('{"comments"')
        except ValueError:
          print os.path.join(corpus,journal,motcle,comfile1)
        iz = comhtml.index(',"u_0_0')
        jcode = json.loads(comhtml[ia:iz])
        print jcode
        artid = jcode["meta"]["targetFBID"]
        comids = jcode["comments"]["idMap"].keys()
        for comid in sorted(comids):
          if "_" in comid:
            comtext = jcode["comments"]["idMap"][comid]["body"]["text"]
            comtext = re.sub(r'\n+',' ', comtext)
            comts = jcode["comments"]["idMap"][comid]["timestamp"]["time"]
            comtuple = time.localtime(comts)
            comtime = time.strftime('%Y-%m-%d %H:%M:%S', comtuple)
            authorid = jcode["comments"]["idMap"][comid]["authorID"]
            authorname = jcode["comments"]["idMap"][authorid]["name"]
            authoruri = jcode["comments"]["idMap"][authorid]["uri"]
            targetid = jcode["comments"]["idMap"][comid]["targetID"]
            if targetid == artid:
              target = "Article principal"
            else:
              targetauthorid = jcode["comments"]["idMap"][targetid]["authorID"]
              target = jcode["comments"]["idMap"][targetauthorid]["name"]
            liste = [journal, motcle, titre, datepub, datemaj, url, comtext, comtime, authorname, authoruri, target]
            string = "\t".join(liste)
            output.write(string)
            output.write("\n")
output.close()
