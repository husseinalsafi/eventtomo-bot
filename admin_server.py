from flask import Flask, request, jsonify, make_response
import json, os, subprocess

app = Flask(__name__)
DAYS_FILE = '/root/eventtomo-bot/days.json'
PASSWORD = 'eventtomo2026'

@app.route('/')
def index():
    pw = request.cookies.get('et_pw','')
    if pw != PASSWORD:
        return LOGIN_HTML
    with open(DAYS_FILE,'r',encoding='utf-8') as f:
        days = json.load(f)
    return PANEL_HTML.replace('__DAYS__', json.dumps(days, ensure_ascii=False))

@app.route('/login', methods=['POST'])
def login():
    pw = request.form.get('pw','')
    if pw != PASSWORD:
        return LOGIN_HTML.replace('</form>','<p style="color:red">كلمة مرور خاطئة</p></form>')
    resp = make_response('<script>location.href="/"</script>')
    resp.set_cookie('et_pw', pw, max_age=86400*30)
    return resp

@app.route('/api/save', methods=['POST'])
def save():
    if request.cookies.get('et_pw') != PASSWORD:
        return jsonify({'ok':False}), 401
    with open(DAYS_FILE,'w',encoding='utf-8') as f:
        json.dump(request.json, f, ensure_ascii=False, indent=2)
    try:
        subprocess.run(['git','-C','/root/eventtomo-bot','add','days.json'],check=True)
        subprocess.run(['git','-C','/root/eventtomo-bot','commit','-m','backup: update days'],check=True)
        subprocess.run(['git','-C','/root/eventtomo-bot','push','origin','main'],check=True)
        return jsonify({'ok':True,'msg':'تم الحفظ على السيرفر وGitHub'})
    except Exception as e:
        return jsonify({'ok':True,'msg':'تم الحفظ على السيرفر فقط'})

LOGIN_HTML = """<!DOCTYPE html>
<html dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>يحدث غداً</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0e1a;min-height:100vh;display:flex;align-items:center;justify-content:center;font-family:system-ui}
.card{background:#1e293b;border-radius:20px;padding:40px;width:300px;text-align:center}
.logo{font-size:48px;margin-bottom:12px}
h1{color:#e2e8f0;font-size:20px;margin-bottom:6px}
p{color:#64748b;font-size:12px;margin-bottom:24px}
input{width:100%;padding:12px;border-radius:10px;border:1px solid #334155;background:#0f172a;color:#e2e8f0;font-size:15px;text-align:center;margin-bottom:12px}
button{width:100%;padding:12px;border-radius:10px;border:none;background:linear-gradient(135deg,#3b82f6,#06b6d4);color:white;font-size:15px;font-weight:700;cursor:pointer}
</style></head>
<body><div class="card">
<div class="logo">📅</div>
<h1>يحدث غداً</h1>
<p>لوحة إدارة الأيام والمناسبات</p>
<form method="post" action="/login">
<input type="password" name="pw" placeholder="كلمة المرور" autofocus>
<button type="submit">دخول ←</button>
</form></div></body></html>"""

PANEL_HTML = """<!DOCTYPE html>
<html dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>يحدث غداً</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0e1a;color:#e2e8f0;font-family:system-ui;padding:16px;max-width:600px;margin:0 auto}
h1{font-size:18px;margin-bottom:16px;color:#60a5fa;text-align:center}
.card{background:#1e293b;border-radius:12px;padding:16px;margin-bottom:12px}
input,select{width:100%;padding:10px;border-radius:8px;border:1px solid #334155;background:#0f172a;color:#e2e8f0;font-size:14px;margin-bottom:8px}
.row{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.btn{padding:10px;border-radius:8px;border:none;cursor:pointer;font-size:14px;font-weight:700;width:100%}
.btn-add{background:linear-gradient(135deg,#3b82f6,#06b6d4);color:white}
.btn-save{background:#16a34a;color:white;margin-top:8px}
.filters{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px}
.fb{padding:6px 12px;border-radius:20px;border:1px solid #334155;background:#1e293b;color:#94a3b8;cursor:pointer;font-size:12px}
.fb.on{background:#3b82f6;color:white;border-color:#3b82f6}
.item{background:#1e293b;border-radius:8px;padding:10px 12px;margin-bottom:6px;display:flex;justify-content:space-between;align-items:center}
.iname{font-size:13px;font-weight:600}
.idate{font-size:11px;color:#64748b;margin-top:2px}
.ibadge{font-size:10px;padding:2px 6px;border-radius:8px;display:inline-block;margin-top:3px}
.bi{background:rgba(59,130,246,0.2);color:#60a5fa}
.br{background:rgba(16,185,129,0.2);color:#34d399}
.bc{background:rgba(245,158,11,0.2);color:#fbbf24}
.del{background:none;border:none;color:#ef4444;cursor:pointer;font-size:16px}
.toast{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);padding:12px 20px;border-radius:10px;font-size:13px;font-weight:600;z-index:99;display:none;white-space:nowrap}
</style></head>
<body>
<h1>📅 يحدث غداً</h1>
<div class="card">
  <input id="nm" placeholder="اسم اليوم *">
  <div class="row">
    <select id="mo">
      <option value="1">يناير</option><option value="2">فبراير</option>
      <option value="3">مارس</option><option value="4">أبريل</option>
      <option value="5">مايو</option><option value="6">يونيو</option>
      <option value="7">يوليو</option><option value="8">أغسطس</option>
      <option value="9">سبتمبر</option><option value="10">أكتوبر</option>
      <option value="11">نوفمبر</option><option value="12">ديسمبر</option>
    </select>
    <input id="dy" type="number" placeholder="اليوم" min="1" max="31">
  </div>
  <div class="row">
    <input id="em" placeholder="إيموجي 📅">
    <select id="tp">
      <option value="international_days">🌍 عالمي</option>
      <option value="iraqi_national_days">🇮🇶 عراقي</option>
      <option value="custom_days">📌 خاص</option>
    </select>
  </div>
  <button class="btn btn-add" onclick="add()">➕ إضافة</button>
</div>
<div class="filters">
  <button class="fb on" onclick="flt('all',this)">الكل</button>
  <button class="fb" onclick="flt('international_days',this)">🌍 عالمي</button>
  <button class="fb" onclick="flt('iraqi_national_days',this)">🇮🇶 عراقي</button>
  <button class="fb" onclick="flt('custom_days',this)">📌 خاص</button>
</div>
<button class="btn btn-save" onclick="save()">💾 حفظ</button>
<div id="lst"></div>
<div class="toast" id="tst"></div>
<script>
var D=__DAYS__;
var cf='all';
var mn=['','يناير','فبراير','مارس','أبريل','مايو','يونيو','يوليو','أغسطس','سبتمبر','أكتوبر','نوفمبر','ديسمبر'];
function render(){
  var all=[];
  ['international_days','iraqi_national_days','custom_days'].forEach(function(c){
    (D[c]||[]).forEach(function(d){all.push(Object.assign({},d,{_c:c}))}); 
  });
  if(cf!='all')all=all.filter(function(d){return d._c===cf});
  all.sort(function(a,b){return a.month-b.month||a.day-b.day});
  var bl={international_days:'bi',iraqi_national_days:'br',custom_days:'bc'};
  var lb={international_days:'عالمي',iraqi_national_days:'عراقي',custom_days:'خاص'};
  document.getElementById('lst').innerHTML=all.map(function(d){
    return '<div class="item"><div><div class="iname">'+d.emoji+' '+d.name+'</div><div class="idate">'+d.day+' '+mn[d.month]+'</div><span class="ibadge '+bl[d._c]+'">'+lb[d._c]+'</span></div><button class="del" onclick="del(\\''+d._c+'\\','+d.month+','+d.day+')">🗑</button></div>';
  }).join('');
}
function flt(f,b){cf=f;document.querySelectorAll('.fb').forEach(function(x){x.classList.remove('on')});b.classList.add('on');render();}
function add(){
  var n=document.getElementById('nm').value.trim();
  var d=parseInt(document.getElementById('dy').value);
  var m=parseInt(document.getElementById('mo').value);
  var e=document.getElementById('em').value.trim()||'📅';
  var t=document.getElementById('tp').value;
  if(!n||!d)return toast('❌ أكمل الحقول','#ef4444');
  D[t].push({month:m,day:d,name:n,emoji:e});
  D[t].sort(function(a,b){return a.month-b.month||a.day-b.day});
  document.getElementById('nm').value='';document.getElementById('dy').value='';document.getElementById('em').value='';
  render();toast('✅ تمت الإضافة - اضغط حفظ','#16a34a');
}
function del(c,m,d){D[c]=D[c].filter(function(x){return!(x.month===m&&x.day===d)});render();toast('🗑 تم الحذف','#f59e0b');}
function save(){
  fetch('/api/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(D)})
  .then(function(r){return r.json()})
  .then(function(r){toast('✅ '+r.msg,'#16a34a')})
  .catch(function(){toast('❌ فشل الحفظ','#ef4444')});
}
function toast(m,c){var t=document.getElementById('tst');t.textContent=m;t.style.background=c;t.style.display='block';setTimeout(function(){t.style.display='none'},3000);}
render();
</script></body></html>"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
