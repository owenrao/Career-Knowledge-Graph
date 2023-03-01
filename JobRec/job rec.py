import re
import numpy as np

def predict(skillset, fasttext, model, df): 
    x_in = []
    for skill in skillset:
        x_in.append(re.sub(r'\([^)]*\)', '', skill).strip(" "))

    x_in = fasttext.wv[" ".join(x_in)].reshape(1, -1)    
    rows = model.kneighbors(x_in, return_distance=False)
    
    res = []
    for row in rows[0]:
        instance = df.iloc[row, :].replace(np.nan, "None").to_dict()
        instance["relatedTitles"] = instance["relatedTitles"].split("; ")
        instance["skills"] = instance["skills"].split("; ")
        res.append(instance)
            
    return res

