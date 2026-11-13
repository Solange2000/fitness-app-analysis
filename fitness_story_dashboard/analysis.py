"""Reproducible, descriptive analysis of the uploaded survey; no fabricated data."""
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
import statsmodels.api as sm

LIKERT={'Strongly disagree':1,'Disagree':2,'Neutral':3,'Agree':4,'Strongly agree':5}
RETURN={'Never':1,'Rarely':2,'Sometimes':3,'Often':4,'Always':5}
GROUPS={'Pre-use orientation':list(range(12,17)),'Perceived post-use impact':list(range(17,22)),'Gamification':list(range(22,26)),'Social support':list(range(26,29)),'Continuation / recommendation':list(range(30,32))}

def load(path):
    df=pd.read_excel(path)
    df.columns=[str(c).strip() for c in df.columns]
    return df

def alpha(frame):
    x=frame.dropna()
    if len(x)<3 or x.shape[1]<2:return np.nan
    variances=x.var(ddof=1)
    total=x.sum(axis=1).var(ddof=1)
    return float(x.shape[1]/(x.shape[1]-1)*(1-variances.sum()/total)) if total>0 else np.nan

def prepare(df):
    d=df.copy()
    for group, indices in GROUPS.items():
        values=d.iloc[:,indices].apply(lambda col:col.astype('string').str.strip().map(LIKERT))
        d[group]=values.mean(axis=1)
    d['Return frequency']=d.iloc[:,29].astype('string').str.strip().map(RETURN)
    return d

def reliability(df):
    return pd.DataFrame([{'Construct':name,'Items':len(indices),'Cronbach alpha':alpha(df.iloc[:,indices].apply(lambda col:col.astype('string').str.strip().map(LIKERT)))} for name,indices in GROUPS.items()])

def associations(d):
    predictors=['Pre-use orientation','Perceived post-use impact','Gamification','Social support']
    rows=[]
    for p in predictors:
        pair=d[[p,'Return frequency']].dropna()
        r,pval=spearmanr(pair[p],pair['Return frequency']) if len(pair)>3 else (np.nan,np.nan)
        rows.append({'Predictor':p,'Spearman rho':r,'p-value':pval,'n':len(pair)})
    return pd.DataFrame(rows)

def regression(d):
    predictors=['Gamification','Social support','Pre-use orientation']
    sample=d[predictors+['Return frequency']].dropna()
    if len(sample)<15 or sample['Return frequency'].nunique()<2:return None,None
    fit=sm.OLS(sample['Return frequency'],sm.add_constant(sample[predictors])).fit(cov_type='HC3')
    coef=pd.DataFrame({'Coefficient':fit.params,'Robust SE':fit.bse,'p-value':fit.pvalues,'CI lower':fit.conf_int()[0],'CI upper':fit.conf_int()[1]})
    return fit,coef
