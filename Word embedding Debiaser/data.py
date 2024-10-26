import json
import os

"""
Tools for data operations

Man is to Computer Programmer as Woman is to Homemaker? Debiasing Word Embeddings
Tolga Bolukbasi, Kai-Wei Chang, James Zou, Venkatesh Saligrama, and Adam Kalai
2016
"""
PKG_DIR = os.path.dirname(os.path.abspath(__file__))


def load_professions():
    professions_file = os.path.join(PKG_DIR, 'data', 'professions.json')
    with open(professions_file, 'r') as f:
        professions = json.load(f)

    return professions
