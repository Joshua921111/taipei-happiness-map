import json, random, os
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

# ==========================================
# 1. 模擬 OpenData 數據庫 (50+ 地點完整版)
# ==========================================
# 數據邏輯：pm25(低優), noise(低優), green(高優), art(高優), sport(高優)

LOCATIONS = [
    # --- 原有景點與地標 ---
    {"id":1, "name":"中正紀念堂", "district":"中正區", "lat":25.0348, "lng":121.5217, "description":"藍白建築與廣闊廣場，國際級展覽與藝文活動的首選展場。", "data":{"pm25":25,"noise":55,"green":60,"art":98,"sport":40}},
    {"id":2, "name":"華山1914文創園區", "district":"中正區", "lat":25.0441, "lng":121.5293, "description":"文青必訪的展演基地，匯集設計展、快閃店與草地野餐。", "data":{"pm25":30,"noise":65,"green":30,"art":100,"sport":10}},
    {"id":3, "name":"榕錦時光生活園區", "district":"大安區", "lat":25.0322, "lng":121.5265, "description":"原臺北刑務所官舍修復，日式老宅氛圍的IG熱門打卡點。", "data":{"pm25":20,"noise":45,"green":50,"art":85,"sport":5}},
    {"id":4, "name":"寶藏巖國際藝術村", "district":"中正區", "lat":25.0105, "lng":121.5323, "description":"依山而建的歷史聚落，共生藝術與獨特地景的探索秘境。", "data":{"pm25":15,"noise":30,"green":80,"art":95,"sport":30}},
    {"id":5, "name":"大安森林公園", "district":"大安區", "lat":25.0300, "lng":121.5358, "description":"城市之肺，適合野餐、慢跑與欣賞露天音樂表演。", "data":{"pm25":18,"noise":45,"green":100,"art":40,"sport":60}},
    {"id":6, "name":"忠泰美術館", "district":"大安區", "lat":25.0435, "lng":121.5372, "description":"專注於「未來」與「城市」議題的精品美術館展場。", "data":{"pm25":20,"noise":50,"green":20,"art":95,"sport":0}},
    {"id":7, "name":"松山文創園區", "district":"信義區", "lat":25.0439, "lng":121.5606, "description":"菸廠古蹟活化，結合誠品書店與設計展演的文化園區。", "data":{"pm25":22,"noise":55,"green":50,"art":95,"sport":20}},
    {"id":8, "name":"四四南村", "district":"信義區", "lat":25.0312, "lng":121.5620, "description":"信義區中的眷村記憶，週末簡單市集與藝文展演空間。", "data":{"pm25":25,"noise":50,"green":30,"art":85,"sport":10}},
    {"id":9, "name":"象山六巨石", "district":"信義區", "lat":25.0267, "lng":121.5746, "description":"社群媒體上最熱門的台北夜景拍攝點，揮灑汗水的絕佳步道。", "data":{"pm25":10,"noise":30,"green":90,"art":10,"sport":90}},
    {"id":10, "name":"臺北市立美術館", "district":"中山區", "lat":25.0722, "lng":121.5246, "description":"臺灣首座現代美術館，純白建築與光影交織的藝術殿堂。", "data":{"pm25":20,"noise":40,"green":50,"art":100,"sport":10}},
    {"id":11, "name":"心中山線形公園", "district":"中山區", "lat":25.0556, "lng":121.5205, "description":"串聯中山與雙連的綠色廊道，週末市集與年輕潮流聚集地。", "data":{"pm25":35,"noise":65,"green":70,"art":60,"sport":30}},
    {"id":12, "name":"經國七海文化園區", "district":"中山區", "lat":25.0789, "lng":121.5332, "description":"結合古蹟、圖書館與劍潭湖美景的寧靜文化園區。", "data":{"pm25":15,"noise":30,"green":85,"art":70,"sport":20}},
    {"id":13, "name":"臺北表演藝術中心", "district":"士林區", "lat":25.0847, "lng":121.5255, "description":"CNN評選全球最具變革性建築，國際級表演藝術場館。", "data":{"pm25":35,"noise":65,"green":10,"art":100,"sport":0}},
    {"id":14, "name":"國立故宮博物院", "district":"士林區", "lat":25.1024, "lng":121.5485, "description":"世界級中華文化寶庫，歷史迷與外國遊客必訪展場。", "data":{"pm25":12,"noise":35,"green":80,"art":100,"sport":10}},
    {"id":15, "name":"台北當代藝術館", "district":"大同區", "lat":25.0504, "lng":121.5186, "description":"日治時期小學校舍改建，前衛當代藝術的指標性展場。", "data":{"pm25":30,"noise":55,"green":10,"art":100,"sport":0}},
    {"id":16, "name":"大稻埕碼頭", "district":"大同區", "lat":25.0567, "lng":121.5076, "description":"落日餘暉下的貨櫃市集，河畔騎車與小酌的放鬆聖地。", "data":{"pm25":25,"noise":60,"green":40,"art":50,"sport":70}},
    {"id":17, "name":"剝皮寮歷史街區", "district":"萬華區", "lat":25.0369, "lng":121.5015, "description":"清代街道風貌保存最完整的區域，經常舉辦藝文特展。", "data":{"pm25":35,"noise":50,"green":10,"art":85,"sport":5}},
    {"id":18, "name":"新富町文化市場", "district":"萬華區", "lat":25.0355, "lng":121.5021, "description":"馬蹄形古蹟市場變身文創基地，建築攝影愛好者必訪。", "data":{"pm25":30,"noise":45,"green":10,"art":80,"sport":0}},
    {"id":19, "name":"臺北流行音樂中心", "district":"南港區", "lat":25.0519, "lng":121.5985, "description":"仿山巒起伏的指標建築，流行音樂展演與文化的最高殿堂。", "data":{"pm25":30,"noise":60,"green":40,"art":95,"sport":20}},
    {"id":20, "name":"瓶蓋工廠台北製造所", "district":"南港區", "lat":25.0543, "lng":121.6001, "description":"老工廠翻新為職人手作基地，充滿工業風的展演空間。", "data":{"pm25":25,"noise":50,"green":30,"art":80,"sport":10}},
    {"id":21, "name":"北投圖書館", "district":"北投區", "lat":25.1363, "lng":121.5063, "description":"全球最美公立圖書館之一，與公園生態共生的木造綠建築。", "data":{"pm25":8,"noise":30,"green":95,"art":70,"sport":10}},
    {"id":22, "name":"法鼓山農禪寺", "district":"北投區", "lat":25.1257, "lng":121.4984, "description":"水月道場的空靈倒影，IG上最熱門的寧靜心靈場所。", "data":{"pm25":10,"noise":20,"green":60,"art":80,"sport":5}},
    {"id":23, "name":"台北田徑場", "district":"松山區", "lat":25.0489, "lng":121.5517, "description":"國際級標準運動場，市民揮灑汗水與能量的中心。", "data":{"pm25":30,"noise":70,"green":20,"art":10,"sport":95}},

    # --- 網紅咖啡廳 (Relax/Art) ---
    {"id":201, "name":"Simple Kaffa Sola 天空興波", "district":"信義區", "lat":25.0339, "lng":121.5644, "description":"位於台北101的88樓，冠軍咖啡與雲端美景的極致享受。", "data":{"pm25":5,"noise":20,"green":10,"art":90,"sport":0}},
    {"id":202, "name":"CAMA COFFEE 豆留森林", "district":"士林區", "lat":25.1332, "lng":121.5567, "description":"陽明山上的昭和風老宅咖啡，竹林環繞的秘境。", "data":{"pm25":5,"noise":30,"green":95,"art":85,"sport":10}},
    {"id":203, "name":"Sidoli Radio 小島裡", "district":"大同區", "lat":25.0553, "lng":121.5126, "description":"結合錄音室與咖啡廳的複合空間，用聲音記錄大稻埕故事。", "data":{"pm25":25,"noise":30,"green":10,"art":95,"sport":0}},
    {"id":204, "name":"ACME｜Taipei Fine Arts Museum", "district":"中山區", "lat":25.0725, "lng":121.5247, "description":"北美館旁的純白玻璃屋，藝術與早午餐的完美結合。", "data":{"pm25":20,"noise":40,"green":60,"art":90,"sport":10}},
    {"id":205, "name":"Tokyobike Taiwan", "district":"萬華區", "lat":25.0355, "lng":121.5021, "description":"位於新富町文化市場內的單車主題咖啡，日式簡約風格。", "data":{"pm25":30,"noise":45,"green":20,"art":85,"sport":40}},
    {"id":206, "name":"% Arabica Taipei Elephant Mountain", "district":"信義區", "lat":25.0275, "lng":121.5707, "description":"京都人氣咖啡台灣首店，象山腳下的純白極簡風格。", "data":{"pm25":10,"noise":40,"green":80,"art":70,"sport":30}},
    {"id":207, "name":"The Hippo Coffee Bar", "district":"信義區", "lat":25.0410, "lng":121.5780, "description":"信義區巷弄內的河馬主題咖啡，清新可愛的療癒空間。", "data":{"pm25":20,"noise":35,"green":20,"art":60,"sport":0}},
    {"id":208, "name":"Woolloomooloo", "district":"信義區", "lat":25.0329, "lng":121.5564, "description":"工業風澳式咖啡餐酒館，都市人下班後的充電站。", "data":{"pm25":25,"noise":60,"green":10,"art":65,"sport":5}},
    {"id":209, "name":"UR LIVING 生活美學", "district":"信義區", "lat":25.0430, "lng":121.5580, "description":"結合服飾與早午餐的複合式空間，OUVERT SEOUL 進駐。", "data":{"pm25":25,"noise":55,"green":15,"art":80,"sport":5}},
    {"id":210, "name":"登波咖啡 Coffee Dumbo", "district":"中山區", "lat":25.0558, "lng":121.5198, "description":"赤峰街美式復古風格咖啡廳，肉桂捲與鐵窗花是招牌。", "data":{"pm25":30,"noise":50,"green":10,"art":85,"sport":0}},
    {"id":211, "name":"Twin Brothers Coffee", "district":"大同區", "lat":25.0495, "lng":121.5170, "description":"台北車站附近最好吃的肉桂捲，雙胞胎兄弟的溫馨小店。", "data":{"pm25":35,"noise":60,"green":5,"art":60,"sport":0}},
    {"id":212, "name":"勺日 Zhuori", "district":"大安區", "lat":25.0415, "lng":121.5435, "description":"韓系奶油黃風格早午餐，可頌鬆餅是必點招牌。", "data":{"pm25":25,"noise":50,"green":15,"art":75,"sport":0}},
    {"id":213, "name":"Congrats Café", "district":"大安區", "lat":25.0335, "lng":121.5545, "description":"文昌街老宅改建的不限時咖啡廳，古董家具與深夜咖啡。", "data":{"pm25":20,"noise":30,"green":20,"art":90,"sport":0}},
    {"id":214, "name":"Häppī Café", "district":"大安區", "lat":25.0255, "lng":121.5430, "description":"簡單清新的日系風格咖啡，適合一個人閱讀或工作。", "data":{"pm25":20,"noise":25,"green":15,"art":70,"sport":0}},

    # --- 特色餐廳 (Art/Vitality) ---
    {"id":301, "name":"詹記麻辣火鍋 西門大世界", "district":"萬華區", "lat":25.0440, "lng":121.5060, "description":"復古台式風格的麻辣鍋名店，充滿90年代懷舊氛圍。", "data":{"pm25":40,"noise":70,"green":5,"art":75,"sport":0}},
    {"id":302, "name":"Spring Leek 春韭", "district":"中山區", "lat":25.0583, "lng":121.5230, "description":"私廚台菜餐廳，充滿古董與老宅韻味的用餐體驗。", "data":{"pm25":25,"noise":30,"green":15,"art":85,"sport":0}},
    {"id":303, "name":"小小樹食", "district":"大安區", "lat":25.0375, "lng":121.5490, "description":"最美蔬食餐廳，打破素食印象的創意料理與粉紅空間。", "data":{"pm25":20,"noise":50,"green":20,"art":80,"sport":5}},
    {"id":304, "name":"香色 Xiang Se", "district":"中正區", "lat":25.0305, "lng":121.5105, "description":"隱身巷弄的南法鄉村風私廚，燭光晚餐的浪漫首選。", "data":{"pm25":20,"noise":30,"green":30,"art":90,"sport":0}},
    {"id":305, "name":"瑪黑餐酒 Ochre", "district":"大安區", "lat":25.0395, "lng":121.5550, "description":"結合家居選物與歐陸料理，極具質感的約會餐廳。", "data":{"pm25":25,"noise":55,"green":10,"art":95,"sport":0}},

    # --- 攀岩與運動場館 (Sport/Energy) ---
    {"id":501, "name":"原岩攀岩館 (萬華店)", "district":"萬華區", "lat":25.0330, "lng":121.4980, "description":"專業抱石場館，路線豐富，適合新手到高手的挑戰。", "data":{"pm25":20,"noise":50,"green":5,"art":20,"sport":100}},
    {"id":502, "name":"Double8 岩究所", "district":"大同區", "lat":25.0600, "lng":121.5100, "description":"隱身迪化街老宅內的攀岩場，結合古蹟與極限運動。", "data":{"pm25":25,"noise":45,"green":10,"art":70,"sport":95}},
    {"id":503, "name":"CORNER Bouldering Gym 角攀岩館", "district":"中山區", "lat":25.0530, "lng":121.5230, "description":"位於市中心的精緻抱石館，交通便利的下班運動首選。", "data":{"pm25":25,"noise":55,"green":5,"art":30,"sport":95}},
    {"id":504, "name":"市民抱石攀岩館", "district":"南港區", "lat":25.0515, "lng":121.6080, "description":"南港展覽館旁的寬敞岩場，擁有挑高空間與多元路線。", "data":{"pm25":20,"noise":50,"green":10,"art":10,"sport":95}},
    {"id":505, "name":"MegaSTONE Climbing Gym", "district":"新莊區", "lat":25.0360, "lng":121.4520, "description":"擁有挑高環狀中島牆的豪華岩館，路線多樣化。", "data":{"pm25":25,"noise":50,"green":10,"art":10,"sport":98}},
    {"id":506, "name":"紅石攀岩館 Red Rock", "district":"士林區", "lat":25.0875, "lng":121.5120, "description":"溫馨的小型抱石館，適合初學者體驗攀岩樂趣。", "data":{"pm25":20,"noise":40,"green":15,"art":20,"sport":90}},
    {"id":507, "name":"大安運動中心", "district":"大安區", "lat":25.0204, "lng":121.5451, "description":"設施完善的現代化運動場館，釋放壓力的好去處。", "data":{"pm25":15,"noise":60,"green":10,"art":5,"sport":90}},
    {"id":508, "name":"內湖運動中心", "district":"內湖區", "lat":25.0718, "lng":121.5750, "description":"擁有國際標準攀岩場的運動中心，極限運動愛好者聚集。", "data":{"pm25":20,"noise":55,"green":20,"art":5,"sport":95}},
    {"id":509, "name":"信義運動中心", "district":"信義區", "lat":25.0320, "lng":121.5700, "description":"鄰近象山，設備新穎，提供多元運動課程。", "data":{"pm25":15,"noise":50,"green":25,"art":5,"sport":90}},
    {"id":510, "name":"文山運動中心", "district":"文山區", "lat":24.9980, "lng":121.5550, "description":"腹地廣大，擁有優質游泳池與體適能中心。", "data":{"pm25":10,"noise":40,"green":30,"art":5,"sport":90}}
]

WEATHER_TYPES = [
    {"icon": "fa-sun", "text": "晴朗", "color": "text-orange-500", "temp": "28°C"},
    {"icon": "fa-cloud-sun", "text": "多雲", "color": "text-yellow-500", "temp": "24°C"},
    {"icon": "fa-wind", "text": "微風", "color": "text-blue-400", "temp": "22°C"},
]

user_points = 0

# ================= 2. 核心算法 =================
def calculate_happiness_indices(loc_data):
    pm25_score = max(0, 100 - loc_data['pm25'] * 1.5)
    noise_score = max(0, 100 - loc_data['noise'] * 1.2)
    relaxation = (pm25_score + noise_score) / 2
    healing = loc_data['green']
    vitality = min(100, (loc_data['art'] * 0.9 + loc_data['noise'] * 0.1))
    energy = loc_data['sport']
    return {
        "relaxation": round(relaxation, 1),
        "healing": round(healing, 1),
        "vitality": round(vitality, 1),
        "energy": round(energy, 1)
    }

# ================= 3. 路由與 API =================
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/locations', methods=['GET'])
def get_locations():
    mood = request.args.get('mood', 'all')
    processed_locations = []
    
    for loc in LOCATIONS:
        indices = calculate_happiness_indices(loc['data'])
        scores = {
            'vitality': indices['vitality'],
            'healing': indices['healing'],
            'energy': indices['energy'],
            'relaxation': indices['relaxation']
        }
        dominant_attr = max(scores, key=scores.get)
        match_score = 0
        tag = ""
        marker_color = "#3b82f6"

        if mood == 'relax':
            match_score = indices['relaxation']; tag = "☁️ 極致放鬆"; marker_color = "#3b82f6"
        elif mood == 'heal':
            match_score = indices['healing']; tag = "🌳 自然療癒"; marker_color = "#10b981"
        elif mood == 'vitality':
            match_score = indices['vitality']; tag = "🎨 藝文活力"; marker_color = "#a855f7"
        elif mood == 'sport':
            match_score = indices['energy']; tag = "🏃‍♂️ 揮灑汗水"; marker_color = "#ef4444"
        else:
            match_score = sum(scores.values()) / 4
            if dominant_attr == 'vitality': tag = "🎨 藝文特區"; marker_color = "#a855f7"
            elif dominant_attr == 'healing': tag = "🌳 療癒綠洲"; marker_color = "#10b981"
            elif dominant_attr == 'energy': tag = "🏃‍♂️ 運動熱點"; marker_color = "#ef4444"
            else: tag = "☁️ 放鬆角落"; marker_color = "#3b82f6"

        loc_obj = loc.copy()
        loc_obj.update({'indices': indices, 'match_score': round(match_score, 1), 'tag': tag, 'weather': random.choice(WEATHER_TYPES), 'marker_color': marker_color})
        processed_locations.append(loc_obj)

    if mood == 'all': random.shuffle(processed_locations)
    processed_locations.sort(key=lambda x: x['match_score'], reverse=True)
    return jsonify(processed_locations)

@app.route('/api/checkin', methods=['POST'])
def checkin():
    global user_points
    data = request.json
    points_earned = random.randint(30, 80)
    user_points += points_earned
    new_badge = None
    if user_points >= 500: new_badge = "臺北幸福大使"
    elif user_points >= 300: new_badge = "數據大師"
    elif user_points >= 100: new_badge = "城市探索者"
    return jsonify({
        "status": "success",
        "message": f"抵達「{data.get('locationName')}」",
        "earned": points_earned,
        "total_points": user_points,
        "new_badge": new_badge
    })

# ================= 4. 前端介面 =================
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
        .mood-btn { transition: all 0.2s; }
        .mood-btn.active { background-color: #3b82f6 !important; color: white !important; border-color: #3b82f6 !important; box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.5); }
        .mood-btn.active i, .mood-btn.active span { color: white !important; }
        .no-scrollbar::-webkit-scrollbar { display: none; } .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
        @keyframes ring { 0%,100% { transform: rotate(0); } 10%,90% { transform: rotate(30deg); } 30%,70% { transform: rotate(-30deg); } 50% { transform: rotate(30deg); } }
        .bell-animation { animation: ring 1s ease-in-out; }
    </style>
</head>
<body class="flex flex-col h-screen text-slate-800">
    <nav class="bg-white shadow-sm z-50 px-4 py-3 flex justify-between items-center shrink-0 border-b border-gray-100">
        <div class="flex items-center gap-2">
            <div id="nav-bell" onclick="ringBell()" class="bg-gradient-to-br from-blue-500 to-blue-600 text-white p-2 rounded-xl shadow-sm cursor-pointer active:scale-95"><i class="fa-solid fa-bell text-sm"></i></div>
            <div><h1 class="text-lg font-bold tracking-tight text-slate-800">幸福地圖</h1><div class="text-[10px] text-slate-500 leading-none">Taipei Happiness Bell</div></div>
        </div>
        <div class="flex items-center gap-3">
            <div onclick="showBadges()" class="cursor-pointer bg-slate-100 p-2 rounded-full hover:bg-slate-200 transition"><i class="fa-solid fa-medal text-slate-600"></i></div>
            <div class="flex items-center gap-1.5 bg-amber-50 border border-amber-100 px-3 py-1.5 rounded-full"><i class="fa-solid fa-star text-amber-500 text-xs"></i><span id="user-points" class="font-bold text-amber-700 text-sm">0</span></div>
        </div>
    </nav>

    <div class="flex flex-1 flex-col md:flex-row overflow-hidden relative">
        <div id="map-container" class="absolute inset-0 md:relative md:w-2/3 md:order-2 z-0 transition-all duration-300 ease-in-out">
            <div id="map" class="h-full w-full"></div>
            <button onclick="toggleSidebar()" class="hidden md:flex absolute top-1/2 left-0 transform -translate-y-1/2 z-[500] bg-white text-slate-500 hover:text-blue-600 p-2 rounded-r-lg shadow-md border border-l-0 border-gray-200 items-center justify-center transition-all hover:pl-3"><i id="sidebar-toggle-icon" class="fa-solid fa-chevron-left"></i></button>
            <button onclick="showGuide()" class="absolute bottom-8 right-4 z-[500] bg-white text-slate-600 p-3 rounded-full shadow-lg border border-gray-200 hover:bg-gray-50 transition-all active:scale-95 hover:text-blue-600"><i class="fa-solid fa-book-open text-xl"></i></button>
            <div class="hidden md:block absolute bottom-8 left-8 bg-white/95 p-4 rounded-xl shadow-xl z-[500] text-xs backdrop-blur-sm border border-gray-100">
                <div class="font-bold mb-3 text-slate-700 text-sm">地圖顏色說明</div>
                <div class="space-y-2">
                    <div class="flex items-center gap-2"><div class="w-3 h-3 bg-purple-500 rounded-full"></div> <span>藝文特區 (Art)</span></div>
                    <div class="flex items-center gap-2"><div class="w-3 h-3 bg-green-500 rounded-full"></div> <span>療癒綠洲 (Healing)</span></div>
                    <div class="flex items-center gap-2"><div class="w-3 h-3 bg-red-500 rounded-full"></div> <span>運動熱點 (Energy)</span></div>
                    <div class="flex items-center gap-2"><div class="w-3 h-3 bg-blue-500 rounded-full"></div> <span>放鬆角落 (Relax)</span></div>
                </div>
            </div>
        </div>

        <div id="sidebar-panel" class="absolute bottom-0 w-full md:relative md:w-1/3 md:order-1 md:h-full z-20 flex flex-col pointer-events-none md:pointer-events-auto transition-all duration-300 ease-in-out origin-left">
            <div class="bg-white rounded-t-3xl md:rounded-none shadow-[0_-8px_30px_rgba(0,0,0,0.12)] flex flex-col h-[55vh] md:h-full pointer-events-auto">
                <div class="w-full flex justify-center pt-3 pb-1 md:hidden"><div class="w-12 h-1.5 bg-gray-200 rounded-full"></div></div>
                <div class="p-5 border-b border-gray-100 bg-white shrink-0">
                    <div class="grid grid-cols-4 gap-3">
                        <button id="btn-relax" onclick="changeMood('relax')" class="mood-btn border border-slate-100 bg-slate-50 text-slate-600 p-2.5 rounded-2xl flex flex-col items-center gap-1.5 hover:bg-slate-100"><i class="fa-solid fa-wind text-xl text-blue-400"></i><span class="text-xs font-bold">放鬆</span></button>
                        <button id="btn-heal" onclick="changeMood('heal')" class="mood-btn border border-slate-100 bg-slate-50 text-slate-600 p-2.5 rounded-2xl flex flex-col items-center gap-1.5 hover:bg-slate-100"><i class="fa-solid fa-tree text-xl text-green-500"></i><span class="text-xs font-bold">療癒</span></button>
                        <button id="btn-vitality" onclick="changeMood('vitality')" class="mood-btn border border-slate-100 bg-slate-50 text-slate-600 p-2.5 rounded-2xl flex flex-col items-center gap-1.5 hover:bg-slate-100"><i class="fa-solid fa-palette text-xl text-purple-500"></i><span class="text-xs font-bold">藝文</span></button>
                        <button id="btn-sport" onclick="changeMood('sport')" class="mood-btn border border-slate-100 bg-slate-50 text-slate-600 p-2.5 rounded-2xl flex flex-col items-center gap-1.5 hover:bg-slate-100"><i class="fa-solid fa-person-running text-xl text-red-500"></i><span class="text-xs font-bold">運動</span></button>
                    </div>
                </div>
                <div class="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50 no-scrollbar" id="location-list"></div>
            </div>
        </div>
    </div>

    <div id="guide-modal" class="hidden fixed inset-0 bg-black/50 z-[2000] flex items-center justify-center p-4 backdrop-blur-sm" onclick="hideModal('guide-modal', event)">
        <div class="bg-white w-full max-w-md rounded-3xl p-6 shadow-2xl relative overflow-hidden" onclick="event.stopPropagation()">
            <div class="absolute top-0 left-0 w-full h-24 bg-gradient-to-r from-blue-500 to-blue-600 -z-10"></div>
            <div class="flex justify-between items-center mb-6 text-white relative z-10"><h3 class="text-xl font-bold flex items-center gap-2"><i class="fa-solid fa-book-open"></i> 使用指南</h3><button onclick="document.getElementById('guide-modal').classList.add('hidden')" class="bg-white/20 hover:bg-white/30 rounded-full p-2 transition"><i class="fa-solid fa-xmark"></i></button></div>
            <div class="space-y-6 max-h-[60vh] overflow-y-auto pr-2 no-scrollbar">
                <div><h4 class="font-bold text-slate-800 mb-2 flex items-center gap-2"><i class="fa-solid fa-chart-bar text-blue-500"></i> 數據指標</h4><ul class="text-sm text-slate-600 space-y-2 bg-slate-50 p-3 rounded-xl"><li><b class="text-blue-500">PM2.5</b>：數值越高代表空氣越好(反轉)。</li><li><b class="text-green-500">綠覆率</b>：綠地覆蓋程度。</li><li><b class="text-purple-500">藝文</b>：展覽活動頻率。</li></ul></div>
                <div><h4 class="font-bold text-slate-800 mb-2 flex items-center gap-2"><i class="fa-solid fa-palette text-purple-500"></i> 顏色代表</h4><div class="grid grid-cols-2 gap-3 text-sm"><div class="flex items-center gap-2 bg-purple-50 p-2 rounded-lg"><div class="w-3 h-3 bg-purple-500 rounded-full"></div>藝文特區</div><div class="flex items-center gap-2 bg-green-50 p-2 rounded-lg"><div class="w-3 h-3 bg-green-500 rounded-full"></div>療癒綠洲</div><div class="flex items-center gap-2 bg-red-50 p-2 rounded-lg"><div class="w-3 h-3 bg-red-500 rounded-full"></div>運動熱點</div><div class="flex items-center gap-2 bg-blue-50 p-2 rounded-lg"><div class="w-3 h-3 bg-blue-500 rounded-full"></div>放鬆角落</div></div></div>
            </div>
            <button onclick="document.getElementById('guide-modal').classList.add('hidden')" class="mt-6 w-full py-3 bg-slate-100 hover:bg-slate-200 rounded-xl text-slate-600 font-bold transition">我瞭解了</button>
        </div>
    </div>

    <div id="modal" class="hidden fixed inset-0 bg-slate-900/60 z-[2000] flex items-center justify-center p-6 backdrop-blur-sm transition-opacity opacity-0"><div class="bg-white rounded-3xl shadow-2xl w-full max-w-xs p-8 text-center transform scale-90 transition-transform relative overflow-hidden"><div class="absolute top-0 left-0 w-full h-32 bg-gradient-to-b from-yellow-50 to-white -z-10"></div><div class="relative mb-6"><div class="w-24 h-24 bg-white rounded-full flex items-center justify-center mx-auto shadow-lg border-4 border-yellow-50"><i id="bell-icon" class="fa-solid fa-bell text-5xl text-yellow-500"></i></div><div class="absolute -bottom-2 left-1/2 -translate-x-1/2 bg-yellow-500 text-white text-[10px] px-2 py-0.5 rounded-full font-bold">TASK COMPLETED</div></div><h3 class="text-2xl font-bold text-slate-800 mb-1">任務達成！</h3><p id="modal-text" class="text-sm text-slate-500 mb-6">成功抵達探索地點</p><div class="bg-slate-50 rounded-2xl p-4 mb-6 border border-slate-100"><div class="flex justify-between items-center mb-2"><span class="text-slate-500 text-xs font-bold uppercase">獲得積分</span><span class="font-bold text-yellow-600 flex items-center gap-1 text-lg">+<span id="modal-points">0</span></span></div><div id="badge-notification" class="hidden pt-2 border-t border-slate-200 mt-2"><div class="text-xs text-blue-500 font-bold mb-1">獲得新獎章！</div><div class="flex items-center justify-center gap-2 text-slate-700 font-bold"><i class="fa-solid fa-medal text-blue-500"></i> <span id="badge-name"></span></div></div></div><button onclick="closeModal()" class="w-full bg-slate-800 text-white py-3.5 rounded-xl font-bold shadow-lg shadow-slate-200 active:scale-95 transition-all">收下獎勵</button></div></div>
    
    <div id="badge-modal" class="hidden fixed inset-0 bg-black/50 z-[2000] flex items-center justify-center p-4 backdrop-blur-sm" onclick="hideModal('badge-modal', event)"><div class="bg-white w-full max-w-sm rounded-2xl p-6 shadow-2xl" onclick="event.stopPropagation()"><h3 class="font-bold text-lg mb-4 flex items-center gap-2"><i class="fa-solid fa-medal text-blue-500"></i> 我的成就獎章</h3><div class="grid grid-cols-3 gap-4 text-center"><div class="flex flex-col items-center gap-2 opacity-100"><div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center text-blue-500"><i class="fa-solid fa-user"></i></div><span class="text-xs font-bold text-slate-600">新手上路</span></div><div class="flex flex-col items-center gap-2 opacity-40" id="badge-explorer"><div class="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center text-yellow-500"><i class="fa-solid fa-compass"></i></div><span class="text-xs font-bold text-slate-600">城市探索者</span></div><div class="flex flex-col items-center gap-2 opacity-40" id="badge-data"><div class="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center text-purple-500"><i class="fa-solid fa-chart-pie"></i></div><span class="text-xs font-bold text-slate-600">數據大師</span></div></div><button onclick="document.getElementById('badge-modal').classList.add('hidden')" class="mt-6 w-full py-2 bg-gray-100 rounded-lg text-sm font-bold text-gray-600">關閉</button></div></div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        let map, markers=[], currentLocations=[], isSidebarOpen=true, currentMood='all';
        function initMap() {
            map = L.map('map', {zoomControl:false}).setView([25.06, 121.55], 12);
            L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {attribution:'OpenStreetMap', maxZoom:19}).addTo(map);
            fetchLocations('all');
        }
        function toggleSidebar() {
            const sb=document.getElementById('sidebar-panel'), mc=document.getElementById('map-container'), icon=document.getElementById('sidebar-toggle-icon');
            isSidebarOpen = !isSidebarOpen;
            if(isSidebarOpen){ sb.classList.remove('md:w-0','hidden'); sb.classList.add('md:w-1/3'); mc.classList.remove('md:w-full'); mc.classList.add('md:w-2/3'); icon.classList.replace('fa-chevron-right','fa-chevron-left'); }
            else { sb.classList.remove('md:w-1/3'); sb.classList.add('md:w-0','hidden'); mc.classList.remove('md:w-2/3'); mc.classList.add('md:w-full'); icon.classList.replace('fa-chevron-left','fa-chevron-right'); }
            setTimeout(()=>map.invalidateSize(), 300);
        }
        function changeMood(m) { 
            if(currentMood === m) currentMood = 'all'; else currentMood = m;
            fetchLocations(currentMood); 
        }
        async function fetchLocations(m) {
            document.querySelectorAll('.mood-btn').forEach(b=>b.classList.remove('active'));
            if(m!=='all') { const btn=document.getElementById('btn-'+m); if(btn) btn.classList.add('active'); }
            try { const res=await fetch(`/api/locations?mood=${m}`); currentLocations=await res.json(); updateUI(); } catch(e){}
        }
        function updateUI() {
            markers.forEach(m=>map.removeLayer(m)); markers=[];
            const list = document.getElementById('location-list'); list.innerHTML='';
            currentLocations.forEach(loc => {
                const icon = L.divIcon({className:'custom-div-icon', html:`<div style="background-color:${loc.marker_color}; width:16px; height:16px; border-radius:50%; border:3px solid white; box-shadow:0 3px 6px rgba(0,0,0,0.2);"></div>`, iconSize:[16,16], iconAnchor:[8,8]});
                const popup = `
                    <div class="font-sans min-w-[220px] p-1">
                        <div class="flex justify-between items-center mb-2"><span class="text-xs font-bold text-slate-400 uppercase whitespace-nowrap">${loc.district}</span><span class="text-xs font-bold ${loc.weather.color} whitespace-nowrap"><i class="fa-solid ${loc.weather.icon}"></i> ${loc.weather.temp}</span></div>
                        <h3 class="font-bold text-lg text-slate-800 mb-1 leading-tight">${loc.name}</h3><div class="text-xs text-slate-500 mb-3">${loc.tag}</div>
                        <div class="bg-slate-50 p-2 rounded-lg border border-slate-100 mb-3 space-y-1.5">
                            <div class="flex items-center text-[10px] text-slate-500"><span class="w-10 whitespace-nowrap">PM2.5</span><div class="flex-1 ml-2 h-1.5 bg-gray-200 rounded-full overflow-hidden"><div class="h-full bg-blue-400" style="width:${100-loc.data.pm25}%"></div></div></div>
                            <div class="flex items-center text-[10px] text-slate-500"><span class="w-10 whitespace-nowrap">綠覆率</span><div class="flex-1 ml-2 h-1.5 bg-gray-200 rounded-full overflow-hidden"><div class="h-full bg-green-500" style="width:${loc.data.green}%"></div></div></div>
                            <div class="flex items-center text-[10px] text-slate-500"><span class="w-10 whitespace-nowrap">藝文</span><div class="flex-1 ml-2 h-1.5 bg-gray-200 rounded-full overflow-hidden"><div class="h-full bg-purple-500" style="width:${loc.data.art}%"></div></div></div>
                        </div>
                        <div class="grid grid-cols-2 gap-2"><a href="https://www.google.com/maps/dir/?api=1&destination=${loc.lat},${loc.lng}" target="_blank" class="text-center bg-white border border-slate-200 text-slate-600 text-xs py-2 rounded-lg font-bold hover:bg-slate-50 whitespace-nowrap">導航</a><button onclick="checkIn('${loc.name}')" class="bg-blue-600 text-white text-xs py-2 rounded-lg font-bold hover:bg-blue-700 shadow-sm whitespace-nowrap">打卡</button></div>
                    </div>`;
                const m = L.marker([loc.lat, loc.lng], {icon}).addTo(map).bindPopup(popup, {maxWidth:260, minWidth:220, autoPanPadding:[20,20]});
                markers.push(m);
                const card = document.createElement('div');
                card.className = "bg-white p-4 rounded-2xl shadow-sm border border-slate-100 cursor-pointer active:scale-[0.98] transition-all hover:shadow-md hover:border-blue-100";
                let tagBg="bg-slate-100 text-slate-500";
                if(loc.tag.includes("藝文")) tagBg="bg-purple-100 text-purple-600"; else if(loc.tag.includes("療癒")) tagBg="bg-green-100 text-green-600"; else if(loc.tag.includes("運動")) tagBg="bg-red-100 text-red-600"; else if(loc.tag.includes("放鬆")) tagBg="bg-blue-100 text-blue-600";
                card.innerHTML = `<div class="flex gap-4"><div class="flex-shrink-0 w-14 h-14 rounded-2xl flex flex-col items-center justify-center text-white font-bold shadow-sm" style="background-color:${loc.marker_color}"><span class="text-lg leading-none">${Math.round(loc.match_score)}</span><span class="text-[9px] opacity-80">分</span></div><div class="flex-1 min-w-0"><div class="flex justify-between items-start mb-1"><h4 class="font-bold text-slate-800 truncate text-base">${loc.name}</h4><span class="text-[10px] px-2 py-0.5 rounded-full ${tagBg}">${loc.tag}</span></div><p class="text-xs text-slate-500 line-clamp-2 mb-2">${loc.description}</p><div class="flex items-center gap-2 text-[10px] text-slate-400"><span class="${loc.weather.color} font-bold"><i class="fa-solid ${loc.weather.icon}"></i> ${loc.weather.temp}</span><span>•</span><span>${loc.district}</span></div></div></div>`;
                card.onclick = () => { map.flyTo([loc.lat, loc.lng], 16, {duration:1.2}); setTimeout(()=>m.openPopup(), 1200); };
                list.appendChild(card);
            });
        }
        async function checkIn(name) {
            map.closePopup();
            try {
                const res = await fetch('/api/checkin', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({locationName:name})});
                const data = await res.json();
                document.getElementById('user-points').innerText = data.total_points;
                document.getElementById('modal-points').innerText = data.earned;
                document.getElementById('modal-text').innerText = `成功探索 ${name}`;
                if(data.new_badge){ document.getElementById('badge-notification').classList.remove('hidden'); document.getElementById('badge-name').innerText = data.new_badge; updateLocalBadges(data.total_points); } else { document.getElementById('badge-notification').classList.add('hidden'); }
                document.getElementById('modal').classList.remove('hidden');
                new Audio('https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3').play().catch(()=>{});
                setTimeout(()=>{document.getElementById('modal').classList.remove('opacity-0'); document.querySelector('#modal div').classList.remove('scale-90','scale-100'); document.querySelector('#modal div').classList.add('scale-100');}, 10);
                document.getElementById('bell-icon').classList.add('bell-animation'); setTimeout(()=>document.getElementById('bell-icon').classList.remove('bell-animation'), 1000);
            } catch(e){}
        }
        function updateLocalBadges(p) { if(p>=100) document.getElementById('badge-explorer').classList.remove('opacity-40'); if(p>=300) document.getElementById('badge-data').classList.remove('opacity-40'); }
        function ringBell() { 
            const b=document.querySelector('#nav-bell i'); b.parentElement.classList.add('scale-90'); setTimeout(()=>b.parentElement.classList.remove('scale-90'),150);
            new Audio('https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3').play().catch(()=>{});
            b.parentElement.classList.add('bell-animation'); setTimeout(()=>b.parentElement.classList.remove('bell-animation'), 1000);
        }
        function closeModal() { document.getElementById('modal').classList.add('opacity-0'); document.querySelector('#modal div').classList.remove('scale-100'); document.querySelector('#modal div').classList.add('scale-90'); setTimeout(()=>document.getElementById('modal').classList.add('hidden'),300); }
        function showGuide() { document.getElementById('guide-modal').classList.remove('hidden'); }
        function showBadges() { document.getElementById('badge-modal').classList.remove('hidden'); }
        function hideModal(id, e) { if(e.target.id===id) document.getElementById(id).classList.add('hidden'); }
        window.onload = initMap;
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)