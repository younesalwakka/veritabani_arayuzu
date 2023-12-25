import streamlit as st
import psycopg2
import pandas as pd

# Database Connection
def connect_db():
    return psycopg2.connect(host='localhost', dbname='Test', user='postgres', password='440220')

# Generalized function to execute SQL queries
def execute_sql(query, values, success_message):
    conn = connect_db()
    cur = conn.cursor()
    try:
        cur.execute(query, values)
        conn.commit()
        st.success(success_message)
    except Exception as e:
        st.error(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

# Function to fetch data with optional search
def fetch_data(table_name, search_query=None):
    conn = connect_db()
    cur = conn.cursor()
    try:
        if search_query and search_query.strip() != '':
            query = f"SELECT * FROM \"Legal\".\"{table_name}\" WHERE {search_query};"
        else:
            query = f"SELECT * FROM \"Legal\".\"{table_name}\";"
        cur.execute(query)
        rows = cur.fetchall()
        return pd.DataFrame(rows, columns=[desc[0] for desc in cur.description]) if rows else pd.DataFrame()
    except Exception as e:
        st.error(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

# Fetch options for dropdowns
def fetch_dropdown_options(table_name, display_column, id_column):
    conn = connect_db()
    cur = conn.cursor()
    query = f"SELECT \"{id_column}\", \"{display_column}\" FROM \"Legal\".\"{table_name}\";"
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {str(row[0]): row[1] for row in rows}

# Generalized function to add, update, and delete records
def add_record(table_name, values):
    if table_name == "MAHKEME UYESI":
        query = "INSERT INTO \"Legal\".\"MAHKEME UYESI\" (\"uyeSicilNo\", \"adi\", \"soyadi\", \"mahkemeTuruNo\") VALUES (%s, %s, %s, %s)"
    elif table_name == "MAHKEME TURU":
        query = "INSERT INTO \"Legal\".\"MAHKEME TURU\" (\"mahkemeTuruNo\", \"turuAdi\") VALUES (%s, %s)"
    elif table_name == "DAVA DOSYASI":
        query = "INSERT INTO \"Legal\".\"DAVA DOSYASI\" (\"davaNo\", tarih, \"durumNo\", \"davaTuruNo\", \"salonNumarasi\", \"uyeSicilNo\") VALUES (%s, %s, %s, %s, %s, %s)"
    execute_sql(query, values, f"Record added successfully to {table_name}")

def update_record(table_name, primary_key, values):
    if table_name == "MAHKEME UYESI":
        query = "UPDATE \"Legal\".\"MAHKEME UYESI\" SET \"adi\" = %s, \"soyadi\" = %s, \"mahkemeTuruNo\" = %s WHERE \"uyeSicilNo\" = %s"
    elif table_name == "MAHKEME TURU":
        query = "UPDATE \"Legal\".\"MAHKEME TURU\" SET \"turuAdi\" = %s WHERE \"mahkemeTuruNo\" = %s"
    elif table_name == "DAVA DOSYASI":
        query = "UPDATE \"Legal\".\"DAVA DOSYASI\" SET tarih = %s, \"durumNo\" = %s, \"davaTuruNo\" = %s, \"salonNumarasi\" = %s, \"uyeSicilNo\" = %s WHERE \"davaNo\" = %s"
    execute_sql(query, values + (primary_key,), f"Record updated successfully in {table_name}")

def delete_record(table_name, primary_key):
    if table_name == "MAHKEME UYESI":
        query = "DELETE FROM \"Legal\".\"MAHKEME UYESI\" WHERE \"uyeSicilNo\" = %s"
    elif table_name == "MAHKEME TURU":
        query = "DELETE FROM \"Legal\".\"MAHKEME TURU\" WHERE \"mahkemeTuruNo\" = %s"
    elif table_name == "DAVA DOSYASI":
        query = "DELETE FROM \"Legal\".\"DAVA DOSYASI\" WHERE \"davaNo\" = %s"
    execute_sql(query, (primary_key,), f"Record deleted successfully from {table_name}")

# Streamlit UI for All Tables
st.title("Database Management System")

# Sidebar for Table Selection and Actions
table_name = st.sidebar.selectbox("Select a Table", ["MAHKEME UYESI", "MAHKEME TURU", "DAVA DOSYASI"])
action = st.sidebar.selectbox("Action", ["Display/Search", "Add Record", "Update Record", "Delete Record"])

# Common Display/Search Functionality
if action == "Display/Search":
    search_term = st.text_input("Enter search term for " + table_name + " (leave empty to display all records)")
    df = fetch_data(table_name, search_term)
    if not df.empty:
        st.write(df)
    else:
        st.write("No data found in " + table_name + ".")

# Add Record Functionality
if action == "Add Record":
    if table_name == "MAHKEME UYESI":
        with st.form("Add_Record_Form_MAHKEME_UYESI"):
            uyeSicilNo = st.text_input("Uye Sicil No")
            adi = st.text_input("Adi")
            soyadi = st.text_input("Soyadi")
            mahkemeTuruNo = st.text_input("Mahkeme Turu No")
            submit_button = st.form_submit_button("Add Record")
            if submit_button:
                add_record(table_name, (uyeSicilNo, adi, soyadi, mahkemeTuruNo))
    elif table_name == "MAHKEME TURU":
        with st.form("Add_Record_Form_MAHKEME_TURU"):
            mahkemeTuruNo = st.text_input("Mahkeme Turu No")
            turuAdi = st.text_input("Turu Adi")
            submit_button = st.form_submit_button("Add Record")
            if submit_button:
                add_record(table_name, (mahkemeTuruNo, turuAdi))
    elif table_name == "DAVA DOSYASI":
        durum_options = fetch_dropdown_options("DAVA DURUMU", "durumu", "durumNo")
        dava_turu_options = fetch_dropdown_options("DAVA TURU", "adı", "davaTuruNo")
        salon_options = fetch_dropdown_options("DURUSMA SALONU", "salonNumarasi", "salonNumarasi")
        uye_options = fetch_dropdown_options("MAHKEME UYESI", "adi", "uyeSicilNo")

        with st.form("Add_Record_Form"):
            davaNo = st.text_input("Dava No")
            tarih = st.date_input("Tarih")
            durumNo = st.selectbox("Durum No", list(durum_options.keys()), format_func=lambda x: durum_options[x])
            davaTuruNo = st.selectbox("Dava Turu No", list(dava_turu_options.keys()), format_func=lambda x: dava_turu_options[x])
            salonNumarasi = st.selectbox("Salon Numarasi", list(salon_options.keys()))
            uyeSicilNo = st.selectbox("Uye Sicil No", list(uye_options.keys()), format_func=lambda x: f"{uye_options[x]} ({x})")
            submit_button = st.form_submit_button("Add Record")
            if submit_button:
                values = (davaNo, tarih, durumNo, davaTuruNo, salonNumarasi, uyeSicilNo)
                add_record(table_name, values)
# Update Record Functionality
if action == "Update Record":
    primary_key = st.text_input(f"Enter the primary key of the record in {table_name} to update")
    if primary_key:
        if table_name == "MAHKEME UYESI":
            with st.form("Update_Record_Form_MAHKEME_UYESI"):
                new_adi = st.text_input("New Adi")
                new_soyadi = st.text_input("New Soyadi")
                new_mahkemeTuruNo = st.text_input("New Mahkeme Turu No")
                update_button = st.form_submit_button("Update Record")
                if update_button:
                    update_record(table_name, primary_key, (new_adi, new_soyadi, new_mahkemeTuruNo))
        elif table_name == "MAHKEME TURU":
            with st.form("Update_Record_Form_MAHKEME_TURU"):
                new_turuAdi = st.text_input("New Turu Adi")
                update_button = st.form_submit_button("Update Record")
                if update_button:
                    update_record(table_name, primary_key, (new_turuAdi,))
        elif table_name == "DAVA DOSYASI":
            with st.form("Update_Record_Form"):
                new_tarih = st.date_input("New Tarih")
                new_durumNo = st.text_input("New Durum No")
                new_davaTuruNo = st.text_input("New Dava Turu No")
                new_salonNumarasi = st.text_input("New Salon Numarasi")
                new_uyeSicilNo = st.text_input("New Uye Sicil No")
                update_button = st.form_submit_button("Update Record")
                if update_button:
                    update_record(table_name, primary_key, (new_tarih, new_durumNo, new_davaTuruNo, new_salonNumarasi, new_uyeSicilNo))

# Delete Record Functionality
if action == "Delete Record":
    primary_key_to_delete = st.text_input(f"Enter the primary key of the record in {table_name} to delete")
    if primary_key_to_delete and st.button("Delete Record"):
        delete_record(table_name, primary_key_to_delete)

# End of Streamlit UI
