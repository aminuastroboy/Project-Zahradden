import streamlit as st
from io import BytesIO
from PIL import Image
import heapq
import os

# ----------------------
# HUFFMAN ENCODING LOGIC
# ----------------------
class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq


def build_huffman_tree(data):
    freq = {}
    for byte in data:
        freq[byte] = freq.get(byte, 0) + 1

    heap = [Node(byte, f) for byte, f in freq.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = Node(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)

    return heap[0]


def build_codes(root):
    codes = {}

    def generate_codes(node, current_code):
        if node is None:
            return
        if node.char is not None:
            codes[node.char] = current_code
        generate_codes(node.left, current_code + "0")
        generate_codes(node.right, current_code + "1")

    generate_codes(root, "")
    return codes


def huffman_compress(data):
    root = build_huffman_tree(data)
    codes = build_codes(root)

    encoded_data = "".join(codes[byte] for byte in data)

    # Convert bits to bytes
    padding = 8 - len(encoded_data) % 8
    encoded_data += "0" * padding
    padded_info = "{0:08b}".format(padding)

    b = bytearray()
    b.append(int(padded_info, 2))
    for i in range(0, len(encoded_data), 8):
        byte = encoded_data[i:i+8]
        b.append(int(byte, 2))

    return bytes(b), root


# ----------------------
# STREAMLIT APP
# ----------------------
st.markdown(
    "<h3 style='text-align: center; font-size:22px; font-weight:bold;'>📦 Project Zahraddeen | Huffman Image Compressor</h3>",
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png", "bmp"])

if uploaded_file:
    # Load and display image
    img = Image.open(uploaded_file).convert("RGB")
    st.image(img, caption="Uploaded Image", use_container_width=True)

    # Convert to BMP (uncompressed raw format)
    bmp_buffer = BytesIO()
    img.save(bmp_buffer, format="BMP")
    bmp_data = bmp_buffer.getvalue()

    # Compress BMP data
    compressed_data, tree = huffman_compress(bmp_data)

    # Size comparison
    original_size = len(bmp_data) / 1024  # KB
    compressed_size = len(compressed_data) / 1024  # KB
    ratio = compressed_size / original_size * 100

    st.subheader("📊 Compression Results")
    st.write(f"**Original Size:** {original_size:.2f} KB")
    st.write(f"**Compressed Size:** {compressed_size:.2f} KB")
    st.write(f"**Compression Ratio:** {ratio:.2f}%")

    # Save compressed file
    compressed_filename = os.path.splitext(uploaded_file.name)[0] + "_compressed.bin"
    st.download_button(
        label="Download Compressed File",
        data=compressed_data,
        file_name=compressed_filename,
        mime="application/octet-stream"
    )