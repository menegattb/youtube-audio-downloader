import streamlit as st
import json
from pathlib import Path

st.set_page_config(page_title="YouTube Downloads", layout="wide")

def load_progress():
    progress_file = Path("downloads/audio/playlist_progress.json")
    if progress_file.exists():
        with open(progress_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"playlists": {}}

def main():
    st.title("YouTube Downloads Progress")
    
    data = load_progress()
    playlists = data.get("playlists", {})
    
    # Create three columns for different status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📥 In Progress")
        for playlist_id, info in playlists.items():
            if info["status"] == "in_progress":
                with st.expander(info["title"]):
                    st.write(f"Total videos: {info.get('total_videos', 0)}")
                    st.write(f"Downloaded: {len(info['downloaded_videos'])}")
                    if "total_videos" in info and info["total_videos"] > 0:
                        progress = len(info["downloaded_videos"]) / info["total_videos"]
                        st.progress(progress)
    
    with col2:
        st.subheader("✅ Completed")
        for playlist_id, info in playlists.items():
            if info["status"] == "completed":
                with st.expander(info["title"]):
                    st.write(f"Total videos: {len(info['downloaded_videos'])}")
                    st.progress(1.0)
    
    with col3:
        st.subheader("📊 Statistics")
        total_playlists = len(playlists)
        completed = sum(1 for p in playlists.values() if p["status"] == "completed")
        in_progress = sum(1 for p in playlists.values() if p["status"] == "in_progress")
        
        st.metric("Total Playlists", total_playlists)
        st.metric("Completed", completed)
        st.metric("In Progress", in_progress)

if __name__ == "__main__":
    main()
