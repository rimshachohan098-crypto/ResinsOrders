import streamlit as st
import requests
import random
import datetime

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Store Catalog & Direct Orders",
    page_icon="🛍️",
    layout="wide"
)

# Your Verified Telegram Bot Credentials
TELEGRAM_BOT_TOKEN = "8644129117:AAG3CJ4xJVteiTmwuImnTQz5PXWFvhfqPLs"
TELEGRAM_CHAT_ID = "6359572760"

# Sample Product Inventory (Replace or expand with your actual products)
PRODUCTS = [
    {
        "id": 101,
        "name": "Wireless Noise-Canceling Headphones",
        "category": "Electronics",
        "price": 89.99,
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500",
        "description": "High-fidelity Bluetooth headphones with active noise cancellation."
    },
    {
        "id": 102,
        "name": "Smart Fitness Watch",
        "category": "Electronics",
        "price": 49.99,
        "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500",
        "description": "Track steps, heart rate, and sleep cycles with an AMOLED display."
    },
    {
        "id": 103,
        "name": "Minimalist Canvas Backpack",
        "category": "Fashion",
        "price": 34.50,
        "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500",
        "description": "Durable water-resistant canvas backpack with a 15-inch laptop sleeve."
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

def send_telegram_order(order_data):
    """Sends background order notifications directly to your Telegram chat."""
    message_text = (
        f"🛒 *NEW ORDER RECEIVED*\n"
        f"-------------------------------\n"
        f"*Order No:* `{order_data['order_no']}`\n"
        f"*Product:* {order_data['product_name']}\n"
        f"*Quantity:* {order_data['quantity']}\n"
        f"*Total Price:* ${order_data['total_price']:.2f}\n\n"
        f"👤 *CUSTOMER DETAILS*\n"
        f"*Name:* {order_data['customer_name']}\n"
        f"*Phone:* {order_data['customer_phone']}\n"
        f"*Address:* {order_data['customer_address']}\n"
        f"*Notes:* {order_data['customer_notes'] or 'None'}\n"
        f"-------------------------------"
    )
    
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

# -----------------------------------------------------------------------------
# Main User Interface
# -----------------------------------------------------------------------------
st.title("🛍️ Online Store Catalog")
st.write("Browse products and place orders instantly.")

# Sidebar Filters
st.sidebar.header("Filter Products")
categories = ["All"] + sorted(list(set(p["category"] for p in PRODUCTS)))
selected_category = st.sidebar.selectbox("Select Category", categories)

filtered_products = PRODUCTS if selected_category == "All" else [p for p in PRODUCTS if p["category"] == selected_category]

# Session State
if "selected_product" not in st.session_state:
    st.session_state.selected_product = None

cols = st.columns(3)
for idx, product in enumerate(filtered_products):
    col = cols[idx % 3]
    with col:
        st.image(product["image"], use_container_width=True)
        st.subheader(product["name"])
        st.write(f"**Price:** ${product['price']:.2f}")
        if st.button("Order Now", key=f"btn_{product['id']}"):
            st.session_state.selected_product = product

# Order Modal Dialog
if st.session_state.selected_product is not None:
    prod = st.session_state.selected_product
    
    @st.dialog(f"Order: {prod['name']}")
    def show_order_modal():
        st.image(prod["image"], use_container_width=True)
        st.write(f"**Price per item:** ${prod['price']:.2f}")
        st.write(prod["description"])
        
        st.divider()
        
        with st.form("checkout_form"):
            quantity = st.number_input("Quantity", min_value=1, max_value=50, value=1)
            total_price = quantity * prod["price"]
            st.info(f"Total Amount: **${total_price:.2f}**")
            
            customer_name = st.text_input("Full Name *")
            customer_phone = st.text_input("Phone Number *")
            customer_address = st.text_area("Delivery Address *")
            customer_notes = st.text_area("Order Description / Special Notes (Optional)")
            
            submitted = st.form_submit_button("Submit Order")
            
            if submitted:
                if not customer_name.strip() or not customer_phone.strip() or not customer_address.strip():
                    st.error("Please fill in all required fields marked with *.")
                else:
                    order_data = {
                        "order_no": generate_order_number(),
                        "product_name": prod["name"],
                        "quantity": quantity,
                        "total_price": total_price,
                        "customer_name": customer_name,
                        "customer_phone": customer_phone,
                        "customer_address": customer_address,
                        "customer_notes": customer_notes
                    }
                    
                    with st.spinner("Processing order..."):
                        success, result = send_telegram_order(order_data)
                    
                    if success:
                        st.success(f"🎉 Thank you, {customer_name}! Your order #{order_data['order_no']} has been placed successfully.")
                        st.balloons()
                    else:
                        st.error(f"Failed to deliver order message to Telegram. Error: {result}")

        if st.button("Close"):
            st.session_state.selected_product = None
            st.rerun()

    show_order_modal()
