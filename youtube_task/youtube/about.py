import streamlit as st

def about():
    st.markdown(
        """
        <style>
          /* Overall page styling */
          .about-container {
              background: linear-gradient(135deg, #ff7e5f, #feb47b);
              border-radius: 15px;
              padding: 2rem;
              color: #ffffff;
              font-family: 'Arial', sans-serif;
              box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
          }
          
          /* Title styling */
          .about-container h3 {
              font-size: 2.5rem;
              font-weight: bold;
              text-align: center;
              margin-bottom: 1rem;
              text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.4);
          }
          
          /* List styling */
          .about-container ul {
              list-style: none;
              padding: 0;
          }
          .about-container li {
              margin: 0.75rem 0;
              padding-left: 1.5rem;
              position: relative;
              font-size: 1.2rem;
          }
          .about-container li::before {
              content: "🎬";
              position: absolute;
              left: 0;
              top: 0;
          }
          
          /* Additional fancy text styling */
          .about-container p {
              font-size: 1.1rem;
              line-height: 1.6;
              margin-bottom: 1rem;
          }
          
          /* Footer note */
          .about-container .footer-note {
              text-align: center;
              font-size: 0.9rem;
              opacity: 0.8;
              margin-top: 2rem;
          }
        </style>

        <div class="about-container">
          <h3>About YouTube Task</h3>
          <p>Welcome to <strong>YouTube Task</strong>, your one‑stop app for all YouTube utilities. Here’s how it works:</p>
          <ul>
            <li><strong>YouTube/Google Login:</strong> No login is required unless you want to fetch age‑restricted videos.</li>
            <li><strong>Age Restricted Videos:</strong> Currently, the app cannot fetch age‑restricted videos (a user login is required).</li>
            <li><strong>Video Resolution:</strong> Not every video is available in all resolutions – the resolution you choose might not exist.</li>
            <li><strong>Recommended Hardware:</strong> This is a lightweight app designed to work on modest hardware.</li>
            <li><strong>Proxies:</strong> An option exists in the downloader modules to use proxy server IPs for improved connectivity.</li>
          </ul>
          <p>Enjoy exploring the powerful and beautifully designed YouTube Task utilities!</p>
          <div class="footer-note">Crafted with passion &amp; creativity.</div>
        </div>
        """,
        unsafe_allow_html=True
    )