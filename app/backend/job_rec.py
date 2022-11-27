import pickle
import numpy as np
import pandas as pd

def _validate_vector(u, dtype=None):
    u = np.asarray(u, dtype=int, order='c')
    if u.ndim == 1:
        return u
    raise ValueError("Input vector should be 1-D.")

def distance(u, v):
    u = _validate_vector(u)
    v = _validate_vector(v)
#     nonzero = np.bitwise_or(u != 0, v != 0)
#     unequal_nonzero = np.bitwise_and((u != v), nonzero)
    arr = np.bitwise_and(u, v)
#     a = np.double(unequal_nonzero.sum())
    b = np.double(arr.sum())

    return -b
    
def predict(skillset, mapping, model, df): 

    x_in = np.zeros((1, 2060), dtype=int)
    hash_skills = set()
    for skill in skillset:
        if skill.lower() in mapping:
            hash_skills.add(mapping[skill.lower()])
    hash_skills = list(hash_skills)
    x_in[0, hash_skills] = 1
    
    rows = model.kneighbors(x_in, return_distance=False)
    
    res = []
    for row in rows[0]:
        instance = df.iloc[row, :].replace(np.nan, "None").to_dict()
        instance["relatedTitles"] = instance["relatedTitles"].split("; ")
        instance["skills"] = instance["skills"].split("; ")
        res.append(instance)
            
    return res