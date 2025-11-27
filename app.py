import json
import random
import os
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

# ==========================================
# 1. 模擬 OpenData 數據庫 (對應簡報：客觀環境數據)
# ==========================================
# 這裡的數據直接對應簡報中的「空氣品質」、「綠地」、「藝文」、「運動」、「噪音」
# 數值定義：0 (差) - 100 (優/高)

LOCATIONS = [
    # --- 中正區 ---
    {
        "id": 101, "name": "中正紀念堂", "district": "中正區",
        "lat": 25.0348, "lng": 121.5217,
        "description": "宏偉的藍白建築與廣闊廣場，藝文與散步的絕佳交會點。",
        "data": {"pm25": 25, "noise": 55, "green": 60, "art": 95, "sport": 40}
    },
    {
        "id": 102, "name": "華山1914文創園區", "district": "中正區",
        "lat": 25.0441, "lng": 121.5293,
        "description": "舊酒廠變身的前衛藝術基地，展覽與市集的聚集地。",
        "data": {"pm25": 30, "noise": 65, "green": 40, "art": 100, "sport": 10}
    },
    {
        "id": 103, "name": "臺北植物園", "district": "中正區",
        "lat": 25.0333, "lng": 121.5096,
        "description": "城市中的綠色圖書館，荷花池畔的寧靜時光。",
        "data": {"pm25": 15, "noise": 40, "green": 95, "art": 30, "sport": 20}
    },
    # --- 大安區 ---
    {
        "id": 201, "name": "大安森林公園", "district": "大安區",
        "lat": 25.0300, "lng": 121.5358,
        "description": "臺北之肺，擁有豐富生態與露天音樂台的都會綠洲。",
        "data": {"pm25": 18, "noise": 45, "green": 100, "art": 40, "sport": 60}
    },
    {
        "id": 202, "name": "大安運動中心", "district": "大安區",
        "lat": 25.0204, "lng": 121.5451,
        "description": "設施完善的現代化運動場館，釋放壓力的好去處。",
        "data": {"pm25": 10, "noise": 60, "green": 10, "art": 5, "sport": 100}
    },
    # --- 信義區 ---
    {
        "id": 301, "name": "象山親山步道", "district": "信義區",
        "lat": 25.0273, "lng": 121.5707,
        "description": "近距離欣賞台北101夜景的最佳登山步道。",
        "data": {"pm25": 8, "noise": 30, "green": 90, "art": 10, "sport": 85}
    },
    {
        "id": 302, "name": "四四南村", "district": "信義區",
        "lat": 25.0312, "lng": 121.5620,
        "description": "繁華信義區中的眷村記憶，新舊交融的文青景點。",
        "data": {"pm25": 25, "noise": 50, "green": 30, "art": 85, "sport": 10}
    },
    {
        "id": 303, "name": "松山文創園區", "district": "信義區",
        "lat": 25.0439, "lng": 121.5606,
        "description": "菸廠古蹟與生態池的結合，充滿設計感的休憩空間。",
        "data": {"pm25": 22, "noise": 55, "green": 50, "art": 95, "sport": 20}
    },
    # --- 松山區 ---
    {
        "id": 401, "name": "彩虹橋河濱公園", "district": "松山區",
        "lat": 25.0520, "lng": 121.5776,
        "description": "基隆河畔的愛情地標，適合夜騎與漫步。",
        "data": {"pm25": 20, "noise": 50, "green": 70, "art": 40, "sport": 80}
    },
    {
        "id": 402, "name": "台北田徑場", "district": "松山區",
        "lat": 25.0489, "lng": 121.5517,
        "description": "國際級標準運動場，城市中心的熱血競技場。",
        "data": {"pm25": 30, "noise": 70, "green": 20, "art": 10, "sport": 95}
    },
    # --- 士林區 ---
    {
        "id": 501, "name": "國立故宮博物院", "district": "士林區",
        "lat": 25.1024, "lng": 121.5485,
        "description": "世界級的中華文化寶庫，群山環抱的文化殿堂。",
        "data": {"pm25": 12, "noise": 35, "green": 80, "art": 100, "sport": 10}
    },
    {
        "id": 502, "name": "臺北表演藝術中心", "district": "士林區",
        "lat": 25.0847, "lng": 121.5255,
        "description": "獨特球體建築，匯聚國際級表演藝術的能量中心。",
        "data": {"pm25": 35, "noise": 65, "green": 10, "art": 100, "sport": 0}
    },
    {
        "id": 503, "name": "芝山文化生態綠園", "district": "士林區",
        "lat": 25.1054, "lng": 121.5298,
        "description": "全臺北市第一座文化生態公園，古蹟與自然的秘境。",
        "data": {"pm25": 10, "noise": 25, "green": 95, "art": 60, "sport": 30}
    },
    # --- 北投區 ---
    {
        "id": 601, "name": "北投圖書館", "district": "北投區",
        "lat": 25.1363, "lng": 121.5063,
        "description": "全球最美公立圖書館之一，森林中的木造書屋。",
        "data": {"pm25": 8, "noise": 30, "green": 95, "art": 70, "sport": 10}
    },
    {
        "id": 602, "name": "法鼓山農禪寺", "district": "北投區",
        "lat": 25.1257, "lng": 121.4984,
        "description": "水月道場的空靈倒影，沉澱心靈的極致靜謐之地。",
        "data": {"pm25": 10, "noise": 20, "green": 60, "art": 80, "sport": 5}
    },
    {
        "id": 603, "name": "軍艦岩親山步道", "district": "北投區",
        "lat": 25.1206, "lng": 121.5135,
        "description": "巨岩崢嶸，登頂可360度俯瞰臺北盆地。",
        "data": {"pm25": 5, "noise": 25, "green": 90, "art": 0, "sport": 90}
    },
    # --- 內湖區 ---
    {
        "id": 701, "name": "大湖公園", "district": "內湖區",
        "lat": 25.0838, "lng": 121.5936,
        "description": "錦帶橋與落羽松的絕美倒影，野餐與釣魚勝地。",
        "data": {"pm25": 15, "noise": 40, "green": 90, "art": 20, "sport": 50}
    },
    {
        "id": 702, "name": "內湖運動中心", "district": "內湖區",
        "lat": 25.0718, "lng": 121.5750,
        "description": "擁有攀岩場與射擊場的特色運動中心。",
        "data": {"pm25": 20, "noise": 60, "green": 20, "art": 5, "sport": 95}
    },
    # --- 文山區 ---
    {
        "id": 801, "name": "臺北市立動物園", "district": "文山區",
        "lat": 24.9983, "lng": 121.5810,
        "description": "亞洲最大的動物園，親子共遊與生態教育的首選。",
        "data": {"pm25": 12, "noise": 50, "green": 85, "art": 30, "sport": 70}
    },
    {
        "id": 802, "name": "貓空壺穴步道", "district": "文山區",
        "lat": 24.9669, "lng": 121.5888,
        "description": "茶香與壺穴地形交織，遠離塵囂的品茗勝地。",
        "data": {"pm25": 5, "noise": 30, "green": 95, "art": 40, "sport": 60}
    },
    # --- 萬華區 ---
    {
        "id": 901, "name": "西門紅樓", "district": "萬華區",
        "lat": 25.0423, "lng": 121.5061,
        "description": "百年紅磚樓中的創意市集，年輕活力的發源地。",
        "data": {"pm25": 40, "noise": 85, "green": 5, "art": 80, "sport": 10}
    },
    {
        "id": 902, "name": "青年公園", "district": "萬華區",
        "lat": 25.0233, "lng": 121.5034,
        "description": "南台北最大的公園，擁有多元運動設施與高爾夫球場。",
        "data": {"pm25": 25, "noise": 55, "green": 90, "art": 20, "sport": 80}
    },
    # --- 大同區 ---
    {
        "id": 1001, "name": "大稻埕碼頭", "district": "大同區",
        "lat": 25.0567, "lng": 121.5076,
        "description": "落日餘暉下的貨櫃市集，享受河畔微風與美食。",
        "data": {"pm25": 25, "noise": 60, "green": 40, "art": 60, "sport": 70}
    },
    {
        "id": 1002, "name": "臺灣新文化運動紀念館", "district": "大同區",
        "lat": 25.0593, "lng": 121.5137,
        "description": "日治時期警察署古蹟，見證台灣文化覺醒的歷史現場。",
        "data": {"pm25": 30, "noise": 45, "green": 20, "art": 95, "sport": 0}
    },
    # --- 中山區 ---
    {
        "id": 1101, "name": "臺北市立美術館", "district": "中山區",
        "lat": 25.0722, "lng": 121.5246,
        "description": "臺灣首座現代美術館，純白建築中的藝術靈魂。",
        "data": {"pm25": 20, "noise": 40, "green": 50, "art": 100, "sport": 10}
    },
    {
        "id": 1102, "name": "花博公園新生園區", "district": "中山區",
        "lat": 25.0711, "lng": 121.5317,
        "description": "擁有迷宮花園與玫瑰園，飛機從頭頂呼嘯而過的震撼。",
        "data": {"pm25": 25, "noise": 75, "green": 85, "art": 30, "sport": 60}
    },
    # --- 南港區 ---
    {
        "id": 1201, "name": "臺北流行音樂中心", "district": "南港區",
        "lat": 25.0519, "lng": 121.5985,
        "description": "仿山巒起伏的建築，流行音樂的心臟地帶。",
        "data": {"pm25": 30, "noise": 60, "green": 40, "art": 95, "sport": 20}
    },
    {
        "id": 1202, "name": "南港山水綠生態公園", "district": "南港區",
        "lat": 25.0315, "lng": 121.6212,
        "description": "垃圾掩埋場變身的超大綠地，生態復育的典範。",
        "data": {"pm25": 15, "noise": 30, "green": 95, "art": 10, "sport": 50}
    }
]

# 天氣模擬
WEATHER_TYPES = [
    {"icon": "fa-sun", "text": "晴朗", "color": "text-orange-500", "temp": "28°C"},
    {"icon": "fa-cloud-sun", "text": "多雲", "color": "text-yellow-500", "temp": "24°C"},
    {"icon": "fa-wind", "text": "微風", "color": "text-blue-400", "temp": "22°C"},
]

user_points = 0

# ==========================================
# 2. 核心算法：將 OpenData 轉化為幸福指標
# ==========================================
def calculate_happiness_indices(loc_data):
    # 根據簡報公式邏輯計算
    pm25_score = max(0, 100 - loc_data['pm25'] * 1.5)
    noise_score = max(0, 100 - loc_data['noise'] * 1.2)
    relaxation = (pm25_score + noise_score) / 2
    healing = loc_data['green']
    vitality = min(100, (loc_data['art'] * 0.8 + loc_data['sport'] * 0.2 + loc_data['noise'] * 0.3))
    energy = loc_data['sport']
    return {
        "relaxation": round(relaxation, 1),
        "healing": round(healing, 1),
        "vitality": round(vitality, 1),
        "energy": round(energy, 1)
    }

# ==========================================
# 3. 路由設定
# ==========================================

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/locations', methods=['GET'])
def get_locations():
    mood = request.args.get('mood', 'all')
    processed_locations = []
    
    for loc in LOCATIONS:
        indices = calculate_happiness_indices(loc['data'])
        match_score = 0
        tag = ""
        
        # 個人化心境匹配
        if mood == 'relax':
            match_score = indices['relaxation']
            tag = "☁️ 極致放鬆"
        elif mood == 'heal':
            match_score = indices['healing']
            tag = "🌳 自然療癒"
        elif mood == 'vitality':
            match_score = indices['vitality']
            tag = "🎨 藝文活力"
        elif mood == 'sport':
            match_score = indices['energy']
            tag = "🏃‍♂️ 揮灑汗水"
        else:
            match_score = (indices['relaxation'] + indices['healing'] + indices['vitality']) / 3
            tag = "📍 綜合推薦"

        loc_obj = loc.copy()
        loc_obj['indices'] = indices
        loc_obj['match_score'] = round(match_score, 1)
        loc_obj['tag'] = tag
        loc_obj['weather'] = random.choice(WEATHER_TYPES)
        processed_locations.append(loc_obj)

    processed_locations.sort(key=lambda x: x['match_score'], reverse=True)
    return jsonify(processed_locations[:15])

@app.route('/api/checkin', methods=['POST'])
def checkin():
    global user_points
    data = request.json
    points_earned = random.randint(30, 80)
    user_points += points_earned
    
    # 簡報提到的：虛擬獎章系統
    new_badge = None
    if user_points >= 100 and user_points < 200:
        new_badge = "城市探索者"
    elif user_points >= 300 and user_points < 400:
        new_badge = "數據大師"
    elif user_points >= 500:
        new_badge = "臺北幸福大使"

    return jsonify({
        "status": "success",
        "message": f"抵達「{data.get('locationName')}」",
        "earned": points_earned,
        "total_points": user_points,
        "new_badge": new_badge
    })

# ==========================================
# 4. 前端 HTML 模板
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>臺北市幸福鈴 | 城市幸福地圖</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" />
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Noto Sans TC', sans-serif; background-color: #f8fafc; overflow: hidden; }
        #map { height: 100%; width: 100%; z-index: 1; }
        
        /* 心情按鈕樣式優化 */
        .mood-btn { transition: all 0.2s; }
        .mood-btn.active { 
            background-color: #3b82f6 !important; 
            color: white !important; 
            border-color: #3b82f6 !important; 
            box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.5);
        }
        .mood-btn.active i, .mood-btn.active span { color: white !important; }

        /* 隱藏滾動條 */
        .no-scrollbar::-webkit-scrollbar { display: none; }
        .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
        
        /* 鈴鐺動畫 */
        @keyframes ring {
            0% { transform: rotate(0); }
            10% { transform: rotate(30deg); }
            30% { transform: rotate(-28deg); }
            50% { transform: rotate(34deg); }
            70% { transform: rotate(-32deg); }
            90% { transform: rotate(30deg); }
            100% { transform: rotate(0); }
        }
        .bell-animation { animation: ring 1s ease-in-out; }
    </style>
</head>
<body class="flex flex-col h-screen text-slate-800">

    <!-- 頂部導航欄 -->
    <nav class="bg-white shadow-sm z-50 px-4 py-3 flex justify-between items-center shrink-0 border-b border-gray-100">
        <div class="flex items-center gap-2">
            <div class="bg-gradient-to-br from-blue-500 to-blue-600 text-white p-2 rounded-xl shadow-sm">
                <i class="fa-solid fa-bell text-sm"></i>
            </div>
            <div>
                <h1 class="text-lg font-bold tracking-tight text-slate-800">幸福地圖</h1>
                <div class="text-[10px] text-slate-500 leading-none">Taipei Happiness Bell</div>
            </div>
        </div>
        <div class="flex items-center gap-3">
            <div onclick="showBadges()" class="cursor-pointer bg-slate-100 p-2 rounded-full hover:bg-slate-200 transition">
                <i class="fa-solid fa-medal text-slate-600"></i>
            </div>
            <div class="flex items-center gap-1.5 bg-amber-50 border border-amber-100 px-3 py-1.5 rounded-full">
                <i class="fa-solid fa-star text-amber-500 text-xs"></i>
                <span id="user-points" class="font-bold text-amber-700 text-sm">0</span>
            </div>
        </div>
    </nav>

    <!-- 主內容區 -->
    <div class="flex flex-1 flex-col md:flex-row overflow-hidden relative">
        
        <!-- 地圖區域 -->
        <div class="absolute inset-0 md:relative md:w-2/3 md:order-2 z-0">
            <div id="map" class="h-full w-full"></div>
            
            <!-- 熱力圖開關 -->
            <button onclick="toggleHeatmap()" id="heatmap-btn" class="absolute top-4 right-4 z-[500] bg-white p-3 rounded-xl shadow-lg text-slate-500 hover:text-red-500 hover:bg-red-50 transition-colors">
                <i class="fa-solid fa-fire-flame-curved text-xl"></i>
            </button>

            <!-- 數據指標說明 (桌面版) -->
            <div class="hidden md:block absolute bottom-8 left-8 bg-white/95 p-4 rounded-xl shadow-xl z-[500] text-xs backdrop-blur-sm border border-gray-100">
                <div class="font-bold mb-3 text-slate-700 text-sm">OpenData 幸福指標</div>
                <div class="space-y-2">
                    <div class="flex items-center gap-2"><div class="w-2 h-2 bg-blue-500 rounded-full"></div> <span>放鬆值 (空氣/噪音)</span></div>
                    <div class="flex items-center gap-2"><div class="w-2 h-2 bg-green-500 rounded-full"></div> <span>療癒值 (綠覆率)</span></div>
                    <div class="flex items-center gap-2"><div class="w-2 h-2 bg-purple-500 rounded-full"></div> <span>活力值 (藝文活動)</span></div>
                    <div class="flex items-center gap-2"><div class="w-2 h-2 bg-red-500 rounded-full"></div> <span>能量值 (運動設施)</span></div>
                </div>
            </div>
        </div>

        <!-- 側邊欄/底部抽屜 -->
        <div class="absolute bottom-0 w-full md:relative md:w-1/3 md:order-1 md:h-full z-20 flex flex-col pointer-events-none md:pointer-events-auto">
            <div class="bg-white rounded-t-3xl md:rounded-none shadow-[0_-8px_30px_rgba(0,0,0,0.12)] flex flex-col h-[55vh] md:h-full pointer-events-auto transition-all duration-300">
                
                <!-- 手機版把手 -->
                <div class="w-full flex justify-center pt-3 pb-1 md:hidden"><div class="w-12 h-1.5 bg-gray-200 rounded-full"></div></div>

                <!-- 1. 個人化心境匹配 (對應簡報) -->
                <div class="p-5 border-b border-gray-100 bg-white shrink-0">
                    <h2 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                        <i class="fa-solid fa-sliders"></i> 設定您的幸福動線
                    </h2>
                    <div class="grid grid-cols-4 gap-3">
                        <button onclick="changeMood('relax')" class="mood-btn border border-slate-100 bg-slate-50 text-slate-600 p-2.5 rounded-2xl flex flex-col items-center gap-1.5 hover:bg-slate-100">
                            <i class="fa-solid fa-wind text-xl text-blue-400"></i><span class="text-xs font-bold">放鬆</span>
                        </button>
                        <button onclick="changeMood('heal')" class="mood-btn border border-slate-100 bg-slate-50 text-slate-600 p-2.5 rounded-2xl flex flex-col items-center gap-1.5 hover:bg-slate-100">
                            <i class="fa-solid fa-tree text-xl text-green-500"></i><span class="text-xs font-bold">療癒</span>
                        </button>
                        <button onclick="changeMood('vitality')" class="mood-btn border border-slate-100 bg-slate-50 text-slate-600 p-2.5 rounded-2xl flex flex-col items-center gap-1.5 hover:bg-slate-100">
                            <i class="fa-solid fa-palette text-xl text-purple-500"></i><span class="text-xs font-bold">藝文</span>
                        </button>
                        <button onclick="changeMood('sport')" class="mood-btn border border-slate-100 bg-slate-50 text-slate-600 p-2.5 rounded-2xl flex flex-col items-center gap-1.5 hover:bg-slate-100">
                            <i class="fa-solid fa-person-running text-xl text-red-500"></i><span class="text-xs font-bold">運動</span>
                        </button>
                    </div>
                </div>

                <!-- 地點列表 -->
                <div class="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50 no-scrollbar" id="location-list">
                    <div class="flex flex-col items-center justify-center h-full text-slate-400 gap-3">
                        <div class="bg-white p-4 rounded-full shadow-sm"><i class="fa-solid fa-map-location-dot text-3xl text-slate-300"></i></div>
                        <p class="text-sm font-medium">請選擇上方心情，開始探索</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- 幸福響鈴任務達成 Modal (對應簡報) -->
    <div id="modal" class="hidden fixed inset-0 bg-slate-900/60 z-[2000] flex items-center justify-center p-6 backdrop-blur-sm transition-opacity opacity-0">
        <div class="bg-white rounded-3xl shadow-2xl w-full max-w-xs p-8 text-center transform scale-90 transition-transform relative overflow-hidden">
            <!-- 裝飾背景 -->
            <div class="absolute top-0 left-0 w-full h-32 bg-gradient-to-b from-yellow-50 to-white -z-10"></div>
            
            <div class="relative mb-6">
                <div class="w-24 h-24 bg-white rounded-full flex items-center justify-center mx-auto shadow-lg border-4 border-yellow-50">
                    <i id="bell-icon" class="fa-solid fa-bell text-5xl text-yellow-500"></i>
                </div>
                <div class="absolute -bottom-2 left-1/2 -translate-x-1/2 bg-yellow-500 text-white text-[10px] px-2 py-0.5 rounded-full font-bold">TASK COMPLETED</div>
            </div>
            
            <h3 class="text-2xl font-bold text-slate-800 mb-1">任務達成！</h3>
            <p id="modal-text" class="text-sm text-slate-500 mb-6">成功抵達探索地點</p>
            
            <!-- 獲得獎勵顯示 -->
            <div class="bg-slate-50 rounded-2xl p-4 mb-6 border border-slate-100">
                <div class="flex justify-between items-center mb-2">
                    <span class="text-slate-500 text-xs font-bold uppercase">獲得積分</span>
                    <span class="font-bold text-yellow-600 flex items-center gap-1 text-lg">
                        +<span id="modal-points">0</span>
                    </span>
                </div>
                <!-- 虛擬獎章 (動態插入) -->
                <div id="badge-notification" class="hidden pt-2 border-t border-slate-200 mt-2">
                    <div class="text-xs text-blue-500 font-bold mb-1">獲得新獎章！</div>
                    <div class="flex items-center justify-center gap-2 text-slate-700 font-bold">
                        <i class="fa-solid fa-medal text-blue-500"></i> <span id="badge-name"></span>
                    </div>
                </div>
            </div>

            <button onclick="closeModal()" class="w-full bg-slate-800 text-white py-3.5 rounded-xl font-bold shadow-lg shadow-slate-200 active:scale-95 transition-all">
                收下獎勵
            </button>
        </div>
    </div>

    <!-- 獎章列表 Modal -->
    <div id="badge-modal" class="hidden fixed inset-0 bg-black/50 z-[2000] flex items-center justify-center p-4 backdrop-blur-sm" onclick="hideBadges(event)">
        <div class="bg-white w-full max-w-sm rounded-2xl p-6 shadow-2xl" onclick="event.stopPropagation()">
            <h3 class="font-bold text-lg mb-4 flex items-center gap-2"><i class="fa-solid fa-medal text-blue-500"></i> 我的成就獎章</h3>
            <div class="grid grid-cols-3 gap-4 text-center">
                <div class="flex flex-col items-center gap-2 opacity-100">
                    <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center text-blue-500"><i class="fa-solid fa-user"></i></div>
                    <span class="text-xs font-bold text-slate-600">新手上路</span>
                </div>
                <div class="flex flex-col items-center gap-2 opacity-40" id="badge-explorer">
                    <div class="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center text-yellow-500"><i class="fa-solid fa-compass"></i></div>
                    <span class="text-xs font-bold text-slate-600">城市探索者</span>
                </div>
                <div class="flex flex-col items-center gap-2 opacity-40" id="badge-data">
                    <div class="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center text-purple-500"><i class="fa-solid fa-chart-pie"></i></div>
                    <span class="text-xs font-bold text-slate-600">數據大師</span>
                </div>
            </div>
            <button onclick="document.getElementById('badge-modal').classList.add('hidden')" class="mt-6 w-full py-2 bg-gray-100 rounded-lg text-sm font-bold text-gray-600">關閉</button>
        </div>
    </div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>
    
    <script>
        let map;
        let markers = [];
        let heatLayer = null;
        let currentLocations = [];
        let isHeatmapActive = false;

        function initMap() {
            map = L.map('map', { zoomControl: false }).setView([25.06, 121.55], 12);
            L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
                attribution: 'OpenStreetMap', maxZoom: 19
            }).addTo(map);
            fetchLocations('all');
        }

        function changeMood(mood) { fetchLocations(mood); }

        function toggleHeatmap() {
            isHeatmapActive = !isHeatmapActive;
            const btn = document.getElementById('heatmap-btn');
            if (isHeatmapActive) {
                btn.classList.add('text-red-500', 'bg-red-50');
                drawHeatmap();
            } else {
                btn.classList.remove('text-red-500', 'bg-red-50');
                if (heatLayer) { map.removeLayer(heatLayer); heatLayer = null; }
            }
        }

        function drawHeatmap() {
            if (heatLayer) map.removeLayer(heatLayer);
            if (!isHeatmapActive || currentLocations.length === 0) return;
            const heatData = currentLocations.map(loc => [loc.lat, loc.lng, loc.match_score / 100]);
            heatLayer = L.heatLayer(heatData, { radius: 35, blur: 20, maxZoom: 14, gradient: {0.4: 'blue', 0.65: 'lime', 1: 'red'} }).addTo(map);
        }

        async function fetchLocations(mood) {
            document.querySelectorAll('.mood-btn').forEach(btn => btn.classList.remove('active'));
            const moodMap = {'relax':0, 'heal':1, 'vitality':2, 'sport':3};
            if(moodMap[mood] !== undefined) document.querySelectorAll('.mood-btn')[moodMap[mood]].classList.add('active');

            try {
                const res = await fetch(`/api/locations?mood=${mood}`);
                currentLocations = await res.json();
                updateUI();
                if (isHeatmapActive) drawHeatmap();
            } catch(e) { console.error(e); }
        }

        function updateUI() {
            markers.forEach(m => map.removeLayer(m));
            markers = [];
            const list = document.getElementById('location-list');
            list.innerHTML = '';

            currentLocations.forEach((loc) => {
                // Marker
                const markerIcon = L.divIcon({
                    className: 'custom-div-icon',
                    html: `<div style="background-color:${getScoreColor(loc.match_score)}; width:16px; height:16px; border-radius:50%; border:3px solid white; box-shadow:0 3px 6px rgba(0,0,0,0.2);"></div>`,
                    iconSize: [16, 16], iconAnchor: [8, 8]
                });
                
                // 地點資訊卡 (對應簡報：科學依據可視化)
                const popupContent = `
                    <div class="font-sans min-w-[200px] p-1">
                        <div class="flex justify-between items-center mb-2">
                            <span class="text-xs font-bold text-slate-400 uppercase tracking-wide">${loc.district}</span>
                            <span class="text-xs font-bold ${loc.weather.color}"><i class="fa-solid ${loc.weather.icon}"></i> ${loc.weather.temp}</span>
                        </div>
                        <h3 class="font-bold text-lg text-slate-800 mb-1 leading-tight">${loc.name}</h3>
                        <div class="text-xs text-slate-500 mb-3">${loc.tag}</div>
                        
                        <!-- 科學數據儀表板 -->
                        <div class="bg-slate-50 p-2 rounded-lg border border-slate-100 mb-3 space-y-1.5">
                            <div class="flex items-center justify-between text-[10px] text-slate-500">
                                <span>PM2.5</span>
                                <div class="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden"><div class="h-full bg-blue-400" style="width:${100 - loc.data.pm25}%"></div></div>
                            </div>
                            <div class="flex items-center justify-between text-[10px] text-slate-500">
                                <span>綠覆率</span>
                                <div class="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden"><div class="h-full bg-green-500" style="width:${loc.data.green}%"></div></div>
                            </div>
                             <div class="flex items-center justify-between text-[10px] text-slate-500">
                                <span>藝文</span>
                                <div class="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden"><div class="h-full bg-purple-500" style="width:${loc.data.art}%"></div></div>
                            </div>
                        </div>

                        <div class="grid grid-cols-2 gap-2">
                            <a href="https://www.google.com/maps/dir/?api=1&destination=${loc.lat},${loc.lng}" target="_blank" class="text-center bg-white border border-slate-200 text-slate-600 text-xs py-2 rounded-lg font-bold hover:bg-slate-50">導航</a>
                            <button onclick="checkIn('${loc.name}')" class="bg-blue-600 text-white text-xs py-2 rounded-lg font-bold hover:bg-blue-700 shadow-sm shadow-blue-200">打卡任務</button>
                        </div>
                    </div>
                `;

                const marker = L.marker([loc.lat, loc.lng], {icon: markerIcon}).addTo(map).bindPopup(popupContent);
                markers.push(marker);

                // 列表卡片
                const card = document.createElement('div');
                card.className = "bg-white p-4 rounded-2xl shadow-sm border border-slate-100 cursor-pointer active:scale-[0.98] transition-all hover:shadow-md hover:border-blue-100";
                card.innerHTML = `
                    <div class="flex gap-4">
                        <div class="flex-shrink-0 w-14 h-14 rounded-2xl flex flex-col items-center justify-center text-white font-bold shadow-sm" style="background-color: ${getScoreColor(loc.match_score)}">
                            <span class="text-lg leading-none">${Math.round(loc.match_score)}</span>
                            <span class="text-[9px] opacity-80">分</span>
                        </div>
                        <div class="flex-1 min-w-0">
                            <div class="flex justify-between items-start mb-1">
                                <h4 class="font-bold text-slate-800 truncate text-base">${loc.name}</h4>
                                <span class="text-[10px] px-2 py-0.5 bg-slate-100 text-slate-500 rounded-full">${loc.tag}</span>
                            </div>
                            <p class="text-xs text-slate-500 line-clamp-2 mb-2">${loc.description}</p>
                            <div class="flex items-center gap-2 text-[10px] text-slate-400">
                                <span class="${loc.weather.color} font-bold"><i class="fa-solid ${loc.weather.icon}"></i> ${loc.weather.temp}</span>
                                <span>•</span>
                                <span>${loc.district}</span>
                            </div>
                        </div>
                    </div>
                `;
                card.onclick = () => { map.flyTo([loc.lat, loc.lng], 16, { duration: 1.2 }); setTimeout(() => marker.openPopup(), 1200); };
                list.appendChild(card);
            });
        }

        function getScoreColor(score) { return score >= 80 ? '#10b981' : (score >= 60 ? '#3b82f6' : '#f59e0b'); }

        async function checkIn(name) {
            map.closePopup();
            try {
                const res = await fetch('/api/checkin', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ locationName: name })
                });
                const data = await res.json();
                
                // 更新 UI
                document.getElementById('user-points').innerText = data.total_points;
                document.getElementById('modal-points').innerText = data.earned;
                document.getElementById('modal-text').innerText = `成功探索 ${name}`;
                
                // 獎章邏輯
                const badgeNotif = document.getElementById('badge-notification');
                if(data.new_badge) {
                    badgeNotif.classList.remove('hidden');
                    document.getElementById('badge-name').innerText = data.new_badge;
                    updateLocalBadges(data.total_points);
                } else {
                    badgeNotif.classList.add('hidden');
                }

                // 顯示 Modal 與鈴鐺動畫
                const modal = document.getElementById('modal');
                const bell = document.getElementById('bell-icon');
                modal.classList.remove('hidden');
                setTimeout(() => { modal.classList.remove('opacity-0'); modal.querySelector('div').classList.remove('scale-90'); modal.querySelector('div').classList.add('scale-100'); }, 10);
                bell.classList.add('bell-animation');
                setTimeout(() => bell.classList.remove('bell-animation'), 1000);

            } catch(e) {}
        }

        function updateLocalBadges(points) {
            if(points >= 100) document.getElementById('badge-explorer').classList.remove('opacity-40');
            if(points >= 300) document.getElementById('badge-data').classList.remove('opacity-40');
        }

        function closeModal() {
            const modal = document.getElementById('modal');
            modal.classList.add('opacity-0'); modal.querySelector('div').classList.remove('scale-100'); modal.querySelector('div').classList.add('scale-90');
            setTimeout(() => { modal.classList.add('hidden'); }, 300);
        }

        function showBadges() { document.getElementById('badge-modal').classList.remove('hidden'); }
        function hideBadges(e) { if(e.target.id === 'badge-modal') document.getElementById('badge-modal').classList.add('hidden'); }

        window.onload = initMap;
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)