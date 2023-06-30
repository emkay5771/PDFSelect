import os
import time
import fitz as fitz #type: ignore
from base64 import b64decode
from dateutil.relativedelta import relativedelta #type: ignore
from datetime import date #type: ignore
from datetime import datetime as dt #type: ignore
from datetime import timedelta #type: ignore
import streamlit as st #type: ignore
import markdownlit #type: ignore
from markdownlit import mdlit as mdlit #type: ignore
import streamlit_toggle as stt #type: ignore
from streamlit_pills_multiselect import pills #type: ignore
import PyPDF2 #type: ignore
from PyPDF2 import PdfMerger #type: ignore
import glob

st.set_page_config(page_title="PDF Section Selector", page_icon="📚", layout="wide", initial_sidebar_state="collapsed")
st.header("PDF Section Selector (BETA) 📚")
def find_next_bookmark(toc, current_index):
    for i in range(current_index + 1, len(toc)):
        print(f"I = {i}")
        #TODO: Fix this so that it doesn't break when the last SUBsection is selected
        if i == len(toc)-1:
            print("Last section")
            #if last section is selected, then return the last page of the pdf
            return toc[i][2] - 1
        if toc[i][0] == 1:
            return toc[i][2] - 1
        if toc[i][0] == 2:
            return toc[i][2] - 1
        if toc[i][0] == 3:
            return toc[i][2] - 1
        if toc[i][0] == 4:
            return toc[i][2] - 1
    return None

def dedupe(pages, pages2, pages3, start_page, end_page): #dedupes the pages when appending, to ensure that pages aren't repeated
    pages2.append(start_page)
    pages2.append(end_page)
    if start_page in pages:
        start_page = start_page + 1
        pages.append(start_page)
        pages3.append(start_page)
    if end_page in pages:
        end_page = end_page - 1
        pages.append(end_page)
        pages3.append(end_page)
    if start_page not in pages:
        pages.append(start_page)
    if end_page not in pages:
        pages.append(end_page)
    return start_page,end_page

def dynamicmake(session, contentsdict): #compiles pdf after collecting all the necessary files
    output_dir = ""
    toc = []
    doc_out = fitz.open()
    pages = []
    pages2 = []
    pages3 = []
    #st.write(contentsdict)
    print("dynamicmake2")
    toc = doc.get_toc() #get the table of contents
    for q, n in contentsdict.items():
        for i, item in enumerate(toc): #type: ignore
            #st.write(item)
            #print(item)
            
            if item[1] == q:
                print(f"Found: {item[1]}")
                #print("Likutei Sichos found")
                page_num_start = item[2] - 1
                print(page_num_start)
                if n == 1:
                    page_num_end = find_next_bookmark(toc, i)
                    print(page_num_end)
                elif n != 1:
                    print("Getting next sublevel")
                    page_num_end = find_next_bookmark(toc, i)
                    print(page_num_end)
                page_num_start, page_num_end = dedupe(pages, pages2, pages3, page_num_start, page_num_end) #type: ignore 
                doc_out.insert_pdf(doc, from_page=page_num_start, to_page=page_num_end) #type: ignore
                break

    doc_out.save(os.path.join(output_dir, f"output_dynamic{session}.pdf"))
    doc_out.close()


def checkbox_callback(checkbox_key):
    st.session_state["checkbox"] = not st.session_state["checkbox"]

if 'checkbox' not in st.session_state:
    st.session_state['checkbox'] = False
uploaded_file = st.file_uploader("Upload a PDF file. NOTE: This file must have an outline for the program to work.", type=["pdf"]) #upload the pdf file

if uploaded_file is None:
    st.subheader("Please upload a PDF file")
if uploaded_file is not None:
    doublesub = False
    st.subheader("Select the sections you would like to include in your PDF")
    st.info("NOTE: Subsection listing might get unwieldy.")
    sublevel_listing = stt.st_toggle_switch("Include Sublevels?", key="sublevel_listing", default_value=False) #toggle switch for sublevels
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf") #open the pdf file
    toc = doc.get_toc() #get the table of contents
    toclist = enumerate(toc)
    #st.write(toc)
    a=0
    if sublevel_listing == True:
        st.warning("NOTE: Turning on the below toggle may make the list super unwieldy. You have been warned.")
        doublesub = stt.st_toggle_switch("Include Sublevels beyond one level?", key="sublevel_listing2", default_value=False) #toggle switch for sublevels
    for each in toclist:
        astr=str(a)
        if each[1][0] == 1:
            checkbox_key = each[1][1]+astr
            if checkbox_key not in st.session_state:
                st.session_state[checkbox_key] = False
            st.checkbox(each[1][1], key=checkbox_key, on_change=checkbox_callback, args=(checkbox_key,))
            a+=1
        elif each[1][0] == 2:
            checkbox_key = f"SUBLEVEL: {each[1][1]+astr}"
            if checkbox_key not in st.session_state:
                st.session_state[checkbox_key] = False
            if sublevel_listing == True:
                st.checkbox(f"SUBLEVEL: {each[1][1]}", key=checkbox_key, on_change=checkbox_callback, args=(checkbox_key,))
                #st.write(each[1][1]+astr)
            a+=1
        elif each[1][0] == 3:
            checkbox_key = f"SUBLEVEL2: {each[1][1]+astr}"
            if checkbox_key not in st.session_state:
                st.session_state[checkbox_key] = False
            if doublesub == True:
                st.checkbox(f"SUBLEVEL2: {each[1][1]}", key=checkbox_key, on_change=checkbox_callback, args=(checkbox_key,))
            a+=1
        elif each[1][0] == 4:
            checkbox_key = f"SUBLEVEL3: {each[1][1]+astr}"
            if checkbox_key not in st.session_state:
                st.session_state[checkbox_key] = False
            if doublesub == True:
                st.checkbox(f"SUBLEVEL3: {each[1][1]}", key=checkbox_key, on_change=checkbox_callback, args=(checkbox_key,))
            a+=1

with st.form(key="dvarform", clear_on_submit=False): #streamlit form for user input
    submit_button = st.form_submit_button(label="Generate PDF ▶️")
    

if submit_button: #if the user submits the form, run the following code, which will create the pdf using above functions
    if id not in st.session_state:
        st.session_state['id'] = dt.now()
    
    session = st.session_state['id']
    #st.write(session2)
    #st.write(session)
    contentsdict={}
    toc = doc.get_toc() #get the table of contents #type: ignore
    toclist = enumerate(toc)
    #st.write(toc)
    b=0
    #for key, value in st.session_state.items():
        #st.write(key, value)
            
    for each in toclist:
        astr=str(b)
        try:
            if st.session_state[each[1][1]+astr] == True:
                #print(each[1][1])
                contentsdict[each[1][1]] = each[1][0]
                #st.write(each[1][1])
        except KeyError:
            try:
                if st.session_state[f"SUBLEVEL: {each[1][1]+astr}"] == True:
                    #print(each[1][1])
                    contentsdict[each[1][1]] = each[1][0]
                    #st.write(each[1][1])
            except KeyError:
                try:
                    if st.session_state[f"SUBLEVEL2: {each[1][1]+astr}"] == True:
                        #print(each[1][1])
                        contentsdict[each[1][1]] = each[1][0]
                        #st.write(each[1][1])
                except KeyError:
                    try:
                        if st.session_state[f"SUBLEVEL3: {each[1][1]+astr}"] == True:
                            #print(each[1][1])
                            contentsdict[each[1][1]] = each[1][0]
                            #st.write(each[1][1])
                    except KeyError:
                        print(f"KeyError: {each[1][1]+astr}")
                        pass
        b+=1
    #st.write(contents)
    #st.write(contentsdict)
    dynamicmake(session, contentsdict)

    if os.path.exists(f"output_dynamic{session}.pdf"):
        st.success("PDF created successfully!")
        st.balloons()
        with open(f"output_dynamic{session}.pdf", "rb") as f:
            st.download_button(label="Download ⬇️", data=f, file_name="Split_PDF.pdf", mime="application/pdf")
 
    if glob.glob("output_dynamic*.pdf"):
        for file in glob.glob("output_dynamic*.pdf"):
            # remove the prefix "flights" and the suffix ".csv" from the file name
            timestamp = file.lstrip("output_dynamic").rstrip(".pdf")
            # parse the timestamp using the format string "%Y-%m-%d %H:%M:%S.%f"
            file_datetime = dt.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
            # check if the file is older than 10 minutes
            if dt.now() - file_datetime > timedelta(minutes=1):
                if file != f'output_dynamic{session}.pdf':
                    os.remove(file)
markdownlit.mdlit("**Any major bugs noticed? Features that you'd like to see? Comments? Email me [📧 here!](mailto:mkievman@outlook.com)**")

