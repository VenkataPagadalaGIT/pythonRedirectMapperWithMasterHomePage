import streamlit as st
from polyfuzz import PolyFuzz
import pandas as pd
from polyfuzz.models import TFIDF

st.title('Python URL / Redirect Mapping Tool with Default Value')
st.subheader('Directions:')
st.write('- Upload complete crawl \n - Upload a list of 404s in.CSV format (URL column named URL) \n - Would not '
         'recommend with over 10k URLs (very slow) ')

st.write(' Note: If similarity is less than 0.86, The tool recommend redirect default value( Home page ) ')
st.write("Author - [Venkata Pagadala](https://www.linkedin.com/in/venkata-pagadala/)")
# Importing the URL CSV files
url = st.text_input('The URL to Match', placeholder='Enter domain (www.google.com)')
file1 = st.file_uploader("Upload 404 CSV File")
file2 = st.file_uploader("Upload Crawl CSV File")
if file1 is not None and file2 is not None:
    broken = pd.read_csv(file1)
    current = pd.read_csv(file2)
    ROOTDOMAIN = url
    # Converting DF to List
    broken_list = broken["URL"].tolist()
    broken_list = [sub.replace(ROOTDOMAIN, '') for sub in broken_list]
    current_list = current["Address"].tolist()
    current_list = [sub.replace(ROOTDOMAIN, '') for sub in current_list]

    tfidf = TFIDF(n_gram_range=(2, 2))
    model = PolyFuzz(tfidf)

    #model = PolyFuzz("EditDistance")
    model.match(broken_list,current_list)
    df1 = model.get_matches()
    # Polishing and Pruning
    df1["Similarity"] = df1["Similarity"].round(3)
    index_names = df1.loc[df1['Similarity'] < .16].index
    amt_dropped = len(index_names)
    df1.drop(index_names, inplace=True)
    df1["To"] = ROOTDOMAIN + df1["To"]
    df1["From"] = ROOTDOMAIN + df1["From"]
    df = pd.DataFrame()
    df['To'] = current['Address']
    df['Title'] = current['Title 1']
    df['Meta Description'] = current['Meta Description 1']
    df['H1'] = current['H1-1']
    val = df[df['To'].str.contains(ROOTDOMAIN)]
    mainTitle = val['Title'][0]
    mainMeta = val['Meta Description'][0]
    mainH1 = val['H1'][0]
    df3 = pd.merge(df, df1, on='To')
    df3 = df3[['Similarity', 'From', 'To', 'Title', 'Meta Description', 'H1']]
    df3.loc[df3["Similarity"] < .23, "To"] = ROOTDOMAIN
    df3.loc[df3["Similarity"] < .23, "Title"] = mainTitle
    df3.loc[df3["Similarity"] < .23, "Meta Description"] = mainMeta
    df3.loc[df3["Similarity"] < .23, "H1"] = mainH1
    df3 = df3.sort_values(by='Similarity', ascending=False)
    df3
    # Downloading of File
    @st.cache
    def convert_df(df3):
        return df3.to_csv().encode('utf-8')
    csv = convert_df(df3)
    st.download_button("Download Output", csv, "file.csv", "text/csv", key='download-csv')
