import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

class ChatbotState(Enum):
    GREETING = "greeting"
    TAKING_ORDER = "taking_order"
    CONFIRMING_ORDER = "confirming_order"
    WAITING_HUMAN = "waiting_human"
    ORDER_COMPLETE = "order_complete"

@dataclass
class MenuItem:
    id: str
    name: str
    price: float
    category: str
    description: str = ""
    available: bool = True

@dataclass
class OrderItem:
    menu_item: MenuItem
    quantity: int = 1
    modifiers: List[str] = field(default_factory=list)
    special_requests: str = ""

@dataclass
class Order:
    items: List[OrderItem] = field(default_factory=list)
    customer_name: str = ""
    total: float = 0.0
    order_id: str = ""

class MenuManager:
    def __init__(self):
        self.menu = {
            # Kopi
            "espresso": MenuItem("espresso", "Espresso", 15000, "kopi", "Kopi hitam pekat dengan rasa kuat"),
            "americano": MenuItem("americano", "Americano", 18000, "kopi", "Espresso dengan air panas"),
            "cappuccino": MenuItem("cappuccino", "Cappuccino", 25000, "kopi", "Espresso dengan susu berbusa"),
            "latte": MenuItem("latte", "Caffe Latte", 28000, "kopi", "Espresso dengan susu steamed"),
            "macchiato": MenuItem("macchiato", "Macchiato", 26000, "kopi", "Espresso dengan sedikit susu berbusa"),
            "mocha": MenuItem("mocha", "Mocha", 32000, "kopi", "Latte dengan sirup coklat"),
            "kopi_susu": MenuItem("kopi_susu", "Kopi Susu Tradisional", 20000, "kopi", "Kopi robusta dengan susu kental manis"),
            
            # Teh
            "teh_tarik": MenuItem("teh_tarik", "Teh Tarik", 15000, "teh", "Teh dengan susu yang ditarik"),
            "teh_hijau": MenuItem("teh_hijau", "Teh Hijau", 12000, "teh", "Teh hijau segar"),
            "thai_tea": MenuItem("thai_tea", "Thai Tea", 18000, "teh", "Teh Thailand dengan susu"),
            "es_teh": MenuItem("es_teh", "Es Teh Manis", 10000, "teh", "Teh manis dingin"),
            
            # Minuman Dingin
            "es_kopi_susu": MenuItem("es_kopi_susu", "Es Kopi Susu", 22000, "dingin", "Kopi susu dingin dengan es"),
            "iced_latte": MenuItem("iced_latte", "Iced Latte", 30000, "dingin", "Latte dingin dengan es"),
            "cold_brew": MenuItem("cold_brew", "Cold Brew", 25000, "dingin", "Kopi seduh dingin 12 jam"),
            "frappuccino": MenuItem("frappuccino", "Frappuccino", 35000, "dingin", "Minuman kopi blended dengan es"),
            
            # Makanan
            "croissant": MenuItem("croissant", "Croissant", 18000, "makanan", "Roti pastry Prancis"),
            "sandwich": MenuItem("sandwich", "Sandwich Club", 35000, "makanan", "Sandwich dengan daging dan sayuran"),
            "pasta": MenuItem("pasta", "Pasta Carbonara", 45000, "makanan", "Pasta dengan saus krim dan bacon"),
            "nasi_goreng": MenuItem("nasi_goreng", "Nasi Goreng Spesial", 28000, "makanan", "Nasi goreng dengan telur dan ayam"),
            "cake": MenuItem("cake", "Slice Cake Coklat", 22000, "makanan", "Kue coklat lembut"),
            
            # Snack
            "cookies": MenuItem("cookies", "Cookies Choco Chip", 15000, "snack", "Kue kering coklat chip"),
            "muffin": MenuItem("muffin", "Blueberry Muffin", 20000, "snack", "Muffin dengan blueberry"),
            "donut": MenuItem("donut", "Glazed Donut", 12000, "snack", "Donut glazur manis")
        }
        
        self.modifiers = {
            "susu": ["soy", "almond", "oat", "regular"],
            "gula": ["tanpa_gula", "gula_sedikit", "gula_normal", "extra_manis"],
            "ukuran": ["small", "medium", "large"],
            "suhu": ["panas", "dingin", "es"],
            "extra": ["extra_shot", "decaf", "extra_foam", "no_foam"]
        }

    def get_menu_by_category(self, category: str) -> List[MenuItem]:
        return [item for item in self.menu.values() if item.category == category and item.available]
    
    def get_all_menu(self) -> List[MenuItem]:
        return [item for item in self.menu.values() if item.available]
    
    def search_menu(self, query: str) -> List[MenuItem]:
        query = query.lower()
        results = []
        for item in self.menu.values():
            if query in item.name.lower() or query in item.description.lower():
                results.append(item)
        return results
    
    def get_item_by_id(self, item_id: str) -> Optional[MenuItem]:
        return self.menu.get(item_id)

class OrderManager:
    def __init__(self):
        self.current_order = Order()
        self.order_counter = 1000
    
    def add_to_order(self, menu_item: MenuItem, quantity: int = 1, modifiers: List[str] = None, special_requests: str = ""):
        if modifiers is None:
            modifiers = []
        
        # Cek apakah item sudah ada di order
        for existing_item in self.current_order.items:
            if (existing_item.menu_item.id == menu_item.id and 
                existing_item.modifiers == modifiers and 
                existing_item.special_requests == special_requests):
                existing_item.quantity += quantity
                self._calculate_total()
                return f"Ditambahkan {quantity} {menu_item.name} ke pesanan (total: {existing_item.quantity})"
        
        # Tambah item baru
        order_item = OrderItem(menu_item, quantity, modifiers, special_requests)
        self.current_order.items.append(order_item)
        self._calculate_total()
        return f"Berhasil menambahkan {quantity} {menu_item.name} ke pesanan"
    
    def remove_from_order(self, item_index: int) -> str:
        if 0 <= item_index < len(self.current_order.items):
            removed_item = self.current_order.items.pop(item_index)
            self._calculate_total()
            return f"Berhasil menghapus {removed_item.menu_item.name} dari pesanan"
        return "Item tidak ditemukan dalam pesanan"
    
    def clear_order(self):
        self.current_order = Order()
        return "Pesanan telah dibersihkan"
    
    def get_order_summary(self) -> str:
        if not self.current_order.items:
            return "Pesanan masih kosong"
        
        summary = "📋 RINGKASAN PESANAN:\n"
        summary += "=" * 30 + "\n"
        
        for i, item in enumerate(self.current_order.items, 1):
            summary += f"{i}. {item.menu_item.name} x{item.quantity}\n"
            summary += f"   Harga: Rp {item.menu_item.price:,.0f}\n"
            
            if item.modifiers:
                summary += f"   Modifikasi: {', '.join(item.modifiers)}\n"
            
            if item.special_requests:
                summary += f"   Catatan: {item.special_requests}\n"
            
            subtotal = item.menu_item.price * item.quantity
            summary += f"   Subtotal: Rp {subtotal:,.0f}\n"
            summary += "-" * 25 + "\n"
        
        summary += f"\n💰 TOTAL: Rp {self.current_order.total:,.0f}"
        return summary
    
    def _calculate_total(self):
        total = 0
        for item in self.current_order.items:
            total += item.menu_item.price * item.quantity
        self.current_order.total = total
    
    def confirm_order(self) -> Dict[str, Any]:
        if not self.current_order.items:
            return {"success": False, "message": "Pesanan masih kosong"}
        
        return {
            "success": True,
            "order_summary": self.get_order_summary(),
            "total": self.current_order.total,
            "item_count": len(self.current_order.items)
        }
    
    def place_order(self, customer_name: str = "") -> Dict[str, Any]:
        if not self.current_order.items:
            return {"success": False, "message": "Tidak ada pesanan untuk diproses"}
        
        self.order_counter += 1
        self.current_order.order_id = f"ORD-{self.order_counter}"
        self.current_order.customer_name = customer_name
        
        # Simulasi pemrosesan pesanan
        order_result = {
            "success": True,
            "order_id": self.current_order.order_id,
            "customer_name": customer_name,
            "total": self.current_order.total,
            "estimated_time": "15-20 menit",
            "message": f"Pesanan berhasil! ID: {self.current_order.order_id}"
        }
        
        # Reset order setelah berhasil
        self.current_order = Order()
        return order_result

class KafeChatbot:
    def __init__(self):
        self.menu_manager = MenuManager()
        self.order_manager = OrderManager()
        self.state = ChatbotState.GREETING
        self.conversation_history = []
        self.awaiting_confirmation = False
        
    def start(self):
        """Memulai chatbot dengan pesan selamat datang"""
        welcome_msg = """
☕ Selamat datang di Kafe Digital! ☕

Saya adalah asisten virtual Anda untuk membantu pemesanan.
Ketik 'menu' untuk melihat daftar menu atau langsung sebutkan minuman/makanan yang Anda inginkan.
Ketik 'quit' untuk keluar.

Ada yang bisa saya bantu hari ini?
        """
        print(welcome_msg)
        self.state = ChatbotState.TAKING_ORDER
        return welcome_msg
    
    def process_message(self, user_input: str) -> str:
        """Memproses pesan dari user"""
        user_input = user_input.strip()
        
        # Handle quit command
        if user_input.lower() in ['quit', 'q', 'keluar', 'exit']:
            return self._handle_quit()
        
        # Log conversation
        self.conversation_history.append({"user": user_input, "timestamp": "now"})
        
        # Process based on current state
        if self.state == ChatbotState.GREETING:
            return self._handle_greeting(user_input)
        elif self.state == ChatbotState.TAKING_ORDER:
            return self._handle_taking_order(user_input)
        elif self.state == ChatbotState.CONFIRMING_ORDER:
            return self._handle_confirmation(user_input)
        elif self.state == ChatbotState.WAITING_HUMAN:
            return self._handle_human_response(user_input)
        else:
            return "Maaf, terjadi kesalahan sistem. Silakan mulai lagi."
    
    def _handle_greeting(self, user_input: str) -> str:
        self.state = ChatbotState.TAKING_ORDER
        return self._handle_taking_order(user_input)
    
    def _handle_taking_order(self, user_input: str) -> str:
        user_input_lower = user_input.lower()
        
        # Command untuk melihat menu
        if any(word in user_input_lower for word in ['menu', 'daftar', 'katalog', 'pilihan']):
            return self._show_menu()
        
        # Command untuk melihat pesanan saat ini
        if any(word in user_input_lower for word in ['pesanan', 'order', 'keranjang', 'list']):
            return self._show_current_order()
        
        # Command untuk konfirmasi pesanan
        if any(word in user_input_lower for word in ['konfirmasi', 'confirm', 'pesan', 'bayar', 'selesai']):
            return self._start_confirmation()
        
        # Command untuk membersihkan pesanan
        if any(word in user_input_lower for word in ['hapus semua', 'clear', 'reset', 'bersihkan']):
            self.order_manager.clear_order()
            return "✅ Pesanan telah dibersihkan. Silakan mulai memesan lagi!"
        
        # Proses pemesanan item
        return self._process_order_request(user_input)
    
    def _handle_confirmation(self, user_input: str) -> str:
        user_input_lower = user_input.lower()
        
        if any(word in user_input_lower for word in ['ya', 'yes', 'benar', 'ok', 'oke', 'lanjut']):
            return self._finalize_order()
        elif any(word in user_input_lower for word in ['tidak', 'no', 'batal', 'ubah']):
            self.state = ChatbotState.TAKING_ORDER
            return "Baik, Anda bisa mengubah pesanan. Apa yang ingin ditambah atau diubah?"
        else:
            return "Mohon konfirmasi dengan 'ya' untuk melanjutkan atau 'tidak' untuk mengubah pesanan."
    
    def _handle_human_response(self, user_input: str) -> str:
        """Handle respons setelah human node"""
        self.state = ChatbotState.TAKING_ORDER
        return f"Terima kasih atas responnya! {self._process_order_request(user_input)}"
    
    def _handle_quit(self) -> str:
        return "Terima kasih telah menggunakan layanan Kafe Digital! Sampai jumpa! 👋"
    
    def _show_menu(self) -> str:
        """Tool untuk menampilkan menu"""
        menu_text = "📜 MENU KAFE DIGITAL 📜\n"
        menu_text += "=" * 40 + "\n\n"
        
        categories = {}
        for item in self.menu_manager.get_all_menu():
            if item.category not in categories:
                categories[item.category] = []
            categories[item.category].append(item)
        
        category_names = {
            "kopi": "☕ KOPI",
            "teh": "🍵 TEH", 
            "dingin": "🧊 MINUMAN DINGIN",
            "makanan": "🍽️ MAKANAN",
            "snack": "🍪 SNACK"
        }
        
        for category, items in categories.items():
            menu_text += f"{category_names.get(category, category.upper())}\n"
            menu_text += "-" * 25 + "\n"
            for item in items:
                menu_text += f"• {item.name} - Rp {item.price:,.0f}\n"
                menu_text += f"  {item.description}\n\n"
            menu_text += "\n"
        
        menu_text += "💡 Tips: Sebutkan nama minuman/makanan yang Anda inginkan!\n"
        menu_text += "Contoh: 'Saya mau 2 cappuccino dan 1 sandwich'"
        
        return menu_text
    
    def _show_current_order(self) -> str:
        """Tool untuk menampilkan pesanan saat ini"""
        return self.order_manager.get_order_summary()
    
    def _process_order_request(self, user_input: str) -> str:
        """Tool untuk memproses permintaan pesanan"""
        # Extract numbers (quantity)
        numbers = re.findall(r'\d+', user_input)
        
        # Search for menu items in user input
        found_items = []
        user_input_lower = user_input.lower()
        
        for item in self.menu_manager.get_all_menu():
            # Check if item name is mentioned
            if item.name.lower() in user_input_lower:
                found_items.append(item)
            # Check for partial matches
            elif any(word in item.name.lower() for word in user_input_lower.split()):
                found_items.append(item)
        
        if not found_items:
            # Try to suggest similar items
            suggestions = self._get_suggestions(user_input)
            if suggestions:
                return f"Maaf, item tidak ditemukan. Mungkin maksud Anda:\n{suggestions}\n\nAtau ketik 'menu' untuk melihat semua pilihan."
            else:
                return "Maaf, saya tidak menemukan item yang Anda maksud. Ketik 'menu' untuk melihat semua pilihan yang tersedia."
        
        # Add items to order
        result_messages = []
        for i, item in enumerate(found_items):
            quantity = 1
            if i < len(numbers):
                quantity = int(numbers[i])
            elif numbers and i == 0:
                quantity = int(numbers[0])
            
            # Extract modifiers (simplified)
            modifiers = self._extract_modifiers(user_input)
            
            result = self.order_manager.add_to_order(item, quantity, modifiers)
            result_messages.append(result)
        
        response = "\n".join(result_messages)
        response += f"\n\n{self.order_manager.get_order_summary()}"
        response += "\n\n💬 Ada lagi yang ingin ditambahkan? Atau ketik 'konfirmasi' untuk melanjutkan pesanan."
        
        return response
    
    def _extract_modifiers(self, user_input: str) -> List[str]:
        """Extract modifiers dari input user"""
        modifiers = []
        user_input_lower = user_input.lower()
        
        # Check for size modifiers
        if any(word in user_input_lower for word in ['large', 'besar', 'jumbo']):
            modifiers.append("large")
        elif any(word in user_input_lower for word in ['small', 'kecil']):
            modifiers.append("small")
        else:
            modifiers.append("medium")
        
        # Check for milk modifiers
        if any(word in user_input_lower for word in ['soy', 'kedelai']):
            modifiers.append("soy")
        elif any(word in user_input_lower for word in ['almond']):
            modifiers.append("almond")
        elif any(word in user_input_lower for word in ['oat']):
            modifiers.append("oat")
        
        # Check for sugar modifiers
        if any(word in user_input_lower for word in ['tanpa gula', 'no sugar', 'sugar free']):
            modifiers.append("tanpa_gula")
        elif any(word in user_input_lower for word in ['extra manis', 'very sweet']):
            modifiers.append("extra_manis")
        
        # Check for temperature
        if any(word in user_input_lower for word in ['es', 'dingin', 'cold', 'iced']):
            modifiers.append("dingin")
        elif any(word in user_input_lower for word in ['panas', 'hot']):
            modifiers.append("panas")
        
        return modifiers
    
    def _get_suggestions(self, user_input: str) -> str:
        """Memberikan saran berdasarkan input user"""
        user_input_lower = user_input.lower()
        suggestions = []
        
        # Keyword matching for suggestions
        if any(word in user_input_lower for word in ['kopi', 'coffee']):
            kopi_items = self.menu_manager.get_menu_by_category("kopi")[:3]
            suggestions.extend([f"• {item.name}" for item in kopi_items])
        
        if any(word in user_input_lower for word in ['teh', 'tea']):
            teh_items = self.menu_manager.get_menu_by_category("teh")[:3]
            suggestions.extend([f"• {item.name}" for item in teh_items])
        
        if any(word in user_input_lower for word in ['makanan', 'makan', 'food']):
            makanan_items = self.menu_manager.get_menu_by_category("makanan")[:3]
            suggestions.extend([f"• {item.name}" for item in makanan_items])
        
        return "\n".join(suggestions) if suggestions else ""
    
    def _start_confirmation(self) -> str:
        """Tool untuk memulai konfirmasi pesanan"""
        confirmation_result = self.order_manager.confirm_order()
        
        if not confirmation_result["success"]:
            return confirmation_result["message"]
        
        self.state = ChatbotState.CONFIRMING_ORDER
        response = confirmation_result["order_summary"]
        response += "\n\n❓ Apakah pesanan sudah benar? (ya/tidak)"
        response += "\nJika ya, silakan berikan nama Anda untuk pesanan."
        
        return response
    
    def _finalize_order(self) -> str:
        """Tool untuk finalisasi pesanan"""
        # Extract customer name from conversation history
        customer_name = "Pelanggan"
        if self.conversation_history:
            last_input = self.conversation_history[-1]["user"]
            # Simple name extraction
            words = last_input.split()
            if len(words) >= 2 and not any(word.lower() in ['ya', 'yes', 'ok', 'oke'] for word in words):
                customer_name = " ".join(words[1:3])  # Take 1-2 words as name
        
        # Place order
        order_result = self.order_manager.place_order(customer_name)
        
        if order_result["success"]:
            self.state = ChatbotState.ORDER_COMPLETE
            response = f"""
🎉 PESANAN BERHASIL! 🎉

📋 Detail Pesanan:
• ID Pesanan: {order_result['order_id']}
• Nama: {order_result['customer_name']}
• Total: Rp {order_result['total']:,.0f}
• Estimasi waktu: {order_result['estimated_time']}

✅ Pesanan Anda sedang diproses!
Silakan menunggu di meja Anda atau ambil di counter.

Terima kasih telah memesan di Kafe Digital! 
Ketik pesan apapun untuk memulai pesanan baru.
            """
            return response.strip()
        else:
            return f"❌ Gagal memproses pesanan: {order_result['message']}"

def main():
    """Fungsi utama untuk menjalankan chatbot"""
    chatbot = KafeChatbot()
    
    # Start chatbot
    print(chatbot.start())
    
    while True:
        try:
            # Get user input
            user_input = input("\n👤 Anda: ").strip()
            
            if not user_input:
                continue
                
            # Process message
            response = chatbot.process_message(user_input)
            print(f"\n🤖 Bot: {response}")
            
            # Check if user wants to quit
            if user_input.lower() in ['quit', 'q', 'keluar', 'exit']:
                break
                
            # Reset state if order is complete
            if chatbot.state == ChatbotState.ORDER_COMPLETE:
                chatbot.state = ChatbotState.TAKING_ORDER
                
        except KeyboardInterrupt:
            print("\n\n👋 Terima kasih telah menggunakan Kafe Digital!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Silakan coba lagi.")

# Untuk testing interaktif
class ChatbotTester:
    def __init__(self):
        self.chatbot = KafeChatbot()
        
    def test_flow(self):
        """Test flow chatbot"""
        print("🧪 TESTING CHATBOT FLOW")
        print("=" * 40)
        
        # Test 1: Start chatbot
        print("\n1. Starting chatbot...")
        response = self.chatbot.start()
        print(f"Bot: {response}")
        
        # Test 2: Show menu
        print("\n2. Testing menu command...")
        response = self.chatbot.process_message("menu")
        print(f"Bot: {response[:200]}...")  # Truncate for readability
        
        # Test 3: Order items
        print("\n3. Testing order...")
        response = self.chatbot.process_message("Saya mau 2 cappuccino large dan 1 sandwich")
        print(f"Bot: {response}")
        
        # Test 4: Add more items
        print("\n4. Adding more items...")
        response = self.chatbot.process_message("tambah 1 es kopi susu")
        print(f"Bot: {response}")
        
        # Test 5: Confirm order
        print("\n5. Testing confirmation...")
        response = self.chatbot.process_message("konfirmasi")
        print(f"Bot: {response}")
        
        # Test 6: Finalize order
        print("\n6. Finalizing order...")
        response = self.chatbot.process_message("ya, nama saya Budi")
        print(f"Bot: {response}")
        
        print("\n✅ Testing completed!")

if __name__ == "__main__":
    print("🤖 KAFE DIGITAL CHATBOT SYSTEM")
    print("=" * 40)
    print("Pilihan:")
    print("1. Jalankan chatbot interaktif")
    print("2. Test flow chatbot")
    
    choice = input("\nPilih (1/2): ").strip()
    
    if choice == "2":
        tester = ChatbotTester()
        tester.test_flow()
    else:
        main()
