import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime
import random
from db_config import get_connection

# ----------------------------
# Hotjar Tracking Script
# ----------------------------
HOTJAR_ID = 6461822  # 🔁 Replace this with your real Hotjar Site ID
components.html(f"""
<script>
    (function(h,o,t,j,a,r){{
        h.hj=h.hj||function(){{(h.hj.q=h.hj.q||[]).push(arguments)}};
        h._hjSettings={{hjid:6461822,hjsv:6}};
        a=o.getElementsByTagName('head')[0];
        r=o.createElement('script');r.async=1;
        r.src=t+h._hjSettings.hjid+j+h._hjSettings.hjsv;
        a.appendChild(r);
    }})(window,document,'https://static.hotjar.com/c/hotjar-','.js?sv=');
</script>
""", height=0)

# ----------------------------
# Page Setup
# ----------------------------
st.set_page_config(page_title="🛍️ E-commerce Funnel Analysis", layout="wide")
st.title("🛒 Product Funnel Dashboard")

conn = get_connection()
cursor = conn.cursor(dictionary=True)

# ----------------------------
# Sidebar: User Session
# ----------------------------
st.sidebar.header("🧑 User Session")
username = st.sidebar.text_input("Enter your username")
device = st.sidebar.selectbox("Device", ["Mobile", "Desktop", "Tablet"])
location = st.sidebar.text_input("Location")

# Start Session
if st.sidebar.button("Start Session"):
    signup_time = datetime.now()
    cursor.execute(
        "INSERT INTO users (username, device, location, signup_time) VALUES (%s, %s, %s, %s)",
        (username, device, location, signup_time)
    )
    conn.commit()
    st.session_state.user_id = cursor.lastrowid
    st.sidebar.success(f"Session started for {username} (User ID: {st.session_state.user_id})")

# Simulate Dummy Funnel Events
if st.sidebar.button("🚀 Simulate Funnel Traffic"):
    cursor.execute("SELECT user_id FROM users ORDER BY RAND() LIMIT 5")
    users = cursor.fetchall()
    cursor.execute("SELECT product_id FROM products")
    products = cursor.fetchall()

    for _ in range(50):
        user = random.choice(users)['user_id']
        product = random.choice(products)['product_id']
        funnel = ['add_to_cart']
        if random.random() > 0.4:
            funnel.append('checkout')
        if random.random() > 0.5:
            funnel.append('purchase')
        for step in funnel:
            cursor.execute(
                "INSERT INTO events (user_id, product_id, event_type, event_time) VALUES (%s, %s, %s, %s)",
                (user, product, step, datetime.now())
            )
    conn.commit()
    st.sidebar.success("✅ 50 simulated funnel events added.")

# ----------------------------
# Main Interface
# ----------------------------
if "user_id" in st.session_state:
    # Product Catalog
    st.subheader("🛍️ Product Catalog")
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    for product in products:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                st.markdown(f"**{product['name']}** – ₹{product['price']}")
            with col2:
                if st.button("🛒 Add to Cart", key=f"cart_{product['product_id']}"):
                    cursor.execute(
                        "INSERT INTO events (user_id, product_id, event_type, event_time) VALUES (%s, %s, %s, %s)",
                        (st.session_state.user_id, product['product_id'], "add_to_cart", datetime.now())
                    )
                    conn.commit()
                    st.success(f"{product['name']} added to cart!")
            with col3:
                if st.button("🧾 Checkout", key=f"checkout_{product['product_id']}"):
                    cursor.execute(
                        "INSERT INTO events (user_id, product_id, event_type, event_time) VALUES (%s, %s, %s, %s)",
                        (st.session_state.user_id, product['product_id'], "checkout", datetime.now())
                    )
                    conn.commit()
                    st.info(f"{product['name']} moved to checkout.")
            with col4:
                if st.button("✅ Purchase", key=f"purchase_{product['product_id']}"):
                    cursor.execute(
                        "INSERT INTO events (user_id, product_id, event_type, event_time) VALUES (%s, %s, %s, %s)",
                        (st.session_state.user_id, product['product_id'], "purchase", datetime.now())
                    )
                    conn.commit()
                    st.success(f"{product['name']} purchased!")

    # ----------------------------
    # Funnel Analytics
    # ----------------------------
    st.divider()
    st.subheader("📈 Funnel Performance")

    cursor.execute("""
        SELECT e.event_type, p.name AS product, COUNT(*) AS count
        FROM events e
        JOIN products p ON e.product_id = p.product_id
        WHERE user_id = %s
        GROUP BY e.event_type, p.name
    """, (st.session_state.user_id,))
    
    data = cursor.fetchall()
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df)
        st.bar_chart(df.pivot(index="product", columns="event_type", values="count").fillna(0))
    else:
        st.info("No events yet. Try interacting with the catalog or simulate traffic.")
else:
    st.warning("Start a user session from the sidebar to view the catalog and funnel.")
