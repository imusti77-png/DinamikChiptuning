# -*- coding: utf-8 -*-
import sys, os, shutil, sqlite3
from pathlib import Path
from datetime import datetime
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QAction
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton, QLineEdit,
    QVBoxLayout, QHBoxLayout, QGridLayout, QStackedWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox, QDialog,
    QFormLayout, QComboBox, QTextEdit, QDoubleSpinBox, QCheckBox, QScrollArea
)

APP_NAME = "Dinamik Chiptuning | ECU Yönetim Sistemi"
DATA = Path.home() / "Documents" / "DinamikChiptuning"
DB_PATH = DATA / "dinamik_pro.db"
FILE_DIR = DATA / "ECU_Arsiv"
DATA.mkdir(parents=True, exist_ok=True)
FILE_DIR.mkdir(parents=True, exist_ok=True)

OPERATIONS = {
    "Motor Yazılımı": ["Stage 1", "Stage 2", "Stage 3", "Eco Tuning", "Performans Yazılımı",
        "Güç / Tork Artırımı", "Tork Limiti Düzenleme", "Vmax / Hız Limiti", "Gaz Tepkisi (Throttle)"],
    "Emisyon / Egzoz": ["DPF", "EGR", "AdBlue / SCR", "NOx Sistemi", "OPF / GPF",
        "Katalizör", "Lambda / O2", "Sekonder Hava (SAI)", "Egzoz Klapesi"],
    "Şanzıman / Aktarma": ["TCU Yazılımı", "DSG / DCT", "Otomatik Şanzıman Adaptasyonu",
        "Tork Konvertörü", "Launch Control"],
    "Sürüş / Ek Fonksiyonlar": ["Start-Stop", "Pop & Bang", "Burble", "Hardcut / Limiter",
        "Cold Start", "Warm Start", "Devir Limiti", "Hız Sabitleyici", "Düşük Devir Torku"],
    "ECU / Diğer": ["DTC Arıza Yönetimi", "İmmobilizer", "Checksum Kontrolü", "ECU Klonlama",
        "ECU Virgin / Reset", "Swirl Flap", "TVA / Gaz Kelebeği", "Fan / Termostat Haritası",
        "MAF / MAP Kalibrasyonu"]
}
ALL_OPS = [op for group in OPERATIONS.values() for op in group]

def db():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

with db() as c:
    c.execute("""CREATE TABLE IF NOT EXISTS jobs(
        id INTEGER PRIMARY KEY AUTOINCREMENT, customer TEXT NOT NULL, phone TEXT, plate TEXT NOT NULL,
        brand TEXT, model TEXT, engine TEXT, ecu TEXT, sw TEXT, vin TEXT, operations TEXT,
        fee REAL DEFAULT 0, cost REAL DEFAULT 0, ori TEXT, mod TEXT, notes TEXT, created TEXT)""")

STYLE = """
QMainWindow, QWidget#root { background:#071426; color:#edf6ff; font-family:'Segoe UI'; }
QFrame#sidebar { background:#0b1c34; border-right:1px solid #1b4778; }
QFrame#topbar { background:#091a31; border-bottom:1px solid #1b4778; }
QFrame.panel { background:#0d2140; border:1px solid #1e4f83; border-radius:12px; }
QLabel { color:#edf6ff; }
QLabel.muted { color:#9db7d8; }
QLabel.cyan { color:#8bd8ff; }
QPushButton { background:#12345f; color:#eaf7ff; border:1px solid #2769a7; border-radius:8px; padding:9px 12px; font-weight:600; }
QPushButton:hover { background:#1a4e87; border:1px solid #62c9ff; }
QPushButton#primary { background:#1766c2; border:1px solid #58c2ff; color:white; }
QPushButton#primary:hover { background:#2385eb; }
QPushButton#nav { text-align:left; background:transparent; border:0; border-radius:7px; padding:12px 14px; color:#c6dcf4; }
QPushButton#nav:hover, QPushButton#nav[active="true"] { background:#123f76; color:#8bd8ff; border-left:3px solid #40baff; }
QLineEdit, QComboBox, QTextEdit, QDoubleSpinBox { background:#091a31; border:1px solid #28517e; border-radius:7px; padding:9px; color:#f4f9ff; selection-background-color:#1766c2; }
QTableWidget { background:#091a31; alternate-background-color:#0d2340; gridline-color:#1d426b; border:1px solid #1c4775; border-radius:8px; }
QHeaderView::section { background:#16365d; color:#aee5ff; padding:9px; border:0; font-weight:700; }
QCheckBox { spacing:8px; color:#e7f4ff; }
QCheckBox::indicator { width:16px; height:16px; }
QScrollArea { border:0; }
"""

def panel():
    f=QFrame(); f.setObjectName("panel"); f.setProperty("class","panel"); f.setStyleSheet("QFrame#panel{background:#0d2140;border:1px solid #1e4f83;border-radius:12px;}")
    return f

def title(text, size=20, color="#f4f9ff", weight=700):
    l=QLabel(text); l.setStyleSheet(f"font-size:{size}px;color:{color};font-weight:{weight};")
    return l

def muted(text, size=9):
    l=QLabel(text); l.setStyleSheet(f"font-size:{size}px;color:#9db7d8;")
    return l

class JobDialog(QDialog):
    def __init__(self, parent, record=None):
        super().__init__(parent); self.record=record; self.ori_src=""; self.mod_src=""
        self.setWindowTitle("Araç / Müşteri Kaydı"); self.resize(900,760)
        self.setStyleSheet(STYLE)
        root=QVBoxLayout(self)
        root.addWidget(title("ARAÇ & ECU İŞLEM KARTI",20,"#8bd8ff"))
        root.addWidget(muted("Müşteri, araç, ECU ve dosya bilgilerini kaydedin"))
        scroll=QScrollArea(); scroll.setWidgetResizable(True); root.addWidget(scroll)
        body=QWidget(); scroll.setWidget(body); layout=QVBoxLayout(body)
        form=QGridLayout(); layout.addLayout(form)
        self.fields={}
        keys=[("customer","Müşteri adı *"),("phone","Telefon"),("plate","Plaka *"),("brand","Marka"),
              ("model","Model"),("engine","Motor bilgisi"),("ecu","ECU markası"),("sw","ECU yazılım no"),
              ("vin","Şasi numarası")]
        for i,(key,label) in enumerate(keys):
            cell=QVBoxLayout(); cell.addWidget(muted(label))
            w=QLineEdit(); self.fields[key]=w
            if record: w.setText(record[key] or "")
            cell.addWidget(w); form.addLayout(cell,i//2,i%2)
        layout.addWidget(title("YAPILAN YAZILIM / ECU İŞLEMLERİ",14,"#8bd8ff"))
        self.checks={}
        for group, ops in OPERATIONS.items():
            box=panel(); bl=QVBoxLayout(box); bl.addWidget(title(group.upper(),10,"#68c9ff"))
            grid=QGridLayout()
            for idx,op in enumerate(ops):
                cb=QCheckBox(op)
                if record and op in (record["operations"] or "").split(" | "): cb.setChecked(True)
                self.checks[op]=cb; grid.addWidget(cb,idx//3,idx%3)
            bl.addLayout(grid); layout.addWidget(box)
        customrow=QHBoxLayout(); customrow.addWidget(muted("Diğer / özel işlem:"))
        self.custom=QLineEdit()
        if record:
            known=set(ALL_OPS); custom=self.custom
            custom.setText(", ".join(x for x in (record["operations"] or "").split(" | ") if x not in known))
        customrow.addWidget(self.custom); layout.addLayout(customrow)
        money=QHBoxLayout()
        self.fee=QDoubleSpinBox(); self.fee.setMaximum(99999999); self.fee.setSuffix(" TL"); self.fee.setDecimals(2)
        self.cost=QDoubleSpinBox(); self.cost.setMaximum(99999999); self.cost.setSuffix(" TL"); self.cost.setDecimals(2)
        if record: self.fee.setValue(record["fee"] or 0); self.cost.setValue(record["cost"] or 0)
        for label,w in [("Müşteriden alınan ücret",self.fee),("Maliyet",self.cost)]:
            col=QVBoxLayout(); col.addWidget(muted(label)); col.addWidget(w); money.addLayout(col)
        layout.addLayout(money)
        layout.addWidget(muted("İşlem notları"))
        self.notes=QTextEdit(); self.notes.setMaximumHeight(90)
        if record:self.notes.setPlainText(record["notes"] or "")
        layout.addWidget(self.notes)
        filebox=panel(); fb=QVBoxLayout(filebox); fb.addWidget(title("ORI / MOD DOSYA ARŞİVİ",13,"#8bd8ff"))
        self.ori_label=muted("ORI dosyası: "+(Path(record["ori"]).name if record and record["ori"] else "seçilmedi"))
        self.mod_label=muted("MOD dosyası: "+(Path(record["mod"]).name if record and record["mod"] else "seçilmedi"))
        fb.addWidget(self.ori_label); b=QPushButton("ORI dosyası seç"); b.clicked.connect(lambda:self.pick("ori")); fb.addWidget(b)
        fb.addWidget(self.mod_label); b=QPushButton("MOD dosyası seç"); b.clicked.connect(lambda:self.pick("mod")); fb.addWidget(b)
        layout.addWidget(filebox)
        buttons=QHBoxLayout(); save=QPushButton("KAYDI KAYDET"); save.setObjectName("primary"); save.clicked.connect(self.accept)
        cancel=QPushButton("VAZGEÇ"); cancel.clicked.connect(self.reject); buttons.addWidget(save); buttons.addWidget(cancel); layout.addLayout(buttons)
    def pick(self, kind):
        p,_=QFileDialog.getOpenFileName(self,f"{kind.upper()} dosyasını seç")
        if p:
            if kind=="ori": self.ori_src=p; self.ori_label.setText("ORI dosyası: "+Path(p).name)
            else: self.mod_src=p; self.mod_label.setText("MOD dosyası: "+Path(p).name)
    def values(self):
        d={k:w.text().strip() for k,w in self.fields.items()}
        ops=[k for k,v in self.checks.items() if v.isChecked()]
        if self.custom.text().strip(): ops += [x.strip() for x in self.custom.text().split(",") if x.strip()]
        d.update(operations=" | ".join(ops),fee=self.fee.value(),cost=self.cost.value(),
                 notes=self.notes.toPlainText().strip(),ori_src=self.ori_src,mod_src=self.mod_src)
        return d

class Main(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle(APP_NAME); self.resize(1500,920); self.setMinimumSize(1180,760)
        self.setStyleSheet(STYLE); self.selected_id=None
        root=QWidget(); root.setObjectName("root"); self.setCentralWidget(root)
        outer=QHBoxLayout(root); outer.setContentsMargins(0,0,0,0); outer.setSpacing(0)
        side=QFrame(); side.setObjectName("sidebar"); side.setFixedWidth(235); sv=QVBoxLayout(side); sv.setContentsMargins(12,18,12,16)
        brand=QVBoxLayout(); brand.addWidget(title("DİNAMİK",25,"#f4f9ff")); brand.addWidget(title("CHIPTUNING",13,"#47baff")); brand.addWidget(muted("ECU SOFTWARE MANAGEMENT",8)); sv.addLayout(brand); sv.addSpacing(22)
        self.stack=QStackedWidget(); self.pages={}
        navs=[("⌂  Ana Panel","dashboard"),("♙  Araç / Müşteri Kayıt","form"),("▤  İşlem Kayıtları","archive"),("▣  Dosya Arşivi (ORI/MOD)","archive"),("▦  ECU İşlem Kataloğu","catalog"),("▥  Raporlar & İstatistik","reports"),("☁  Yedekleme","backup")]
        self.nav_buttons=[]
        for text,key in navs:
            b=QPushButton(text); b.setObjectName("nav"); b.clicked.connect(lambda checked=False,k=key:self.navigate(k)); sv.addWidget(b); self.nav_buttons.append((b,key))
        sv.addStretch(); sv.addWidget(muted("LOCAL DATABASE • ACTIVE",8)); sv.addWidget(muted("Dinamik Chiptuning • İstanbul",8))
        outer.addWidget(side)
        right=QVBoxLayout(); right.setContentsMargins(18,14,18,12); right.setSpacing(12); outer.addLayout(right,1)
        top=QHBoxLayout(); top.addWidget(title("ARAÇ YAZILIM & İŞLEM TAKİP SİSTEMİ",16)); top.addStretch()
        self.search=QLineEdit(); self.search.setPlaceholderText("Plaka, müşteri, telefon veya ECU no ara..."); self.search.setFixedWidth(360); self.search.returnPressed.connect(lambda:self.navigate("archive")); top.addWidget(self.search)
        add=QPushButton("＋  YENİ KAYIT"); add.setObjectName("primary"); add.clicked.connect(self.new_job); top.addWidget(add); right.addLayout(top)
        self.stack=QStackedWidget(); right.addWidget(self.stack,1)
        self.make_pages(); self.navigate("dashboard")
        status=QHBoxLayout(); status.addWidget(muted("●  Veritabanı: Bağlı",9)); status.addStretch(); status.addWidget(muted("Veriler bu bilgisayarda saklanır • Düzenli yedek alın",9)); right.addLayout(status)
    def add_page(self,key,w):
        self.pages[key]=w; self.stack.addWidget(w)
    def make_pages(self):
        self.add_page("dashboard",self.dashboard_page())
        self.add_page("archive",self.archive_page())
        self.add_page("catalog",self.catalog_page())
        self.add_page("reports",self.reports_page())
        self.add_page("backup",self.backup_page())
        self.add_page("form",self.archive_page())
    def navigate(self,key):
        if key=="form": self.new_job(); return
        self.stack.setCurrentWidget(self.pages.get(key,self.pages["dashboard"]))
        for b,k in self.nav_buttons:b.setProperty("active",k==key);b.style().unpolish(b);b.style().polish(b)
        if key in ("dashboard","reports"): self.refresh_dashboard()
        if key=="archive": self.refresh_table()
    def metric(self,caption,value,accent="#8bd8ff",symbol="◆"):
        f=panel(); l=QVBoxLayout(f); row=QHBoxLayout(); row.addWidget(muted(caption.upper(),9)); row.addStretch(); row.addWidget(title(symbol,18,accent)); l.addLayout(row); l.addWidget(title(value,24,accent)); return f
    def dashboard_page(self):
        w=QWidget(); v=QVBoxLayout(w); v.setContentsMargins(0,0,0,0); v.addWidget(title("GENEL BAKIŞ",22)); v.addWidget(muted("Atölye performansı, araç kayıtları ve son işlemler"))
        grid=QGridLayout(); self.metrics=[]
        for i,(a,b,c,s) in enumerate([("Toplam araç","0","#8bd8ff","◈"),("Yapılan işlem","0","#51c8ff","▣"),("Toplam ciro","0 TL","#4de0c0","₺"),("Net kazanç","0 TL","#a4c8ff","↗"),("Toplam müşteri","0","#73baff","♙")]):
            card=self.metric(a,b,c,s); grid.addWidget(card,0,i); self.metrics.append((a,card))
        v.addLayout(grid)
        row=QHBoxLayout()
        recent=panel(); rv=QVBoxLayout(recent); rv.addWidget(title("SON KAYITLAR",13,"#8bd8ff")); self.recent=QTableWidget(0,6); self.recent.setHorizontalHeaderLabels(["Tarih","Plaka","Müşteri","Araç","İşlemler","Ücret"]); self.setup_table(self.recent); rv.addWidget(self.recent); row.addWidget(recent,3)
        quick=panel(); qv=QVBoxLayout(quick); qv.addWidget(title("HIZLI İŞLEMLER",13,"#8bd8ff"))
        for txt,fn in [("＋ Yeni araç kaydı",self.new_job),("▤ Tüm araçları görüntüle",lambda:self.navigate("archive")),("▣ ORI / MOD arşivi",lambda:self.navigate("archive")),("☁ Yedekleme klasörünü aç",self.open_data)]:
            b=QPushButton(txt); b.clicked.connect(fn); qv.addWidget(b)
        qv.addStretch(); qv.addWidget(muted("Kayıtlarınız yerel veritabanında saklanır.",8)); row.addWidget(quick,1); v.addLayout(row,1)
        return w
    def archive_page(self):
        w=QWidget(); v=QVBoxLayout(w); v.addWidget(title("ARAÇ & İŞLEM ARŞİVİ",21)); v.addWidget(muted("Plaka, müşteri, telefon ve ECU bilgilerine göre kayıt arayın"))
        self.archive_table=QTableWidget(0,9); self.archive_table.setHorizontalHeaderLabels(["No","Tarih","Plaka","Müşteri","Telefon","Araç","ECU / SW","İşlemler","Ücret"]); self.setup_table(self.archive_table); v.addWidget(self.archive_table,1)
        row=QHBoxLayout()
        for txt,fn in [("Düzenle",self.edit_selected),("ORI dosyasını aç",lambda:self.open_selected_file("ori")),("MOD dosyasını aç",lambda:self.open_selected_file("mod")),("Kaydı sil",self.delete_selected)]:
            b=QPushButton(txt); b.clicked.connect(fn); row.addWidget(b)
        row.addStretch(); v.addLayout(row)
        self.archive_table.itemSelectionChanged.connect(self.select_row)
        return w
    def catalog_page(self):
        w=QWidget(); v=QVBoxLayout(w); v.addWidget(title("ECU İŞLEM KATALOĞU",21)); v.addWidget(muted("Araçta yapılan tüm yazılım ve elektronik işlemlerini kayıt altına alın."))
        scroll=QScrollArea(); scroll.setWidgetResizable(True); body=QWidget(); grid=QGridLayout(body)
        for i,(group,ops) in enumerate(OPERATIONS.items()):
            f=panel(); fl=QVBoxLayout(f); fl.addWidget(title(group.upper(),13,"#8bd8ff"))
            for op in ops: fl.addWidget(muted("•  "+op,10))
            grid.addWidget(f,i//2,i%2)
        scroll.setWidget(body); v.addWidget(scroll); return w
    def reports_page(self):
        w=QWidget(); v=QVBoxLayout(w); v.addWidget(title("RAPORLAR & İSTATİSTİK",21)); v.addWidget(muted("Gelir, maliyet ve işlem hacmi özeti"))
        self.report_text=QLabel(); self.report_text.setStyleSheet("font-size:18px;color:#bdeaff;line-height:2;")
        f=panel(); fl=QVBoxLayout(f); fl.addWidget(self.report_text); v.addWidget(f); v.addStretch(); return w
    def backup_page(self):
        w=QWidget(); v=QVBoxLayout(w); v.addWidget(title("YEDEKLEME MERKEZİ",21)); v.addWidget(muted("Veritabanınızı ve ORI/MOD dosyalarınızı güvenli bir klasöre kopyalayın."))
        f=panel(); fl=QVBoxLayout(f); fl.addWidget(title("Yerel veri klasörü",14)); fl.addWidget(QLabel(str(DATA))); b=QPushButton("Veri klasörünü aç"); b.clicked.connect(self.open_data); fl.addWidget(b)
        b=QPushButton("Şimdi yedek al"); b.setObjectName("primary"); b.clicked.connect(self.backup); fl.addWidget(b); v.addWidget(f); v.addStretch(); return w
    def setup_table(self,t):
        t.setAlternatingRowColors(True); t.setEditTriggers(QTableWidget.NoEditTriggers); t.setSelectionBehavior(QTableWidget.SelectRows); t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); t.verticalHeader().setVisible(False)
    def refresh_dashboard(self):
        with db() as c:
            r=c.execute("SELECT COUNT(*) n,COALESCE(SUM(fee),0) rev,COALESCE(SUM(cost),0) cost,COUNT(DISTINCT phone) customers FROM jobs").fetchone()
            jobs=c.execute("SELECT * FROM jobs ORDER BY id DESC LIMIT 10").fetchall()
            op_count=c.execute("SELECT COUNT(*) n FROM jobs WHERE operations<>''").fetchone()["n"]
        vals=[str(r["n"]),str(op_count),f'{r["rev"]:,.2f} TL',f'{r["rev"]-r["cost"]:,.2f} TL',str(r["customers"])]
        for (name,card),value in zip(self.metrics,vals):
            card.findChild(QLabel).parent()
            labels=card.findChildren(QLabel)
            if len(labels)>1: labels[-1].setText(value)
        self.fill_table(self.recent,jobs,["created","plate","customer",None,"operations","fee"],recent=True)
        if hasattr(self,"report_text"):
            self.report_text.setText(f'Toplam araç: {r["n"]}\nToplam işlem kaydı: {op_count}\nToplam ciro: {r["rev"]:,.2f} TL\nToplam maliyet: {r["cost"]:,.2f} TL\nNet kazanç: {r["rev"]-r["cost"]:,.2f} TL')
    def fill_table(self,t,rows,fields,recent=False):
        t.setRowCount(0)
        for r in rows:
            i=t.rowCount(); t.insertRow(i)
            vals=[]
            for f in fields:
                if f is None: vals.append(f'{r["brand"] or ""} {r["model"] or ""}'.strip())
                elif f=="fee": vals.append(f'{r["fee"] or 0:,.2f} TL')
                else: vals.append(str(r[f] or ""))
            if not recent: vals=[str(r["id"])]+vals
            for j,val in enumerate(vals): t.setItem(i,j,QTableWidgetItem(val))
    def refresh_table(self):
        q=self.search.text().strip()
        with db() as c:
            rows=c.execute("SELECT * FROM jobs WHERE plate LIKE ? OR customer LIKE ? OR phone LIKE ? OR ecu LIKE ? OR sw LIKE ? ORDER BY id DESC",
                tuple(f"%{q}%" for _ in range(5))).fetchall()
        self.fill_table(self.archive_table,rows,["created","plate","customer","phone",None,"ecu","operations","fee"])
    def new_job(self):
        d=JobDialog(self)
        if d.exec()==QDialog.Accepted:self.save_record(d.values())
    def save_record(self,d):
        if not d["customer"] or not d["plate"]:
            QMessageBox.warning(self,"Eksik bilgi","Müşteri adı ve plaka zorunludur."); return
        def copy(src,kind):
            if not src:return ""
            folder=FILE_DIR/"".join(x if x.isalnum() or x in "-_" else "_" for x in d["plate"].upper()); folder.mkdir(parents=True,exist_ok=True)
            dest=folder/(datetime.now().strftime("%Y%m%d_%H%M%S_")+kind+"_"+Path(src).name); shutil.copy2(src,dest); return str(dest)
        ori=copy(d["ori_src"],"ORI"); mod=copy(d["mod_src"],"MOD")
        with db() as c:
            c.execute("""INSERT INTO jobs(customer,phone,plate,brand,model,engine,ecu,sw,vin,operations,fee,cost,ori,mod,notes,created)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",(d["customer"],d["phone"],d["plate"].upper(),d["brand"],d["model"],d["engine"],d["ecu"],d["sw"],d["vin"],d["operations"],d["fee"],d["cost"],ori,mod,d["notes"],datetime.now().strftime("%d.%m.%Y %H:%M")))
        self.refresh_dashboard(); self.refresh_table(); QMessageBox.information(self,"Dinamik Chiptuning","Kayıt başarıyla eklendi.")
    def select_row(self):
        row=self.archive_table.currentRow()
        self.selected_id=int(self.archive_table.item(row,0).text()) if row>=0 and self.archive_table.item(row,0) else None
    def edit_selected(self):
        QMessageBox.information(self,"Bilgi","Bu ilk arayüz sürümünde kayıt ekleme ve arşivleme aktiftir. Kayıt düzenleme sonraki sürüme eklenecek.")
    def open_selected_file(self,kind):
        if not self.selected_id:return QMessageBox.information(self,"Kayıt seç","Önce arşivden bir araç seçin.")
        with db() as c:r=c.execute(f"SELECT {kind} FROM jobs WHERE id=?",(self.selected_id,)).fetchone()
        p=r[kind] if r else ""
        if p and Path(p).exists():os.startfile(p) if os.name=="nt" else None
        else:QMessageBox.information(self,"Dosya yok",f"{kind.upper()} dosyası bulunamadı.")
    def delete_selected(self):
        if not self.selected_id:return
        if QMessageBox.question(self,"Onay","Seçili kayıt silinsin mi? Dosyalar arşiv klasöründe kalır.")==QMessageBox.Yes:
            with db() as c:c.execute("DELETE FROM jobs WHERE id=?",(self.selected_id,))
            self.selected_id=None;self.refresh_table();self.refresh_dashboard()
    def open_data(self):
        os.startfile(str(DATA)) if os.name=="nt" else None
    def backup(self):
        dest=QFileDialog.getExistingDirectory(self,"Yedekleme konumunu seç")
        if not dest:return
        target=Path(dest)/("DinamikChiptuning_Yedek_"+datetime.now().strftime("%Y%m%d_%H%M"))
        try:shutil.copytree(DATA,target);QMessageBox.information(self,"Yedek alındı",f"Yedek oluşturuldu:\n{target}")
        except Exception as e:QMessageBox.critical(self,"Yedekleme hatası",str(e))

if __name__=="__main__":
    app=QApplication(sys.argv); app.setStyle("Fusion"); app.setFont(QFont("Segoe UI",9))
    win=Main(); win.show(); sys.exit(app.exec())
