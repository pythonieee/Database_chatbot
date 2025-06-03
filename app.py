import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Add the modules directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

# Import your custom modules
try:
    import modules.sql_connector as sql
    import modules.mysql_query_generator as query_gen
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Database Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .login-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .bot-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4caf50;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .connection-status {
        padding: 0.5rem;
        border-radius: 0.5rem;
        text-align: center;
        font-weight: bold;
        margin: 1rem 0;
    }
    .status-connected {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .status-disconnected {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    .database-selector {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'query_count' not in st.session_state:
    st.session_state.query_count = 0
if 'db_connection' not in st.session_state:
    st.session_state.db_connection = {}
if 'mysql_connection' not in st.session_state:
    st.session_state.mysql_connection = None
if 'available_databases' not in st.session_state:
    st.session_state.available_databases = []
if 'available_tables' not in st.session_state:
    st.session_state.available_tables = []
if 'current_database' not in st.session_state:
    st.session_state.current_database = ""
if 'last_selected_database' not in st.session_state:
    st.session_state.last_selected_database = ""

# Function to switch database
def switch_database(new_database):
    """Switch to a different database"""
    try:
        # Close existing connection
        if st.session_state.mysql_connection:
            sql.close_connection(st.session_state.mysql_connection)
        
        # Create new connection with the selected database
        connection = sql.create_connection(
            st.session_state.db_connection['host'],
            st.session_state.db_connection['username'],
            st.session_state.db_connection['password'],
            new_database
        )
        
        if connection:
            st.session_state.mysql_connection = connection
            st.session_state.current_database = new_database
            st.session_state.db_connection['database'] = new_database
            
            # Fetch tables for the new database
            tables_info = sql.fetch_all_tables(connection)
            if tables_info:
                st.session_state.available_tables = [list(table)[0] for table in tables_info]
            else:
                st.session_state.available_tables = []
            
            return True
        else:
            return False
    except Exception as e:
        st.error(f"Error switching database: {e}")
        return False

# Login Page
def login_page():
    st.markdown('<div class="main-header">🤖 Database Chatbot</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="login-container">
    </div>
    """, unsafe_allow_html=True)
    
    # Create login form
    with st.form("login_form"):
        st.subheader("🔐 MySQL Database Credentials")
        
        host = st.text_input("Host", placeholder="localhost", value="localhost")
        username = st.text_input("Username", placeholder="Enter your username", value="root")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        database = st.text_input("Initial Database", placeholder="Enter database name", value="classicmodels")
        
        st.info("💡 Don't worry! You can switch between databases after connecting.")
        
        st.markdown("---")
        
        # Login button
        login_submitted = st.form_submit_button("🚀 Connect to MySQL Server", use_container_width=True)
        
        if login_submitted:
            # Validate inputs
            if not all([host, username, password, database]):
                st.error("❌ Please fill in all required fields!")
            else:
                # Store connection details
                st.session_state.db_connection = {
                    'host': host,
                    'username': username,
                    'password': password,
                    'database': database,
                    'port': '3306',
                    'db_type': 'MySQL'
                }
                
                # Test actual database connection
                with st.spinner("Connecting to MySQL server..."):
                    try:
                        # First, connect to the specified database
                        connection = sql.create_connection(host, username, password, database)
                        
                        if connection:
                            st.session_state.mysql_connection = connection
                            st.session_state.current_database = database
                            st.session_state.logged_in = True
                            
                            # Fetch all available databases on the server
                            try:
                                # Connect to information_schema or mysql database to get all databases
                                temp_conn = sql.create_connection(host, username, password, 'information_schema')
                                if temp_conn:
                                    databases_info = sql.fetch_database_info(temp_conn)
                                    if databases_info is not None:
                                        # Filter out system databases if needed
                                        all_dbs = databases_info['Database'].tolist()
                                        # Remove system databases that users typically shouldn't access
                                        system_dbs = ['information_schema', 'mysql', 'performance_schema', 'sys']
                                        user_dbs = [db for db in all_dbs if db not in system_dbs]
                                        st.session_state.available_databases = user_dbs if user_dbs else all_dbs
                                    sql.close_connection(temp_conn)
                                
                                # Fetch tables for the current database
                                tables_info = sql.fetch_all_tables(connection)
                                if tables_info:
                                    st.session_state.available_tables = [list(table)[0] for table in tables_info]
                            except Exception as e:
                                st.warning(f"Connected but couldn't fetch all database info: {e}")
                                # Fallback: at least add the current database
                                st.session_state.available_databases = [database]
                            
                            st.success("✅ Successfully connected to MySQL server!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Failed to create database connection!")
                            
                    except Exception as e:
                        st.error(f"❌ Connection failed: {str(e)}")
    
    # Additional info
    with st.expander("ℹ️ Connection Help"):
        st.markdown("""
        ### Connection Tips:
        
        **MySQL Connection Requirements:**
        - Ensure MySQL server is running on port 3306
        - Check firewall settings
        - Verify username and password
        - Make sure you have necessary permissions
        - The initial database should exist, but you can switch to others after connecting
        
        **Database Switching Feature:**
        - After connecting, you'll see all available databases in the sidebar
        - You can switch between databases without reconnecting
        - Each database switch will update the available tables automatically
        
        **Common MySQL Issues:**
        - Connection timeout: Check if MySQL service is running
        - Access denied: Verify credentials and user permissions
        - Host not found: Ensure correct hostname/IP address
        - Database not found: Verify database name exists
        """)

# Main Application Page
def main_page():
    # Sidebar with database info and settings
    with st.sidebar:
        # Database connection info
        st.header("🔗 Database Connection")
        db_info = st.session_state.db_connection
        
        st.markdown(f"""
        <div class="connection-status status-connected">
            🟢 Connected to MySQL Server
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("Connection Details"):
            st.write(f"**Host:** {db_info['host']}")
            st.write(f"**Port:** 3306")
            st.write(f"**Username:** {db_info['username']}")
            st.write(f"**Current Database:** {st.session_state.current_database}")
            st.write(f"**Type:** MySQL")
        
        st.markdown("---")
        
        # Database Selector
        st.subheader("🗄️ Database Selector")
        
        if st.session_state.available_databases:
            # Create selectbox for database selection
            current_db_index = 0
            if st.session_state.current_database in st.session_state.available_databases:
                current_db_index = st.session_state.available_databases.index(st.session_state.current_database)
            
            selected_database = st.selectbox(
                "Choose Database:",
                st.session_state.available_databases,
                index=current_db_index,
                key="database_selector"
            )
            
            # Check if database selection changed
            if selected_database != st.session_state.current_database:
                if st.button("🔄 Switch Database", use_container_width=True):
                    with st.spinner(f"Switching to database: {selected_database}"):
                        if switch_database(selected_database):
                            st.success(f"✅ Switched to database: {selected_database}")
                            # Clear chat history when switching databases
                            if st.checkbox("Clear chat history when switching", value=True):
                                st.session_state.chat_history = []
                                st.session_state.query_count = 0
                            st.rerun()
                        else:
                            st.error(f"❌ Failed to switch to database: {selected_database}")
            
            # Show current database prominently
            st.markdown(f"""
            <div class="database-selector">
                <strong>🎯 Active Database:</strong><br>
                <code>{st.session_state.current_database}</code>
            </div>
            """, unsafe_allow_html=True)
        
        # Available tables for current database
        if st.session_state.available_tables:
            st.subheader("📋 Tables in Current DB")
            with st.expander(f"Tables in {st.session_state.current_database}"):
                for table in st.session_state.available_tables:
                    st.write(f"• {table}")
        
        st.markdown("---")
        
        # Refresh and utility buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Refresh", use_container_width=True):
                try:
                    connection = st.session_state.mysql_connection
                    if connection:
                        # Refresh available databases
                        temp_conn = sql.create_connection(
                            st.session_state.db_connection['host'],
                            st.session_state.db_connection['username'],
                            st.session_state.db_connection['password'],
                            'information_schema'
                        )
                        if temp_conn:
                            databases_info = sql.fetch_database_info(temp_conn)
                            if databases_info is not None:
                                all_dbs = databases_info['Database'].tolist()
                                system_dbs = ['information_schema', 'mysql', 'performance_schema', 'sys']
                                user_dbs = [db for db in all_dbs if db not in system_dbs]
                                st.session_state.available_databases = user_dbs if user_dbs else all_dbs
                            sql.close_connection(temp_conn)
                        
                        # Refresh tables for current database
                        tables_info = sql.fetch_all_tables(connection)
                        if tables_info:
                            st.session_state.available_tables = [list(table)[0] for table in tables_info]
                        
                        st.success("Refreshed!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error refreshing: {e}")
        
        with col2:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.session_state.query_count = 0
                st.success("Chat cleared!")
                st.rerun()
        
        st.markdown("---")
        
        # Session management
        st.subheader("🔧 Session")
        if st.button("🚪 Disconnect", use_container_width=True):
            # Close the database connection
            if st.session_state.mysql_connection:
                try:
                    sql.close_connection(st.session_state.mysql_connection)
                except:
                    pass
            
            # Reset session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Main content area
    st.markdown('<div class="main-header">🤖 Database Chatbot</div>', unsafe_allow_html=True)
    
    # Database status with current database highlighted
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div class="connection-status status-connected">
            🎯 Active Database: <strong>{st.session_state.current_database}</strong>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick stats
    if st.session_state.available_tables:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Available Databases", len(st.session_state.available_databases))
        with col2:
            st.metric("📋 Tables in Current DB", len(st.session_state.available_tables))
        with col3:
            st.metric("💬 Queries Asked", st.session_state.query_count)
    
    # Main chat interface
    st.subheader("💬 Chat Interface")
    
    # Display chat history
    for i, message in enumerate(st.session_state.chat_history):
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.write(message["content"])
            else:  # assistant
                st.write(message["content"])
                
                # Show which database was used for this query
                if "database_used" in message:
                    st.caption(f"🎯 Query executed on database: **{message['database_used']}**")
                
                # Show SQL query if available
                if "sql" in message:
                    with st.expander("Generated SQL Query"):
                        st.code(message["sql"], language='sql')
                
                # Show data if available
                if "data" in message and message["data"] is not None:
                    if isinstance(message["data"], list) and len(message["data"]) > 0:
                        df = pd.DataFrame(message["data"])
                        st.dataframe(df, use_container_width=True)
                        
                        # Add download button with unique key
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Download Results as CSV",
                            data=csv,
                            file_name=f"query_results_{st.session_state.current_database}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}.csv",
                            mime="text/csv",
                            key=f"download_btn_{i}"
                        )
                    elif isinstance(message["data"], list) and len(message["data"]) == 0:
                        st.info("Query executed successfully, but no results returned.")
                
                # Show error if available
                if "error" in message:
                    st.error(f"Error: {message['error']}")
    
    # Chat input
    user_input = st.chat_input(f"Ask me anything about the '{st.session_state.current_database}' database...")
    
    if user_input:
        # Add user message to chat history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Process the query using your backend modules
        with st.spinner("Processing your query..."):
            try:
                connection = st.session_state.mysql_connection
                
                if not connection:
                    st.error("Database connection lost. Please reconnect.")
                    return
                
                # Generate SQL query using your AI module
                generated_sql = query_gen.generate_mysql_query(user_input,connection)
                
                # Execute the query
                query_result = sql.execute_query(connection, generated_sql)
                
                if query_result is not None:
                    # Generate response content
                    if len(query_result) > 0:
                        response_content = f"I found {len(query_result)} result(s) for your query in the '{st.session_state.current_database}' database. Here's what I found:"
                    else:
                        response_content = f"Query executed successfully on '{st.session_state.current_database}' database, but no results were returned."
                    
                    # Add assistant response to chat history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response_content,
                        "sql": generated_sql,
                        "data": query_result,
                        "database_used": st.session_state.current_database
                    })
                else:
                    # Query failed
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": f"I encountered an error while executing your query on the '{st.session_state.current_database}' database. Please check the SQL syntax or try rephrasing your request.",
                        "sql": generated_sql,
                        "error": "Query execution failed",
                        "database_used": st.session_state.current_database
                    })
                
                st.session_state.query_count += 1
                st.rerun()  # Refresh to show the new messages
                
            except Exception as e:
                # Add error message to chat history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"Sorry, there was an error processing your query on the '{st.session_state.current_database}' database: {str(e)}",
                    "error": str(e),
                    "database_used": st.session_state.current_database
                })
                st.rerun()

# Main app logic
if not st.session_state.logged_in:
    login_page()
else:
    main_page()