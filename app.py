# YouTube to MP3 Converter Web App
# Install required libraries: pip install streamlit yt-dlp

import streamlit as st
import yt_dlp
import os
import re
from pathlib import Path

# Configure page
st.set_page_config(
    page_title="YouTube to MP3 Converter",
    page_icon="🎵",
    layout="centered"
)

def clean_filename(filename):
    """
    Remove special characters from filename to avoid file system issues.
    
    Args:
        filename: Original filename string
    
    Returns:
        Cleaned filename safe for file systems
    """
    # Remove special characters, keep only alphanumeric, spaces, hyphens, underscores
    cleaned = re.sub(r'[^\w\s-]', '', filename)
    # Replace multiple spaces with single space
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()

def download_youtube_audio(url, output_path, quality='192'):
    """
    Download YouTube video and convert to MP3.
    
    Args:
        url: YouTube video URL
        output_path: Path object where to save the file
        quality: Audio quality in kbps (128, 192, or 320)
    
    Returns:
        Tuple of (success: bool, message: str, filepath: str or None)
    """
    try:
        # Create downloads folder if it doesn't exist
        output_path.mkdir(exist_ok=True)
        
        # Configure yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',  # Get best audio quality
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',  # Extract audio
                'preferredcodec': 'mp3',  # Convert to MP3
                'preferredquality': quality,  # Set quality
            }],
            'outtmpl': str(output_path / '%(title)s.%(ext)s'),  # Output template
            'quiet': False,  # Show progress
            'no_warnings': False,
        }
        
        # Download and convert
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract video info first
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'video')
            
            # Clean the filename
            clean_title = clean_filename(video_title)
            
            # Update output template with cleaned name
            ydl_opts['outtmpl'] = str(output_path / f'{clean_title}.%(ext)s')
            
            # Download and convert
            with yt_dlp.YoutubeDL(ydl_opts) as ydl_download:
                ydl_download.download([url])
            
            # Find the downloaded file
            mp3_file = output_path / f"{clean_title}.mp3"
            
            if mp3_file.exists():
                return True, f"Successfully converted: {clean_title}", str(mp3_file)
            else:
                return False, "File was downloaded but not found in expected location", None
                
    except Exception as e:
        error_msg = str(e)
        
        # Provide user-friendly error messages
        if "Video unavailable" in error_msg:
            return False, "❌ Error: Video is unavailable or private", None
        elif "Invalid URL" in error_msg or "Unsupported URL" in error_msg:
            return False, "❌ Error: Invalid YouTube URL", None
        elif "network" in error_msg.lower():
            return False, "❌ Error: Network connection issue. Check your internet.", None
        else:
            return False, f"❌ Error: {error_msg}", None

def main():
    """
    Main function to run the Streamlit web app.
    """
    
    # App header
    st.title("🎵 YouTube to MP3 Converter")
    st.markdown("Convert any YouTube video to MP3 audio format")
    st.markdown("---")
    
    # Create two columns for better layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Input field for YouTube URL
        youtube_url = st.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
            help="Paste the full YouTube video URL here"
        )
    
    with col2:
        # Quality selector
        quality = st.selectbox(
            "Audio Quality",
            options=["128", "192", "320"],
            index=1,  # Default to 192kbps
            help="Higher quality = larger file size"
        )
        st.caption(f"{quality}kbps")
    
    # Convert button
    if st.button("🎵 Convert to MP3", type="primary", use_container_width=True):
        
        # Validate URL
        if not youtube_url:
            st.error("⚠️ Please enter a YouTube URL")
            return
        
        if "youtube.com" not in youtube_url and "youtu.be" not in youtube_url:
            st.error("⚠️ Please enter a valid YouTube URL")
            return
        
        # Create downloads folder path
        downloads_path = Path("downloads")
        
        # Show progress
        with st.spinner("🔄 Downloading video..."):
            status_placeholder = st.empty()
            status_placeholder.info("📥 Fetching video information...")
            
            # Perform download and conversion
            success, message, filepath = download_youtube_audio(
                youtube_url, 
                downloads_path, 
                quality
            )
        
        # Show result
        if success:
            st.success(f"✅ {message}")
            
            # Read the file for download
            with open(filepath, 'rb') as f:
                audio_bytes = f.read()
            
            # Get just the filename
            filename = Path(filepath).name
            
            # Create download button
            st.download_button(
                label="⬇️ Download MP3",
                data=audio_bytes,
                file_name=filename,
                mime="audio/mpeg",
                use_container_width=True
            )
            
            st.balloons()  # Celebration animation!
            
            # Show file info
            file_size = len(audio_bytes) / (1024 * 1024)  # Convert to MB
            st.info(f"📊 File size: {file_size:.2f} MB")
            
        else:
            st.error(message)
    
    # Instructions section
    st.markdown("---")
    with st.expander("ℹ️ How to use"):
        st.markdown("""
        **Steps:**
        1. Copy a YouTube video URL
        2. Paste it in the text box above
        3. Select your preferred audio quality
        4. Click "Convert to MP3"
        5. Wait for the conversion to complete
        6. Click "Download MP3" to save the file
        
        **Notes:**
        - Higher quality = larger file size
        - 192kbps is recommended for most users (good balance)
        - 320kbps is best for audiophiles
        - 128kbps is good for saving space
        """)
    
    with st.expander("⚠️ Troubleshooting"):
        st.markdown("""
        **Common issues:**
        - **"Invalid URL"**: Make sure you copied the complete YouTube URL
        - **"Video unavailable"**: Video might be private or deleted
        - **"Network error"**: Check your internet connection
        - **"FFmpeg not found"**: Run `pip install yt-dlp` again
        
        **Supported URLs:**
        - https://www.youtube.com/watch?v=...
        - https://youtu.be/...
        """)
    
    # Footer
    st.markdown("---")
    st.caption("⚠️ Please respect copyright laws and only download content you have permission to use.")

# Run the app
if __name__ == "__main__":
    main()