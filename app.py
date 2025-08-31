import streamlit as st
from collections import Counter, defaultdict
import heapq
import os
from PIL import Image
import io

# =========================
# Page Config
# =========================
st.set_page_config(
    page_title="Huffman Image Compressor",
    page_icon="🗜️",
    layout="centered"
)

# =========================
# Custom CSS
# =========================
st.markdown("""
    <style>
    .title {
        font-size:28px !important;
        font-weight:600;
        text-align:center;
        margin-bottom:20px;
    }
    .footer {
        margin-top:50px;
        text-align:center;
        font-size:14px;
        color: gray;
    }
    </style>
""", unsafe_allow_html=True)

# =========================
# Huffman Coding Implementation
# =========================
class Node:
    def __init__(self, freq, symbol=None, left=None, right=None):
        self.freq = freq
        self.symbol = symbol
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq


def build_huffman_tree(data):
    frequency = Counter(data)
    heap = [Node(freq, symbol) for symbol, freq in frequency.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        n1 = heapq.heappop(heap)
        n2 = heapq.heappop(heap)
        merged = Node(n1.freq + n2.freq, left=n1, right=n2)
        heapq.heappush(heap, merged)

    return heap[0]


def build_codes(node, current_code="", codes=defaultdict()):
    if node is None:
        return
    if node.symbol is not None:
        codes[node.symbol] = current_code
        return
    build_codes(node.left, current_code + "0", codes)
    build_codes(node.right, current_code + "1", codes)
    return codes


def huffman_compress(image_bytes):
    root = build_huffman_tree(image_bytes)
    huffman_codes = build_codes(root)

    encoded_data = "".join([huffman_codes[byte] for byte in image_bytes])
    padding = 8 - len(encoded_data) % 8
    encoded_data += "0" * padding

    padded_info = "{0:08b}".format(padding)
    encoded_data = padded_info + encoded_data

    b = bytearray()
    for i in range(0, len(encoded_data), 8):
        byte = encoded_data[i:i+8]
        b.append(int(byte, 2))

    return bytes(b), huffman_codes


def huffman_decompress(compressed_bytes, huffman_codes):
    bit_string = ""
    for byte in compressed_bytes:
        bit_string += "{0:08b}".format(byte)

    padding = int(bit_string[:8], 2)
    bit_string = bit_string[8:]
    encoded_data = bit_string[:-padding]

    reverse_codes = {v: k for k, v in huffman_codes.items()}

    current_code = ""
    decoded_bytes = bytearray()

    for bit in encoded_data:
        current_code += bit
        if current_code in reverse_codes:
            decoded_bytes.append(reverse_codes[current_code])
            current_code = ""

    return bytes(decoded_bytes)


# =========================
# UI
# =========================
st.markdown("<h1 class='title'>🗜️ Huffman Image Compressor</h1>", unsafe_allow_html=True)
st.write("Upload an image to compress or upload a `.huff` file to decompress it back.")

# Tabs for Compression / Decompression
tab1, tab2 = st.tabs(["📥 Compress Image", "📤 Decompress File"])

# -------------------------
# Compression Tab
# -------------------------
with tab1:
    uploaded_file = st.file_uploader("Upload an Image", type=["png", "jpg", "jpeg"], key="compress")

    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        st.image(img, caption="Uploaded Image", use_container_width=True)

        uploaded_file.seek(0, os.SEEK_END)
        original_size = uploaded_file.tell() / 1024
        uploaded_file.seek(0)

        img_bytes = uploaded_file.read()

        compressed_bytes, huffman_codes = huffman_compress(img_bytes)
        compressed_size = len(compressed_bytes) / 1024

        st.subheader("📊 Compression Results")
        col1, col2 = st.columns(2)
        col1.metric("Original Size", f"{original_size:.2f} KB")
        col2.metric("Compressed Size", f"{compressed_size:.2f} KB")

        # Save codes + data for decompression
        package = {
            "codes": huffman_codes,
            "data": compressed_bytes
        }
        import pickle
        package_bytes = pickle.dumps(package)

        st.download_button(
            label="⬇️ Download Compressed File",
            data=package_bytes,
            file_name="compressed.huff",
            mime="application/octet-stream"
        )

# -------------------------
# Decompression Tab
# -------------------------
with tab2:
    uploaded_compressed = st.file_uploader("Upload a .huff file", type=["huff"], key="decompress")

    if uploaded_compressed is not None:
        import pickle
        package = pickle.loads(uploaded_compressed.read())
        huffman_codes = package["codes"]
        compressed_bytes = package["data"]

        decompressed_bytes = huffman_decompress(compressed_bytes, huffman_codes)

        # Try to load back into an image
        try:
            img = Image.open(io.BytesIO(decompressed_bytes))
            st.image(img, caption="Decompressed Image", use_container_width=True)
            st.download_button(
                label="⬇️ Download Restored Image",
                data=decompressed_bytes,
                file_name="restored.png",
                mime="image/png"
            )
        except Exception:
            st.error("❌ Could not restore image properly. This is a demo implementation, works best with small PNGs.")

# =========================
# Footer (Student Details)
# =========================
st.markdown("""
<div class="footer">
    <hr/>
    <b>Name:</b> ZAHRADDEEN DOKA TANKO <br/>
    <b>Matric/ID Number:</b> CSC/20U/4093 <br/>
    <b>Faculty:</b> COMPUTING <br/>
    <b>Department:</b> COMPUTER SCIENCE <br/>
    <b>Level:</b> 400L <br/>
    <b>Contact:</b> dokahaya2ddeen@gmail.com | 09031641701
</div>
""", unsafe_allow_html=True)
