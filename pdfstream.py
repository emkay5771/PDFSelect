import os
import time
import fitz as fitz #type: ignore
from base64 import b64decode
from dateutil.relativedelta import relativedelta #type: ignore
from datetime import date #type: ignore
from datetime import datetime as dt #type: ignore
from datetime import timedelta #type: ignore
import streamlit as st #type: ignore
import markdownlit
from markdownlit import mdlit as mdlit
import streamlit_toggle as stt
from streamlit_pills_multiselect import pills
import PyPDF2 #type: ignore
from PyPDF2 import PdfMerger #type: ignore
import glob

st.set_page_config(page_title="PDF Section Selector", page_icon="📚", layout="wide", initial_sidebar_state="collapsed")

def rambamenglish(dor, session, opt): # retrieves all rambam versions from chabad.org
    pdf_options = {
    'scale': scale2,
    'margin-top': '0.1in',
    'margin-right': '0.1in',
    'margin-bottom': '0.1in',
    'margin-left': '0.1in',
    }
    merger = PdfMerger()
    if os.path.exists(f"Rambam{session}.pdf") != True:
        for i in dor:
            #st.write(dor)
            #st.write("Rambam" + i)
            driver = webdriver.Chrome(options=options)
            lang = ""
            chapters = ""
            if "Rambam (3)-Bilingual" in opt:
                    lang = "both"
                    chapters = "3"
            elif "Rambam (3)-Hebrew" in opt:
                lang = "he"
                chapters = "3"
            elif "Rambam (3)-English" in opt:
                lang = "primary"
                chapters = "3"
            elif "Rambam (1)-Bilingual" in opt:
                lang = "both"
                chapters = "1"
            elif "Rambam (1)-Hebrew" in opt:
                lang = "he"
                chapters = "1"
            elif "Rambam (1)-English" in opt:
                lang = "primary"
                chapters = "1"
            driver.get(f"https://www.chabad.org/dailystudy/rambam.asp?rambamchapters={chapters}&tdate={i}#lt={lang}")
            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.presence_of_element_located((By.ID, "content")))
            pdf = driver.execute_cdp_cmd("Page.printToPDF", pdf_options)
            with open(f"temp{session}.pdf", "ab") as f:
                f.write(b64decode(pdf["data"]))
            f.close()
            driver.quit()

            merger.append(f"temp{session}.pdf")

        merger.write(f"Rambam{session}.pdf")
        merger.close()
        os.remove(f"temp{session}.pdf")

def hayomyom(dor, session): #gets hayom yom from chabad.org
    pdf_options = {
    'scale': scale3,
    'margin-top': '0.1in',
    'margin-right': '0.1in',
    'margin-bottom': '0.1in',
    'margin-left': '0.1in',
    }
    #st.write(f"{scale}")
    merger3 = PdfMerger()
    if os.path.exists(f"Hayom{session}.pdf") != True:
        for i in dor:
            #st.write(dor)
            #st.write(i)
            driver = webdriver.Chrome(options=options)
            driver.get(f"https://www.chabad.org/dailystudy/hayomyom.asp?tdate={i}")
            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.presence_of_element_located((By.ID, "content")))
            pdf = driver.execute_cdp_cmd("Page.printToPDF", pdf_options)
            with open(f"temp{session}.pdf", "ab") as f:
                f.write(b64decode(pdf["data"]))
            f.close()
            driver.quit()

            merger3.append(f"temp{session}.pdf")

        merger3.write(f"Hayom{session}.pdf")
        merger3.close()
        os.remove(f"temp{session}.pdf")

def find_next_top_level_bookmark(toc, current_index):
    for i in range(current_index + 1, len(toc)):
        if toc[i][0] == 1:
            return toc[i][2] - 2
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

def dynamicmake(dow, optconv, opt, source, session): #compiles pdf after collecting all the necessary files
    output_dir = ""
    toc = []
    doc_out = fitz.open()
    pages = []
    pages2 = []
    pages3 = []
    kriahattatch = False
    #st.write(optconv)
    if source == True:
        try:
            #st.write(f"opening dvar{session}.pdf")
            doc = fitz.open(f"dvar{session}.pdf")
            #st.write("opened dvar")
            toc = doc.get_toc()
            #st.write("got toc")
            if cover == True:
                doc_out.insert_pdf(doc, from_page=0, to_page=0)
        except:
            st.write("Something went wrong with Dvar Malchus. Attempting to use Chabad.org.")
            print(opt)
            if all(option not in chabadoptions for option in opt) and any(option in opt for option in ['Project Likutei Sichos', 'Maamarim', 'Haftorah']):
                st.error("Project Likutei Sichos, the Haftorah, and Maamarim are not available from Chabad.org. Please try again.")
                st.stop()
            source = False
            chabadget(dor, opt, session)
            pass
                
    else:
        #st.write(optconv)
        for q in optconv:
            #st.write(q)
            for z in dow:
                for i, top_level in enumerate(toc): #type: ignore
                    #st.write(top_level)
                    if not top_level[2]:
                        continue  # skip top-level bookmarks without a page number
                    if top_level[1] == q:
                        for j, sub_level in enumerate(toc[i+1:], start=i+1): #type: ignore
                            if sub_level[0] != top_level[0] + 1:
                                break  # stop when we reach the next top-level bookmark
                            if z in sub_level[1]:
                                start_page = sub_level[2] - 1
                                if top_level[1] == "חומש יומי":
                                    if z == 'שבת קודש':
                                        end_page = toc[j+1][2] - 2
                                    else:
                                        end_page = toc[j+1][2] - 1 #type: ignore
                                    print("Chumash found")
                                if top_level[1] == "תניא יומי":
                                    end_page = toc[j+1][2] - 2 #type: ignore
                                    print("Tanya found")
                                if top_level[1] == 'רמב"ם - שלושה פרקים ליום':
                                    end_page = toc[j+1][2] - 1 #type: ignore
                                    print("Rambam found")
                                print(f"Current Start Page: {start_page}. Current End Page: {end_page}") #type: ignore
                                start_page, end_page = dedupe(pages, pages2, pages3, start_page, end_page) #type: ignore
                                print(f"New Start Page: {start_page}. New End Page: {end_page}")
                                doc_out.insert_pdf(doc, from_page=start_page, to_page=end_page) #type: ignore
                                continue
            
            if q == 'חומש לקריאה בציבור' or q == 'מאמרים' or q == 'לקוטי שיחות':
                for i, item in enumerate(toc): #type: ignore
                    #st.write(item)
                    #print(item)
                    if item[1] == 'לקוטי שיחות' and q == 'לקוטי שיחות':
                        print("Likutei Sichos found")
                        pdf_file = open(f"dvar{session}.pdf", "rb")
                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                        page_num_start = item[2] - 1
                        print(page_num_start)
                        page_num_end = find_next_top_level_bookmark(toc, i) #type: ignore
                        print(page_num_end)
                        doc_out.insert_pdf(doc, from_page=page_num_start, to_page=page_num_end) #type: ignore
                    if item[1] == 'מאמרים' and q == 'מאמרים':
                        print("Maamarim found")
                        pdf_file = open(f"dvar{session}.pdf", "rb")
                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                        page_num_start = item[2] - 1
                        print(page_num_start)
                        page_num_end = find_next_top_level_bookmark(toc, i) #type: ignore
                        print(page_num_end)
                        doc_out.insert_pdf(doc, from_page=page_num_start, to_page=page_num_end) #type: ignore
                    if item[1] == 'חומש לקריאה בציבור' and q == 'חומש לקריאה בציבור':
                        pdf_file = open(f"dvar{session}.pdf", "rb")
                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                        page_num_start = item[2] - 1
                        #print(page_num_start)
                        page_num_end = toc[i+1][2] - 3 #type: ignore
                        #print(page_num_end)
                        print("Torah reading found")
                        if "Krias Hatorah (includes Haftorah)" in opt and kriahattatch == False:
                            print("Kriah found")
                            doc_out.insert_pdf(doc, from_page=page_num_start, to_page=page_num_end)
                            kriahattatch = True
                        elif 'Haftorah' in opt and 'Krias Hatorah (includes Haftorah)' not in opt:    
                            for page_num in range(page_num_start, page_num_end):
                                print("Haftorah found")
                                #print(page_num)
                                page = pdf_reader.pages[page_num]
                                text = page.extract_text()
                                #print(text)
                                if "ברכת הפטורה" in text or "xtd enk dxhtdd renyl" in text:
                                    doc_out.insert_pdf(doc, from_page=page_num, to_page=page_num_end) #type: ignore
                                    continue
                        
            if 'Rambam' in q:
                #st.write("Appending Rambam")
                doc_out.insert_pdf(fitz.open(f"Rambam{session}.pdf")) 
                print("Appended")
                continue
            
            if q == 'Hayom Yom':
                print("Hayom Yom found")
                #st.write("Appending Hayom Yom")
                doc_out.insert_pdf(fitz.open(f"Hayom{session}.pdf")) 
                print("Appended")
                continue

            if q == 'Shnayim Mikra':
                print("Shnayim Mikra found")
                #st.write("Appending Shnayim Mikra")
                doc_out.insert_pdf(fitz.open(f"Shnayim{session}.pdf")) 
                print("Appended")
                continue
                       
    doc_out.save(os.path.join(output_dir, f"output_dynamic{session}.pdf"))
    doc_out.close()


@st.cache_data
def dateset():
    session2 = dt.now()
    print(f"Session: {session2}")
    return session2
uploaded_file = st.file_uploader("Upload a PDF file. NOTE: This file must have an outline for the program to work.", type=["pdf"]) #upload the pdf file
with st.form(key="dvarform", clear_on_submit=False): #streamlit form for user input
    st.header("PDF Section Selector 📚")
    if uploaded_file is None:
        st.subheader("Please upload a PDF file")
    if uploaded_file is not None:
        st.subheader("Select the sections you would like to include in your PDF")
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf") #open the pdf file
        toc = doc.get_toc() #get the table of contents
        toclist = enumerate(toc)
        #st.write(toc)
        a=0
        for each in toclist:
            astr=str(a)
            st.checkbox(each[1][1], key=each[1][1]+astr) #create a checkbox for each section in the table of contents
            a+=1

    submit_button = st.form_submit_button(label="Generate PDF ▶️")

if submit_button: #if the user submits the form, run the following code, which will create the pdf using above functions
    if id not in st.session_state:
        st.session_state['id'] = dt.now()
    
    session = st.session_state['id']
    #st.write(session2)
    #st.write(session)
    contents=[]
    toc = doc.get_toc() #get the table of contents
    toclist = enumerate(toc)
    b=0
    for each in toclist:
        astr=str(b)
        if st.session_state[each[1][1]+astr] == True:
            contents.append(each[1][1])
            st.write(each[1][1])
            st.write(contents)
        b+=1
    #dynamicmake(dow, optconv, opt, source, session)

    if os.path.exists(f"output_dynamic{session}.pdf"):
        st.success("PDF created successfully!")
        st.balloons()
        with open(f"output_dynamic{session}.pdf", "rb") as f:
            st.download_button(label="Download ⬇️", data=f, file_name="Custom_Chitas.pdf", mime="application/pdf")
 
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

