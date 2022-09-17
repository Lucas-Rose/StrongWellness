import asyncio
from js import document, FileReader
from pyodide import create_proxy
import pandas as pd
import io
            
async def generate_duplicate_customers(event):
    #READ AND PROCESS PROXY FILE
    file = event.target.files.to_py()
    data=""
    for f in file:
        data = await f.text()
        csv_buffer = io.StringIO(data)

    #FILTER FOR BAD CUSTOMERS
    df = pd.read_csv(csv_buffer)
    df['FullName'] = df['Customer First Name'] + " " + df['Customer Last Name']
    dup_num = df.groupby('Phone').filter(lambda x: len(x) >= 2)
    ready = dup_num.loc[:,['Phone', 'FullName', 'Email']]
    out = ready.groupby('Phone').value_counts().to_csv()

    #APPEND DOWNLOADABLE CSV
    element = document.createElement('a')
    element.setAttribute('href', 'data:text/csv;charset=utf-8,' + out)
    element.innerHTML = "Duplicate Customers Report"    
    document.getElementById("dup-cust-output").appendChild(element)

async def generate_external_giftcards(event):
    #READ AND PROCESS PROXY FILE
    file = event.target.files.to_py()
    data=""
    for f in file:
        data = await f.text()
        csv_buffer = io.StringIO(data)

    #FILTER FOR EXTERNAL BOUGHT GIFTCARDS
    df = pd.read_csv(csv_buffer)
    test = df[['id', 'State', 'Customer Name', 'Items', 'Total']]
    drop = test.dropna()
    gc_sales = drop[drop['Items'].str.contains('for Gift Card')]
    remove_MN = gc_sales[gc_sales['Items'].str.contains('nmin') == False]
    remove_BV = remove_MN[remove_MN['Items'].str.contains('nbel') == False]
    remove_RH = remove_BV[remove_BV['Items'].str.contains('nrou') == False]
    final = remove_RH.to_csv()

    #APPEND DOWNLOADABLE CSV
    element = document.createElement('a')
    element.setAttribute('href', 'data:text/csv;charset=utf-8,' + final)
    element.innerHTML = "Non-Native GiftCard Report"    
    document.getElementById("external-giftcard-output").appendChild(element)
            
def dupCustProxy():
    # Create a Python proxy for the callback function
    # generate_duplicate_customers() is your function to process events from FileReader
    file_event = create_proxy(generate_duplicate_customers)
            
    # Set the listener to the callback
    e = document.getElementById("dupCust")
    e.addEventListener("change", file_event, False)

def extGCProxy():
    # generate_external_giftcards() is your function to process events from FileReader
    file_event = create_proxy(generate_external_giftcards)
    e = document.getElementById("badGC")
    e.addEventListener("change", file_event, False)
            
dupCustProxy()
extGCProxy()
console.log("Good")