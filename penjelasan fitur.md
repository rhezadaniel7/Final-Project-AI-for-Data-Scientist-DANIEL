🏗️ Struktur Flow Chatbot
1. Flow Chatbot Sederhana
- Chatbot memproses semua input user langsung dengan method process_message()
- Menggunakan ChatbotState enum untuk mengelola state percakapan

2. Human Node
- Implementasi state WAITING_HUMAN yang menunggu respons manual
- Method _handle_human_response() untuk memproses feedback manusia
- Percakapan tidak langsung selesai, menunggu konfirmasi user

3. Tool Menu
-  Class MenuManager untuk mengelola menu lengkap
-  Method _show_menu() menampilkan menu berdasarkan kategori
-  Menu mencakup kopi, teh, minuman dingin, makanan, dan snack

4. Tools untuk Handle Order
-  add_to_order() - Menambah item ke pesanan
-  remove_from_order() - Menghapus item dari pesanan
-  clear_order() - Membersihkan seluruh pesanan
-  confirm_order() - Konfirmasi sebelum pemesanan final
-  place_order() - Memproses pesanan final dengan ID unik

5. All Set - Chatbot Siap!
-  Flow lengkap dari greeting → order → confirmation → finalization
-  Error handling dan input validation
-  Conversation history tracking
-  Testing framework included

🚀 Fitur Unggulan
✅ Natural Language Processing - Mengerti berbagai cara menyebutkan pesanan
✅ Smart Menu Search - Pencarian menu dengan keyword
✅ Modifier Support - Size, susu, gula, suhu otomatis terdeteksi
✅ Order Management - Tambah, hapus, modifikasi pesanan
✅ Confirmation Flow - Double-check sebelum finalisasi
✅ Indonesian Language - Full support bahasa Indonesia
✅ Interactive Testing - Built-in testing framework
📋 Cara Penggunaan

Jalankan program: python chatbot.py
Pilih mode: Interaktif atau testing
Mulai pesan: Ketik "menu" atau langsung pesan
Contoh input:
- "menu" → Lihat daftar menu
- "2 cappuccino large" → Pesan 2 cappuccino ukuran besar
- "pesanan" → Lihat keranjang
- "konfirmasi" → Proses pesanan
