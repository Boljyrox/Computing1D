import streamlit as st
import re
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="SUTD Merch Store",
    page_icon="https://sutd.edu.sg/favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS for Styling ---
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# This is a workaround to inject custom CSS
# In a real-world scenario, you'd host this file.
style_css = """
/* General Dark Theme */
body {
    color: #FFFFFF; /* Changed to white for better readability */
    background-color: #2b2b2b;
}
.stApp {
    background-color: #1e1e1e;
}
h1, h2, h3, h4, h5, h6 {
    color: #FFFFFF; /* Ensure headers are white */
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background-color: #252526;
    border-right: 1px solid #444;
}

/* Product Tile Styling */
.product-tile {
    background-color: #333333;
    border: 1px solid #444;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    transition: transform 0.2s;
}
.product-tile:hover {
    transform: scale(1.02);
}
.product-tile img {
    border-radius: 5px;
    margin-bottom: 15px;
}
.product-title {
    font-size: 1.5em;
    font-weight: bold;
    margin-bottom: 10px;
    color: #FFFFFF; /* Ensure title is white */
}
.product-price {
    font-size: 1.2em;
    color: #4CAF50; /* A nice green for price */
    margin-bottom: 15px;
}

/* Checkout Card Styling */
.checkout-card {
    background-color: #252526;
    padding: 25px;
    border-radius: 10px;
    border: 1px solid #444;
    height: 100%;
}
.checkout-title {
    font-size: 1.8em;
    font-weight: bold;
    margin-bottom: 20px;
    border-bottom: 2px solid #4CAF50;
    padding-bottom: 10px;
}
.cart-item {
    margin-bottom: 10px;
    padding-bottom: 10px;
    border-bottom: 1px solid #444;
}

/* Out of Stock Badge */
.out-of-stock {
    color: #dc3545;
    font-weight: bold;
}
"""
with open("style.css", "w") as f:
    f.write(style_css)

local_css("style.css")


# --- Product Data ---
# You can easily change prices, colors, and sizes here.
# NOTE: To use local images, create an 'assets' folder, place your images inside,
# and change the path like: "image": "assets/your_image_name.png"
PRODUCTS = {
    "tshirt1": {"name": "SUTD Classic Tee", "price": 25.00, "type": "T-Shirt", "colors": ["Black", "White", "Grey"], "sizes": ["S", "M", "L", "XL"], "image": "/assets/shirt1.jpeg"},
    "socks1": {"name": "SUTD Ankle Socks", "price": 12.00, "type": "Socks", "colors": ["White", "Black"], "sizes": ["One Size"], "image": "https://placehold.co/400x400/333333/FFFFFF?text=SUTD+Socks"},
    "jacket1": {"name": "SUTD Windbreaker", "price": 65.00, "type": "Jacket", "colors": ["Black", "Blue"], "sizes": ["S", "M", "L", "XL"], "image": "https://placehold.co/400x400/333333/FFFFFF?text=SUTD+Jacket"},
    "jacket2": {"name": "SUTD Bomber Jacket", "price": 80.00, "type": "Jacket", "colors": ["Olive Green"], "sizes": ["M", "L"], "stock": 0, "image": "https://placehold.co/400x400/CCCCCC/FFFFFF?text=Out+of+Stock"},
}

# --- Initialize Session State ---
if 'cart' not in st.session_state:
    st.session_state.cart = {}
if 'student_id' not in st.session_state:
    st.session_state.student_id = ""
if 'discount_applied' not in st.session_state:
    st.session_state.discount_applied = False


# --- Helper Functions ---
def add_to_cart(product_id, name, price, color, size, quantity):
    """Adds an item to the cart in session state."""
    cart_item_key = f"{product_id}-{color}-{size}"
    if cart_item_key in st.session_state.cart:
        st.session_state.cart[cart_item_key]["quantity"] += quantity
    else:
        st.session_state.cart[cart_item_key] = {
            "name": name,
            "price": price,
            "color": color,
            "size": size,
            "quantity": quantity,
        }
    st.success(f"Added {quantity} x {name} ({color}, {size}) to cart!")

def remove_from_cart(cart_item_key):
    """Removes an item from the cart."""
    if cart_item_key in st.session_state.cart:
        del st.session_state.cart[cart_item_key]

def validate_student_id(student_id):
    """Validates SUTD student ID format."""
    pattern = re.compile(r"^1010[0-9]{3}$")
    return pattern.match(student_id)

# --- Sidebar ---
with st.sidebar:
    st.image("https://sutd.edu.sg/SUTD_Stylised_Logo_R_RGB.png", width=200)
    st.title("SUTD Merch Store")
    st.markdown("---")
    st.info("Welcome to the official merchandise store for SUTD students and faculty!")


# --- Main Page Layout ---
main_col, checkout_col = st.columns([2.5, 1])

with main_col:
    st.title("Products")
    st.markdown("---")

    for product_id, details in PRODUCTS.items():
        st.markdown(f'<div class="product-tile">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            image_path = details["image"]
            # Check if it's a local path and if the file exists
            if not image_path.startswith("http") and not os.path.exists(image_path):
                # If local file is missing, use a placeholder and show a warning
                st.warning(f"Image not found: {image_path}")
                st.image("https://placehold.co/400x400/CCCCCC/FFFFFF?text=Image+Missing", use_column_width=True)
            else:
                # Otherwise, display the image from URL or valid local path
                st.image(image_path, use_column_width=True)

        with col2:
            st.markdown(f'<p class="product-title">{details["name"]}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="product-price">${details["price"]:.2f}</p>', unsafe_allow_html=True)

            if details.get("stock", 1) == 0:
                st.markdown('<p class="out-of-stock">Out of Stock</p>', unsafe_allow_html=True)
            else:
                with st.form(key=f"form_{product_id}"):
                    color = st.selectbox("Color", details["colors"], key=f"color_{product_id}")
                    size = st.selectbox("Size", details["sizes"], key=f"size_{product_id}")
                    quantity = st.number_input("Quantity", min_value=1, max_value=10, step=1, key=f"qty_{product_id}")
                    
                    submitted = st.form_submit_button("Add to Cart")
                    if submitted:
                        add_to_cart(product_id, details["name"], details["price"], color, size, quantity)

        st.markdown('</div>', unsafe_allow_html=True)

# --- Checkout Column ---
with checkout_col:
    st.markdown('<div class="checkout-card">', unsafe_allow_html=True)
    st.markdown('<p class="checkout-title">Shopping Cart</p>', unsafe_allow_html=True)

    if not st.session_state.cart:
        st.write("Your cart is empty.")
    else:
        subtotal = 0
        # Iterate over a copy of items to allow deletion
        for key, item in list(st.session_state.cart.items()):
            item_total = item["price"] * item["quantity"]
            subtotal += item_total
            
            item_col, button_col = st.columns([4, 1])
            with item_col:
                st.markdown(f"""
                <div class="cart-item">
                    <b>{item['name']}</b> ({item['color']}, {item['size']})<br>
                    {item['quantity']} x ${item['price']:.2f} = <b>${item_total:.2f}</b>
                </div>
                """, unsafe_allow_html=True)
            with button_col:
                 # Use a unique key for the remove button
                if st.button("Remove", key=f"remove_{key}"):
                    remove_from_cart(key)
                    st.experimental_rerun() # Rerun to update the cart display immediately
        
        st.markdown("---")
        st.subheader(f"Subtotal: ${subtotal:.2f}")

        # Student Discount Section
        st.markdown("---")
        st.subheader("SUTD Student Discount")
        student_id_input = st.text_input(
            "Enter SUTD ID (e.g., 1010123)",
            key="student_id_input",
            help="Must be in the format '1010XXX'"
        )

        if st.button("Apply Discount"):
            if validate_student_id(student_id_input):
                st.session_state.discount_applied = True
                st.success("40% student discount applied!")
            else:
                st.session_state.discount_applied = False
                st.error("Invalid SUTD Student ID format.")

        discount = 0
        if st.session_state.discount_applied:
            discount = subtotal * 0.40
            st.write(f"Discount (40%): -${discount:.2f}")

        final_total = subtotal - discount
        st.header(f"Total: ${final_total:.2f}")

        if st.button("Checkout"):
            st.balloons()
            st.success("Thank you for your purchase! Your order has been placed.")
            st.session_state.cart = {} # Clear cart
            st.session_state.discount_applied = False
            st.experimental_rerun()


    st.markdown('</div>', unsafe_allow_html=True)


# --- About Us Section ---
st.markdown("---")
st.header("About Us")
st.markdown("""
<div style="text-align: center; padding: 20px;">
    <p>This store is proudly founded and run by a team of passionate SUTD students.</p>
    <p><b>Founders:</b> Balaji, Leonard, and Marcus</p>
    <p>We believe in creating high-quality, stylish merchandise that lets you show off your SUTD pride.</p>
</div>
""", unsafe_allow_html=True)

