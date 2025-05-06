import streamlit as st
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth import Authentication
from forum import ForumManager

st.markdown("<h1 style='text-align: center;'>👥 Community Forum</h1>", unsafe_allow_html=True)

# Initialize authentication and forum managers
if 'auth_manager' not in st.session_state:
    st.session_state.auth_manager = Authentication()

if 'forum_manager' not in st.session_state:
    st.session_state.forum_manager = ForumManager()

# Authentication section
auth_tab, forum_tab = st.tabs(["Authentication", "Forum"])

with auth_tab:
    if 'username' not in st.session_state:
        st.session_state.username = None
        
    if st.session_state.username:
        st.success(f"Logged in as {st.session_state.username}")
        
        if st.button("Logout"):
            st.session_state.username = None
            st.rerun()
            
    else:
        login_tab, register_tab = st.tabs(["Login", "Register"])
        
        with login_tab:
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login"):
                if username and password:
                    success, message = st.session_state.auth_manager.authenticate(username, password)
                    if success:
                        st.session_state.username = username
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please enter both username and password")
        
        with register_tab:
            new_username = st.text_input("Choose Username", key="reg_username")
            new_email = st.text_input("Email", key="reg_email")
            new_password = st.text_input("Password", type="password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
            
            if st.button("Register"):
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                elif not all([new_username, new_email, new_password]):
                    st.error("All fields are required")
                else:
                    success, message = st.session_state.auth_manager.register_user(new_username, new_password, new_email)
                    if success:
                        st.success(message)
                        st.session_state.username = new_username
                        st.rerun()
                    else:
                        st.error(message)

with forum_tab:
    # Allow viewing posts without logging in, but require login for posting
    categories = ["General", "Depression", "Anxiety", "Stress Management", 
                  "Mindfulness", "Recovery", "Self-Care", "Support"]
                  
    # Sidebar with categories
    selected_category = st.sidebar.selectbox("Select Category", ["All"] + categories)
    
    # Main forum area
    if selected_category == "All":
        posts = st.session_state.forum_manager.get_posts()
    else:
        posts = st.session_state.forum_manager.get_posts(selected_category)
    
    # Create new post section (only for logged in users)
    if st.session_state.username:
        st.subheader("Create New Post")
        post_title = st.text_input("Post Title")
        post_category = st.selectbox("Category", categories)
        post_content = st.text_area("Content", height=100)
        
        if st.button("Submit Post"):
            if post_title and post_content:
                post_id = st.session_state.forum_manager.create_post(
                    st.session_state.username, post_title, post_content, post_category
                )
                st.success("Post created successfully!")
                st.rerun()
            else:
                st.error("Title and content are required")
    else:
        st.info("Please log in to create posts and participate in discussions")
    
    # Display posts
    st.subheader(f"Forum Posts - {selected_category}")
    
    if not posts:
        st.info("No posts found in this category")
    else:
        # Sort by newest first
        posts = sorted(posts, key=lambda x: x['timestamp'], reverse=True)
        
        for post in posts:
            with st.expander(f"{post['title']} (by {post['author']})"):
                st.write(f"**Category:** {post['category']}")
                st.write(f"**Posted on:** {post['timestamp']}")
                st.write(f"**Likes:** {post['likes']}")
                st.write("---")
                st.write(post['content'])
                st.write("---")
                
                # Like button (only for logged in users)
                if st.session_state.username:
                    already_liked = st.session_state.username in post.get('liked_by', [])
                    like_label = "Unlike" if already_liked else "Like"
                    
                    if st.button(like_label, key=f"like_{post['id']}"):
                        st.session_state.forum_manager.like_post(post['id'], st.session_state.username)
                        st.rerun()
                
                # Comments section
                st.subheader("Comments")
                comments = st.session_state.forum_manager.get_comments(post['id'])
                
                if not comments:
                    st.info("No comments yet")
                else:
                    for comment in comments:
                        st.text_area(
                            f"Comment by {comment['author']} on {comment['timestamp']}",
                            value=comment['content'],
                            disabled=True,
                            key=f"comment_{comment['id']}"
                        )
                
                # Add comment (only for logged in users)
                if st.session_state.username:
                    new_comment = st.text_area("Add a comment", key=f"new_comment_{post['id']}")
                    
                    if st.button("Submit Comment", key=f"submit_comment_{post['id']}"):
                        if new_comment:
                            st.session_state.forum_manager.add_comment(
                                post['id'], st.session_state.username, new_comment
                            )
                            st.success("Comment added successfully!")
                            st.rerun()
                        else:
                            st.error("Comment cannot be empty")
