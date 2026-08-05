import streamlit as st
import streamlit.components.v1 as components
import requests
import random
import datetime
import base64
import os

# -----------------------------------------------------------------------------
# Configuration & Global Styling (Working Animated Gradient + Glassmorphism)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Resins Store Catalog",
    page_icon="💍",
    layout="wide"
)

# Injected Fullscreen Animated Layer + Glassmorphism Styling
st.markdown("""
<style>
    /* Animated Gradient Background Element */
    #animated-bg {
        position: fixed;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        z-index: -9999;
        background: linear-gradient(
            135deg, 
            #1a000d 0%, 
            #5a0022 20%, 
            #990033 40%, 
            #2b021d 60%, 
            #800020 80%, 
            #4a001e 100%
        );
        animation: diagonalMove 12s linear infinite alternate;
    }

    /* Keyframes animating actual CSS translation across the diagonal axis */
    @keyframes diagonalMove {
        0% {
            transform: translate(0, 0);
        }
        100% {
            transform: translate(-25%, -25%);
        }
    }

    /* Transparent Streamlit Shell */
    .stApp {
        background: transparent !important;
        color: #ffffff !important;
    }

    /* Glassmorphism Cards & Containers */
    div[data-testid="stVerticalBlock"] > div[style*="flex"] {
        background: rgba(255, 255, 255, 0.07) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 16px !important;
        padding: 1rem !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
    }

    /* Glassmorphism Buttons */
    .stButton > button {
        background: rgba(255, 255, 255, 0.12) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
    }

    .stButton > button:hover {
        background: rgba(255, 255, 255, 0.25) !important;
        border-color: rgba(255, 255, 255, 0.5) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(233, 30, 99, 0.4) !important;
    }

    /* Glassmorphism Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(30, 0, 15, 0.55) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    /* Glassmorphism Dialog Modal */
    div[role="dialog"] {
        background: rgba(35, 2, 20, 0.85) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 20px !important;
        color: #ffffff !important;
    }

    /* Input Fields Customization */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea, .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
    }

    /* Make Streamlit star icons larger and gold when active */
    div[data-testid="stFeedback"] button {
        transform: scale(1.3);
        margin-right: 8px;
    }
</style>

<!-- Injected HTML element behind app UI -->
<div id="animated-bg"></div>
""", unsafe_allow_html=True)

# Your Verified Telegram Bot Credentials
TELEGRAM_BOT_TOKEN = "8644129117:AAG3CJ4xJVteiTmwuImnTQz5PXWFvhfqPLs"
TELEGRAM_CHAT_ID = "6359572760"

# Product Inventory
PRODUCTS = [
    {
        "id": 1,
        "name": "Resin Ring",
        "category": "Jewellery",
        "description": "A visualization of beauty and aesthetics, along with the modern requirements of today's jewellery fashion. Colours can be customised.",
        "price": 500,
        "images": [
            "images/SaveClip.App_753224950_17897573046550553_9171311841910070315_n.jpg.webp",
            "images/SaveClip.App_729164572_17897573055550553_1935948774416209706_n.jpg.webp",
            "images/SaveClip.App_753604692_17897573067550553_3868263303187958583_n.jpg.webp"
        ]
    }
]

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
def generate_order_number():
    """Generates a unique order ID."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
    rand_id = random.randint(100, 999)
    return f"ORD-{timestamp}-{rand_id}"

def send_telegram_message(message_text):
    """Generic payload sender for orders, reviews, and client opinions."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message_text,
        "parse_mode": "Markdown"
    }
    try:
        res = requests.post(url, json=payload, timeout=5)
        return res.status_code == 200, res.text
    except Exception as e:
        return False, str(e)

def send_telegram_order(order_data):
    """Sends background order notifications directly to your Telegram chat."""
    payment_info = f"*Payment Method:* {order_data['payment_method']}"
    if order_data['payment_method'] == "Online Payment":
        payment_info += f"\n*Transaction ID / Reference:* `{order_data['transaction_id']}`"

    message_text = (
        f"🛒 *NEW ORDER RECEIVED*\n"
        f"-------------------------------\n"
        f"*Order No:* `{order_data['order_no']}`\n"
        f"*Product:* {order_data['product_name']}\n"
        f"*Quantity:* {order_data['quantity']}\n"
        f"*Total Price:* PKR {order_data['total_price']:,}\n\n"
        f"💳 *PAYMENT INFO*\n"
        f"{payment_info}\n\n"
        f"👤 *CUSTOMER DETAILS*\n"
        f"*Name:* {order_data['customer_name']}\n"
        f"*Phone:* {order_data['customer_phone']}\n"
        f"*Address:* {order_data['customer_address']}\n"
        f"*Customization/Notes:* {order_data['customer_notes'] or 'None'}\n"
        f"-------------------------------"
    )
    return send_telegram_message(message_text)

def trigger_side_party_poppers():
    """Fires subtle party popper confetti from the screen sides."""
    confetti_html = """
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
    <script>
        var count = 200;
        var defaults = { origin: { y: 0.7 } };

        function fire(particleRatio, opts) {
          confetti(Object.assign({}, defaults, opts, {
            particleCount: Math.floor(count * particleRatio)
          }));
        }

        fire(0.25, { spread: 26, startVelocity: 55, origin: { x: 0, y: 0.8 } });
        fire(0.2, { spread: 60, origin: { x: 0, y: 0.8 } });
        
        fire(0.25, { spread: 26, startVelocity: 55, origin: { x: 1, y: 0.8 } });
        fire(0.2, { spread: 60, origin: { x: 1, y: 0.8 } });
    </script>
    """
    components.html(confetti_html, height=0, width=0)

def get_base64_image(image_path):
    """Converts local image to base64 so it renders safely inside HTML components."""
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode("utf-8")
            return f"data:image/webp;base64,{encoded}"
    return None

def render_auto_sliding_carousel(image_paths, height=350, interval_sec=4):
    """Renders an automatic horizontal slider cycling photos every 4-5 seconds."""
    img_html_elements = []
    
    for idx, path in enumerate(image_paths):
        b64_str = get_base64_image(path)
        if b64_str:
            img_html_elements.append(
                f'<div class="slide" style="min-width: 100%; width: 100%; flex-shrink: 0; scroll-snap-align: start;">'
                f'<img src="{b64_str}" style="width: 100%; height: {height}px; object-fit: cover; border-radius: 12px;">'
                f'</div>'
            )

    if not img_html_elements:
        st.error("Images could not be loaded. Please verify files exist in the 'images/' folder.")
        return

    unique_id = f"carousel_{random.randint(1000, 9999)}"
    
    carousel_html = f"""
    <div id="{unique_id}_container" style="
        display: flex;
        overflow-x: auto;
        scroll-snap-type: x mandatory;
        scroll-behavior: smooth;
        gap: 0px;
        border-radius: 12px;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: none;
    ">
        {''.join(img_html_elements)}
    </div>
    <style>
        #{unique_id}_container::-webkit-scrollbar {{ display: none; }}
    </style>
    <script>
        (function() {{
            const container = document.getElementById('{unique_id}_container');
            const totalSlides = {len(img_html_elements)};
            let currentIndex = 0;

            if (totalSlides > 1) {{
                setInterval(() => {{
                    currentIndex = (currentIndex + 1) % totalSlides;
                    const scrollAmount = container.clientWidth * currentIndex;
                    container.scrollTo({{
                        left: scrollAmount,
                        behavior: 'smooth'
                    }});
                }}, {interval_sec * 1000});
            }}
        }})();
    </script>
    """
    components.html(carousel_html, height=height + 10)

# -----------------------------------------------------------------------------
# Main User Interface
# -----------------------------------------------------------------------------
st.title("🛍️ Resins Store Catalog")
st.write("Browse products and place orders instantly.")

# Sidebar Filters & Developer Info
st.sidebar.header("Filter Products")
categories = ["All"] + sorted(list(set(p["category"] for p in PRODUCTS)))
selected_category = st.sidebar.selectbox("Select Category", categories)

st.sidebar.divider()
st.sidebar.caption(" **Web Developer:** 0314-4012872")

filtered_products = PRODUCTS if selected_category == "All" else [p for p in PRODUCTS if p["category"] == selected_category]

# Session State
if "selected_product" not in st.session_state:
    st.session_state.selected_product = None

cols = st.columns(3)
for idx, product in enumerate(filtered_products):
    col = cols[idx % 3]
    with col:
        render_auto_sliding_carousel(product["images"], height=320, interval_sec=4.5)
            
        st.subheader(product["name"])
        st.write(f"**Category:** {product['category']}")
        st.write(product["description"])
        st.write(f"**Price:** PKR {product['price']:,}/-")
        
        if st.button("Order Now", key=f"btn_{product['id']}"):
            st.session_state.selected_product = product

# Order Modal Dialog
if st.session_state.selected_product is not None:
    prod = st.session_state.selected_product
    
    @st.dialog(f"Order: {prod['name']}")
    def show_order_modal():
        render_auto_sliding_carousel(prod["images"], height=280, interval_sec=4)
            
        st.subheader(prod["name"])
        st.write(f"**Category:** {prod['category']}")
        st.write(f"**Description:** {prod['description']}")
        st.write(f"**Price per item:** PKR {prod['price']:,}/-")
        
        st.divider()
        
        quantity = st.number_input(
            "Quantity", 
            min_value=1, 
            max_value=50, 
            value=1, 
            key=f"qty_input_{prod['id']}"
        )
        
        total_price = quantity * prod["price"]
        st.info(f"Total Amount: **PKR {total_price:,}/-**")
        
        st.write("### Payment Method")
        payment_method = st.radio(
            "Select Payment Option *",
            ["Online Payment", "COD (Cash on Delivery)"],
            key=f"payment_radio_{prod['id']}"
        )

        if payment_method == "Online Payment":
            st.success(
                "**JazzCash Payment Details**\n\n"
                "• **Account Number:** `0305-8866692`\n\n"
                "• **Account Name:** Rimsha Fatima\n\n"
                "Please send the total amount to the JazzCash account above and enter your transaction ID (TID) below."
            )

        st.divider()
        
        with st.form("checkout_form"):
            transaction_id = ""
            if payment_method == "Online Payment":
                transaction_id = st.text_input("Transaction ID (TID) / Reference Number *")
            
            customer_name = st.text_input("Full Name *")
            customer_phone = st.text_input("Phone Number *")
            customer_address = st.text_area("Delivery Address *")
            customer_notes = st.text_area("Color Customization / Special Instructions (Optional)")
            
            submitted = st.form_submit_button("Submit Order")
            
            if submitted:
                missing_fields = []
                if not customer_name.strip():
                    missing_fields.append("Full Name")
                if not customer_phone.strip():
                    missing_fields.append("Phone Number")
                if not customer_address.strip():
                    missing_fields.append("Delivery Address")
                if payment_method == "Online Payment" and not transaction_id.strip():
                    missing_fields.append("Transaction ID (TID)")

                if missing_fields:
                    st.error(f"Please fill in all required fields: {', '.join(missing_fields)}.")
                else:
                    order_data = {
                        "order_no": generate_order_number(),
                        "product_name": prod["name"],
                        "quantity": quantity,
                        "total_price": total_price,
                        "payment_method": payment_method,
                        "transaction_id": transaction_id,
                        "customer_name": customer_name,
                        "customer_phone": customer_phone,
                        "customer_address": customer_address,
                        "customer_notes": customer_notes
                    }
                    
                    with st.spinner("Processing order..."):
                        success, result = send_telegram_order(order_data)
                    
                    if success:
                        st.success(f"🎉 Thank you, {customer_name}! Your order #{order_data['order_no']} has been placed successfully.")
                        trigger_side_party_poppers()
                    else:
                        st.error(f"Failed to deliver order message to Telegram. Error: {result}")

        st.markdown(
            "💬 *For further order details, contact on "
            "[+92 305-8866692](https://wa.me/923058866692) through WhatsApp.*"
        )
        
        if st.button("Close"):
            st.session_state.selected_product = None
            st.rerun()

    show_order_modal()

# -----------------------------------------------------------------------------
# Bottom Interactive Sections (Review & Brand Opinion Forms)
# -----------------------------------------------------------------------------
st.divider()

# Section 1: Customer Review Box with Interactive Star Selection
st.subheader("⭐ Leave a Review")

# Streamlit native feedback component renders 5 interactive outlined stars (0 to 4 index)
star_rating_index = st.feedback("stars")

with st.form("client_review_form"):
    review_text = st.text_area("How was your experience:", placeholder="Write your experience with Resins By R...")
    review_submitted = st.form_submit_button("Submit Review")

    if review_submitted:
        if star_rating_index is None:
            st.error("Please click on the stars above to select a star rating!")
        elif not review_text.strip():
            st.error("Please fill in 'How was your experience:' before submitting.")
        else:
            # st.feedback returns 0-indexed integers (0 = 1 star, 4 = 5 stars)
            rating_val = star_rating_index + 1
            stars_visual = f"{'★' * rating_val}{'☆' * (5 - rating_val)}"
            
            telegram_msg = (
                f"⭐ *NEW CLIENT REVIEW*\n"
                f"-------------------------------\n"
                f"*Rating:* {rating_val} / 5 Stars ({stars_visual})\n"
                f"*Experience:* {review_text.strip()}\n"
                f"-------------------------------"
            )
            with st.spinner("Submitting review..."):
                ok, err = send_telegram_message(telegram_msg)
            if ok:
                st.success("Thank you for submitting your review!")
            else:
                st.error(f"Could not submit review. Error: {err}")

st.divider()

# Section 2: Brand Description
st.markdown(
    '**"Resins by R"** is a brand worth to be trusted and attended, as it opts the '
    '"quality over quantity" fact, making the clients to trust with all their heart. '
    'We do NOT ignore the service demands of our clients, and ensure all the details '
    'are kept in check, building the pure-trust relation with the clients, instead '
    'of just developing a "Buyer-Seller" sense. We do all our best to keep the clients '
    'satisfied and comfortable with our purchases.\n\n'
    'But still, if you think we can serve you better than we are, your opinion is of '
    'great importance for us.\n\n'
    '*(Resins By R)\'s Development team.*'
)

# Section 3: Client Opinion Form
with st.form("client_opinion_form"):
    opinion_text = st.text_area("Your opinion:", placeholder="Share your suggestions or opinion with us...")
    opinion_submitted = st.form_submit_button("Submit Opinion")

    if opinion_submitted:
        if not opinion_text.strip():
            st.error("Please enter your opinion before submitting.")
        else:
            telegram_msg = (
                f"💡 *NEW CLIENT OPINION*\n"
                f"-------------------------------\n"
                f"*Opinion:* {opinion_text.strip()}\n"
                f"-------------------------------"
            )
            with st.spinner("Submitting opinion..."):
                ok, err = send_telegram_message(telegram_msg)
            if ok:
                st.success("Thank you for sharing your valuable opinion with us!")
            else:
                st.error(f"Could not submit opinion. Error: {err}")

# Footer Developer Information
st.divider()
st.caption("Web Developer: 0314-4012872")
