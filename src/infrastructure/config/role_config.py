"""
Infrastructure: Role Configuration Matrix
Mendefinisikan hak akses navigasi dan halaman berdasarkan peran (Role) user.
"""

# Struktur master data seluruh menu yang ada di aplikasi
MASTER_MENU_GROUPS = [
    {
        "label": "Dashboard",
        "items": [
            {"id": "dashboard", "label": "Dashboard", "icon": "🏠"},
            {"id": "history", "label": "History", "icon": "🕘"},
            {"id": "firebase_status", "label": "Firebase Status", "icon": "⚡"},
        ]
    },
    {
        "label": "Data",
        "items": [
            {"id": "produk_index", "label": "Produk", "icon": "📦"},
            {"id": "user_management_index", "label": "Manajemen Staf", "icon": "👥"}
        ]
    },
    {
        "label": "Keuangan",
        "items": [
            {"id": "keuangan_index", "label": "Keuangan", "icon": "💰"}
        ]
    },
    {
        "label": "TOOLS",
        "items": [
            {"id": "regional_summary", "label": "Regional Summary", "icon": "📊"},
            {"id": "rate_zonasi", "label": "Rate Zonasi", "icon": "📍"},
            {"id": "transformer", "label": "Data Transformer", "icon": "🔄"},
            {"id": "performance", "label": "Performance", "icon": "📈"},
        ]
    }
]

# Matriks Hak Akses Halaman berdasarkan ID item menu
ROLE_ACCESS_MATRIX = {
    "mentor": ["dashboard", "user_management_index", "history", "firebase_status", "produk_index", "keuangan_index", "regional_summary", "rate_zonasi", "transformer", "performance"],
    "admin": ["dashboard", "user_management_index", "history", "firebase_status", "produk_index", "keuangan_index", "regional_summary", "rate_zonasi", "transformer", "performance"],
    
    # Keuangan: Hanya dashboard, firebase status, area keuangan, dan TOOLS
    "keuangan": ["dashboard", "firebase_status", "keuangan_index", "regional_summary", "rate_zonasi", "transformer", "performance"],
    
    # Advertiser: Hanya dashboard, area produk, dan TOOLS
    "advertiser": ["dashboard", "produk_index", "regional_summary", "rate_zonasi", "transformer", "performance"]
}


def get_allowed_menu_for_role(role: str) -> list:
    """Menyaring MASTER_MENU_GROUPS sehingga hanya mengembalikan menu yang diizinkan untuk role tertentu."""
    clean_role = role.strip().lower()
    allowed_ids = ROLE_ACCESS_MATRIX.get(clean_role, ["dashboard"]) # Default fallback ke dashboard jika role tidak dikenali
    
    filtered_groups = []
    
    for group in MASTER_MENU_GROUPS:
        # Saring item di dalam grup yang ID-nya ada di daftar izin role
        filtered_items = [item for item in group["items"] if item["id"] in allowed_ids]
        
        # Jika grup memiliki item yang lolos saringan, masukkan grup tersebut
        if filtered_items:
            filtered_groups.append({
                "label": group["label"],
                "items": filtered_items
            })
            
    return filtered_groups