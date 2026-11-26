from dotenv import load_dotenv
load_dotenv()
import os, sqlite3, smtplib, secrets
from email.message import EmailMessage
from flask import Flask, request, redirect, render_template_string, session, abort, flash
from functools import wraps
app=Flask(__name__)
app.secret_key=os.getenv('SECRET_KEY') or secrets.token_hex(32)
DB=os.getenv('DB_PATH','estoque.db')
def db():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
with db() as c:
 c.executescript('CREATE TABLE IF NOT EXISTS items(id INTEGER PRIMARY KEY,name TEXT UNIQUE,qty INTEGER CHECK(qty>=0),minimum INTEGER,code TEXT,category TEXT,unit TEXT,description TEXT); CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY,person TEXT,email TEXT,sector TEXT,item INTEGER,qty INTEGER,reason TEXT,status TEXT DEFAULT "Pendente",created TEXT DEFAULT CURRENT_TIMESTAMP, notified INTEGER DEFAULT 0);')
with db() as c:
 c.executescript("""CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT); CREATE TABLE IF NOT EXISTS movements(id INTEGER PRIMARY KEY,item INTEGER,delta INTEGER,reason TEXT,sector TEXT,created TEXT DEFAULT CURRENT_TIMESTAMP);""")
def setting(key,default=''):
 with db() as c:
  row=c.execute('SELECT value FROM settings WHERE key=?',(key,)).fetchone()
 return row[0] if row else default
def notify(subject,body,to):
 try:
  m=EmailMessage(); m['Subject']=subject; m['From']=os.environ['SMTP_USER']; m['To']=to; m.set_content(body)
  with smtplib.SMTP(os.environ['SMTP_HOST'],int(os.getenv('SMTP_PORT','587')),timeout=10) as s:
   s.starttls(); s.login(os.environ['SMTP_USER'],os.environ['SMTP_PASSWORD']); s.send_message(m)
  return True
 except Exception: return False
def admin(f):
 @wraps(f)
 def wrapped(*a,**k):
  if not session.get('admin'): return redirect('/login')
  return f(*a,**k)
 return wrapped
@app.before_request
def csrf():
 if 'csrf' not in session: session['csrf']=secrets.token_hex(24)
 if request.method=='POST' and not secrets.compare_digest(request.form.get('csrf',''),session['csrf']): abort(400)
PAGE='''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#101d48"><title>Samsung | Central de Materiais</title><style>
:root{--blue:#1428a0;--navy:#101d48;--ink:#18243c;--muted:#67758b;--line:#e0e6ef;--bg:#f4f6fa}*{box-sizing:border-box}body{margin:0;background:var(--bg);font:15px/1.55 Inter,Segoe UI,Arial,sans-serif;color:var(--ink)}a{color:var(--blue);text-decoration:none;font-weight:600}a:hover{text-decoration:underline}.shell{min-height:100vh;display:grid;grid-template-columns:248px minmax(0,1fr)}aside{background:var(--navy);color:#fff;padding:32px 22px;display:flex;flex-direction:column;gap:34px}.brand{font-size:24px;font-weight:900;letter-spacing:3px}.brand-sub{color:#a9b9e4;font-size:11px;letter-spacing:1.5px;text-transform:uppercase;margin-top:5px}.nav-label{font-size:10px;color:#9cafd7;letter-spacing:2px;text-transform:uppercase;margin:10px 12px}.nav a{display:block;color:#e5ebff;padding:13px 12px;border-radius:9px;margin:5px 0;font-size:14px}.nav a:hover,.nav a.active{background:#293e86;text-decoration:none}.nav a span{display:inline-block;width:28px}.aside-foot{margin-top:auto;color:#a9b9e4;font-size:12px;border-top:1px solid #33446f;padding-top:20px}.workspace{min-width:0}header{display:flex;justify-content:space-between;align-items:center;background:white;padding:18px 36px;border-bottom:1px solid var(--line);gap:12px}.crumb{color:var(--muted);font-size:13px}.pill{background:#edf2ff;color:var(--blue);border-radius:30px;padding:7px 13px;font-size:11px;font-weight:700;white-space:nowrap}.hero{border-radius:20px;padding:32px;color:white;background:linear-gradient(115deg,#1428a0,#254bc8 75%,#4573e2);position:relative;overflow:hidden;margin-bottom:24px}.hero:after{content:"";position:absolute;width:280px;height:280px;border:1px solid #ffffff35;border-radius:50%;right:-70px;top:-100px;box-shadow:0 0 0 30px #ffffff0c,0 0 0 60px #ffffff0a;pointer-events:none}.hero h1{font-size:clamp(25px,4vw,37px);margin:7px 0 8px;letter-spacing:-1.2px;line-height:1.15;color:white}.hero p{color:#e1e9ff;max-width:600px;margin:0}.eyebrow{font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#c5d5ff}main{max-width:1300px;margin:auto;padding:32px 36px}section{background:white;border:1px solid var(--line);padding:28px;border-radius:17px;margin-bottom:22px;box-shadow:0 5px 16px #15254a06}h1,h2,h3{letter-spacing:-.6px;line-height:1.25;margin:0 0 14px}h1{font-size:27px}h2{font-size:21px}h3{font-size:17px;margin-top:22px}p{margin:0 0 16px}section>p{color:var(--muted)}form{display:grid;gap:8px}label{font-size:13px;font-weight:650;margin-top:8px;color:#34425d}input,select,textarea,button{font:inherit;border-radius:9px;max-width:100%}input,select,textarea{width:100%;background:#fbfcfe;border:1px solid #d5deeb;padding:12px 13px;color:var(--ink);outline:none}input:focus,select:focus,textarea:focus{border-color:#4567d9;box-shadow:0 0 0 3px #4567d922}textarea{min-height:90px;resize:vertical}button{background:var(--blue);color:white;cursor:pointer;border:0;padding:12px 20px;font-weight:650;margin-top:8px;transition:background .15s,transform .15s}button:hover{background:#2039c5}button:active{transform:translateY(1px)}button:disabled{opacity:.45;cursor:not-allowed}button[value=reject]{background:#fce9e9;color:#9c3030}table{width:100%;border-collapse:collapse;font-size:13px;white-space:normal}th{background:#f5f7fb;color:#64728a;font-size:11px;text-transform:uppercase;letter-spacing:.7px}td,th{text-align:left;padding:15px 13px;border-bottom:1px solid var(--line)}td{vertical-align:middle}tr:hover td{background:#fafbfe}.scroll{overflow:auto;border:1px solid var(--line);border-radius:12px}td form{min-width:110px}td button{padding:8px 12px;font-size:12px}.msg{background:#eaf1ff;border:1px solid #cbdcff;padding:14px;border-radius:10px;color:#244498}footer{color:var(--muted);font-size:11px;padding:10px 0 24px}.portal main{max-width:940px}.portal section{max-width:100%}.portal section form{grid-template-columns:1fr 1fr;column-gap:20px}.portal section form label,.portal section form input,.portal section form select,.portal section form textarea,.portal section form button{grid-column:1/-1}.portal section form button{width:100%;margin-top:16px}.portal .hero{padding:38px}.portal section{padding:30px}.portal .shell{grid-template-columns:230px minmax(0,1fr)}.portal .brand-sub{font-size:10px}.info{padding:14px;border:1px solid #e2e9fa;border-radius:12px;background:#f6f8fd;color:#596b8a;font-size:13px;margin-bottom:20px}@media(min-width:900px){.portal section form{grid-template-columns:180px 1fr;align-items:center}.portal section form label{grid-column:1;margin:0}.portal section form input,.portal section form select,.portal section form textarea{grid-column:2}.portal section form button{grid-column:2}}@media(max-width:760px){.shell,.portal .shell{display:block}aside{padding:18px 20px;gap:12px}.nav{display:flex;flex-wrap:wrap;gap:4px}.nav a{margin:0;padding:8px 10px;font-size:12px}.nav-label,.aside-foot{display:none}header{padding:14px 20px}main{padding:18px}.hero,.portal .hero{padding:24px}section,.portal section{padding:19px}.brand{font-size:20px}td,th{padding:11px}.portal section form{display:block}.portal label{display:block;margin-top:12px}}
</style></head><body class="{{ 'admin' if session.get('admin') else 'portal' }}"><div class="shell"><aside><div><div class="brand">SAMSUNG</div><div class="brand-sub">Central de materiais</div></div><div><div class="nav-label">Navegação</div><nav class="nav">{% if session.get('admin') %}<a href="/admin" class="{{'active' if request.path=='/admin' else ''}}"><span>▦</span>Visão geral</a><a href="/movements" class="{{'active' if request.path=='/movements' else ''}}"><span>↔</span>Movimentações</a><a href="/settings" class="{{'active' if request.path=='/settings' else ''}}"><span>⚙</span>Configurações</a><a href="/"><span>↗</span>Portal do colaborador</a>{% else %}<a href="/" class="{{ 'active' if request.path=='/' else '' }}"><span>＋</span>Solicitar material</a><a href="/admin" class="{{ 'active' if request.path=='/login' else '' }}"><span>⚿</span>Portal administrativo</a>{% endif %}</nav></div><div class="aside-foot">Almoxarifado digital<br>Gestão e organização de recursos</div></aside><div class="workspace"><header><div class="crumb">Central de materiais / <strong>{{ 'Administração' if session.get('admin') else 'Solicitações' }}</strong></div><span class="pill">{{ 'ACESSO RESTRITO' if session.get('admin') else 'PORTAL DO COLABORADOR' }}</span></header><main><div class="hero"><div class="eyebrow">Gestão inteligente de recursos</div><h1>{{ 'Controle seu almoxarifado.' if session.get('admin') else ('Acesso administrativo' if request.path=='/login' else 'O material que você precisa, em um só lugar.') }}</h1><p>{{ 'Acompanhe os materiais, registre movimentações e gerencie as solicitações.' if session.get('admin') else ('Área exclusiva do responsável pelo estoque.' if request.path=='/login' else 'Solicite materiais para o seu departamento de forma simples e organizada.') }}</p></div>{% for m in get_flashed_messages() %}<p class="msg" role="status">{{m}}</p>{% endfor %}{{ body|safe }}<footer>Ambiente demonstrativo independente • Não insira dados corporativos reais.</footer></main></div></div></body></html>'''
def page(body,**kw): return render_template_string(PAGE,body=render_template_string(body,**kw))
TOKEN='<input type="hidden" name="csrf" value="{{session.csrf}}">'
@app.route('/',methods=['GET','POST'])
def home():
 if request.method=='POST':
  f=request.form
  try:
   qty=int(f['qty']); item=int(f['item'])
   if not 0<qty<=10000: raise ValueError()
  except (ValueError,KeyError): abort(400)
  if not all(f.get(k,'').strip() for k in ['person','email','sector']): abort(400)
  with db() as c:
   i=c.execute('SELECT * FROM items WHERE id=?',(item,)).fetchone()
   if not i: abort(400)
   oid=c.execute('INSERT INTO orders(person,email,sector,item,qty,reason) VALUES(?,?,?,?,?,?)',(f['person'],f['email'],f['sector'],item,qty,f.get('reason',''))).lastrowid
  ok=notify(f'Nova solicitação de material #{oid}',f"Colaborador: {f['person']}\nE-mail: {f['email']}\nSetor: {f['sector']}\nMaterial: {i['name']}\nQuantidade: {qty}\nJustificativa: {f.get('reason','')}",setting('recipient',os.getenv('STOCK_EMAIL','')))
  with db() as c: c.execute('UPDATE orders SET notified=? WHERE id=?',(int(ok),oid))
  flash(f'Solicitação #{oid} registrada. '+('E-mail enviado.' if ok else 'Notificação não enviada; pedido disponível no painel.'))
  return redirect('/')
 with db() as c: items=c.execute('SELECT * FROM items ORDER BY name').fetchall()
 return page('<section><h1>Solicitar material</h1><p>Preencha os dados para encaminhar seu pedido ao estoque.</p>{% if not items %}<p>Nenhum material cadastrado.</p>{% endif %}<form method="post">'+TOKEN+'''<label>Nome completo</label><input name="person" required maxlength="120"><label>E-mail corporativo</label><input type="email" name="email" required><label>Setor</label><input name="sector" required><label>Material</label><select name="item" required>{% for i in items %}<option value="{{i.id}}">{{i.name}}</option>{% endfor %}</select><label>Quantidade</label><input type="number" name="qty" min="1" max="10000" value="1" required><label>Justificativa</label><textarea name="reason" maxlength="1000"></textarea><button {% if not items %}disabled{% endif %}>Enviar solicitação</button></form></section>''',items=items)
@app.route('/login',methods=['GET','POST'])
def login():
 if request.method=='POST':
  password=os.getenv('ADMIN_PASSWORD')
  if password and secrets.compare_digest(request.form.get('password',''),password): session['admin']=True; return redirect('/admin')
  flash('Senha inválida ou administrador não configurado.')
 return page('<section><h1>Acesso do responsável</h1><form method="post">'+TOKEN+'<label>Senha</label><input type="password" name="password" required><button>Entrar</button></form></section>')
@app.route('/admin')
@admin
def dashboard():
 with db() as c:
  items=c.execute('SELECT * FROM items ORDER BY name').fetchall(); orders=c.execute('SELECT orders.*,items.name FROM orders JOIN items ON items.id=orders.item ORDER BY orders.id DESC').fetchall()
 return page('''<section><h1>Painel administrativo</h1><p><a href="/movements">Histórico e saída manual</a> · <a href="/settings">Configurações de e-mail</a></p><p>{{items|length}} materiais cadastrados • {{orders|selectattr('status','equalto','Pendente')|list|length}} pedidos pendentes</p><form method="post" action="/logout">'''+TOKEN+'''<button>Sair</button></form></section><section><h2>Estoque</h2><div class="scroll"><table><tr><th>Material</th><th>Saldo</th><th>Situação</th><th>Entrada</th><th>Editar</th></tr>{% for i in items %}<tr><td>{{i.name}}</td><td>{{i.qty}}</td><td>{{'Baixo' if i.qty<=i.minimum else 'Disponível'}}</td><td><form method="post" action="/stock/{{i.id}}">'''+TOKEN+'''<input type="number" name="qty" min="1" required style="width:100px"><button>Adicionar</button></form></td><td><a href="/items/{{i.id}}/edit">Editar</a></td></tr>{% endfor %}</table></div><h3>Novo material</h3><form method="post" action="/items">'''+TOKEN+'''<label>Nome</label><input name="name" required><label>Código</label><input name="code"><label>Categoria</label><input name="category"><label>Unidade</label><input name="unit" value="un"><label>Descrição</label><textarea name="description"></textarea><label>Estoque inicial</label><input name="qty" type="number" min="0" value="0" required><label>Estoque mínimo</label><input name="minimum" type="number" min="0" value="5" required><button>Cadastrar</button></form></section><section><h2>Solicitações</h2><div class="scroll"><table><tr><th>Pedido</th><th>Colaborador</th><th>Material</th><th>Status</th><th>E-mail</th><th>Ação</th></tr>{% for o in orders %}<tr><td>#{{o.id}}<br>{{o.created}}</td><td>{{o.person}}<br>{{o.sector}}<br>{{o.email}}<br>{{o.reason}}</td><td>{{o.qty}} × {{o.name}}</td><td>{{o.status}}</td><td>{{'Enviado' if o.notified else 'Não enviado'}}</td><td>{% if o.status=='Pendente' %}<form method="post" action="/orders/{{o.id}}">'''+TOKEN+'''<button name="action" value="deliver">Entregar</button><button name="action" value="reject">Recusar</button></form>{% endif %}</td></tr>{% endfor %}</table></div></section>''',items=items,orders=orders)
@app.post('/logout')
def logout(): session.clear(); return redirect('/')
@app.post('/items')
@admin
def add():
 try:
  q=int(request.form['qty']); m=int(request.form['minimum']); name=request.form['name'].strip()
  if min(q,m)<0 or not name: raise ValueError()
  with db() as c:
   iid=c.execute('INSERT INTO items(name,qty,minimum,code,category,unit,description) VALUES(?,?,?,?,?,?,?)',(name,q,m,*[request.form.get(k,'').strip() for k in ['code','category','unit','description']])).lastrowid
   if q: c.execute('INSERT INTO movements(item,delta,reason,sector) VALUES(?,?,?,?)',(iid,q,'Estoque inicial','Almoxarifado'))
 except (ValueError,sqlite3.IntegrityError): flash('Material inválido ou já cadastrado.')
 return redirect('/admin')
@app.route('/items/<int:i>/edit',methods=['GET','POST'])
@admin
def edit(i):
 with db() as c:
  item=c.execute('SELECT * FROM items WHERE id=?',(i,)).fetchone()
  if not item: abort(404)
  if request.method=='POST':
   try:
    q=int(request.form['qty']); m=int(request.form['minimum']); name=request.form['name'].strip()
    if min(q,m)<0 or not name: raise ValueError()
    c.execute('UPDATE items SET name=?,qty=?,minimum=?,code=?,category=?,unit=?,description=? WHERE id=?',(name,q,m,*[request.form.get(k,'').strip() for k in ['code','category','unit','description']],i))
    if q!=item['qty']: c.execute('INSERT INTO movements(item,delta,reason,sector) VALUES(?,?,?,?)',(i,q-item['qty'],'Ajuste manual','Almoxarifado'))
   except (ValueError,sqlite3.IntegrityError): flash('Dados inválidos ou nome duplicado.'); return redirect(request.path)
   flash('Material atualizado.'); return redirect('/admin')
 return page('<section><h1>Editar material</h1><form method="post">'+TOKEN+'''{% for k,l in [('name','Nome'),('code','Código'),('category','Categoria'),('unit','Unidade'),('description','Descrição')] %}<label>{{l}}</label><input name="{{k}}" value="{{item[k]}}" {% if k=='name' %}required{% endif %}>{% endfor %}<label>Saldo atual</label><input type="number" name="qty" min="0" value="{{item.qty}}" required><label>Estoque mínimo</label><input type="number" name="minimum" min="0" value="{{item.minimum}}" required><button>Salvar alterações</button></form></section>''',item=item)
@app.post('/stock/<int:i>')
@admin
def stock(i):
 try:
  q=int(request.form['qty'])
  if q<=0: raise ValueError()
 except ValueError: abort(400)
 with db() as c:
  if c.execute('UPDATE items SET qty=qty+? WHERE id=?',(q,i)).rowcount: c.execute('INSERT INTO movements(item,delta,reason,sector) VALUES(?,?,?,?)',(i,q,'Entrada manual','Almoxarifado'))
 return redirect('/admin')
@app.post('/orders/<int:i>')
@admin
def order(i):
 with db() as c:
  c.execute('BEGIN IMMEDIATE'); o=c.execute('SELECT * FROM orders WHERE id=? AND status="Pendente"',(i,)).fetchone()
  if not o: return redirect('/admin')
  if request.form.get('action')=='deliver':
   r=c.execute('UPDATE items SET qty=qty-? WHERE id=? AND qty>=?',(o['qty'],o['item'],o['qty']))
   if not r.rowcount: flash('Saldo insuficiente.'); return redirect('/admin')
   c.execute('INSERT INTO movements(item,delta,reason,sector) VALUES(?,?,?,?)',(o['item'],-o['qty'],'Entrega pedido #'+str(i),o['sector']))
   status='Entregue'
  elif request.form.get('action')=='reject': status='Recusado'
  else: abort(400)
  c.execute('UPDATE orders SET status=? WHERE id=?',(status,i))
 return redirect('/admin')
@app.route('/settings',methods=['GET','POST'])
@admin
def settings():
 if request.method=='POST':
  email=request.form.get('recipient','').strip()
  if email and ('@' not in email or '\\n' in email or '\\r' in email): abort(400)
  with db() as c: c.execute('INSERT OR REPLACE INTO settings VALUES(?,?)',('recipient',email))
  flash('Destinatário salvo. O servidor SMTP precisa ser configurado separadamente.')
  return redirect('/settings')
 return page('<section><h1>Configurações de e-mail</h1><p><a href="/admin">Voltar ao painel</a></p><form method="post">'+TOKEN+'<label>E-mail do responsável pelo estoque</label><input type="email" name="recipient" value="{{recipient}}"><button>Salvar</button></form><p>SMTP: {{smtp}}</p></section>',recipient=setting('recipient',os.getenv('STOCK_EMAIL','')),smtp='Configurado (envio não testado)' if all(os.getenv(k) for k in ['SMTP_HOST','SMTP_USER','SMTP_PASSWORD']) else 'Pendente')
@app.route('/movements',methods=['GET','POST'])
@admin
def movements():
 if request.method=='POST':
  try:
   i=int(request.form['item']); q=int(request.form['qty'])
   if q<=0: raise ValueError()
  except (ValueError,KeyError): abort(400)
  direction=request.form.get('direction')
  if direction not in ['in','out']: abort(400)
  delta=q if direction=='in' else -q
  reason=request.form.get('reason','').strip(); sector=request.form.get('sector','').strip()
  if not reason or not sector: abort(400)
  with db() as c:
   c.execute('BEGIN IMMEDIATE')
   if c.execute('UPDATE items SET qty=qty+? WHERE id=? AND qty+?>=0',(delta,i,delta)).rowcount:
    c.execute('INSERT INTO movements(item,delta,reason,sector) VALUES(?,?,?,?)',(i,delta,reason,sector)); flash('Movimentação registrada.')
   else: flash('Material inexistente ou saldo insuficiente.')
  return redirect('/movements')
 with db() as c:
  items=c.execute('SELECT * FROM items ORDER BY name').fetchall()
  logs=c.execute('SELECT movements.*,items.name FROM movements JOIN items ON items.id=movements.item ORDER BY movements.id DESC').fetchall()
 return page('<section><h1>Movimentações de estoque</h1><p><a href="/admin">Voltar ao painel</a></p><form method="post">'+TOKEN+'''<label>Tipo</label><select name="direction"><option value="in">Entrada</option><option value="out">Saída</option></select><label>Material</label><select name="item" required>{% for i in items %}<option value="{{i.id}}">{{i.name}} — saldo {{i.qty}}</option>{% endfor %}</select><label>Quantidade</label><input name="qty" type="number" min="1" required><label>Departamento ou origem</label><input name="sector" required><label>Motivo / responsável</label><input name="reason" required><button {% if not items %}disabled{% endif %}>Registrar movimentação</button></form></section><section><h2>Histórico</h2><div class="scroll"><table><tr><th>Data (UTC)</th><th>Material</th><th>Tipo</th><th>Quantidade</th><th>Departamento</th><th>Motivo</th></tr>{% for l in logs %}<tr><td>{{l.created}}</td><td>{{l.name}}</td><td>{{'Entrada' if l.delta>0 else 'Saída'}}</td><td>{{l.delta|abs}}</td><td>{{l.sector}}</td><td>{{l.reason}}</td></tr>{% endfor %}</table></div></section>''',items=items,logs=logs)
if __name__=='__main__': app.run(host='127.0.0.1',port=5000)
