import streamlit as st
from PIL import Image
import heapq, pickle, os

# Node class for Huffman tree
class Node:
    def __init__(self, value, freq, left=None, right=None):
        self.value = value
        self.freq = freq
        self.left = left
        self.right = right
    def __lt__(self, other):
        return self.freq < other.freq

def build_codes(node, prefix="", codes={}):
    if node is None:
        return
    if node.value is not None:
        codes[node.value] = prefix
    build_codes(node.left, prefix + "0", codes)
    build_codes(node.right, prefix + "1", codes)
    return codes

st.set_page_config(page_title="Huffman Image Compressor | Project By Zahraddeen", layout="centered")
st.title("📦 Huffman Image Compressor | Project By Zahraddeen")
st.write("Upload an image and see Huffman coding compression in action!")

uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # Step 1: Load Image
    img = Image.open(uploaded_file).convert("L")  # grayscale
    st.image(img, caption="Uploaded Image", use_column_width=True)
    st.success("✅ Step 1: Image loaded successfully")

    # Step 2: Build Frequency Table
    flat_data = list(img.getdata())
    freq = {}
    for pixel in flat_data:
        freq[pixel] = freq.get(pixel, 0) + 1
    st.success("✅ Step 2: Frequency table built")

    # Step 3: Build Huffman Tree
    heap = [Node(val, f) for val, f in freq.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        n1 = heapq.heappop(heap)
        n2 = heapq.heappop(heap)
        merged = Node(None, n1.freq + n2.freq, n1, n2)
        heapq.heappush(heap, merged)
    root = heap[0]
    st.success("✅ Step 3: Huffman tree created")

    # Step 4: Generate Codes
    codes = build_codes(root, "")
    st.success("✅ Step 4: Huffman codes generated")

    # Step 5: Encode Pixels
    encoded_data = "".join(codes[p] for p in flat_data)
    st.success("✅ Step 5: Image pixels encoded")

    # Step 6: Pack Bits into Bytes
    extra = (8 - len(encoded_data) % 8) % 8
    encoded_data = f"{extra:08b}" + encoded_data + "0" * extra
    b = bytearray()
    for i in range(0, len(encoded_data), 8):
        byte = encoded_data[i:i+8]
        b.append(int(byte, 2))
    st.success("✅ Step 6: Data packed into bytes")

    # Step 7: Save Compressed File
    output_file = "compressed.huff"
    with open(output_file, "wb") as f:
        pickle.dump((img.size, freq, b), f)
    st.success("✅ Step 7: Compressed file created")

    # Step 8: Show Results
file_size = len(uploaded_file.getbuffer())

comp_size = os.path.getsize(output_file)
ratio = (1 - comp_size / orig_size) * 100

st.subheader("📊 Compression Results")
st.write(f"**Original Size:** {orig_size/1024:.2f} KB")
st.write(f"**Compressed Size:** {comp_size/1024:.2f} KB")
st.write(f"**Saved:** {ratio:.2f}%")

with open(output_file, "rb") as f:
        st.download_button("⬇️ Download Compressed File", f, file_name="compressed.huff")
