# coding: utf-8
#!/usr/bin/env python

""" Evaluate two kind of summeries (models/systems) with the ROUGE score

"""

import re
import os
import sys
import argparse
import xml.etree.ElementTree as ET

#######################################################################

__author__ = "Remi Cadene"

#######################################################################


class Summary(object):
    
    def __init__(self, path2file):
        self.path2file = path2file
        self.lines = []
    
    def getLines(self):
        return self.lines    
    
    def loadFromOriginal(self):
        """ The only saved lines are preceded by a '*'.
        """  
        with open(self.path2file, 'r') as f:
            for i, line in enumerate(f):
                reg = r"^\* *(.+)\n"
                match = re.findall(reg, line)
                if match:
                    EDU = match[0]
                    self.lines.append(EDU)


class SummariesFactory(object):

    @staticmethod
    def loadFromOriginal(path2files):
        summaries = []
        for path in path2files:
            summary = Summary(path)
            summary.loadFromOriginal()
            summaries.append(summary)
        return summaries


class Rouge(object):
    """ Help to evaluate the summaries generated by your system(s)
        using the summaries wroten by your peers and the rouge
        score ROUGE-1.5.5.pl
    """
    
    def __init__(self, path2rouge='../ROUGE-1.5.5/ROUGE-1.5.5.pl',
                 path='./', models=[], systems=[]):
        self.path2rouge = path2rouge
        self.path = path 
        self.models = models
        self.systems = systems
    
    def createModels(self):
        """ Create the models files which are reference summaries that
            will be used for evaluation. Each file can be identified by
            the the the set of documents for which the summary was
            generated. Say, a summary was generated for document set 3,
            by human 2. Then the file name can be something like
            human2_doc3.html
        """
        self.createSummaries('models')
      
    def createSystems(self):
        """ Create the systems files which are generated summaries that
            will be used for evaluation. Each file can be identified by
            the id of the system and the set of documents for which the
            summary was generated. Say, a summary was generated for
            document set 3, by system 1. Then the file name can be
            something like system1_doc3.html.
        """
        self.createSummaries('systems')
    
    def createSummaries(self, type='models'):
        if not os.path.exists(self.path + type):
            os.mkdir(self.path + type)
        summaries = self.models if type == 'models' else self.systems
        for summ_id, summary in enumerate(summaries):
            html = ET.Element('html')
            head = ET.SubElement(html, 'head')
            title = ET.SubElement(head, 'title').text = str(summ_id)
            body = ET.SubElement(html, 'body', bgcolor="white")
            for line_id, line in enumerate(summary.getLines()):
                a = ET.SubElement(body, 'a', name=str(line_id))
                a.text = '[' + str(line_id) + ']'
                href = '#' + str(line_id)
                a = ET.SubElement(body, 'a', href=href, id=str(line_id))
                a.text = line
            tree = ET.ElementTree(html)
            tree.write(self.path + type + '/' + str(summ_id) + '.html')
            with open(self.path + type + '/' + str(summ_id) + '.html', 'r+') as f:
                data = f.read()
                # replace id="1" by id=1
                replaced = re.sub(r'id="([0-9]+)"', r'id=\1', data)
                # add \n afeter <body
                replaced = re.sub(r'<body bgcolor="white">', r'<body bgcolor="white">\n', replaced)
                # add space after ]</a>
                replaced = re.sub(r']</a>', r']</a> ', replaced)
                # add \n after the other </a>
                replaced = re.sub(r'([a-zA-Z0-9 ])</a>', r'\1</a>\n', replaced)
                f.seek(0)
                f.write(replaced)
                f.truncate()
    
    def createSettings(self):
        """ The file settings.xml is the core file that
            specifies which peer summaries should use
            which model summaries for evaluation.
        """
        rouge_eval = ET.Element('ROUGE-EVAL', version="1.5.5")
        eval = ET.SubElement(rouge_eval, 'EVAL', ID="1")
        peer_root = ET.SubElement(eval, 'PEER-ROOT').text = self.path + 'systems'
        model_root = ET.SubElement(eval, 'MODEL-ROOT').text = self.path + 'models'
        input_format = ET.SubElement(eval, 'INPUT-FORMAT', TYPE="SEE")
        peers = ET.SubElement(eval, 'PEERS') # systems files
        for i in xrange(len(self.systems)):
            m = ET.SubElement(peers, 'P', ID=str(i)).text = str(i) + '.html'
        models = ET.SubElement(eval, 'MODELS')
        for i in xrange(len(self.models)):
            m = ET.SubElement(models, 'M', ID=str(i)).text = str(i) + '.html'
        tree = ET.ElementTree(rouge_eval)
        tree.write(self.path + 'settings.xml')  
    
    def evaluation(self):
        """ system call to ROUGE-1.5.5 """
        syscall = 'perl ' + self.path2rouge
        #syscall += ' -e data -c 95 -2 -1 -U -r 1000 -n 4 -w 1.2'
        syscall += ' -e ' + self.path2rouge + 'data'
        syscall += ' -a ' + self.path + 'settings.xml'
        print syscall
        os.system(syscall)



if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('path2rouge', type=str,
                        help="path to the file ROUGE-1.5.5.pl")
    parser.add_argument('path', type=str,
                        help="path to the directory used for the generation of the rouge files")
    parser.add_argument('-s', '--systems', type=str, nargs='+', required=True,
                        help="path to the systems generated summary files")
    parser.add_argument('-m', '--models', type=str, nargs='+', required=True,
                        help="path to the reference summary files")
    args = parser.parse_args()
    #print args

    models = SummariesFactory.loadFromOriginal(args.models)
    systems = SummariesFactory.loadFromOriginal(args.systems)

    rouge = Rouge(args.path2rouge, args.path, models, systems)
    rouge.createModels()
    rouge.createSystems()
    rouge.createSettings()
    rouge.evaluation()
    



