# coding: utf-8
#!/usr/bin/env python

import os
import re
import argparse

#######################################################################

__author__ = "Remi Cadene"

#######################################################################

class Evaluation:

    def __init__(self, path2rslt='./rslt/'
                 path2txt='./corpus/txt/',
                 path2summaries='./corpus/summaries/',
                 path2models='./corpus/RST-DT/EXT-EDUS-30/',
                 path2summaries2rouge='./src/summaries2rouge/summaries2rouge.py',
                 path2rouge2csv='./src/rouge2csv/rouge2csv.py',
                 path2rouge='./src/ROUGE-1.5.5/ROUGE-1.5.5.pl',
                 path2summarize='./../SummarizeApp/discourse/src/summarize.py'):
        self.path2txt = path2txt
        self.path2summaries = path2summaries
        self.path2model = path2models
        self.path2summaries2rouge = path2summaries2rouge
        self.path2rouge2csv = path2rouge2csv
        self.path2rouge = path2rouge
        self.path2summarize = path2summarize
        self.model_fname_EDUs = {}
        self.extensions = ['.abs.name1', '.abs.name2', '.ext.name4',
                           '.shortabs.name1', '.shortabs.name2']

    def loadModels(self):
        """ First method to call in order to recover the number of EDUs
            for each model files """
        model_fnames = []
        model_EDUs = []
        for fname in os.listdir(self.path2model):
            nb_EDUs = 0
            with open(self.path2model + fname, 'r') as f:
                for line in f:
                    reg = r"^\* *(.+)\n"
                    match = re.findall(reg, line)
                    if match:
                        nb_EDUs += 1
            self.model_fname_EDUs[fname] = nb_EDUs
            model_fnames.append(fname)
            model_EDUs.append(nb_EDUs)
        # for i, nb_EDUs in enumerate(model_EDUs):
        #     if i > 0 and i % 5 == 0:
        #         print "--"
        #     print nb_EDUs
        # return model_fnames, model_EDUs

    def generateSummaries(self):
        """ Second method to call in order to generate the summaries
            for each txt files (optionnal if you already have them)
        """
        for fname in os.listdir(self.path2txt):
            name = fname.split('.')[0]
            for ext in self.extensions:
                model_fname = name + ext
                l = self.model_fname_EDUs[model_fname]
                path2file = self.path2txt
                input_fname = fname
                output_fname = model_fname
                self.__syscallSummarize(l, path2file,
                            input_fname, output_fname)


    def __syscallSummarize(self, l='10', path2file='./',
                           input_fname='file1.txt',
                           output_fname='file1.abs.name1'):
        syscall = 'python ' + path2summarize
        syscall += ' -l ' + l
        #syscall += ' -d ' + self.path2rslt + output_fname
        syscall += ' ' + path2file + input_fname
        syscall += ' > ' + self.path2summaries + output_fname
        os.system(syscall)
    

    def generateRougeScore(self):
        """ Third method to call in order to generate the
            ROUGE score
        """
        for fname in os.listdir(self.path2txt):
            name = fname.split('.')[0]
            for ext in self.extensions:
                system_fname = name + ext
                model_fname = system_fname
                self.__syscallRouge(model_fname, system_fname)


    def __syscallRouge(self, model_fname='file1.abs.name1',
                       system_fname='file1.abs.name1'):
        syscall = 'python ' + self.path2summary2rouge
        syscall += ' ' + self.path2rouge
        syscall += ' ' + self.path2rslt
        syscall += ' -m'
        syscall += ' ' + self.path2rst + model_fname
        syscall += ' -s'
        syscall += ' ' + self.path2summeries + system_fname
        os.system(syscall)


    
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('path2summarize', type=str,
                        help="path to the file summarize.py",
                        default='./../SummarizeApp/discourse/src/summarize.py')
    args = parser.parse_args()

    evaluation = Evaluation(path2summarize=args.path2summarize)
    evaluation.loadModels()
    evaluation.generateSummaries()
    evaluation.generateRougeScore()
    


