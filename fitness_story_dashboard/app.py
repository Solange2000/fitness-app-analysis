import io
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from analysis import load,prepare,reliability,associations,regression,GROUPS,LIKERT

st.set_page_config(page_title='Beyond the Download | Fitness Research',page_icon='🏃',layout='wide',initial_sidebar_state='expanded')
st.markdown('''
<style>
    .block-container{padding-top:1.5rem;max-width:1250px}
    h1,h2,h3{color:#173452}
    [data-testid="stSidebar"]{background:#eef4f7;border-right:1px solid #d5e0e6;min-width:330px;max-width:420px}
    [data-testid="stSidebar"] > div:first-child{padding:1.2rem 1.1rem 1.5rem}
    [data-testid="stSidebar"] .stRadio, [data-testid="stSidebar"] .stFileUploader, [data-testid="stSidebar"] .stSelectbox{width:100%}
    [data-testid="stMetric"]{background:#f1f6fa;border:1px solid #dce8f1;border-radius:12px;padding:14px}
    .story{background:#eaf5f2;border-left:5px solid #16856b;padding:16px 20px;border-radius:7px;margin:14px 0 22px}
</style>
''',unsafe_allow_html=True)
DEFAULT=Path(__file__).parent/'data'/'responses.xlsx'
with st.sidebar:
    st.title('🏃 Research explorer')
    uploaded=st.file_uploader('Optional: replace survey data',type=['xlsx'])
    st.caption('Original 100-response dataset is bundled and loads automatically.')
    section=st.radio('Navigate the story',['Overview','01 · Meet the participants','02 · The adoption journey','03 · Perceived changes','04 · Motivation & community','05 · What predicts return?','06 · Findings & limitations','Data dictionary'])
    st.divider()
    st.caption('Research: young adults in Buffalo City Metropolitan Municipality. Descriptive, cross-sectional, self-reported survey.')
try:
    raw=load(io.BytesIO(uploaded.getvalue()) if uploaded else DEFAULT)
    if raw.shape[1]<32:st.error('Expected at least 32 questionnaire columns in the original order.');st.stop()
    df=prepare(raw)
except Exception as exc:
    st.error(f'Unable to read dataset: {exc}');st.stop()

age=df.iloc[:,2].astype(str).str.strip();gender=df.iloc[:,3].astype(str).str.strip();employment=df.iloc[:,5].astype(str).str.strip()
usage=df.iloc[:,9].astype(str).str.strip();experience=df.iloc[:,10].astype(str).str.strip()
with st.sidebar:
    st.subheader('Explore subgroups')
    selected_age=st.selectbox(
        'Age group',
        [None,*sorted(age.unique())],
        format_func=lambda value:'All age groups' if value is None else value,
    )
    selected_gender=st.selectbox(
        'Gender',
        [None,*sorted(gender.unique())],
        format_func=lambda value:'All genders' if value is None else value,
    )
    st.caption('Filters apply to all results. Statistical models use the filtered sample and may be unstable for small groups.')
mask=pd.Series(True,index=df.index)
if selected_age is not None:
    mask &= age.eq(selected_age)
if selected_gender is not None:
    mask &= gender.eq(selected_gender)
d=df.loc[mask].copy()
if d.empty:st.warning('No responses match these filters.');st.stop()

def chart_count(series,title,order=None,color='#2b7790'):
    counts=series.value_counts().reindex(order,fill_value=0) if order else series.value_counts()
    fig,ax=plt.subplots(figsize=(8,3.5));sns.barplot(x=counts.values,y=counts.index,ax=ax,color=color)
    for i,v in enumerate(counts.values):ax.text(v+max(counts.values)*.015,i,str(v),va='center',fontsize=10)
    ax.set_xlim(0,max(counts.values)*1.18 if max(counts.values) else 1);ax.set_xlabel('Respondents');ax.set_ylabel('');ax.set_title(title,loc='left',fontweight='bold');sns.despine();st.pyplot(fig);plt.close(fig)

def story(text):st.markdown(f'<div class="story"><strong>What this tells us</strong><br>{text}</div>',unsafe_allow_html=True)

def metric_mean(col):return f'{d[col].mean():.2f} / 5'

st.title('Beyond the Download')
st.caption('How fitness-app features relate to awareness, motivation and returning to the app | Microsoft Forms survey | Buffalo City, Eastern Cape')

if section=='Overview':
    st.subheader('The story in six chapters')
    a,b,c,dcol=st.columns(4)
    a.metric('Responses in view',len(d));b.metric('Use at least weekly',f'{usage.loc[mask].isin(["Daily","Weekly"]).mean():.0%}');c.metric('Return often / always',f'{(d["Return frequency"]>=4).mean():.0%}');dcol.metric('App represented',d.iloc[:,8].nunique())
    st.markdown('### A promising signal, with important limits')
    story('Respondents frequently report returning to their fitness app, but this is self-reported engagement—not measured retention. The sample consists of app-experienced respondents and does not measure awareness among non-users.')
    col1,col2=st.columns(2)
    with col1:chart_count(usage.loc[mask],'How often apps are used',order=['Daily','Weekly','Monthly','Yearly','Never'])
    with col2:chart_count(d.iloc[:,29].astype(str).str.strip(),'How often respondents return',order=['Always','Often','Sometimes','Rarely','Never'],color='#16856b')
    st.info('Use the left-hand navigation to follow the evidence from demographics through statistical analysis to conclusions.')
elif section=='01 · Meet the participants':
    st.header('01 · Who answered the questionnaire?')
    st.write('Understanding the respondents is essential before interpreting any association.')
    c1,c2=st.columns(2)
    with c1:chart_count(age.loc[mask],'Age distribution')
    with c2:chart_count(gender.loc[mask],'Gender distribution',color='#16856b')
    chart_count(employment.loc[mask],'Employment status')
    story('These are characteristics of the respondents, not estimates for all young adults in Buffalo City. Recruitment and selection limit generalisability.')
elif section=='02 · The adoption journey':
    st.header('02 · From trying an app to using it regularly')
    c1,c2=st.columns(2)
    with c1:chart_count(usage.loc[mask],'App usage frequency',order=['Daily','Weekly','Monthly','Yearly','Never'])
    with c2:chart_count(experience.loc[mask],'Time using fitness apps')
    st.subheader('Reasons for using fitness apps')
    reasons=d.iloc[:,11].fillna('').astype(str).str.split(';').explode().str.strip();reasons=reasons[reasons.ne('')]
    chart_count(reasons,'Reasons selected (multiple responses allowed)',color='#16856b')
    story('App use and time since adoption are different. Frequent use does not establish long-term retention, and respondents could select multiple reasons for adoption.')
elif section=='03 · Perceived changes':
    st.header('03 · What respondents say about fitness before and after adoption')
    st.warning('These are retrospective self-assessments collected once—not a longitudinal before-and-after experiment. Pre-use and post-use statements are worded differently; their means are not a causal change score.')
    c1,c2=st.columns(2)
    c1.metric('Pre-use orientation',metric_mean('Pre-use orientation'));c2.metric('Perceived post-use impact',metric_mean('Perceived post-use impact'))
    labels=['Understanding exercise','Healthy lifestyle awareness','Motivation','Goal setting','Tracking progress']
    pre=d.iloc[:,12:17].apply(lambda x:x.astype('string').str.strip().map(LIKERT)).mean().values
    post=d.iloc[:,17:22].apply(lambda x:x.astype('string').str.strip().map(LIKERT)).mean().values
    fig,ax=plt.subplots(figsize=(10,4.4));y=np.arange(5);ax.barh(y-.18,pre,.35,label='Retrospective pre-use',color='#2b7790');ax.barh(y+.18,post,.35,label='Perceived post-use',color='#16856b');ax.set_yticks(y,labels);ax.invert_yaxis();ax.set_xlim(0,5);ax.set_xlabel('Mean agreement (1–5)');ax.legend();sns.despine();st.pyplot(fig);plt.close(fig)
    story('The graph compares agreement with two sets of differently framed statements. It does not demonstrate an objectively measured improvement or deterioration after adopting an app.')
elif section=='04 · Motivation & community':
    st.header('04 · Game mechanics versus community support')
    c1,c2=st.columns(2);c1.metric('Gamification mean',metric_mean('Gamification'));c2.metric('Social support mean',metric_mean('Social support'))
    labels=['Points & rewards','Badges','Challenges','Leaderboards','Sharing progress','Group challenges','Peer encouragement']
    vals=d.iloc[:,22:29].apply(lambda x:x.astype('string').str.strip().map(LIKERT)).mean().values
    fig,ax=plt.subplots(figsize=(10,4.6));sns.barplot(x=vals,y=labels,ax=ax,color='#2b7790');ax.set_xlim(0,5);ax.set_xlabel('Mean agreement (1–5)');sns.despine();st.pyplot(fig);plt.close(fig)
    story('These items measure reported motivation from features. They do not show whether users actually encountered every feature, or whether those features caused them to exercise more.')
elif section=='05 · What predicts return?':
    st.header('05 · What is associated with returning to the app?')
    st.caption('Primary outcome: the questionnaire item “I regularly return to my fitness application…” coded Never=1 to Always=5.')
    st.subheader('Rank correlations')
    corr=associations(d);st.dataframe(corr.style.format({'Spearman rho':'{:.3f}','p-value':'{:.4f}'}),hide_index=True,use_container_width=True)
    fig,ax=plt.subplots(figsize=(7,3.5));sns.barplot(data=corr,x='Spearman rho',y='Predictor',ax=ax,color='#16856b');ax.axvline(0,color='black',lw=.8);ax.set_xlim(-1,1);sns.despine();st.pyplot(fig);plt.close(fig)
    st.subheader('Internal consistency')
    rel=reliability(d);st.dataframe(rel.style.format({'Cronbach alpha':'{:.3f}'}),hide_index=True,use_container_width=True)
    st.caption('Cronbach’s alpha measures consistency of items, not proof of validity. The continuation/recommendation pair combines different intentions and should be interpreted cautiously.')
    st.subheader('Exploratory regression')
    fit,coeff=regression(d)
    if fit is not None:
        c1,c2,c3=st.columns(3);c1.metric('R²',f'{fit.rsquared:.3f}');c2.metric('Adjusted R²',f'{fit.rsquared_adj:.3f}');c3.metric('Complete cases',int(fit.nobs))
        st.dataframe(coeff.style.format('{:.4f}'),use_container_width=True)
        st.caption('OLS with HC3 robust standard errors. Predictors: gamification, social support and pre-use orientation. Ordinal outcome and cross-sectional design limit interpretation; coefficients are associations, not causal effects.')
        fig,ax=plt.subplots(figsize=(8,3));sns.scatterplot(x=fit.fittedvalues,y=fit.resid,ax=ax,color='#2b7790');ax.axhline(0,ls='--',color='gray');ax.set_xlabel('Fitted return-frequency score');ax.set_ylabel('Residual');sns.despine();st.pyplot(fig);plt.close(fig)
    else:st.warning('Insufficient variation or sample size for the exploratory regression.')
    story('Check both effect size and uncertainty. Statistical significance alone does not establish practical importance or causation. Subgroup filtering can substantially change these estimates.')
elif section=='06 · Findings & limitations':
    st.header('06 · What can the research reasonably conclude?')
    assoc=associations(d).set_index('Predictor')
    for label in ['Social support','Gamification']:
        rho=assoc.loc[label,'Spearman rho'];p=assoc.loc[label,'p-value']
        st.write(f'**{label}:** Spearman ρ = {rho:.3f}, p = {p:.4f} with self-reported app-return frequency (filtered sample).')
    st.subheader('Evidence-based implications')
    st.markdown('''- **Design:** Evaluate supportive social interactions alongside game mechanics; avoid claiming a feature causes retention from this survey alone.
- **Research:** Include non-users in a future awareness study and use app logs or repeated follow-ups to measure retention.
- **Interpretation:** Treat the before/after items as perceptions recalled at one survey date, not measured changes.
- **Scope:** This dataset describes 100 surveyed respondents, all reporting Strava; it is not representative of every fitness app or young adult in the municipality.''')
    story('The study provides evidence about associations within this sample, rather than causal proof that gamification or social features improve fitness outcomes.')
else:
    st.header('Data dictionary & reproducibility')
    st.write('Original spreadsheet columns, their positions and response examples:')
    st.dataframe(pd.DataFrame({'Position':[i+1 for i in range(raw.shape[1])],'Question':raw.columns,'Nonmissing':[int(raw.iloc[:,i].notna().sum()) for i in range(raw.shape[1])]}),hide_index=True,use_container_width=True)
    st.write('**Scale coding:** Strongly disagree=1, Disagree=2, Neutral=3, Agree=4, Strongly agree=5; Never=1, Rarely=2, Sometimes=3, Often=4, Always=5.')
    st.write('**Constructs:** Pre-use (columns 13–17), perceived post-use (18–22), gamification (23–26), social support (27–29), return frequency (30), continuation/recommendation (31–32). Positions are 1-indexed.')
    st.write('**Statistical methods:** Cronbach alpha, Spearman rank correlation, exploratory OLS with HC3 robust SE. Results recalculate under sidebar filters.')

st.divider()
st.caption('Source: uploaded Microsoft Forms questionnaire workbook. Individual-level data are used locally in the app. No network requests or external APIs are required.')
summary=d[['Pre-use orientation','Perceived post-use impact','Gamification','Social support','Return frequency']].describe().round(3)
st.download_button('Download summary statistics (CSV)',summary.to_csv().encode(),file_name='survey_summary.csv',mime='text/csv')
