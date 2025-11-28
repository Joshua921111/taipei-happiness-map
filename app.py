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
        
        .mood-btn { transition: all 0.2s; }
        .mood-btn.active { 
            background-color: #3b82f6 !important; 
            color: white !important; 
            border-color: #3b82f6 !important; 
            box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.5);
        }
        .mood-btn.active i, .mood-btn.active span { color: white !important; }

        .no-scrollbar::-webkit-scrollbar { display: none; }
        .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
        
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
            <div id="nav-bell" onclick="ringBell()" class="bg-gradient-to-br from-blue-500 to-blue-600 text-white p-2 rounded-xl shadow-sm cursor-pointer transition-transform active:scale-95">
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
        <div id="map-container" class="absolute inset-0 md:relative md:w-2/3 md:order-2 z-0 transition-all duration-300 ease-in-out">
            <div id="map" class="h-full w-full"></div>
            
            <button onclick="toggleSidebar()" class="hidden md:flex absolute top-1/2 left-0 transform -translate-y-1/2 z-[500] bg-white text-slate-500 hover:text-blue-600 p-2 rounded-r-lg shadow-md border border-l-0 border-gray-200 items-center justify-center transition-all hover:pl-3">
                <i id="sidebar-toggle-icon" class="fa-solid fa-chevron-left"></i>
            </button>

            <!-- 指標說明 -->
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

        <!-- 側邊欄 -->
        <div id="sidebar-panel" class="absolute bottom-0 w-full md:relative md:w-1/3 md:order-1 md:h-full z-20 flex flex-col pointer-events-none md:pointer-events-auto transition-all duration-300 ease-in-out origin-left">
            <div class="bg-white rounded-t-3xl md:rounded-none shadow-[0_-8px_30px_rgba(0,0,0,0.12)] flex flex-col h-[55vh] md:h-full pointer-events-auto">
                <div class="w-full flex justify-center pt-3 pb-1 md:hidden"><div class="w-12 h-1.5 bg-gray-200 rounded-full"></div></div>

                <div class="p-5 border-b border-gray-100 bg-white shrink-0">
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

                <div class="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50 no-scrollbar" id="location-list">
                    <div class="flex flex-col items-center justify-center h-full text-slate-400 gap-3">
                        <div class="bg-white p-4 rounded-full shadow-sm"><i class="fa-solid fa-map-location-dot text-3xl text-slate-300"></i></div>
                        <p class="text-sm font-medium">請選擇上方心情，開始探索</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal -->
    <div id="modal" class="hidden fixed inset-0 bg-slate-900/60 z-[2000] flex items-center justify-center p-6 backdrop-blur-sm transition-opacity opacity-0">
        <div class="bg-white rounded-3xl shadow-2xl w-full max-w-xs p-8 text-center transform scale-90 transition-transform relative overflow-hidden">
            <div class="absolute top-0 left-0 w-full h-32 bg-gradient-to-b from-yellow-50 to-white -z-10"></div>
            <div class="relative mb-6">
                <div class="w-24 h-24 bg-white rounded-full flex items-center justify-center mx-auto shadow-lg border-4 border-yellow-50">
                    <i id="bell-icon" class="fa-solid fa-bell text-5xl text-yellow-500"></i>
                </div>
                <div class="absolute -bottom-2 left-1/2 -translate-x-1/2 bg-yellow-500 text-white text-[10px] px-2 py-0.5 rounded-full font-bold">TASK COMPLETED</div>
            </div>
            <h3 class="text-2xl font-bold text-slate-800 mb-1">任務達成！</h3>
            <p id="modal-text" class="text-sm text-slate-500 mb-6">成功抵達探索地點</p>
            <div class="bg-slate-50 rounded-2xl p-4 mb-6 border border-slate-100">
                <div class="flex justify-between items-center mb-2">
                    <span class="text-slate-500 text-xs font-bold uppercase">獲得積分</span>
                    <span class="font-bold text-yellow-600 flex items-center gap-1 text-lg">+<span id="modal-points">0</span></span>
                </div>
                <div id="badge-notification" class="hidden pt-2 border-t border-slate-200 mt-2">
                    <div class="text-xs text-blue-500 font-bold mb-1">獲得新獎章！</div>
                    <div class="flex items-center justify-center gap-2 text-slate-700 font-bold">
                        <i class="fa-solid fa-medal text-blue-500"></i> <span id="badge-name"></span>
                    </div>
                </div>
            </div>
            <button onclick="closeModal()" class="w-full bg-slate-800 text-white py-3.5 rounded-xl font-bold shadow-lg shadow-slate-200 active:scale-95 transition-all">收下獎勵</button>
        </div>
    </div>

    <!-- Badge Modal -->
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
    
    <script>
        let map;
        let markers = [];
        let currentLocations = [];
        let isSidebarOpen = true;

        function initMap() {
            map = L.map('map', { zoomControl: false }).setView([25.06, 121.55], 12);
            L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
                attribution: 'OpenStreetMap', maxZoom: 19
            }).addTo(map);
            fetchLocations('all');
        }

        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar-panel');
            const mapContainer = document.getElementById('map-container');
            const icon = document.getElementById('sidebar-toggle-icon');
            isSidebarOpen = !isSidebarOpen;
            if (isSidebarOpen) {
                sidebar.classList.remove('md:w-0', 'md:overflow-hidden', 'hidden');
                sidebar.classList.add('md:w-1/3');
                mapContainer.classList.remove('md:w-full');
                mapContainer.classList.add('md:w-2/3');
                icon.classList.remove('fa-chevron-right'); icon.classList.add('fa-chevron-left');
            } else {
                sidebar.classList.remove('md:w-1/3');
                sidebar.classList.add('md:w-0', 'md:overflow-hidden', 'hidden'); 
                mapContainer.classList.remove('md:w-2/3');
                mapContainer.classList.add('md:w-full');
                icon.classList.remove('fa-chevron-left'); icon.classList.add('fa-chevron-right');
            }
            setTimeout(() => { map.invalidateSize(); }, 300);
        }

        function changeMood(mood) { fetchLocations(mood); }

        async function fetchLocations(mood) {
            document.querySelectorAll('.mood-btn').forEach(btn => btn.classList.remove('active'));
            const moodMap = {'relax':0, 'heal':1, 'vitality':2, 'sport':3};
            if(moodMap[mood] !== undefined) document.querySelectorAll('.mood-btn')[moodMap[mood]].classList.add('active');
            try {
                const res = await fetch(`/api/locations?mood=${mood}`);
                currentLocations = await res.json();
                updateUI();
            } catch(e) { console.error(e); }
        }

        function updateUI() {
            markers.forEach(m => map.removeLayer(m));
            markers = [];
            const list = document.getElementById('location-list');
            list.innerHTML = '';

            currentLocations.forEach((loc) => {
                const markerColor = loc.marker_color || getScoreColor(loc.match_score);
                const markerIcon = L.divIcon({
                    className: 'custom-div-icon',
                    html: `<div style="background-color:${markerColor}; width:16px; height:16px; border-radius:50%; border:3px solid white; box-shadow:0 3px 6px rgba(0,0,0,0.2);"></div>`,
                    iconSize: [16, 16], iconAnchor: [8, 8]
                });
                
                const popupContent = `
                    <div class="font-sans min-w-[220px] p-1">
                        <div class="flex justify-between items-center mb-2">
                            <span class="text-xs font-bold text-slate-400 uppercase tracking-wide whitespace-nowrap">${loc.district}</span>
                            <span class="text-xs font-bold ${loc.weather.color} whitespace-nowrap"><i class="fa-solid ${loc.weather.icon}"></i> ${loc.weather.temp}</span>
                        </div>
                        <h3 class="font-bold text-lg text-slate-800 mb-1 leading-tight">${loc.name}</h3>
                        <div class="text-xs text-slate-500 mb-3">${loc.tag}</div>
                        <div class="bg-slate-50 p-2 rounded-lg border border-slate-100 mb-3 space-y-1.5">
                            <div class="flex items-center text-[10px] text-slate-500"><span class="w-10 whitespace-nowrap">PM2.5</span><div class="flex-1 ml-2 h-1.5 bg-gray-200 rounded-full overflow-hidden"><div class="h-full bg-blue-400" style="width:${100 - loc.data.pm25}%"></div></div></div>
                            <div class="flex items-center text-[10px] text-slate-500"><span class="w-10 whitespace-nowrap">綠覆率</span><div class="flex-1 ml-2 h-1.5 bg-gray-200 rounded-full overflow-hidden"><div class="h-full bg-green-500" style="width:${loc.data.green}%"></div></div></div>
                            <div class="flex items-center text-[10px] text-slate-500"><span class="w-10 whitespace-nowrap">藝文</span><div class="flex-1 ml-2 h-1.5 bg-gray-200 rounded-full overflow-hidden"><div class="h-full bg-purple-500" style="width:${loc.data.art}%"></div></div></div>
                        </div>
                        <div class="grid grid-cols-2 gap-2">
                            <a href="https://www.google.com/maps/dir/?api=1&destination=${loc.lat},${loc.lng}" target="_blank" class="text-center bg-white border border-slate-200 text-slate-600 text-xs py-2 rounded-lg font-bold hover:bg-slate-50 whitespace-nowrap">導航</a>
                            <button onclick="checkIn('${loc.name}')" class="bg-blue-600 text-white text-xs py-2 rounded-lg font-bold hover:bg-blue-700 shadow-sm shadow-blue-200 whitespace-nowrap">打卡任務</button>
                        </div>
                    </div>
                `;

                const marker = L.marker([loc.lat, loc.lng], {icon: markerIcon}).addTo(map).bindPopup(popupContent, { maxWidth: 260, minWidth: 220, autoPanPadding: [20, 20] });
                markers.push(marker);

                const card = document.createElement('div');
                card.className = "bg-white p-4 rounded-2xl shadow-sm border border-slate-100 cursor-pointer active:scale-[0.98] transition-all hover:shadow-md hover:border-blue-100";
                
                let tagBgColor = "bg-slate-100 text-slate-500";
                if(loc.tag.includes("藝文")) tagBgColor = "bg-purple-100 text-purple-600";
                else if(loc.tag.includes("療癒")) tagBgColor = "bg-green-100 text-green-600";
                else if(loc.tag.includes("運動")) tagBgColor = "bg-red-100 text-red-600";
                else if(loc.tag.includes("放鬆")) tagBgColor = "bg-blue-100 text-blue-600";

                card.innerHTML = `
                    <div class="flex gap-4">
                        <div class="flex-shrink-0 w-14 h-14 rounded-2xl flex flex-col items-center justify-center text-white font-bold shadow-sm" style="background-color: ${markerColor}">
                            <span class="text-lg leading-none">${Math.round(loc.match_score)}</span>
                            <span class="text-[9px] opacity-80">分</span>
                        </div>
                        <div class="flex-1 min-w-0">
                            <div class="flex justify-between items-start mb-1">
                                <h4 class="font-bold text-slate-800 truncate text-base">${loc.name}</h4>
                                <span class="text-[10px] px-2 py-0.5 rounded-full ${tagBgColor}">${loc.tag}</span>
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
                document.getElementById('user-points').innerText = data.total_points;
                document.getElementById('modal-points').innerText = data.earned;
                document.getElementById('modal-text').innerText = `成功探索 ${name}`;
                
                const badgeNotif = document.getElementById('badge-notification');
                if(data.new_badge) {
                    badgeNotif.classList.remove('hidden');
                    document.getElementById('badge-name').innerText = data.new_badge;
                    updateLocalBadges(data.total_points);
                } else { badgeNotif.classList.add('hidden'); }

                const modal = document.getElementById('modal');
                const bell = document.getElementById('bell-icon');
                modal.classList.remove('hidden');
                
                const audio = new Audio('https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3');
                audio.play();

                setTimeout(() => { modal.classList.remove('opacity-0'); modal.querySelector('div').classList.remove('scale-90'); modal.querySelector('div').classList.add('scale-100'); }, 10);
                bell.classList.add('bell-animation');
                setTimeout(() => bell.classList.remove('bell-animation'), 1000);
            } catch(e) {}
        }

        function updateLocalBadges(points) {
            if(points >= 100) document.getElementById('badge-explorer').classList.remove('opacity-40');
            if(points >= 300) document.getElementById('badge-data').classList.remove('opacity-40');
        }

        function ringBell() {
            const bell = document.querySelector('#nav-bell i');
            bell.parentElement.classList.add('scale-90');
            setTimeout(() => bell.parentElement.classList.remove('scale-90'), 150);
            const audio = new Audio('https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3');
            audio.volume = 0.5;
            audio.play().catch(e => console.log("Audio play failed:", e));
            bell.parentElement.classList.add('bell-animation');
            setTimeout(() => bell.parentElement.classList.remove('bell-animation'), 1000);
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