import numpy as np
import pandas as pd
from tools import WordEmbedding
import learn_gender_specific
import data
import json
import debias


#constants
delta = 1
lambd = 0.2
analogies = []
hard_analogies = []
soft_analogies = []

bias_model = WordEmbedding("w2v_gnews_small.txt")
hard_model = WordEmbedding("w2v_gnews_small.txt")
soft_model = WordEmbedding("w2v_gnews_small.txt")


#Load jobs
professions = data.load_professions()
professions_words = [p[0] for p in professions]
#Find gender direction of subspacea
gender_Dir = bias_model.diff('she', 'he')
#Create analogies between gender and professions
gender_analogies = bias_model.best_analogies_dist_thresh(gender_Dir)
for (a,b,c) in gender_analogies:
    analogies.append([a, b])


with open('./data/definitional_pairs.json', "r") as f:
    defs = json.load(f)

with open('./data/equalize_pairs.json', "r") as f:
    equalize_pairs = json.load(f)

with open('./data/gender_specific_seed.json', "r") as f:
    gender_specific_words = json.load(f)

debias.debias(hard_model, gender_specific_words, defs, equalize_pairs)


#Soft debiasing

vectors = soft_model.vecs

def debias_single_word(embedding, W, lambd):
    x_i = embedding
    I = np.eye(len(x_i))

    # Calculate debiased embedding using the equation
    x_i_db = np.linalg.inv(I + lambd * W) @ x_i

    return x_i_db

W = np.outer(gender_Dir, gender_Dir)
for count, i in enumerate(vectors):
    print(count)
    soft_model.vecs[count] = debias_single_word(i, W, lambd)


def cosine_similarity(a, b):
    return np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b))

#Define method for returning the effect size
def weat_value(target1, target2, attribute1, attribute2, permutations=False):


    # Compute the mean embeddings for the target and attribute words
    t1_embedding = np.mean([word for word in target1], axis=0)
    t2_embedding = np.mean([word for word in target2], axis=0)
    a1_embedding = np.mean([word for word in attribute1], axis=0)
    a2_embedding = np.mean([word for word in attribute2], axis=0)


    # Compute the cosine similarities between the target and attribute embeddings
    sim_t1_a2 = cosine_similarity(t1_embedding, a2_embedding)
    sim_t2_a1 = cosine_similarity(t2_embedding, a1_embedding)
    sim_t2_a2 = cosine_similarity(t2_embedding, a2_embedding)
    sim_t1_a1 = cosine_similarity(t1_embedding, a1_embedding)

    # Compute the means and standard deviations of the cosine similarities
    mean_t1_a = np.mean([sim_t1_a1, sim_t1_a2])
    mean_t2_a = np.mean([sim_t2_a1, sim_t1_a2])
    std_t1_a = np.std([sim_t1_a1, sim_t1_a2])
    std_t2_a = np.std([sim_t2_a1, sim_t2_a2])

    # Compute the effect size using Cohen's d
    effect_size = (mean_t1_a - mean_t2_a) / np.sqrt((std_t1_a ** 2 + std_t2_a ** 2) / 2)
    
    value = mean_t1_a-mean_t2_a
    return effect_size, value




equalize_pairs = np.array(equalize_pairs)
female_vectors = [bias_model.v(word) for word in equalize_pairs[:,0] if np.linalg.norm(bias_model.v(word)) != 0]
male_vectors = [bias_model.v(word) for word in equalize_pairs[:,1] if np.linalg.norm(bias_model.v(word)) != 0]


bias_analogy1_vectors = [bias_model.v(word[0]) for word in analogies]
bias_analogy2_vectors = [bias_model.v(word[1]) for word in analogies]
analogies = np.array(analogies)


#Find gender direction of subspace
gender_Dir = hard_model.diff('she', 'he')
#Create analogies between gender and professions
hard_gender_analogies = hard_model.best_analogies_dist_thresh(gender_Dir)
for (a,b,c) in hard_gender_analogies:
    hard_analogies.append([a, b])

hard_analogy1_vectors = [hard_model.v(word[0]) for word in hard_analogies]
hard_analogy2_vectors = [hard_model.v(word[1]) for word in hard_analogies]
hard_analogies = np.array(hard_analogies)


#Find gender direction of subspace
gender_Dir = soft_model.diff('she', 'he')
#Create analogies between gender and professions
soft_gender_analogies = soft_model.best_analogies_dist_thresh(gender_Dir)
for (a,b,c) in soft_gender_analogies:
    soft_analogies.append([a, b])

soft_analogy1_vectors = [soft_model.v(word[0]) for word in soft_analogies]
soft_analogy2_vectors = [soft_model.v(word[1]) for word in soft_analogies]
soft_analogies = np.array(soft_analogies)

data = {"She(Bias)":analogies[:152,0], "He(Bias)":analogies[:152,1], "She(Hard)":hard_analogies[:,0], "He(Hard)":hard_analogies[:,1], "She(Soft)":soft_analogies[:152,0], "He(Soft)":soft_analogies[:152,1]}

df = pd.DataFrame(data)
df.to_csv("Results.csv")
WEAT_hard = weat_value(female_vectors, male_vectors, hard_analogy1_vectors, hard_analogy2_vectors)
WEAT_soft = weat_value(female_vectors, male_vectors, soft_analogy1_vectors, soft_analogy2_vectors)
WEAT_bias = weat_value(female_vectors, male_vectors, bias_analogy1_vectors, bias_analogy2_vectors)

weats = {"WEAT for bias (Effect size | Weat)":WEAT_bias, "WEAT for hard (Effect size | Weat)":WEAT_hard, "WEAT for soft (Effect size | Weat)":WEAT_soft}
print(pd.DataFrame(weats))

