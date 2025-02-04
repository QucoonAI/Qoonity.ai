import streamlit as st
from main import get_response
import time
import pandas as pd
import service
import api

st.title('Qoonity.ai')
st.write('Welcome to Qoonity.ai!')

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "application_details" not in st.session_state:
    st.session_state.application_details = {}

if "entities" not in st.session_state:
    st.session_state.entities = []

if "tables_created" not in st.session_state:
    st.session_state.tables_created = False

if "application_created" not in st.session_state:
    st.session_state.application_created = False

if "entities_created" not in st.session_state:
    st.session_state.entities_created = False

if "attributes_created" not in st.session_state:
    st.session_state.attributes_created = False

# Initialize response_type
if "response_type" not in st.session_state:
    st.session_state.response_type = ""

if "application_table_data" not in st.session_state:
    st.session_state.application_table_data = {}

if "application_id" not in st.session_state:
    st.session_state.application_id = 0

# Sidebar Chat
with st.sidebar:
    messages = st.container(height=650)
    
    # Display chat messages from history
    for message in st.session_state.messages:
        messages.chat_message(message["role"]).write(message["content"])
            
    if prompt := st.chat_input("What would you like to build today?"):
        messages.chat_message("user").write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        with messages:
            with st.spinner('Wait for it...'):
                response = get_response(prompt)
                time.sleep(1)
        
        st.session_state.response_type = response.get("request_type", "generic_request")
        chat_response = response.get("response", "I'm sorry, I didn't understand that.")
        response.pop("response", None)
        messages.chat_message("assistant").write(chat_response)
        st.session_state.messages.append({"role": "assistant", "content": chat_response})

        if st.session_state.response_type == "application_design":
            st.session_state.application_details = response.get("application_details", {})
            st.session_state.entities = response.get("entities", [])

# Using the response_type safely
if st.session_state.response_type == "application_design":
    application_details = st.session_state.application_details
    new_entities = st.session_state.entities

    if new_entities:
        for entity in new_entities:
            st.subheader(f"{entity['entityName']}", divider=True)
            entity_df = pd.DataFrame(entity["attributes"])

            entity_df = entity_df[["attributeName", "dataType"]]
            entity_df.columns = ["Attribute", "Datatype"]

            def add_emoji(datatype):
                emoji_map = {
                    "string": "🟨",
                    "integer": "🟦",
                    "datetime": "🟥",
                }
                return f"{datatype.upper()} {emoji_map.get(datatype, '')}"

            entity_df["Datatype"] = entity_df["Datatype"].apply(add_emoji)
            st.data_editor(entity_df)


# Application Details Form
if st.session_state.entities:
    if st.button("Validate Design"):
        application_details = st.session_state.application_details
        application_name = st.text_input("Application Name", application_details.get("applicationName", ""))
        application_description = st.text_input("Application Description", application_details.get("applicationDescription", ""))
        application_prefix = st.text_input("Application Prefix", application_details.get("applicationTablePrefix", ""))

        application_architecture = st.selectbox("Application Architecture", ["Web App", "Mobile App"])
        application_language = st.selectbox("Application Language", ["Kotlin", "Java", "Javascript", "Python"])
        application_framework = st.selectbox("Application Framework", ["SpringBoot", "Koin", "Django", "FastAPI", "Node.js"])
        application_cloud = st.selectbox("Application Cloud Provider", ["AWS", "Azure", "GCP", "Huawei"])
        application_compute = st.selectbox("Application Compute Mode", ["Serverless", "VM", "Container"])
        application_database = st.selectbox("Application Database", ["Microsoft SQL", "MySQL", "SQL Server"])

        application_table_data = {
            "applicationId": None,
            "applicationProjectId": 100,
            "applicationUserId": 103,
            "applicationName": application_name,
            "applicationDescription": application_description,
            "applicationArchitecture": application_architecture,
            "applicationFramework": application_framework,
            "applicationLanguage": application_language,
            "applicationCloudProvider": application_cloud,
            "applicationCloudCompute": application_compute,
            "applicationDatabase": application_database,
            "applicationTablePrefix": application_prefix,
            "applicationStatus": "ACTIVE",
            "applicationCreatedAt": None,
            "applicationUpdatedAt": None,
            "applicationWorkplaceId": 100,
            "applicationEnableMakerChecker": "NO"
        }

        st.session_state.application_table_data = application_table_data

# Generate Excel Data
if st.session_state.application_table_data:
    st.info("Let go ahead to Deploy!")
    if st.session_state.entities:
        if st.button("Generate Qoonity Excel"):
            entities = st.session_state.entities

            application_table_df = pd.DataFrame([st.session_state.application_table_data])
            st.session_state.generated_application_table = application_table_df
            st.write("Application Table")
            st.dataframe(application_table_df)

            entity_table_data = service.generate_entity_table(entities)
            entity_table_df = pd.DataFrame(entity_table_data)
            st.session_state.generated_entity_table = entity_table_df
            st.write("Entity Table")
            st.dataframe(entity_table_df)

            attribute_table_data = service.generate_attribute_table(entities)
            attribute_table_df = pd.DataFrame(attribute_table_data)
            st.session_state.generated_attribute_table = attribute_table_df
            st.write("Attribute Table")
            st.dataframe(attribute_table_df)

            st.session_state.tables_created = True

    # Deploy Application
    if st.session_state.tables_created:
        if st.button("QooDeploy"):
            with st.spinner('Logging in...'):
                login_auth_data = api.login()
                auth_token = login_auth_data.get("token", None)

                if not auth_token:
                    st.error("Authentication Failed!")
                    st.stop()

            # Process 1: Configure Application
            with st.spinner('Configuring Application'):
                application_create = api.create_application(auth_token, st.session_state.application_table_data)
                if application_create["responseCode"] == "00":
                    new_application = api.get_application_by_name(auth_token, st.session_state.application_table_data["applicationName"])
                    if new_application["responseCode"] == "00":
                        st.session_state.application_created = True
                        new_application_id = new_application["data"][0]["applicationId"]
                        st.session_state.application_id = new_application_id
                        st.success("Application Configuration Done ✅")
                    else:
                        st.error(f"Application Configuration Failed: {new_application['responseMessage']}")
                else:
                    st.error(f"Application Configuration Failed: {application_create['responseMessage']}")
                time.sleep(1)

            # Process 2: Configure Entities
            if st.session_state.application_created:
                with st.spinner('Configuring Entities'):
                    entity_table_data = service.generate_entity_table(st.session_state.entities)
                    for entity in entity_table_data:
                        print(new_application_id)
                        entity["entityApplicationId"] = new_application_id  # Assign new app ID
                    
                    entity_create = api.bulk_create_entity(auth_token, entity_table_data)
                    
                    if entity_create["responseCode"] == "00":
                        st.session_state.entities_created = True
                        st.success("Entity Configuration Done ✅")
                    else:
                        st.error("Entity Configuration Failed")
                    time.sleep(1)

            # Process 3: Configure Attributes
            if st.session_state.entities_created:
                with st.spinner('Configuring Attributes'):
                    attribute_table_data = service.generate_attribute_table(st.session_state.entities)
                    attribute_create = api.bulk_create_attribute(auth_token, attribute_table_data)
                    if attribute_create["responseCode"] == "00":
                        st.session_state.attributes_created = True
                        st.success("Attribute Configuration Done ✅")
                    else:
                        st.error("Attribute Configuration Failed")
            
            # 
            if st.session_state.attributes_created:
                applicationId = st.session_state.application_id
                if st.button("Download Codes"):
                    file = api.code_download(applicationId)
                    print()
                    #add button to download 
                
                applicationId = st.session_state.application_id
                if st.button("Deploy Codes"):
                    swagger_link = api.code_download(applicationId)
                    # add button to link to link
