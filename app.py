import json, random, os, datetime, math
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

# ==========================================
# 1. 模擬 OpenData 數據庫 (對應簡報需求)
# ==========================================
# 數據定義：
# - pm25: 數值低=放鬆值高 (空氣好)
# - green: 密度高=療癒值高
# - art: 數量多=活力值高
# - sport: 密度高=能量值高
# - noise: 數值低=寧靜值高 (整合進放鬆)

LOCATIONS = [
    # --- 藝文特區 (Vitality) ---
    {"id":1, "name":"華山1914文創園區", "district":"中正區", "lat":25.0441, "lng":121.5293, "tag":"藝文", "desc":"文青必訪的展演基地，匯集設計展、快閃店與草地野餐。", "data":{"pm25":30,"noise":65,"green":30,"art":100,"sport":10}},
    {"id":2, "name":"松山文創園區", "district":"信義區", "lat":25.0439, "lng":121.5606, "tag":"藝文", "desc":"菸廠古蹟活化，結合誠品書店與設計展演的文化園區。", "data":{"pm25":22,"noise":55,"green":50,"art":95,"sport":20}},
    {"id":3, "name":"中正紀念堂", "district":"中正區", "lat":25.0348, "lng":121.5217, "tag":"藝文", "desc":"藍白建築與廣闊廣場，國際級展覽與藝文活動的首選展場。", "data":{"pm25":25,"noise":55,"green":60,"art":98,"sport":40}},
    {"id":4, "name":"臺北流行音樂中心", "district":"南港區", "lat":25.0519, "lng":121.5985, "tag":"藝文", "desc":"仿山巒起伏的指標建築，流行音樂展演與文化的最高殿堂。", "data":{"pm25":30,"noise":60,"green":40,"art":95,"sport":20}},
    {"id":5, "name":"臺北表演藝術中心", "district":"士林區", "lat":25.0847, "lng":121.5255, "tag":"藝文", "desc":"CNN評選全球最具變革性建築，國際級表演藝術場館。", "data":{"pm25":35,"noise":65,"green":10,"art":100,"sport":0}},
    {"id":6, "name":"寶藏巖國際藝術村", "district":"中正區", "lat":25.0105, "lng":121.5323, "tag":"藝文", "desc":"依山而建的歷史聚落，共生藝術與獨特地景的探索秘境。", "data":{"pm25":15,"noise":30,"green":80,"art":95,"sport":30}},
    {"id":7, "name":"西門紅樓", "district":"萬華區", "lat":25.0423, "lng":121.5061, "tag":"藝文", "desc":"百年紅磚樓中的創意市集，年輕活力的發源地。", "data":{"pm25":40,"noise":80,"green":5,"art":90,"sport":5}},
    {"id":8, "name":"忠泰美術館", "district":"大安區", "lat":25.0435, "lng":121.5372, "tag":"藝文", "desc":"專注於「未來」與「城市」議題的精品美術館展場。", "data":{"pm25":20,"noise":50,"green":20,"art":95,"sport":0}},
    {"id":9, "name":"台北當代藝術館", "district":"大同區", "lat":25.0504, "lng":121.5186, "tag":"藝文", "desc":"日治時期小學校舍改建，前衛當代藝術的指標性展場。", "data":{"pm25":30,"noise":55,"green":10,"art":100,"sport":0}},
    {"id":10, "name":"國立故宮博物院", "district":"士林區", "lat":25.1024, "lng":121.5485, "tag":"藝文", "desc":"世界級中華文化寶庫，歷史迷與外國遊客必訪展場。", "data":{"pm25":12,"noise":35,"green":80,"art":100,"sport":10}},
    
    # --- 療癒綠洲 (Heal) ---
    {"id":20, "name":"大安森林公園", "district":"大安區", "lat":25.0300, "lng":121.5358, "tag":"療癒", "desc":"城市之肺，適合野餐、慢跑與欣賞露天音樂表演。", "data":{"pm25":18,"noise":45,"green":100,"art":40,"sport":60}},
    {"id":21, "name":"陽明山花鐘", "district":"北投區", "lat":25.1550, "lng":121.5430, "tag":"療癒", "desc":"陽明山地標，四季花卉綻放，遊客必訪的打卡點。", "data":{"pm25":5,"noise":25,"green":100,"art":20,"sport":30}},
    {"id":22, "name":"擎天崗大草原", "district":"士林區", "lat":25.1667, "lng":121.5760, "tag":"療癒", "desc":"一望無際的綠草地與悠閒的水牛，野餐與踏青聖地。", "data":{"pm25":2,"noise":20,"green":100,"art":0,"sport":60}},
    {"id":23, "name":"北投圖書館", "district":"北投區", "lat":25.1363, "lng":121.5063, "tag":"療癒", "desc":"全球最美公立圖書館之一，與公園生態共生的木造綠建築。", "data":{"pm25":8,"noise":30,"green":95,"art":70,"sport":10}},
    {"id":24, "name":"法鼓山農禪寺", "district":"北投區", "lat":25.1257, "lng":121.4984, "tag":"療癒", "desc":"水月道場的空靈倒影，IG上最熱門的寧靜心靈場所。", "data":{"pm25":10,"noise":20,"green":60,"art":80,"sport":5}},
    {"id":25, "name":"大湖公園", "district":"內湖區", "lat":25.0838, "lng":121.5936, "tag":"療癒", "desc":"錦帶橋與落羽松的絕美倒影，野餐與釣魚勝地。", "data":{"pm25":15,"noise":40,"green":90,"art":20,"sport":50}},
    {"id":26, "name":"象山六巨石", "district":"信義區", "lat":25.0267, "lng":121.5746, "tag":"療癒", "desc":"社群媒體上最熱門的台北夜景拍攝點，揮灑汗水的絕佳步道。", "data":{"pm25":10,"noise":30,"green":90,"art":10,"sport":90}},
    {"id":27, "name":"臺北植物園", "district":"中正區", "lat":25.0333, "lng":121.5096, "tag":"療癒", "desc":"城市中的綠色圖書館，荷花池畔的寧靜時光。", "data":{"pm25":15,"noise":40,"green":95,"art":30,"sport":20}},
    {"id":28, "name":"士林官邸", "district":"士林區", "lat":25.0935, "lng":121.5300, "tag":"療癒", "desc":"中西合璧的庭園造景，四季皆有主題花展。", "data":{"pm25":15,"noise":45,"green":95,"art":60,"sport":20}},
    {"id":29, "name":"花博公園新生園區", "district":"中山區", "lat":25.0711, "lng":121.5317, "tag":"療癒", "desc":"擁有迷宮花園與玫瑰園，飛機從頭頂呼嘯而過的震撼。", "data":{"pm25":20,"noise":60,"green":85,"art":30,"sport":60}},

    # --- 運動熱點 (Sport) ---
    {"id":40, "name":"台北田徑場", "district":"松山區", "lat":25.0489, "lng":121.5517, "tag":"運動", "desc":"國際級標準運動場，市民揮灑汗水與能量的中心。", "data":{"pm25":30,"noise":70,"green":20,"art":10,"sport":95}},
    {"id":41, "name":"大安運動中心", "district":"大安區", "lat":25.0204, "lng":121.5451, "tag":"運動", "desc":"設施完善的現代化運動場館，提供游泳、健身等多樣課程。", "data":{"pm25":15,"noise":60,"green":10,"art":5,"sport":90}},
    {"id":42, "name":"中正運動中心", "district":"中正區", "lat":25.0355, "lng":121.5190, "tag":"運動", "desc":"交通便利的運動中心，擁有優質的射箭場與體適能中心。", "data":{"pm25":20,"noise":65,"green":5,"art":5,"sport":90}},
    {"id":43, "name":"內湖運動中心", "district":"內湖區", "lat":25.0718, "lng":121.5750, "tag":"運動", "desc":"擁有國際標準攀岩場，吸引許多極限運動愛好者。", "data":{"pm25":20,"noise":55,"green":20,"art":5,"sport":95}},
    {"id":44, "name":"原岩攀岩館 (萬華店)", "district":"萬華區", "lat":25.0330, "lng":121.4980, "tag":"運動", "desc":"專業抱石場館，路線豐富，適合新手到高手的挑戰。", "data":{"pm25":20,"noise":50,"green":5,"art":20,"sport":100}},
    {"id":45, "name":"Double8 岩究所", "district":"大同區", "lat":25.0600, "lng":121.5100, "tag":"運動", "desc":"隱身迪化街老宅內的攀岩場，結合古蹟與極限運動。", "data":{"pm25":25,"noise":45,"green":10,"art":70,"sport":95}},
    {"id":46, "name":"台北小巨蛋冰上樂園", "district":"松山區", "lat":25.0510, "lng":121.5500, "tag":"運動", "desc":"全台唯一符合國際標準的溜冰場，四季皆可享受滑冰樂趣。", "data":{"pm25":15,"noise":55,"green":0,"art":20,"sport":95}},
    {"id":47, "name":"Roller186滑輪場", "district":"松山區", "lat":25.0512, "lng":121.5502, "tag":"運動", "desc":"復古美式風格的滑輪場，好玩又好拍的約會聖地。", "data":{"pm25":15,"noise":65,"green":0,"art":50,"sport":85}},
    {"id":48, "name":"大佳河濱公園", "district":"中山區", "lat":25.0730, "lng":121.5450, "tag":"運動", "desc":"寬廣的河岸腹地，適合跑步、騎自行車與親子放電。", "data":{"pm25":15,"noise":45,"green":95,"art":10,"sport":80}},
    {"id":49, "name":"Space Cycle 明曜旗艦館", "district":"大安區", "lat":25.0410, "lng":121.5520, "tag":"運動", "desc":"結合音樂與飛輪的時尚運動空間，充滿活力的運動體驗。", "data":{"pm25":10,"noise":60,"green":0,"art":40,"sport":90}},
    {"id":50, "name":"E7Play 三重店", "district":"三重區", "lat":25.0680, "lng":121.5000, "tag":"運動", "desc":"一票玩到底的複合式娛樂場館，保齡球、撞球、飛鏢應有盡有。", "data":{"pm25":25,"noise":75,"green":0,"art":5,"sport":85}},

    # --- 放鬆角落 (Relax) ---
    {"id":60, "name":"Simple Kaffa Sola", "district":"信義區", "lat":25.0339, "lng":121.5644, "tag":"放鬆", "desc":"位於台北101的88樓，冠軍咖啡與雲端美景的極致享受。", "data":{"pm25":5,"noise":20,"green":10,"art":90,"sport":0}},
    {"id":61, "name":"CAMA 豆留森林", "district":"士林區", "lat":25.1332, "lng":121.5567, "tag":"放鬆", "desc":"陽明山上的昭和風老宅咖啡，竹林環繞的秘境。", "data":{"pm25":5,"noise":30,"green":95,"art":85,"sport":10}},
    {"id":62, "name":"Sidoli Radio 小島裡", "district":"大同區", "lat":25.0553, "lng":121.5126, "tag":"放鬆", "desc":"結合錄音室與咖啡廳的複合空間，用聲音記錄大稻埕故事。", "data":{"pm25":25,"noise":30,"green":10,"art":95,"sport":0}},
    {"id":63, "name":"ACME｜TFAM", "district":"中山區", "lat":25.0725, "lng":121.5247, "tag":"放鬆", "desc":"北美館旁的純白玻璃屋，藝術與早午餐的完美結合。", "data":{"pm25":20,"noise":40,"green":60,"art":90,"sport":10}},
    {"id":64, "name":"Tokyobike Taiwan", "district":"萬華區", "lat":25.0355, "lng":121.5021, "tag":"放鬆", "desc":"位於新富町文化市場內的單車主題咖啡，日式簡約風格。", "data":{"pm25":30,"noise":45,"green":20,"art":85,"sport":40}},
    {"id":65, "name":"The Hippo Coffee Bar", "district":"信義區", "lat":25.0410, "lng":121.5780, "tag":"放鬆", "desc":"信義區巷弄內的河馬主題咖啡，清新可愛的療癒空間。", "data":{"pm25":20,"noise":35,"green":20,"art":60,"sport":0}},
    {"id":66, "name":"Woolloomooloo", "district":"信義區", "lat":25.0329, "lng":121.5564, "tag":"放鬆", "desc":"工業風澳式咖啡餐酒館，都市人下班後的充電站。", "data":{"pm25":25,"noise":60,"green":10,"art":65,"sport":5}},
    {"id":67, "name":"Hoto Cafe", "district":"中山區", "lat":25.0530, "lng":121.5250, "tag":"放鬆", "desc":"巷弄內的溫馨日式咖啡館，手工甜點深受喜愛。", "data":{"pm25":30,"noise":40,"green":30,"art":60,"sport":0}},
    {"id":68, "name":"山上聊", "district":"士林區", "lat":25.1400, "lng":121.5600, "tag":"療癒", "desc":"陽明山上的景觀咖啡，坐擁百萬夜景與寧靜氛圍。", "data":{"pm25":5,"noise":20,"green":90,"art":50,"sport":10}},
    {"id":69, "name":"別處咖啡 Away cafe", "district":"中正區", "lat":25.0200, "lng":121.5250, "tag":"放鬆", "desc":"羅斯福路巷弄內的老宅咖啡，提供家常料理與手沖咖啡。", "data":{"pm25":25,"noise":40,"green":15,"art":75,"sport":0}}
]

# 補足剩餘地點 (模擬)
districts = {"大安區":(25.03,121.54),"信義區":(25.03,121.57),"松山區":(25.05,121.55),"中山區":(25.06,121.53),"中正區":(25.03,121.51),"萬華區":(25.03,121.49),"士林區":(25.10,121.52),"北投區":(25.12,121.50),"內湖區":(25.08,121.59),"南港區":(25.05,121.60),"大同區":(25.06,121.51),"文山區":(24.99,121.56)}
prefixes = ["幸福","快樂","寧靜","活力","陽光","微風","城市","轉角","巷弄","老樹"]
suffixes_park = ["公園","綠地","廣場","散步道"]
suffixes_cafe = ["咖啡","小館","食堂","茶屋"]

for i in range(len(LOCATIONS)+1, 201):
    dist_name, coords = random.choice(list(districts.items()))
    is_park = random.choice([True, False])
    name = random.choice(prefixes) + (random.choice(suffixes_park) if is_park else random.choice(suffixes_cafe))
    lat = coords[0] + random.uniform(-0.02, 0.02)
    lng = coords[1] + random.uniform(-0.02, 0.02)
    tag = "療癒" if is_park else "放鬆"
    desc = "位於城市角落的隱藏版好去處，適合想要暫時遠離喧囂的你，享受片刻的寧靜時光。" if is_park else "溫馨舒適的小角落，提供美味的餐點與飲品，是放鬆身心的絕佳選擇。"
    data = {"pm25":random.randint(10,40), "noise":random.randint(30,60), "green":random.randint(50,90) if is_park else random.randint(10,40), "art":random.randint(10,50), "sport":random.randint(20,60)}
    LOCATIONS.append({"id":i, "name":name, "district":dist_name, "lat":lat, "lng":lng, "tag":tag, "desc":desc, "data":data})

WEATHER_TYPES = [{"icon":"fa-sun","text":"晴朗","color":"text-orange-500","temp":"28°C"},{"icon":"fa-cloud-sun","text":"多雲","color":"text-yellow-500","temp":"24°C"},{"icon":"fa-wind","text":"微風","color":"text-blue-400","temp":"22°C"}]
user_points = 0
user_steps = 0
REVIEWS = {}

def calculate_happiness_indices(d):
    pm25=max(0,100-d['pm25']*1.5); noise=max(0,100-d['noise']*1.2)
    relax=(pm25+noise)/2; heal=d['green']; vitality=min(100,(d['art']*0.9+d['noise']*0.1)); energy=d['sport']
    return {"relaxation":round(relax,1), "healing":round(heal,1), "vitality":round(vitality,1), "energy":round(energy,1)}

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/api/locations', methods=['GET'])
def get_locations():
    mood = request.args.get('mood','all')
    res = []
    for loc in LOCATIONS:
        idx = calculate_happiness_indices(loc['data'])
        scores = {'vitality':idx['vitality'], 'healing':idx['healing'], 'energy':idx['energy'], 'relaxation':idx['relaxation']}
        dom = max(scores, key=scores.get)
        ms, tag, color = 0, "", "#3b82f6"
        
        if mood=='relax': ms=idx['relaxation']; tag="☁️ 極致放鬆"; color="#f97316"
        elif mood=='heal': ms=idx['healing']; tag="🌳 自然療癒"; color="#10b981"
        elif mood=='vitality': ms=idx['vitality']; tag="🎨 藝文活力"; color="#a855f7"
        elif mood=='sport': ms=idx['energy']; tag="🏃‍♂️ 揮灑汗水"; color="#ef4444"
        else:
            ms=sum(scores.values())/4
            if dom=='vitality': tag="🎨 藝文特區"; color="#a855f7"
            elif dom=='healing': tag="🌳 療癒綠洲"; color="#10b981"
            elif dom=='energy': tag="🏃‍♂️ 運動熱點"; color="#ef4444"
            else: tag="☁️ 放鬆角落"; color="#f97316"
            
        loc_reviews = REVIEWS.get(str(loc['id']), [])
        avg_rating = sum(r['rating'] for r in loc_reviews) / len(loc_reviews) if loc_reviews else 0
        
        l=loc.copy()
        l.update({'indices':idx, 'match_score':round(ms,1), 'tag':tag, 'weather':random.choice(WEATHER_TYPES), 'marker_color':color, 'avg_rating': round(avg_rating, 1), 'review_count': len(loc_reviews)})
        res.append(l)

    if mood=='all': random.shuffle(res)
    res.sort(key=lambda x:x['match_score'], reverse=True)
    return jsonify(res[:50]) # Return top 50 to avoid lag

@app.route('/api/checkin', methods=['POST'])
def checkin():
    global user_points, user_steps
    user_points += random.randint(30,80)
    user_steps += random.randint(1000, 2000)
    new_badge = None
    if user_points >= 500: new_badge = "臺北幸福大使"
    elif user_points >= 300: new_badge = "數據大師"
    elif user_points >= 100: new_badge = "城市探索者"
    return jsonify({"status":"success", "message":f"抵達「{request.json.get('locationName')}」", "earned":50, "total_points":user_points, "total_steps":user_steps, "new_badge":new_badge})

@app.route('/api/reviews/<loc_id>', methods=['GET'])
def get_reviews(loc_id): return jsonify(REVIEWS.get(str(loc_id), []))

@app.route('/api/review', methods=['POST'])
def submit_review():
    data = request.json; loc_id = str(data.get('location_id'))
    review = {'user': '訪客', 'rating': int(data.get('rating')), 'comment': data.get('comment'), 'date': datetime.datetime.now().strftime("%Y-%m-%d")}
    if loc_id not in REVIEWS: REVIEWS[loc_id] = []
    REVIEWS[loc_id].insert(0, review)
    return jsonify({'status': 'success', 'review': review})

HTML_TEMPLATE = """
<!DOCTYPE html><html lang="zh-TW"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"><title>臺北市幸福鈴</title>
<script src="https://cdn.tailwindcss.com"></script><link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"/>
<style>
    body{font-family:sans-serif;background:#f8fafc;overflow:hidden} #map{height:100%;width:100%;z-index:1} 
    .mood-btn{transition:all 0.2s} 
    #btn-relax.active { background-color: #f97316 !important; border-color: #f97316 !important; color: white !important; }
    #btn-heal.active { background-color: #10b981 !important; border-color: #10b981 !important; color: white !important; }
    #btn-vitality.active { background-color: #a855f7 !important; border-color: #a855f7 !important; color: white !important; }
    #btn-sport.active { background-color: #ef4444 !important; border-color: #ef4444 !important; color: white !important; }
    .mood-btn.active i,.mood-btn.active span{color:white!important} 
    .no-scrollbar::-webkit-scrollbar{display:none} 
    @keyframes ring{0%,100%{transform:rotate(0)}10%,90%{transform:rotate(30deg)}30%,70%{transform:rotate(-30deg)}50%{transform:rotate(30deg)}} .bell-animation{animation:ring 1s ease-in-out} 
    .user-loc {animation: pulse-ring 2s infinite;} 
    @keyframes pulse-ring {0% {box-shadow: 0 0 0 0 rgba(37, 99, 235, 0.7);} 70% {box-shadow: 0 0 0 10px rgba(37, 99, 235, 0);} 100% {box-shadow: 0 0 0 0 rgba(37, 99, 235, 0);}}
    .rating-star { cursor: pointer; color: #d1d5db; } .rating-star.active { color: #f59e0b; }
</style></head>
<body class="flex flex-col h-screen text-slate-800">
<nav class="bg-white shadow-sm z-50 px-4 py-3 flex justify-between items-center shrink-0 border-b border-gray-100">
<div class="flex items-center gap-2"><div id="nav-bell" onclick="ringBell()" class="bg-blue-500 text-white p-2 rounded-xl shadow-sm cursor-pointer active:scale-95"><i class="fa-solid fa-bell text-sm"></i></div><div><h1 class="text-lg font-bold">幸福地圖</h1><div class="text-[10px] text-slate-500">Taipei Happiness Bell</div></div></div>
<div class="flex items-center gap-3"><div class="hidden md:flex items-center gap-1 text-xs text-slate-500 font-bold"><i class="fa-solid fa-shoe-prints"></i> <span id="user-steps">0</span> 步</div><div onclick="showBadges()" class="cursor-pointer bg-slate-100 p-2 rounded-full hover:bg-slate-200"><i class="fa-solid fa-medal text-slate-600"></i></div><div class="flex items-center gap-1.5 bg-amber-50 border border-amber-100 px-3 py-1.5 rounded-full"><i class="fa-solid fa-star text-amber-500 text-xs"></i><span id="user-points" class="font-bold text-amber-700 text-sm">0</span></div></div></nav>
<div class="flex flex-1 flex-col md:flex-row overflow-hidden relative">
<div id="map-container" class="absolute inset-0 md:relative md:w-2/3 md:order-2 z-0 transition-all duration-300 ease-in-out"><div id="map" class="h-full w-full"></div>
<button onclick="toggleSidebar()" class="hidden md:flex absolute top-4 left-4 z-[500] bg-white text-slate-500 hover:text-blue-600 p-2 rounded shadow-md w-10 h-10 items-center justify-center transition-all"><i id="sidebar-toggle-icon" class="fa-solid fa-chevron-left"></i></button>
<button onclick="getLocation()" class="absolute top-4 left-4 md:top-16 z-[500] bg-white text-slate-500 hover:text-blue-600 p-2 rounded shadow-md w-10 h-10 items-center justify-center transition-all active:scale-95" title="我的位置"><i class="fa-solid fa-crosshairs"></i></button>
<button onclick="showGuide()" class="absolute top-20 right-4 md:top-auto md:bottom-8 md:right-4 z-[500] bg-white text-slate-600 p-0 rounded shadow-md w-10 h-10 flex items-center justify-center transition-all active:scale-95 hover:text-blue-600"><i class="fa-solid fa-book-open text-lg"></i></button>
<div class="hidden md:block absolute bottom-8 left-8 bg-white/95 p-4 rounded-xl shadow-xl z-[500] text-xs backdrop-blur-sm border border-gray-100"><div class="font-bold mb-3 text-slate-700">地圖顏色說明</div><div class="space-y-2"><div class="flex items-center gap-2"><div class="w-3 h-3 bg-purple-500 rounded-full"></div><span>藝文特區</span></div><div class="flex items-center gap-2"><div class="w-3 h-3 bg-green-500 rounded-full"></div><span>療癒綠洲</span></div><div class="flex items-center gap-2"><div class="w-3 h-3 bg-red-500 rounded-full"></div><span>運動熱點</span></div><div class="flex items-center gap-2"><div class="w-3 h-3 bg-orange-500 rounded-full"></div><span>放鬆角落</span></div></div></div></div>
<div id="sidebar-panel" class="absolute bottom-0 w-full md:relative md:w-1/3 md:order-1 md:h-full z-20 flex flex-col pointer-events-none md:pointer-events-auto transition-all duration-300 ease-in-out origin-left"><div class="bg-white rounded-t-3xl md:rounded-none shadow-xl flex flex-col h-[55vh] md:h-full pointer-events-auto">
<div class="w-full flex justify-center pt-3 pb-1 md:hidden"><div class="w-12 h-1.5 bg-gray-200 rounded-full cursor-grab active:cursor-grabbing" onclick="toggleSidebarMobile()"></div></div>
<div class="p-5 border-b border-gray-100 bg-white shrink-0"><div class="grid grid-cols-4 gap-3">
<button id="btn-relax" onclick="changeMood('relax')" class="mood-btn border border-slate-100 bg-slate-50 text-slate-600 p-2.5 rounded-2xl flex flex-col items-center gap-1.5"><i class="fa-solid fa-wind text-xl text-orange-400"></i><span class="text-xs font-bold">放鬆</span></button>
<button id="btn-heal" onclick="changeMood('heal')" class="mood-btn border border-slate-100 bg-slate-50 text-slate-600 p-2.5 rounded-2xl flex flex-col items-center gap-1.5"><i class="fa-solid fa-tree text-xl text-green-500"></i><span class="text-xs font-bold">療癒</span></button>
<button id="btn-vitality" onclick="changeMood('vitality')" class="mood-btn border border-slate-100 bg-slate-50 text-slate-600 p-2.5 rounded-2xl flex flex-col items-center gap-1.5"><i class="fa-solid fa-palette text-xl text-purple-500"></i><span class="text-xs font-bold">藝文</span></button>
<button id="btn-sport" onclick="changeMood('sport')" class="mood-btn border border-slate-100 bg-slate-50 text-slate-600 p-2.5 rounded-2xl flex flex-col items-center gap-1.5"><i class="fa-solid fa-person-running text-xl text-red-500"></i><span class="text-xs font-bold">運動</span></button>
</div></div><div class="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50 no-scrollbar" id="location-list"></div></div></div></div>

<div id="guide-modal" class="hidden fixed inset-0 bg-black/50 z-[2000] flex items-center justify-center p-4 backdrop-blur-sm" onclick="hideModal('guide-modal',event)"><div class="bg-white w-full max-w-md rounded-3xl p-6 shadow-2xl relative overflow-hidden" onclick="event.stopPropagation()"><div class="absolute top-0 left-0 w-full h-24 bg-gradient-to-r from-blue-500 to-blue-600 -z-10"></div><div class="flex justify-between items-center mb-6 text-white relative z-10"><h3 class="text-xl font-bold flex items-center gap-2"><i class="fa-solid fa-book-open"></i> 使用指南</h3><button onclick="document.getElementById('guide-modal').classList.add('hidden')"><i class="fa-solid fa-xmark"></i></button></div><div class="space-y-6 max-h-[60vh] overflow-y-auto pr-2 no-scrollbar">
<div><h4 class="font-bold text-slate-800 mb-2 flex items-center gap-2"><i class="fa-solid fa-chart-pie text-blue-500"></i> 幸福契合度 (左側數字)</h4><p class="text-sm text-slate-600 bg-blue-50 p-3 rounded-xl">卡片左側的圓形數字代表該地點與您當前選擇心情的<b>「契合百分比」</b> (0-100分)。<br>分數越高，代表該地點的環境數據 (如空氣、綠地、噪音) 越符合您的需求。</p></div>
<div><h4 class="font-bold text-slate-800 mb-2 flex items-center gap-2"><i class="fa-solid fa-palette text-purple-500"></i> 顏色代表</h4><div class="grid grid-cols-2 gap-3 text-sm"><div class="flex items-center gap-2 bg-purple-50 p-2 rounded-lg"><div class="w-3 h-3 bg-purple-500 rounded-full"></div>藝文特區</div><div class="flex items-center gap-2 bg-green-50 p-2 rounded-lg"><div class="w-3 h-3 bg-green-500 rounded-full"></div>療癒綠洲</div><div class="flex items-center gap-2 bg-red-50 p-2 rounded-lg"><div class="w-3 h-3 bg-red-500 rounded-full"></div>運動熱點</div><div class="flex items-center gap-2 bg-orange-50 p-2 rounded-lg"><div class="w-3 h-3 bg-orange-500 rounded-full"></div>放鬆角落</div></div></div>
<div><h4 class="font-bold text-slate-800 mb-2 flex items-center gap-2"><i class="fa-solid fa-layer-group text-orange-500"></i> 更多功能</h4><ul class="text-sm text-slate-600 bg-orange-50 p-3 rounded-xl space-y-1"><li><i class="fa-solid fa-bus text-yellow-500"></i> <b>公車動態</b>：點擊地點卡片上的黃色按鈕，查詢附近公車。</li><li><i class="fa-solid fa-comment-dots text-orange-500"></i> <b>評論評分</b>：點擊橘色按鈕，查看或撰寫地點評論。</li><li><i class="fa-solid fa-bell text-blue-500"></i> <b>幸福鈴</b>：點擊左上角鈴鐺，獲得祝福音效。</li></ul></div></div><button onclick="document.getElementById('guide-modal').classList.add('hidden')" class="mt-6 w-full py-3 bg-slate-100 rounded-xl font-bold text-slate-600">我瞭解了</button></div></div>

<div id="modal" class="hidden fixed inset-0 bg-slate-900/60 z-[2000] flex items-center justify-center p-6 backdrop-blur-sm transition-opacity opacity-0"><div class="bg-white rounded-3xl shadow-2xl w-full max-w-xs p-8 text-center transform scale-90 transition-transform relative overflow-hidden"><div class="absolute top-0 left-0 w-full h-32 bg-gradient-to-b from-yellow-50 to-white -z-10"></div><div class="relative mb-6"><div class="w-24 h-24 bg-white rounded-full flex items-center justify-center mx-auto shadow-lg border-4 border-yellow-50"><i id="bell-icon" class="fa-solid fa-bell text-5xl text-yellow-500"></i></div><div class="absolute -bottom-2 left-1/2 -translate-x-1/2 bg-yellow-500 text-white text-[10px] px-2 py-0.5 rounded-full font-bold">TASK COMPLETED</div></div><h3 class="text-2xl font-bold text-slate-800 mb-1">任務達成！</h3><p id="modal-text" class="text-sm text-slate-500 mb-6">成功抵達探索地點</p><div class="bg-slate-50 rounded-2xl p-4 mb-6 border border-slate-100"><div class="flex justify-between items-center mb-2"><span class="text-slate-500 text-xs font-bold uppercase">獲得積分</span><span class="font-bold text-yellow-600 flex items-center gap-1 text-lg">+<span id="modal-points">0</span></span></div>
<div class="flex justify-between items-center mb-2"><span class="text-slate-500 text-xs font-bold uppercase">累積步數</span><span class="font-bold text-blue-600 flex items-center gap-1 text-lg"><i class="fa-solid fa-shoe-prints text-sm"></i> <span id="modal-steps">0</span></span></div>
<div id="badge-notification" class="hidden pt-2 border-t border-slate-200 mt-2"><div class="text-xs text-blue-500 font-bold mb-1">獲得新獎章！</div><div class="flex items-center justify-center gap-2 text-slate-700 font-bold"><i class="fa-solid fa-medal text-blue-500"></i> <span id="badge-name"></span></div></div></div><button onclick="closeModal()" class="w-full bg-slate-800 text-white py-3.5 rounded-xl font-bold shadow-lg active:scale-95 transition-all">收下獎勵</button></div></div>

<div id="badge-modal" class="hidden fixed inset-0 bg-black/50 z-[2000] flex items-center justify-center p-4 backdrop-blur-sm" onclick="hideModal('badge-modal', event)"><div class="bg-white w-full max-w-sm rounded-2xl p-6 shadow-2xl" onclick="event.stopPropagation()"><h3 class="font-bold text-lg mb-4 flex items-center gap-2"><i class="fa-solid fa-medal text-blue-500"></i> 我的成就獎章</h3><div class="grid grid-cols-3 gap-4 text-center"><div class="flex flex-col items-center gap-2 opacity-100"><div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center text-blue-500"><i class="fa-solid fa-user"></i></div><span class="text-xs font-bold text-slate-600">新手上路</span></div><div class="flex flex-col items-center gap-2 opacity-40 grayscale" id="badge-explorer"><div class="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center text-yellow-500"><i class="fa-solid fa-compass"></i></div><span class="text-xs font-bold text-slate-600">城市探索者</span></div><div class="flex flex-col items-center gap-2 opacity-40 grayscale" id="badge-data"><div class="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center text-purple-500"><i class="fa-solid fa-chart-pie"></i></div><span class="text-xs font-bold text-slate-600">數據大師</span></div></div>
<div class="mt-6 p-3 bg-gray-50 rounded-xl text-center"><div class="text-xs text-slate-500 font-bold uppercase mb-1">目前累積步數 (模擬)</div><div class="text-2xl font-bold text-blue-600"><i class="fa-solid fa-shoe-prints"></i> <span id="badge-steps">0</span></div></div>
<button onclick="document.getElementById('badge-modal').classList.add('hidden')" class="mt-4 w-full py-2 bg-gray-100 rounded-lg text-sm font-bold text-gray-600">關閉</button></div></div>

<div id="review-modal" class="hidden fixed inset-0 bg-black/50 z-[2000] flex items-center justify-center p-4 backdrop-blur-sm" onclick="hideModal('review-modal', event)"><div class="bg-white w-full max-w-md rounded-2xl p-6 shadow-2xl relative overflow-hidden" onclick="event.stopPropagation()"><h3 class="text-lg font-bold mb-4">評價與評論 - <span id="review-location-name"></span></h3><div class="mb-6 border-b pb-4"><div class="flex items-center justify-center gap-2 mb-3 text-2xl" id="star-input"><i class="fa-solid fa-star rating-star" data-value="1"></i><i class="fa-solid fa-star rating-star" data-value="2"></i><i class="fa-solid fa-star rating-star" data-value="3"></i><i class="fa-solid fa-star rating-star" data-value="4"></i><i class="fa-solid fa-star rating-star" data-value="5"></i></div><textarea id="review-comment" class="w-full border rounded-lg p-2 text-sm mb-3" rows="3" placeholder="寫下您的心得..."></textarea><button onclick="submitReview()" class="w-full bg-blue-500 text-white py-2 rounded-lg font-bold hover:bg-blue-600">提交評論</button></div><div class="max-h-[40vh] overflow-y-auto no-scrollbar space-y-3" id="reviews-list"></div><button onclick="document.getElementById('review-modal').classList.add('hidden')" class="mt-4 w-full py-2 bg-gray-100 rounded-lg text-sm font-bold text-gray-600">關閉</button></div></div>
<div id="bus-modal" class="hidden fixed inset-0 bg-black/50 z-[2000] flex items-center justify-center p-4 backdrop-blur-sm" onclick="hideModal('bus-modal', event)"><div class="bg-white w-full max-w-sm rounded-2xl p-5 shadow-2xl relative overflow-hidden" onclick="event.stopPropagation()"><div class="flex justify-between items-center mb-4 border-b pb-2"><h3 class="text-lg font-bold flex items-center gap-2"><i class="fa-solid fa-bus text-yellow-500"></i> 公車動態</h3><button onclick="document.getElementById('bus-modal').classList.add('hidden')" class="text-gray-400 hover:text-gray-600"><i class="fa-solid fa-xmark"></i></button></div><div class="space-y-2 max-h-[50vh] overflow-y-auto no-scrollbar" id="bus-list"></div><div class="mt-3 text-xs text-gray-400 text-center">資料來源：臺北市公共運輸處 (模擬)</div></div></div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
    let map, markers=[], currentLocations=[], isSidebarOpen=true, currentMood='all', userLocationMarker=null;
    let currentReviewLocationId = null; let selectedRating = 5;
    function initMap() {
        map = L.map('map', {zoomControl:false}).setView([25.06, 121.55], 12);
        L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {attribution:'OpenStreetMap', maxZoom:19}).addTo(map);
        fetchLocations('all'); getLocation();
        document.querySelectorAll('.rating-star').forEach(star => {
            star.addEventListener('click', function() { selectedRating = this.getAttribute('data-value'); updateStarDisplay(selectedRating); });
        });
    }
    function updateStarDisplay(rating) {
        document.querySelectorAll('.rating-star').forEach(star => { if (star.getAttribute('data-value') <= rating) star.classList.add('active'); else star.classList.remove('active'); });
    }
    function getLocation() { if (navigator.geolocation) navigator.geolocation.watchPosition(showPosition, (e)=>console.log(e), {enableHighAccuracy:true, maximumAge:2000, timeout:5000}); }
    function showPosition(position) {
        const lat = position.coords.latitude; const lng = position.coords.longitude;
        if(userLocationMarker) map.removeLayer(userLocationMarker);
        userLocationMarker = L.marker([lat, lng], { icon: L.divIcon({className:'user-loc', html:'<div class="w-4 h-4 bg-blue-600 rounded-full border-2 border-white shadow-lg pulse-ring"></div>', iconSize:[16,16]}) }).addTo(map);
        if (!window.hasCentered) { map.flyTo([lat, lng], 15); window.hasCentered = true; }
    }
    function toggleSidebar() {
        const sb=document.getElementById('sidebar-panel'), mc=document.getElementById('map-container'), icon=document.getElementById('sidebar-toggle-icon');
        isSidebarOpen = !isSidebarOpen;
        if(isSidebarOpen){ sb.classList.remove('md:w-0','hidden'); sb.classList.add('md:w-1/3'); mc.classList.remove('md:w-full'); mc.classList.add('md:w-2/3'); icon.classList.replace('fa-chevron-right','fa-chevron-left'); }
        else { sb.classList.remove('md:w-1/3'); sb.classList.add('md:w-0','hidden'); mc.classList.remove('md:w-2/3'); mc.classList.add('md:w-full'); icon.classList.replace('fa-chevron-left','fa-chevron-right'); }
        setTimeout(()=>map.invalidateSize(), 300);
    }
    function toggleSidebarMobile() {
        const sb = document.getElementById('sidebar-panel');
        if (sb.classList.contains('h-[55vh]')) { sb.classList.remove('h-[55vh]'); sb.classList.add('h-[80px]'); } else { sb.classList.remove('h-[80px]'); sb.classList.add('h-[55vh]'); }
    }
    function changeMood(m) { if(currentMood === m) currentMood = 'all'; else currentMood = m; fetchLocations(currentMood); }
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
            let starsHtml = ''; for(let i=1; i<=5; i++) starsHtml += `<i class="fa-solid fa-star ${i <= Math.round(loc.avg_rating) ? 'text-yellow-400' : 'text-gray-300'} text-xs"></i>`;
            const popup = `
                <div class="font-sans min-w-[240px] p-1">
                    <div class="flex justify-between items-center mb-2"><span class="text-xs font-bold text-slate-400 uppercase whitespace-nowrap">${loc.district}</span><span class="text-xs font-bold ${loc.weather.color} whitespace-nowrap"><i class="fa-solid ${loc.weather.icon}"></i> ${loc.weather.temp}</span></div>
                    <h3 class="font-bold text-lg text-slate-800 mb-1 leading-tight">${loc.name}</h3>
                    <div class="flex items-center gap-1 mb-2"><div class="flex">${starsHtml}</div><span class="text-xs text-gray-500">(${loc.review_count})</span></div>
                    <div class="text-xs text-slate-500 mb-3">${loc.tag}</div><div class="text-xs text-slate-600 mb-3 leading-relaxed line-clamp-2">${loc.desc}</div>
                    <div class="bg-slate-50 p-2 rounded-lg border border-slate-100 mb-3 space-y-1.5">
                        <div class="flex items-center text-[10px] text-slate-500"><span class="w-10 whitespace-nowrap">PM2.5</span><div class="flex-1 ml-2 h-1.5 bg-gray-200 rounded-full overflow-hidden"><div class="h-full bg-blue-400" style="width:${100-loc.data.pm25}%"></div></div></div>
                        <div class="flex items-center text-[10px] text-slate-500"><span class="w-10 whitespace-nowrap">綠覆率</span><div class="flex-1 ml-2 h-1.5 bg-gray-200 rounded-full overflow-hidden"><div class="h-full bg-green-500" style="width:${loc.data.green}%"></div></div></div>
                        <div class="flex items-center text-[10px] text-slate-500"><span class="w-10 whitespace-nowrap">藝文</span><div class="flex-1 ml-2 h-1.5 bg-gray-200 rounded-full overflow-hidden"><div class="h-full bg-purple-500" style="width:${loc.data.art}%"></div></div></div>
                    </div>
                    <div class="grid grid-cols-4 gap-1">
                        <a href="https://www.google.com/maps/dir/?api=1&destination=${loc.lat},${loc.lng}" target="_blank" class="col-span-2 text-center bg-white border border-slate-200 text-slate-600 text-xs py-2 rounded-lg font-bold hover:bg-slate-50 whitespace-nowrap">導航</a>
                        <button onclick="showBusInfo('${loc.name}')" class="bg-yellow-400 text-white text-xs py-2 rounded-lg font-bold hover:bg-yellow-500 shadow-sm"><i class="fa-solid fa-bus"></i></button>
                        <button onclick="openReviewModal(${loc.id}, '${loc.name}')" class="bg-orange-400 text-white text-xs py-2 rounded-lg font-bold hover:bg-orange-500 shadow-sm"><i class="fa-solid fa-comment-dots"></i></button>
                    </div>
                    <button onclick="checkIn('${loc.name}')" class="mt-2 w-full bg-blue-600 text-white text-xs py-2 rounded-lg font-bold hover:bg-blue-700 shadow-sm whitespace-nowrap">打卡任務</button>
                </div>`;
            const m = L.marker([loc.lat, loc.lng], {icon}).addTo(map).bindPopup(popup, {maxWidth:280, minWidth:240, autoPanPadding:[20,20]});
            markers.push(m);
            const card = document.createElement('div');
            card.className = "bg-white p-4 rounded-2xl shadow-sm border border-slate-100 cursor-pointer active:scale-[0.98] transition-all hover:shadow-md hover:border-blue-100";
            let tagBg="bg-slate-100 text-slate-500";
            if(loc.tag.includes("藝文")) tagBg="bg-purple-100 text-purple-600"; else if(loc.tag.includes("療癒")) tagBg="bg-green-100 text-green-600"; else if(loc.tag.includes("運動")) tagBg="bg-red-100 text-red-600"; else if(loc.tag.includes("放鬆")) tagBg="bg-orange-100 text-orange-600";
            card.innerHTML = `<div class="flex gap-4"><div class="flex-shrink-0 w-14 h-14 rounded-2xl flex flex-col items-center justify-center text-white font-bold shadow-sm" style="background-color:${loc.marker_color}"><span class="text-lg leading-none">${Math.round(loc.match_score)}</span><span class="text-[9px] opacity-80">分</span></div><div class="flex-1 min-w-0"><div class="flex justify-between items-start mb-1"><h4 class="font-bold text-slate-800 truncate text-base">${loc.name}</h4><span class="text-[10px] px-2 py-0.5 rounded-full ${tagBg}">${loc.tag}</span></div><p class="text-xs text-slate-500 line-clamp-2 mb-2">${loc.desc}</p><div class="flex items-center gap-2 text-[10px] text-slate-400"><span class="${loc.weather.color} font-bold"><i class="fa-solid ${loc.weather.icon}"></i> ${loc.weather.temp}</span><span>•</span><span>${loc.district}</span></div></div></div>`;
            card.onclick = () => { map.flyTo([loc.lat, loc.lng], 16, {duration:1.2}); setTimeout(()=>m.openPopup(), 1200); };
            list.appendChild(card);
        });
    }
    function showBusInfo(name) {
        const busList = document.getElementById('bus-list'); busList.innerHTML = '';
        const routes = ['204', '307', '262', '651', '212', '承德幹線', '信義幹線', '藍29']; const statuses = ['進站中', '約 3 分', '約 5 分', '約 8 分', '約 12 分'];
        const numRoutes = Math.floor(Math.random() * 3) + 2; 
        for(let i=0; i<numRoutes; i++) {
            const route = routes[Math.floor(Math.random() * routes.length)]; const status = statuses[Math.floor(Math.random() * statuses.length)];
            let color = 'text-gray-600'; if(status === '進站中') color = 'text-red-500 font-bold blink'; else if(status.includes('3') || status.includes('5')) color = 'text-yellow-600 font-bold';
            const item = document.createElement('div'); item.className = "flex justify-between items-center bg-gray-50 p-2 rounded border border-gray-100";
            item.innerHTML = `<div class="flex items-center gap-2"><span class="bg-blue-100 text-blue-800 text-xs font-bold px-2 py-1 rounded">${route}</span><span>往 台北車站</span></div><span class="text-xs ${color}">${status}</span>`;
            busList.appendChild(item);
        }
        document.getElementById('bus-modal').classList.remove('hidden');
    }
    async function checkIn(name) {
        map.closePopup();
        try {
            const res = await fetch('/api/checkin', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({locationName:name})});
            const data = await res.json();
            document.getElementById('user-points').innerText = data.total_points;
            if(document.getElementById('user-steps')) document.getElementById('user-steps').innerText = data.total_steps;
            document.getElementById('modal-points').innerText = data.earned;
            document.getElementById('modal-steps').innerText = data.total_steps;
            document.getElementById('badge-steps').innerText = data.total_steps;
            document.getElementById('modal-text').innerText = `成功探索 ${name}`;
            if(data.new_badge){ document.getElementById('badge-notification').classList.remove('hidden'); document.getElementById('badge-name').innerText = data.new_badge; updateLocalBadges(data.total_points); } else { document.getElementById('badge-notification').classList.add('hidden'); }
            document.getElementById('modal').classList.remove('hidden');
            new Audio('https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3').play().catch(()=>{});
            setTimeout(()=>{document.getElementById('modal').classList.remove('opacity-0'); document.querySelector('#modal div').classList.remove('scale-90','scale-100'); document.querySelector('#modal div').classList.add('scale-100');}, 10);
            document.getElementById('bell-icon').classList.add('bell-animation'); setTimeout(()=>document.getElementById('bell-icon').classList.remove('bell-animation'), 1000);
        } catch(e){}
    }
    async function openReviewModal(id, name) {
        currentReviewLocationId = id; document.getElementById('review-location-name').innerText = name; document.getElementById('review-modal').classList.remove('hidden'); document.getElementById('review-comment').value = ''; updateStarDisplay(5); selectedRating = 5;
        const res = await fetch(`/api/reviews/${id}`); const reviews = await res.json(); const list = document.getElementById('reviews-list'); list.innerHTML = '';
        if(reviews.length === 0) { list.innerHTML = '<div class="text-center text-gray-400 text-sm py-4">尚無評論，成為第一個評論的人吧！</div>'; } 
        else { reviews.forEach(r => { let stars = ''; for(let i=1; i<=5; i++) stars += `<i class="fa-solid fa-star ${i<=r.rating ? 'text-yellow-400' : 'text-gray-200'} text-xs"></i>`; const item = document.createElement('div'); item.className = "bg-slate-50 p-3 rounded-lg border border-slate-100"; item.innerHTML = `<div class="flex justify-between items-center mb-1"><span class="font-bold text-sm text-slate-700">${r.user}</span><span class="text-[10px] text-slate-400">${r.date}</span></div><div class="flex mb-1">${stars}</div><p class="text-xs text-slate-600">${r.comment}</p>`; list.appendChild(item); }); }
    }
    async function submitReview() {
        const comment = document.getElementById('review-comment').value; if(!comment) return alert('請輸入評論內容');
        await fetch('/api/review', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ location_id: currentReviewLocationId, rating: selectedRating, comment: comment }) });
        openReviewModal(currentReviewLocationId, document.getElementById('review-location-name').innerText); fetchLocations(currentMood);
    }
    function updateLocalBadges(p) { if(p>=100) document.getElementById('badge-explorer').classList.remove('opacity-40','grayscale'); if(p>=300) document.getElementById('badge-data').classList.remove('opacity-40','grayscale'); }
    function ringBell() { const b=document.querySelector('#nav-bell i'); b.parentElement.classList.add('scale-90'); setTimeout(()=>b.parentElement.classList.remove('scale-90'),150); new Audio('https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3').play().catch(()=>{}); b.parentElement.classList.add('bell-animation'); setTimeout(()=>b.parentElement.classList.remove('bell-animation'), 1000); }
    function closeModal() { document.getElementById('modal').classList.add('opacity-0'); document.querySelector('#modal div').classList.remove('scale-100'); document.querySelector('#modal div').classList.add('scale-90'); setTimeout(()=>document.getElementById('modal').classList.add('hidden'),300); }
    function showGuide() { document.getElementById('guide-modal').classList.remove('hidden'); }
    function showBadges() { document.getElementById('badge-modal').classList.remove('hidden'); }
    function hideModal(id, e) { if(e.target.id===id) document.getElementById(id).classList.add('hidden'); }
    window.onload = initMap;
</script></body></html>
"""

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
