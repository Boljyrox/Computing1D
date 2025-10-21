import streamlit as st
import re  # Import regular expressions for student ID validation
import os  # Import os to check if local image files exist
import time # Import time to add a delay after checkout

# --- Page Configuration ---
# st.set_page_config must be the first Streamlit command in your script.
st.set_page_config(
    page_title="SUTD Merch Store",  # Title that appears in the browser tab
    page_icon="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRN6vYzOHBz2f3kF3VuIysSmO-EU2gmTw1JQA&s", # Icon for the browser tab
    layout="wide",  # Use the full width of the page
    initial_sidebar_state="expanded",  # Keep the sidebar open by default
)

# --- Custom CSS for Styling ---
# A function to load and inject a local CSS file
def local_css(file_name):
    """Reads a local CSS file and applies its styles."""
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# This is a workaround to inject custom CSS.
# We define the CSS as a string, write it to a file, then read it back.
# In a real-world scenario, you'd just have a separate 'style.css' file.
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
/* ... (rest of your CSS) ... */

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
# Write the CSS string to a file named 'style.css'
with open("style.css", "w") as f:
    f.write(style_css)

# Call the function to load the 'style.css' file
local_css("style.css")


# --- Product Data ---
# This dictionary acts as our simple database for products.
# We can easily add/remove products or change details here.
# "stock": 0 is used to mark an item as "Out of Stock".
PRODUCTS = {
    "tshirt1": {"name": "SUTD Classic Tee", "price": 25.00, "type": "T-Shirt", "colors": ["Black", "White"], "sizes": ["S", "M", "L", "XL"], "image": "https://down-sg.img.susercontent.com/file/id-11134207-7r98u-lz3ih4krf1fs0f@resize_w900_nl.webp"},
    "socks2": {"name": "SUTD Crew Socks", "price": 15.00, "type": "Socks", "colors": ["White", "Black"], "sizes": ["One Size"], "image": "https://thesockshack.com/cdn/shop/files/the-sock-shack-maine-womens-crew-socks-three-pack-roll-top-comfort-fit-non-binding-white-k-bell-cotton_grande.jpg?v=1704911061"},
    "jacket1": {"name": "SUTD Hoodie", "price": 65.00, "type": "Jacket", "colors": ["Black"], "sizes": ["S", "M", "L", "XL"], "image": "https://down-sg.img.susercontent.com/file/id-11134207-7r991-lmd380f7uwind0@resize_w900_nl.webp"},
    "jacket2": {"name": "SUTD Bomber Jacket", "price": 80.00, "type": "Jacket", "colors": ["Olive Green"], "sizes": ["M", "L"], "stock": 0, "image": "https://placehold.co/400x400/CCCCCC/FFFFFF?text=Out+of+Stock"},
}

# --- Initialize Session State ---
# st.session_state is a dictionary that persists variables across script reruns (user interactions).
# This is crucial for keeping the cart and other user data alive.

# Initialize 'cart' as an empty dictionary if it doesn't already exist
if 'cart' not in st.session_state:
    st.session_state.cart = {}
# Initialize 'student_id' as an empty string
if 'student_id' not in st.session_state:
    st.session_state.student_id = ""
# Initialize 'discount_applied' as False. This flag tracks if the discount is active.
if 'discount_applied' not in st.session_state:
    st.session_state.discount_applied = False


# --- Helper Functions ---
def add_to_cart(product_id, name, price, color, size, quantity):
    """Adds an item to the cart in session state."""
    # Create a unique key for the cart item based on its ID and selected options
    cart_item_key = f"{product_id}-{color}-{size}"
    
    # If the exact item (same product, color, size) is already in the cart, just increase the quantity
    if cart_item_key in st.session_state.cart:
        st.session_state.cart[cart_item_key]["quantity"] += quantity
    # Otherwise, add this item as a new entry in the cart dictionary
    else:
        st.session_state.cart[cart_item_key] = {
            "name": name,
            "price": price,
            "color": color,
            "size": size,
            "quantity": quantity,
        }
    # Display a temporary success message to the user
    st.success(f"Added {quantity} x {name} ({color}, {size}) to cart!")

def remove_from_cart(cart_item_key):
    """Removes an item from the cart."""
    # Check if the item exists before trying to delete it
    if cart_item_key in st.session_state.cart:
        del st.session_state.cart[cart_item_key]
    # (Note: This function is defined but not used in the final app.
    # The removal logic is handled directly in the checkout column for simplicity.)

def validate_student_id(student_id):
    """Validates SUTD student ID format using regex."""
    # Defines a regex pattern:
    # ^      - start of the string
    # 1010   - must start with "1010"
    # [0-9]{3} - must be followed by exactly 3 digits (0-9)
    # $      - end of the string
    pattern = re.compile(r"^1010[0-9]{3}$")
    # pattern.match() checks if the student_id matches this pattern
    return pattern.match(student_id)

# --- Sidebar ---
# 'with st.sidebar:' puts all the elements inside this block into the sidebar
with st.sidebar:
    st.image("https://www.sutd.edu.sg/asd/wp-content/uploads/sites/3/2024/11/SUTD-logo-white@2x.png", width=200)
    st.title("SUTD Merch Store")
    st.markdown("---") # Adds a horizontal line
    st.info("Welcome to the official merchandise store for SUTD students!")


# --- Main Page Layout ---
# Create two main columns for the page layout
# main_col will be 2.5 times wider than checkout_col
main_col, checkout_col = st.columns([2.5, 1])

# This block populates the main (left) column
with main_col:
    st.title("Products")
    st.markdown("---")

    # Iterate through our PRODUCTS dictionary to display each one
    for product_id, details in PRODUCTS.items():
        # Use st.markdown to inject our custom 'product-tile' CSS class for styling
        st.markdown(f'<div class="product-tile">', unsafe_allow_html=True)
        
        # Create two inner columns: one for the image, one for the product details
        col1, col2 = st.columns([1, 2])
        
        with col1:
            image_path = details["image"]
            # Check if the image path is a local path (not a URL) AND if the file doesn't exist
            if not image_path.startswith("http") and not os.path.exists(image_path):
                # If the local image is missing, show a warning and a placeholder
                st.warning(f"Image not found: {image_path}")
                st.image("https://media.karousell.com/media/photos/products/2022/1/26/sutd_asd_t_shirt_1643201711_155bf5e7_progressive.jpg", use_container_width=True)
            else:
                # If it's a URL or a valid local file, display it
                st.image(image_path, use_container_width=True)

        with col2:
            # Display product details using our custom CSS classes
            st.markdown(f'<p class="product-title">{details["name"]}</p>', unsafe_allow_html=True)
            # Format the price to 2 decimal places
            st.markdown(f'<p class="product-price">${details["price"]:.2f}</p>', unsafe_allow_html=True)

            # Check if the product is out of stock (stock is 0 or key doesn't exist)
            # .get("stock", 1) safely gets the stock value, defaulting to 1 (in stock) if not specified
            if details.get("stock", 1) == 0:
                st.markdown('<p class="out-of-stock">Out of Stock</p>', unsafe_allow_html=True)
            else:
                # If the item is in stock, create a form to add it to the cart
                # 'st.form' groups inputs. The script only reruns when 'st.form_submit_button' is pressed.
                # This prevents the page from reloading every time a user changes the color or quantity.
                with st.form(key=f"form_{product_id}"):
                    # Select boxes for color and size options
                    color = st.selectbox("Color", details["colors"], key=f"color_{product_id}")
                    size = st.selectbox("Size", details["sizes"], key=f"size_{product_id}")
                    # Number input for quantity
                    quantity = st.number_input("Quantity", min_value=1, max_value=10, step=1, key=f"qty_{product_id}")
                    
                    # The "Add to Cart" button for this form
                    submitted = st.form_submit_button("Add to Cart")
                    if submitted:
                        # When the button is clicked, call our helper function
                        add_to_cart(product_id, details["name"], details["price"], color, size, quantity)

        # Close the 'product-tile' div
        st.markdown('</div>', unsafe_allow_html=True)

# --- Checkout Column ---
# This block populates the checkout (right) column
with checkout_col:
    # Use st.markdown to inject our custom 'checkout-title' CSS class
    st.markdown('<p class="checkout-title">Shopping Cart</p>', unsafe_allow_html=True)

    # --- Item Removal Logic ---
    # This logic runs at the *top* of the checkout block.
    # It checks if a 'remove_key' was set by clicking an "X" button.
    if "remove_key" in st.session_state:
        key_to_remove = st.session_state.remove_key
        # If the key (e.g., "tshirt1-Black-M") is in the cart, delete it
        if key_to_remove in st.session_state.cart:
            del st.session_state.cart[key_to_remove]
        # After processing, remove the 'remove_key' itself from session state
        del st.session_state.remove_key
        # Force the script to rerun immediately to reflect the empty cart
        st.rerun()

    # --- Display cart items ---
    # Check if the cart is empty
    if not st.session_state.cart:
        st.write("Your cart is empty.")
    else:
        # If the cart has items, calculate the total
        subtotal = 0

        # Iterate over a list copy of the cart's items.
        # We use list() so we can safely modify the cart (remove items) while iterating.
        for key, item in list(st.session_state.cart.items()):
            # Calculate total for this item
            item_total = item["price"] * item["quantity"]
            # Add to the subtotal
            subtotal += item_total

            # Create columns for the item text and the "X" remove button
            item_col, button_col = st.columns([4, 1])
            with item_col:
                # Display item details using an f-string with HTML
                st.markdown(f"""
                <div class="cart-item">
                    <b>{item['name']}</b> ({item['color']}, {item['size']})<br>
                    {item['quantity']} x ${item['price']:.2f} = <b>${item_total:.2f}</b>
                </div>
                """, unsafe_allow_html=True)

            with button_col:
                # Create a remove button. Each button needs a unique key.
                if st.button("X", key=f"remove_{key}"):
                    # If this button is clicked, set the 'remove_key' in session state
                    st.session_state.remove_key = key
                    # Force a rerun. The logic at the top of this `with` block will catch this key.
                    st.rerun()

        # Display the subtotal after the loop
        st.markdown(f"<hr><b>Subtotal: ${subtotal:.2f}</b>", unsafe_allow_html=True)


        # --- Student Discount Section ---
        st.markdown("---")
        st.subheader("SUTD Student Discount")
        student_id_input = st.text_input(
            "Enter SUTD ID (e.g., 1010123)",
            key="student_id_input", # A unique key for this widget
            help="Must be in the format '1010XXX'" # Tooltip for the user
        )

        # "Apply Discount" button
        if st.button("Apply Discount"):
            # Check the ID using our validation function
            if validate_student_id(student_id_input):
                # If valid, set the discount flag in session state
                st.session_state.discount_applied = True
                st.success("40% student discount applied!")
            else:
                # If invalid, ensure the flag is False and show an error
                st.session_state.discount_applied = False
                st.error("Invalid SUTD Student ID format.")

        discount = 0
        # If the discount flag is True (set in session state), calculate the discount
        if st.session_state.discount_applied:
            discount = subtotal * 0.40
            st.write(f"Discount (40%): -${discount:.2f}")

        # Calculate and display the final total
        final_total = subtotal - discount
        st.header(f"Total: ${final_total:.2f}")

        # --- Checkout Button ---
        if st.button("Checkout"):
            st.balloons() # Show a fun balloon animation
            st.success("Thank you for your purchase! Your order has been placed.")
            
            # Reset the cart and discount after a successful purchase
            st.session_state.cart = {}
            st.session_state.discount_applied = False
            
            # Wait 2 seconds so the user can read the success message
            time.sleep(2)
            # Rerun the script to show the now-empty cart
            st.rerun()

    # This closing div is for the 'checkout-card' (though it's outside the 'else' block)
    st.markdown('</div>', unsafe_allow_html=True)


# --- About Us Section ---
# This is a simple footer for the page
st.markdown("---")
st.header("About Us")
# Using st.markdown with HTML for centered text and styling
st.markdown("""
<div style="text-align: center; padding: 20px;">
    <p>This store is proudly founded and run by a team of passionate SUTD students.</p>
    <p><b>Founders:</b> Balaji, Leonard, and Marcus</p>
    <p>We believe in creating high-quality, stylish merchandise that lets you show off your SUTD pride.</p>
</div>
""", unsafe_allow_html=True)