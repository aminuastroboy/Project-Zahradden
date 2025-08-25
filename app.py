import streamlit as st
from PIL import Image
import heapq
from collections import defaultdict
import io

# -------------------------------
# Huffman Coding Helper Classes
# -------------------------------
class Node:
    def __init__(self, freq, symbol, left=None, right=None):
        self.freq = freq
        self.symbol = symbol
        self.left = left
        self.right = right
        self.huff = ''

    def __lt__(self, nxt):
        return self.freq < nxt.freq


def build_huffman_tree(frequencies):
    heap = [Node(freq, sym) for sym, freq in frequencies.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        left.huff = "0"
        right.huff = "1"
        new_node = Node(left.freq + right.freq, None, left, right)
        heapq.heappush(heap, new_node)

    return heap[0]


def generate_codes(node, val="", codes={}):
    newVal = val + node.huff
    if node.left:
        generate_codes(node.left, newVal, codes)
    if node.right:
        generate_codes(node.right, newVal, codes)
    if node.symbol is not None:
        codes[node.symbol] = newVal
    return codes


# -------------------------------
# Streamlit Web App
# -------------------------------
st.set_page_config(page_title="Project Zahraddeen | Huffman Image Compressor", page_icon="🗜️")

st.title("🗜️ Project Zahraddeen | Huffman Image Compressor")
st.write("Upload an image and compress it using Huffman Coding.")

uploaded_file = st.file_uploader("Choose an image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # ✅ Safe way to get file size
    file_size_kb = len(uploaded_file.getbuffer()) / 1024

    # Ignore image color (grayscale)
    img = Image.open(uploaded_file).convert("L")

    st.image(img, caption="Original Image", use_container_width=True)

    # Convert image to byte array
    img_bytes = img.tobytes()

    # Frequency dictionary
    frequency = defaultdict(int)
    for byte in img_bytes:
        frequency[byte] += 1

    # Build Huffman tree and codes
    huffman_tree = build_huffman_tree(frequency)
    huffman_codes = generate_codes(huffman_tree)

    # Encode
    encoded_data = "".join([huffman_codes[byte] for byte in img_bytes])

    # Estimate compressed size (in bits → bytes)
    compressed_size_kb = len(encoded_data) / 8 / 1024

    st.subheader("📊 Compression Details")
    st.write(f"📂 Original Size: **{file_size_kb:.2f} KB**")
    st.write(f"🗜️ Compressed Size: **{compressed_size_kb:.2f} KB**")
    st.write(f"⚡ Compression Ratio: **{(compressed_size_kb/file_size_kb):.2f}x smaller**")

    # Offer download of encoded file
    compressed_bytes = int(encoded_data, 2).to_bytes((len(encoded_data) + 7) // 8, byteorder="big")
    st.download_button("⬇️ Download Compressed File", compressed_bytes, file_name="compressed.huff")

    st.success("✅ Compression completed successfully!")