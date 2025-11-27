import json
import random
import os
from flask import Flask, render_template_string, jsonify, request

# ==========================================
# 1. 應用程式配置
# ==========================================

app = Flask(__name__)

# ==========================================
# 2. 全臺北市幸福地點資料庫 (Simulated OpenData)
# ==========================================
# 為了讓地圖更豐富，這裡擴充了台北市主要行政區的指標性地點
# 數據邏輯：
# pm25: 低=好, noise: 低=靜, green: 高=綠, art: 高=文, sport: 高=動

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

user_points = 0

# ==========================================
# 3. 核心邏輯層 (Business Logic)
# ==========================================

def calculate_happiness_indices(loc_data):
    """
    將 OpenData 轉換為幸福指標 (0-100)
    """
    # 1. 放鬆值 (Relaxation): 喜歡安靜與好空氣
    pm25_score = max(0, 100 - loc_data['pm25'] * 1.5)
    noise_score = max(0, 100 - loc_data['noise'] * 1.2)
    relaxation = (pm25_score + noise_score) / 2

    # 2. 療癒值 (Healing): 喜歡高綠覆率
    healing = loc_data['green']

    # 3. 活力值 (Vitality): 喜歡藝文活動與人氣(適度噪音)
    vitality = min(100, (loc_data['art'] * 0.8 + loc_data['sport'] * 0.2 + loc_data['noise'] * 0.3))

    # 4. 能量值 (Energy): 專指運動
    energy = loc_data['sport']

    return {
        "relaxation": round(relaxation, 1),
        "healing": round(healing, 1),
        "vitality": round(vitality, 1),
        "energy": round(energy, 1)
    }

# ==========================================
# 4. 視圖與路由 (Views & Routes)
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
        
        # 根據心情決定權重
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
        processed_locations.append(loc_obj)

    # 排序並只回傳前 15 筆最適合的，避免地圖太亂
    processed_locations.sort(key=lambda x: x['match_score'], reverse=True)
    return jsonify(processed_locations[:15])

@app.route('/api/checkin', methods=['POST'])
def checkin():
    global user_points
    data = request.json
    points_earned = random.randint(10, 50)
    user_points += points_earned
    return jsonify({
        "status": "success",
        "message": f"探索「{data.get('locationName')}」成功！",
        "earned": points_earned,
        "total_points": user_points
    })

# ==========================================
# 5. 前端模板 (Mobile First Design)
# ==========================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>臺北市幸福鈴 | 城市幸福地圖 v2.1</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" />
    <style>
        body { font-family: 'Microsoft JhengHei', sans-serif; background-color: #f3f4f6; overflow: hidden; }
        #map { height: 100%; width: 100%; z-index: 1; }
        .mood-btn.active { background-color: #3b82f6; color: white; border-color: #3b82f6; }
        .mood-btn.active i { color: white; }
        .mood-btn.active span { color: white; }
        /* 隱藏 Scrollbar 但保持功能 */
        .no-scrollbar::-webkit-scrollbar { display: none; }
        .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
    </style>
</head>
<body class="flex flex-col h-screen">

    <!-- Navbar -->
    <nav class="bg-white shadow-md z-50 px-4 py-3 flex justify-between items-center shrink-0">
        <div class="flex items-center gap-2">
            <div class="bg-blue-600 text-white p-1.5 rounded-lg">
                <i class="fa-solid fa-bell text-sm"></i>
            </div>
            <h1 class="text-lg font-bold text-gray-800">幸福地圖 <span class="text-xs text-gray-500 bg-gray-100 px-1 rounded">Beta</span></h1>
        </div>
        <div class="flex items-center gap-2 bg-yellow-50 border border-yellow-200 px-3 py-1 rounded-full">
            <i class="fa-solid fa-coins text-yellow-500"></i>
            <span id="user-points" class="font-bold text-yellow-700">0</span>
        </div>
    </nav>

    <!-- Main Container -->
    <div class="flex flex-1 flex-col md:flex-row overflow-hidden relative">
        
        <!-- Map (Mobile: Fullscreen background, Desktop: Right side) -->
        <div class="absolute inset-0 md:relative md:w-2/3 md:order-2 z-0">
            <div id="map" class="h-full w-full"></div>
            <!-- Legend (Desktop Only) -->
            <div class="hidden md:block absolute bottom-6 left-6 bg-white/90 p-3 rounded-lg shadow-lg z-[500] text-xs backdrop-blur-sm">
                <div class="font-bold mb-2 text-gray-700">OpenData 數據指標</div>
                <div class="grid grid-cols-2 gap-x-4 gap-y-1">
                    <div class="flex items-center gap-1"><div class="w-2 h-2 bg-blue-500 rounded-full"></div> 放鬆值 (空氣/噪音)</div>
                    <div class="flex items-center gap-1"><div class="w-2 h-2 bg-green-500 rounded-full"></div> 療癒值 (綠覆率)</div>
                    <div class="flex items-center gap-1"><div class="w-2 h-2 bg-purple-500 rounded-full"></div> 活力值 (藝文)</div>
                    <div class="flex items-center gap-1"><div class="w-2 h-2 bg-red-500 rounded-full"></div> 能量值 (運動)</div>
                </div>
            </div>
        </div>

        <!-- Control Panel (Mobile: Bottom Sheet, Desktop: Left Sidebar) -->
        <div class="absolute bottom-0 w-full md:relative md:w-1/3 md:order-1 md:h-full z-20 flex flex-col pointer-events-none md:pointer-events-auto">
            
            <div class="bg-white rounded-t-2xl md:rounded-none shadow-[0_-5px_20px_rgba(0,0,0,0.1)] flex flex-col h-[50vh] md:h-full pointer-events-auto transition-all duration-300">
                
                <!-- Handle bar for mobile -->
                <div class="w-full flex justify-center pt-2 pb-1 md:hidden">
                    <div class="w-12 h-1.5 bg-gray-300 rounded-full"></div>
                </div>

                <!-- Mood Selector -->
                <div class="p-4 border-b shrink-0">
                    <h2 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">我想尋找...</h2>
                    <div class="grid grid-cols-4 gap-2">
                        <button onclick="changeMood('relax')" class="mood-btn border border-gray-100 bg-gray-50 text-gray-600 p-2 rounded-xl flex flex-col items-center gap-1 transition-all active:scale-95 hover:bg-gray-100">
                            <i class="fa-solid fa-wind text-lg text-blue-400"></i>
                            <span class="text-xs font-bold">放鬆</span>
                        </button>
                        <button onclick="changeMood('heal')" class="mood-btn border border-gray-100 bg-gray-50 text-gray-600 p-2 rounded-xl flex flex-col items-center gap-1 transition-all active:scale-95 hover:bg-gray-100">
                            <i class="fa-solid fa-tree text-lg text-green-500"></i>
                            <span class="text-xs font-bold">療癒</span>
                        </button>
                        <button onclick="changeMood('vitality')" class="mood-btn border border-gray-100 bg-gray-50 text-gray-600 p-2 rounded-xl flex flex-col items-center gap-1 transition-all active:scale-95 hover:bg-gray-100">
                            <i class="fa-solid fa-palette text-lg text-purple-500"></i>
                            <span class="text-xs font-bold">藝文</span>
                        </button>
                        <button onclick="changeMood('sport')" class="mood-btn border border-gray-100 bg-gray-50 text-gray-600 p-2 rounded-xl flex flex-col items-center gap-1 transition-all active:scale-95 hover:bg-gray-100">
                            <i class="fa-solid fa-person-running text-lg text-red-500"></i>
                            <span class="text-xs font-bold">運動</span>
                        </button>
                    </div>
                </div>

                <!-- Location List -->
                <div class="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50 no-scrollbar" id="location-list">
                    <div class="flex flex-col items-center justify-center h-full text-gray-400 gap-2">
                        <i class="fa-solid fa-map-location-dot text-3xl"></i>
                        <p class="text-sm">選擇上方心情，開始探索臺北</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Check-in Modal -->
    <div id="modal" class="hidden fixed inset-0 bg-black/60 z-[2000] flex items-center justify-center p-6 backdrop-blur-sm transition-opacity opacity-0">
        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-xs p-6 text-center transform scale-90 transition-transform">
            <div class="relative">
                <div class="absolute -top-12 left-1/2 -translate-x-1/2 bg-yellow-100 p-4 rounded-full border-4 border-white shadow-lg">
                    <i class="fa-solid fa-trophy text-3xl text-yellow-500"></i>
                </div>
            </div>
            <div class="mt-8">
                <h3 class="text-xl font-bold text-gray-800">任務達成！</h3>
                <p id="modal-text" class="text-sm text-gray-500 mt-2 mb-6">您已完成地點探索</p>
                <div class="flex justify-between items-center bg-gray-50 rounded-lg p-3 mb-4">
                    <span class="text-gray-500 text-sm">獲得獎勵</span>
                    <span class="font-bold text-yellow-600 flex items-center gap-1">
                        +<span id="modal-points">0</span> <i class="fa-solid fa-coins"></i>
                    </span>
                </div>
                <button onclick="closeModal()" class="w-full bg-blue-600 text-white py-3 rounded-xl font-bold shadow-lg shadow-blue-200 active:scale-95 transition-all">
                    太棒了！
                </button>
            </div>
        </div>
    </div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        let map;
        let markers = [];
        let currentLocations = [];

        function initMap() {
            // 臺北市中心點
            map = L.map('map', { zoomControl: false }).setView([25.06, 121.55], 12);
            
            L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
                attribution: '&copy; OpenStreetMap &copy; CARTO',
                subdomains: 'abcd',
                maxZoom: 19
            }).addTo(map);

            L.control.zoom({ position: 'topright' }).addTo(map);

            fetchLocations('all');
        }

        // --- 修正點：補上這個被遺漏的函式 ---
        function changeMood(mood) {
            fetchLocations(mood);
        }
        // ------------------------------------

        async function fetchLocations(mood) {
            // UI 更新
            document.querySelectorAll('.mood-btn').forEach(btn => btn.classList.remove('active'));
            const moodMap = {'relax':0, 'heal':1, 'vitality':2, 'sport':3};
            if(moodMap[mood] !== undefined) {
                document.querySelectorAll('.mood-btn')[moodMap[mood]].classList.add('active');
            }

            // 顯示 Loading
            const list = document.getElementById('location-list');
            list.innerHTML = '<div class="flex justify-center py-10"><i class="fa-solid fa-circle-notch fa-spin text-blue-500"></i></div>';

            try {
                const res = await fetch(`/api/locations?mood=${mood}`);
                currentLocations = await res.json();
                updateUI();
            } catch(e) {
                list.innerHTML = '<div class="text-center text-red-400">載入失敗，請稍後再試</div>';
            }
        }

        function updateUI() {
            // 清除舊 Marker
            markers.forEach(m => map.removeLayer(m));
            markers = [];
            
            const list = document.getElementById('location-list');
            list.innerHTML = '';

            if(currentLocations.length === 0) {
                list.innerHTML = '<div class="text-center text-gray-400 py-10">沒有找到相關地點</div>';
                return;
            }

            currentLocations.forEach((loc, index) => {
                // 1. 建立地圖 Marker
                const markerIcon = L.divIcon({
                    className: 'custom-div-icon',
                    html: `<div style="background-color:${getScoreColor(loc.match_score)}; width:12px; height:12px; border-radius:50%; border:2px solid white; box-shadow:0 2px 4px rgba(0,0,0,0.3);"></div>`,
                    iconSize: [12, 12],
                    iconAnchor: [6, 6]
                });

                const marker = L.marker([loc.lat, loc.lng], {icon: markerIcon}).addTo(map);
                
                // Marker Popup
                const popupContent = `
                    <div class="text-center p-1 font-sans">
                        <div class="text-xs text-gray-500 mb-1">${loc.district}</div>
                        <h3 class="font-bold text-base mb-1">${loc.name}</h3>
                        <div class="text-xs bg-gray-100 inline-block px-2 py-0.5 rounded text-gray-600 mb-2">${loc.tag}</div>
                        <button onclick="checkIn('${loc.name}')" class="w-full bg-blue-500 text-white text-xs py-1.5 rounded hover:bg-blue-600 transition-colors">
                            <i class="fa-solid fa-location-dot mr-1"></i> 打卡
                        </button>
                    </div>
                `;
                marker.bindPopup(popupContent);
                markers.push(marker);

                // 2. 建立列表卡片
                const card = document.createElement('div');
                card.className = "bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex gap-3 cursor-pointer active:scale-[0.98] transition-all duration-200 hover:shadow-md";
                
                // 根據分數決定顯示顏色
                const scoreColor = getScoreColor(loc.match_score);
                
                card.innerHTML = `
                    <div class="flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-sm shadow-sm" style="background-color: ${scoreColor}">
                        ${Math.round(loc.match_score)}
                    </div>
                    <div class="flex-1 min-w-0">
                        <div class="flex justify-between items-start">
                            <div>
                                <h4 class="font-bold text-gray-800 truncate">${loc.name}</h4>
                                <p class="text-xs text-gray-400">${loc.district}</p>
                            </div>
                            <span class="text-[10px] px-2 py-1 bg-gray-100 text-gray-500 rounded-full whitespace-nowrap">${loc.tag}</span>
                        </div>
                        <p class="text-xs text-gray-500 mt-1 line-clamp-2">${loc.description}</p>
                    </div>
                `;
                
                card.onclick = () => {
                    map.flyTo([loc.lat, loc.lng], 16, { duration: 1.5 });
                    setTimeout(() => marker.openPopup(), 1500);
                };

                list.appendChild(card);
            });
            
            // 自動調整地圖視野以包含所有點
            if(markers.length > 0) {
                const group = new L.featureGroup(markers);
                map.fitBounds(group.getBounds().pad(0.1));
            }
        }

        function getScoreColor(score) {
            if(score >= 80) return '#10b981'; // Green-500
            if(score >= 60) return '#3b82f6'; // Blue-500
            return '#f59e0b'; // Amber-500
        }

        async function checkIn(name) {
            map.closePopup();
            try {
                const res = await fetch('/api/checkin', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ locationName: name })
                });
                const data = await res.json();
                
                document.getElementById('user-points').innerText = data.total_points;
                document.getElementById('modal-points').innerText = data.earned;
                document.getElementById('modal-text').innerText = `您已抵達 ${name}`;
                
                const modal = document.getElementById('modal');
                modal.classList.remove('hidden');
                setTimeout(() => {
                    modal.classList.remove('opacity-0');
                    modal.querySelector('div').classList.remove('scale-90');
                    modal.querySelector('div').classList.add('scale-100');
                }, 10);

            } catch(e) { console.error(e); }
        }

        function closeModal() {
            const modal = document.getElementById('modal');
            modal.classList.add('opacity-0');
            modal.querySelector('div').classList.remove('scale-100');
            modal.querySelector('div').classList.add('scale-90');
            
            setTimeout(() => {
                modal.classList.add('hidden');
            }, 300);
        }

        window.onload = initMap;
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)