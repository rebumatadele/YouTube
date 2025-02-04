import streamlit as st

def app():
    st.markdown(
        """
        <style>
          /* Background and container styling */
          .about-container {
              background: url("https://images.unsplash.com/photo-1504384308090-c894fdcc538d?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80") no-repeat center center fixed;
              background-size: cover;
              padding: 3rem;
              border-radius: 15px;
              color: #fff;
              box-shadow: 0 10px 20px rgba(0,0,0,0.3);
              font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          }
          /* Overlay to darken the background image for readability */
          .about-overlay {
              background-color: rgba(0, 0, 0, 0.6);
              padding: 2rem;
              border-radius: 15px;
          }
          /* Title styling */
          .about-container h2 {
              font-size: 3rem;
              margin-bottom: 0.5rem;
              text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
          }
          /* Subtitle styling */
          .about-container p {
              font-size: 1.3rem;
              margin-bottom: 2rem;
              text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
          }
          /* List styling */
          .about-container ul {
              list-style: none;
              padding: 0;
          }
          .about-container li {
              font-size: 1.2rem;
              margin: 1rem 0;
              padding-left: 2.5rem;
              position: relative;
          }
          /* SVG icon for list items */
          .about-container li::before {
              content: "";
              position: absolute;
              left: 0;
              top: 0;
              width: 2rem;
              height: 2rem;
              background: url("data:image/svg+xml;utf8,<svg fill='%23FFD700' xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><path d='M12 .587l3.668 7.431 8.2 1.192-5.934 5.787 1.402 8.177L12 18.897l-7.336 3.852 1.402-8.177L.132 9.21l8.2-1.192z'/></svg>") no-repeat center center;
              background-size: contain;
          }
          /* Horizontal rule styling */
          hr {
              border: 0;
              height: 2px;
              background: #fff;
              margin: 2rem 0;
          }
          /* Footer styling */
          .footer {
              margin-top: 2rem;
              font-size: 0.9rem;
              text-align: center;
              opacity: 0.8;
          }
        </style>

        <div class="about-container">
            <div class="about-overlay">
                <h2>Welcome to YouTube Task</h2>
                <p>
                  <strong>Download YouTube videos, transcripts, thumbnails, and channel data – all in one place.</strong>
                </p>
                <hr>
                <h3>How It Works</h3>
                <ul>
                    <li><strong>Video Downloader:</strong> Paste a YouTube or Shorts URL to download the video in your chosen resolution.</li>
                    <li><strong>Transcript Downloader:</strong> Retrieve transcripts for multiple videos at once.</li>
                    <li><strong>Thumbnail Downloader:</strong> Download thumbnails for selected videos.</li>
                    <li><strong>Channel Downloader:</strong> Fetch all video IDs and URLs from a YouTube channel.</li>
                </ul>
                <div class="footer">
                  <p>Made with Passion.</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    app()
